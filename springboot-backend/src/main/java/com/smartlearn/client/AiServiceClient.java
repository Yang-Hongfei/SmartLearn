package com.smartlearn.client;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.smartlearn.config.AiClientConfig;
import com.smartlearn.config.ApiKeyHolder;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import java.util.Map;
import java.util.HashMap;
import java.util.List;

@Component
public class AiServiceClient {
    private static final Logger log = LoggerFactory.getLogger(AiServiceClient.class);
    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;
    private final String baseUrl;

    public AiServiceClient(RestTemplate aiRestTemplate, ObjectMapper objectMapper, AiClientConfig config) {
        this.restTemplate = aiRestTemplate;
        this.objectMapper = objectMapper;
        this.baseUrl = config.getAiBaseUrl();
    }

    private HttpHeaders jsonHeaders() {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        String key = ApiKeyHolder.get();
        if (key != null && !key.isEmpty()) {
            headers.set("X-Api-Key", key);
        }
        return headers;
    }

    public AnswerAnalysisResponse submitAnswer(SubmitAnswerRequest request) {
        try {
            String body = objectMapper.writeValueAsString(request);
            HttpHeaders headers = jsonHeaders();
            HttpEntity<String> entity = new HttpEntity<>(body, headers);
            return restTemplate.postForObject(baseUrl + "/api/analysis/submit-answer", entity, AnswerAnalysisResponse.class);
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Failed to serialize request", e);
        }
    }

    public AnswerAnalysisResponse submitAnswer(String userId, String questionId, String questionType,
            String questionContent, String[] options, String correctAnswer, String userAnswer,
            String[] knowledgePointIds, int difficulty) {
        QuestionItem question = new QuestionItem(questionId, questionType, questionContent,
                options, correctAnswer, knowledgePointIds, difficulty);
        SubmitAnswerRequest request = new SubmitAnswerRequest(userId, question, userAnswer);
        return submitAnswer(request);
    }

    public Map parsePdfMap(PdfParseRequest request) {
        try {
            String body = objectMapper.writeValueAsString(request);
            HttpHeaders headers = jsonHeaders();
            HttpEntity<String> entity = new HttpEntity<>(body, headers);
            String rawResponse = restTemplate.postForObject(baseUrl + "/api/pdf/parse-qa", entity, String.class);
            log.info("FastAPI raw response length: {}", rawResponse != null ? rawResponse.length() : 0);
            if (rawResponse != null) {
                return objectMapper.readValue(rawResponse, Map.class);
            }
            return new HashMap();
        } catch (Exception e) {
            throw new RuntimeException("Failed to parse PDF", e);
        }
    }

    // --- Learn agent APIs ---

    public Map<String, Object> generateLearnPlan(Long pdfImportId, String pdfName, List<Map<String, Object>> questions) {
        try {
            Map<String, Object> req = new HashMap<>();
            req.put("pdf_import_id", pdfImportId);
            req.put("pdf_name", pdfName);
            req.put("questions", questions);
            String body = objectMapper.writeValueAsString(req);
            HttpHeaders headers = jsonHeaders();
            HttpEntity<String> entity = new HttpEntity<>(body, headers);
            String rawResponse = restTemplate.postForObject(baseUrl + "/api/learn/generate-plan", entity, String.class);
            if (rawResponse != null) {
                return objectMapper.readValue(rawResponse, Map.class);
            }
            return new HashMap<>();
        } catch (Exception e) {
            throw new RuntimeException("Failed to generate learn plan", e);
        }
    }

    public Map<String, Object> submitLearnAnswer(Object request) {
        try {
            String body = objectMapper.writeValueAsString(request);
            HttpHeaders headers = jsonHeaders();
            HttpEntity<String> entity = new HttpEntity<>(body, headers);
            String rawResponse = restTemplate.postForObject(baseUrl + "/api/learn/submit-answer", entity, String.class);
            if (rawResponse != null) {
                return objectMapper.readValue(rawResponse, Map.class);
            }
            return new HashMap<>();
        } catch (Exception e) {
            throw new RuntimeException("Failed to submit learn answer", e);
        }
    }

    // --- Config ---

    public Map<String, Object> getApiKeyStatus() {
        try {
            String raw = restTemplate.getForObject(baseUrl + "/api/config/api-key", String.class);
            if (raw != null) return objectMapper.readValue(raw, Map.class);
            return new HashMap<>();
        } catch (Exception e) {
            throw new RuntimeException("Failed to get API key status", e);
        }
    }

    public Map<String, Object> setApiKey(String apiKey) {
        try {
            Map<String, Object> req = new HashMap<>();
            req.put("api_key", apiKey);
            String body = objectMapper.writeValueAsString(req);
            HttpHeaders headers = jsonHeaders();
            HttpEntity<String> entity = new HttpEntity<>(body, headers);
            String raw = restTemplate.postForObject(baseUrl + "/api/config/api-key", entity, String.class);
            if (raw != null) return objectMapper.readValue(raw, Map.class);
            return new HashMap<>();
        } catch (Exception e) {
            throw new RuntimeException("Failed to set API key", e);
        }
    }

