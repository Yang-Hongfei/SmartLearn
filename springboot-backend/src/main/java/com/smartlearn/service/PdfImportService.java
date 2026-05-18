package com.smartlearn.service;

import com.smartlearn.client.AiServiceClient;
import com.smartlearn.mapper.PdfImportMapper;
import com.smartlearn.mapper.QuestionMapper;
import com.smartlearn.model.entity.PdfImport;
import com.smartlearn.model.entity.Question;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.text.PDFTextStripper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;
import java.util.Map;

@Service
public class PdfImportService {
    private static final Logger log = LoggerFactory.getLogger(PdfImportService.class);
    private static final int MAX_CHUNK_CHARS = 5000;

    private final PdfImportMapper importMapper;
    private final QuestionMapper questionMapper;
    private final AiServiceClient aiClient;

    @Value("${smartlearn.upload.path}")
    private String uploadPath;

    public PdfImportService(PdfImportMapper importMapper, QuestionMapper questionMapper, AiServiceClient aiClient) {
        this.importMapper = importMapper;
        this.questionMapper = questionMapper;
        this.aiClient = aiClient;
    }

    @Transactional
    public PdfImport uploadAndParse(MultipartFile file) {
        String filename = file.getOriginalFilename();
        long fileSize = file.getSize();

        // 1. Save file to disk
        Path uploadDir = Paths.get(uploadPath);
        try {
            Files.createDirectories(uploadDir);
        } catch (IOException e) {
            throw new RuntimeException("无法创建上传目录", e);
        }
        String savedName = UUID.randomUUID().toString().substring(0, 8) + "_" + filename;
        Path filePath = uploadDir.resolve(savedName);
        try {
            file.transferTo(filePath.toFile());
        } catch (IOException e) {
            throw new RuntimeException("文件保存失败", e);
        }

        // 2. Create import record
        PdfImport pdfImport = new PdfImport();
        pdfImport.setFilename(filename);
        pdfImport.setFileSize(fileSize);
        pdfImport.setStatus("processing");
        importMapper.insert(pdfImport);

        try {
            // 3. Extract text from PDF
            String fullText = extractText(filePath.toFile());
            pdfImport.setTotalPages(countPages(filePath.toFile()));
            pdfImport.setRawTextSnippet(fullText.length() > 2000 ? fullText.substring(0, 2000) : fullText);

            // 4. Split into chunks
            List<String> chunks = splitIntoChunks(fullText);
            pdfImport.setTotalChunks(chunks.size());
            importMapper.updateChunkProgress(pdfImport.getId(), 0, "processing");

            // 5. Process each chunk using Map-based response (more reliable deserialization)
            List<Map<String, Object>> allQuestions = new ArrayList<>();
            for (int i = 0; i < chunks.size(); i++) {
                AiServiceClient.PdfParseRequest request = new AiServiceClient.PdfParseRequest(
                        chunks.get(i), filename, i, chunks.size());
                Map responseMap = aiClient.parsePdfMap(request);
                if (responseMap != null && responseMap.containsKey("questions")) {
                    Object questionsObj = responseMap.get("questions");
                    if (questionsObj instanceof List) {
                        List<Map<String, Object>> chunkQuestions = (List<Map<String, Object>>) questionsObj;
                        allQuestions.addAll(chunkQuestions);
                        log.info("Chunk {}/{} parsed {} questions", i + 1, chunks.size(), chunkQuestions.size());
                    }
                }
                importMapper.updateChunkProgress(pdfImport.getId(), i + 1,
                        i + 1 < chunks.size() ? "processing" : "processing");
            }

            log.info("Total questions from all chunks: {}", allQuestions.size());

            // 6. Deduplicate & insert questions
            int inserted = 0;
            Set<String> seen = new HashSet<>();
            for (Map<String, Object> eq : allQuestions) {
                String content = (String) eq.getOrDefault("content", "");
                String key = !content.isEmpty() ? content.trim().substring(0, Math.min(50, content.length())) : "";
                if (key.isEmpty() || seen.contains(key)) continue;
                seen.add(key);

                Question q = new Question();
                q.setType((String) eq.getOrDefault("type", "essay"));
                q.setContent(content);
                Object optsObj = eq.get("options");
                q.setOptions(optsObj != null ? toJsonFromList((List<String>) optsObj) : null);
                q.setCorrectAnswer((String) eq.getOrDefault("answer", ""));
                Object kpObj = eq.get("knowledge_point_ids");
                q.setKnowledgePointIds(kpObj != null ? toJsonFromList((List<String>) kpObj) : null);
                Object diffObj = eq.get("difficulty");
                int diff = 3;
                if (diffObj instanceof Integer) diff = (Integer) diffObj;
                else if (diffObj instanceof Number) diff = ((Number) diffObj).intValue();
                q.setDifficulty(diff);
                q.setTopic((String) eq.getOrDefault("topic", ""));
                q.setSourcePdfName(filename);
                q.setImportBatchId(pdfImport.getId());
                questionMapper.insert(q);
                inserted++;
            }

            pdfImport.setQuestionsExtracted(inserted);
            pdfImport.setStatus("completed");
            importMapper.updateResult(pdfImport.getId(), inserted, "completed", null);

        } catch (Exception e) {
            log.error("PDF import failed", e);
            importMapper.updateResult(pdfImport.getId(), 0, "failed", e.getMessage());
            pdfImport.setStatus("failed");
            pdfImport.setErrorMessage(e.getMessage());
        }

        return pdfImport;
    }