    public Map<String, Object> markLearned(Long pdfImportId, String knowledgePointId) {
        try {
            Map<String, Object> req = new HashMap<>();
            req.put("pdf_import_id", pdfImportId);
            req.put("knowledge_point_id", knowledgePointId);
            String body = objectMapper.writeValueAsString(req);
            HttpHeaders headers = jsonHeaders();
            HttpEntity<String> entity = new HttpEntity<>(body, headers);
            String rawResponse = restTemplate.postForObject(baseUrl + "/api/learn/mark-learned", entity, String.class);
            if (rawResponse != null) {
                return objectMapper.readValue(rawResponse, Map.class);
            }
            return new HashMap<>();
        } catch (Exception e) {
            throw new RuntimeException("Failed to mark learned", e);
        }
    }

    // --- Test generation & evaluation ---

    public Map<String, Object> generateTest(Object request) {
        try {
            String body = objectMapper.writeValueAsString(request);
            HttpHeaders headers = jsonHeaders();
            HttpEntity<String> entity = new HttpEntity<>(body, headers);
            String rawResponse = restTemplate.postForObject(baseUrl + "/api/learn/generate-test", entity, String.class);
            if (rawResponse != null) {
                return objectMapper.readValue(rawResponse, Map.class);
            }
            return new HashMap<>();
        } catch (Exception e) {
            throw new RuntimeException("Failed to generate test", e);
        }
    }

    public Map<String, Object> evaluateTest(Object request) {
        try {
            String body = objectMapper.writeValueAsString(request);
            HttpHeaders headers = jsonHeaders();
            HttpEntity<String> entity = new HttpEntity<>(body, headers);
            String rawResponse = restTemplate.postForObject(baseUrl + "/api/learn/evaluate-test", entity, String.class);
            if (rawResponse != null) {
                return objectMapper.readValue(rawResponse, Map.class);
            }
            return new HashMap<>();
        } catch (Exception e) {
            throw new RuntimeException("Failed to evaluate test", e);
        }
    }

    public PdfParseResponse parsePdf(PdfParseRequest request) {
        try {
            String body = objectMapper.writeValueAsString(request);
            HttpHeaders headers = jsonHeaders();
            HttpEntity<String> entity = new HttpEntity<>(body, headers);
            return restTemplate.postForObject(baseUrl + "/api/pdf/parse-qa", entity, PdfParseResponse.class);
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Failed to serialize PDF parse request", e);
        }
    }

    // --- DTO classes (Java 8, no records) ---

    public static class SubmitAnswerRequest {
        public String user_id;
        public QuestionItem question;
        public String user_answer;
        public SubmitAnswerRequest() {}
        public SubmitAnswerRequest(String user_id, QuestionItem question, String user_answer) {
            this.user_id = user_id; this.question = question; this.user_answer = user_answer;
        }
    }
    public static class QuestionItem {
        public String id, type, content;
        public String[] options;
        public String correct_answer;
        public String[] knowledge_point_ids;
        public int difficulty;
        public QuestionItem() {}
        public QuestionItem(String id, String type, String content, String[] options,
                String correct_answer, String[] knowledge_point_ids, int difficulty) {
            this.id = id; this.type = type; this.content = content; this.options = options;
            this.correct_answer = correct_answer; this.knowledge_point_ids = knowledge_point_ids;
            this.difficulty = difficulty;
        }
    }
    public static class AnswerAnalysisResponse {
        public String user_id, question_id, generated_at;
        public boolean is_correct;
        public ErrorAnalysis error_analysis;
        public WeakPointAnalysis[] weak_point_analysis;
        public LearningPathNode[] learning_path;
    }
    public static class ErrorAnalysis {
        public String user_answer, correct_answer, explanation, error_type, error_detail;
    }
    public static class WeakPointAnalysis {
        public String knowledge_point_id, knowledge_point_name, reason;
        public double current_mastery;
    }
    public static class LearningPathNode {
        public int order;
        public KnowledgePoint knowledge_point;
        public String reason;
    }
    public static class KnowledgePoint {
        public String id, name, description, category;
        public int difficulty;
    }
    public static class PdfParseRequest {
        public String raw_text, filename;
        public int chunk_index, total_chunks;
        public PdfParseRequest() {}
        public PdfParseRequest(String raw_text, String filename, int chunk_index, int total_chunks) {
            this.raw_text = raw_text; this.filename = filename;
            this.chunk_index = chunk_index; this.total_chunks = total_chunks;
        }
    }
    public static class PdfParseResponse {
        public ExtractedQuestion[] questions;
        public int total_extracted;
        public String[] topics_found;
    }
    public static class ExtractedQuestion {
        public String topic, question_number, content, type;
        public String[] options;
        public String answer;
        public int difficulty;
        public String[] knowledge_point_ids;
    }
}