    private String extractText(File file) throws IOException {
        try (PDDocument document = PDDocument.load(file)) {
            PDFTextStripper stripper = new PDFTextStripper();
            stripper.setSortByPosition(true);
            return stripper.getText(document);
        }
    }

    private int countPages(File file) {
        try (PDDocument document = PDDocument.load(file)) {
            return document.getNumberOfPages();
        } catch (IOException e) {
            return 0;
        }
    }

    private List<String> splitIntoChunks(String text) {
        List<String> chunks = new ArrayList<>();
        if (text.length() <= MAX_CHUNK_CHARS) {
            chunks.add(text);
            return chunks;
        }

        // Split by page markers or character count
        int start = 0;
        while (start < text.length()) {
            int end = Math.min(start + MAX_CHUNK_CHARS, text.length());
            // Try to find a good break point (page marker or double newline) near the end
            if (end < text.length()) {
                int breakPoint = -1;
                // Prefer page markers like "No. X / 89"
                int pageMarker = text.lastIndexOf("No. ", end);
                if (pageMarker > start && end - pageMarker < 500) {
                    breakPoint = pageMarker;
                }
                // Fallback to a newline near the boundary
                if (breakPoint < 0) {
                    int nl = text.lastIndexOf("\n", end);
                    if (nl > start && end - nl < 500) {
                        breakPoint = nl;
                    }
                }
                if (breakPoint > start) {
                    end = breakPoint;
                }
            }
            chunks.add(text.substring(start, end).trim());
            start = end;
        }
        return chunks;
    }

    private String toJsonFromList(List<String> arr) {
        if (arr == null) return null;
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < arr.size(); i++) {
            if (i > 0) sb.append(",");
            sb.append("\"").append(arr.get(i).replace("\"", "\\\"")).append("\"");
        }
        sb.append("]");
        return sb.toString();
    }

    private String toJson(String[] arr) {
        if (arr == null) return null;
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < arr.length; i++) {
            if (i > 0) sb.append(",");
            sb.append("\"").append(arr[i].replace("\"", "\\\"")).append("\"");
        }
        sb.append("]");
        return sb.toString();
    }

    public List<PdfImport> getImports(int page, int size) {
        return importMapper.findAll((page - 1) * size, size);
    }

    public long countImports() { return importMapper.count(); }

    public PdfImport getImport(Long id) { return importMapper.findById(id); }

    @Transactional
    public void deleteImport(Long id) {
        questionMapper.deleteByBatchId(id);
        importMapper.deleteById(id);
    }
}
