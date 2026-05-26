package com.smartlearn.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.smartlearn.client.AiServiceClient;
import com.smartlearn.config.ApiKeyHolder;
import com.smartlearn.config.UserContext;
import com.smartlearn.mapper.LearnProgressMapper;
import com.smartlearn.mapper.PdfImportMapper;
import com.smartlearn.mapper.QuestionMapper;
import com.smartlearn.model.dto.*;
import com.smartlearn.model.entity.LearnProgress;
import com.smartlearn.model.entity.PdfImport;
import com.smartlearn.model.entity.Question;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.*;

@Service
public class LearnService {
    private final LearnProgressMapper learnProgressMapper;
    private final PdfImportMapper pdfImportMapper;
    private final QuestionMapper questionMapper;
    private final AiServiceClient aiClient;
    private final ObjectMapper objectMapper = new ObjectMapper();

    public LearnService(LearnProgressMapper learnProgressMapper, PdfImportMapper pdfImportMapper,
                        QuestionMapper questionMapper, AiServiceClient aiClient) {
        this.learnProgressMapper = learnProgressMapper;
        this.pdfImportMapper = pdfImportMapper;
        this.questionMapper = questionMapper;
        this.aiClient = aiClient;
    }

    public Map<String, Object> generatePlan(Long pdfImportId) {
        Long userId = UserContext.getUserId();
        PdfImport pdf = pdfImportMapper.findById(pdfImportId);
        if (pdf == null) throw new RuntimeException("PDF not found");

        // Fetch all questions from this PDF
        List<Question> questions = questionMapper.findByBatchId(pdfImportId);
        if (questions == null || questions.isEmpty()) {
            throw new RuntimeException("No questions found for this PDF. Please re-import.");
        }

        // Build compact question list for FastAPI
        List<Map<String, Object>> questionList = new ArrayList<>();
        for (Question q : questions) {
            Map<String, Object> qMap = new HashMap<>();
            qMap.put("id", q.getId());
            qMap.put("topic", q.getTopic() != null ? q.getTopic() : "");
            qMap.put("type", q.getType());
            qMap.put("content", q.getContent());
            qMap.put("difficulty", q.getDifficulty());
            qMap.put("correctAnswer", q.getCorrectAnswer());
            questionList.add(qMap);
        }

        // Fail early if no API key configured
        if (ApiKeyHolder.get() == null || ApiKeyHolder.get().isEmpty()) {
            throw new RuntimeException("请先配置 DeepSeek API Key。点击右上角「设置」按钮，输入您的 API Key 即可使用 AI 功能。");
        }

        // Send all questions to FastAPI for LLM to read, summarize, and plan
        Map<String, Object> planResult = aiClient.generateLearnPlan(pdfImportId, pdf.getFilename(), questionList);
        List<Map<String, Object>> learningPath = (List<Map<String, Object>>) planResult.get("learningPath");
        if (learningPath == null) learningPath = new ArrayList<>();

        // Save progress
        LearnProgress progress = new LearnProgress();
        progress.setUserId(userId);
        progress.setPdfImportId(pdfImportId);
        progress.setCurrentNodeIndex(0);
        progress.setCurrentNodeState("explain");
        progress.setCompletedNodes("[]");
        progress.setReflectionLogJson("[]");
        progress.setQuizHistoryJson("[]");
        try {
            progress.setLearningPathJson(objectMapper.writeValueAsString(learningPath));
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Failed to serialize learning path", e);
        }

        LearnProgress existing = learnProgressMapper.findByUserAndPdf(userId, pdfImportId);
        if (existing != null) {
            progress.setId(existing.getId());
            learnProgressMapper.update(progress);
        } else {
            learnProgressMapper.insert(progress);
        }

        Map<String, Object> result = new HashMap<>();
        result.put("pdfName", pdf.getFilename());
        result.put("learningPath", learningPath);
        return result;
    }

    public Map<String, Object> getProgress(Long pdfImportId) {
        Long userId = UserContext.getUserId();
        LearnProgress progress = learnProgressMapper.findByUserAndPdf(userId, pdfImportId);
        if (progress == null) return null;

        PdfImport pdf = pdfImportMapper.findById(pdfImportId);

        try {
            List<Map<String, Object>> learningPath = objectMapper.readValue(
                    progress.getLearningPathJson(),
                    objectMapper.getTypeFactory().constructCollectionType(List.class, Map.class));
            List<Map<String, Object>> reflectionLog = objectMapper.readValue(
                    progress.getReflectionLogJson(),
                    objectMapper.getTypeFactory().constructCollectionType(List.class, Map.class));

            Map<String, Object> result = new HashMap<>();
            result.put("pdfName", pdf != null ? pdf.getFilename() : "");
            result.put("learningPath", learningPath);
            result.put("currentNodeIndex", progress.getCurrentNodeIndex());
            result.put("currentNodeState", progress.getCurrentNodeState());
            result.put("completedNodes", progress.getCompletedNodes());
            result.put("reflectionLog", reflectionLog);

            // Restore saved question if resuming in quiz state
            if (progress.getCurrentQuestionId() != null) {
                Question savedQ = questionMapper.findById(progress.getCurrentQuestionId());
                if (savedQ != null) {
                    Map<String, Object> qMap = questionToMap(savedQ);
                    result.put("currentQuestion", qMap);
                }
            }
            return result;
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Failed to parse learning progress", e);
        }
    }

    public List<Map<String, Object>> listProgress() {
        Long userId = UserContext.getUserId();
        List<LearnProgress> list = learnProgressMapper.findByUser(userId);
        List<Map<String, Object>> result = new ArrayList<>();
        for (LearnProgress p : list) {
            try {
                List<Map<String, Object>> learningPath = objectMapper.readValue(
                        p.getLearningPathJson(),
                        objectMapper.getTypeFactory().constructCollectionType(List.class, Map.class));

                PdfImport pdf = pdfImportMapper.findById(p.getPdfImportId());

                Map<String, Object> item = new HashMap<>();
                item.put("pdfImportId", p.getPdfImportId());
                item.put("pdfName", pdf != null ? pdf.getFilename() : "");
                item.put("completedCount", p.getCurrentNodeIndex() != null ? p.getCurrentNodeIndex() : 0);
                item.put("totalNodes", learningPath != null ? learningPath.size() : 0);
                item.put("updatedAt", p.getUpdatedAt() != null ? p.getUpdatedAt().toString() : null);
                result.add(item);
            } catch (JsonProcessingException e) {
                // skip corrupted records
            }
        }
        return result;
    }

    public Map<String, Object> submitAnswer(LearnSubmitRequest req) {
        Long userId = UserContext.getUserId();
        LearnProgress progress = learnProgressMapper.findByUserAndPdf(userId, req.getPdfImportId());
        if (progress == null) throw new RuntimeException("No learning progress found");

        if (ApiKeyHolder.get() == null || ApiKeyHolder.get().isEmpty()) {
            throw new RuntimeException("请先配置 DeepSeek API Key。点击右上角「设置」按钮，输入您的 API Key 即可使用 AI 功能。");
        }

        if (req.getCorrectAnswer() == null && req.getQuestion() != null) {
            Object ca = req.getQuestion().get("correctAnswer");
            if (ca != null) req.setCorrectAnswer(String.valueOf(ca));
        }

        Map<String, Object> reflectionResult = aiClient.submitLearnAnswer(req);

        try {
            List<Map<String, Object>> reflectionLog = objectMapper.readValue(
                    progress.getReflectionLogJson(),
                    objectMapper.getTypeFactory().constructCollectionType(List.class, Map.class));
            if (reflectionLog == null) reflectionLog = new ArrayList<>();
            Map<String, Object> entry = new HashMap<>();
            entry.put("nodeId", req.getKnowledgePointId());
            entry.put("summary", reflectionResult.get("reflectionSummary"));
            entry.put("conclusion", reflectionResult.get("conclusion"));
            entry.put("score", reflectionResult.get("score"));
            entry.put("level", reflectionResult.get("level"));
            entry.put("timestamp", LocalDateTime.now().toString());
            reflectionLog.add(entry);
            progress.setReflectionLogJson(objectMapper.writeValueAsString(reflectionLog));
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Failed to update reflection log", e);
        }

        String conclusion = (String) reflectionResult.get("conclusion");
        if ("forward".equals(conclusion)) {
            int next = (progress.getCurrentNodeIndex() != null ? progress.getCurrentNodeIndex() : 0) + 1;
            progress.setCurrentNodeIndex(next);
            progress.setCurrentNodeState("explain");
            progress.setCurrentQuestionId(null);
        } else if ("reinforce".equals(conclusion)) {
            progress.setCurrentNodeState("quiz");
        } else if ("rollback".equals(conclusion)) {
            progress.setCurrentQuestionId(null);
            String rollbackId = (String) reflectionResult.get("rollbackToNodeId");
            try {
                List<Map<String, Object>> learningPath = objectMapper.readValue(
                        progress.getLearningPathJson(),
                        objectMapper.getTypeFactory().constructCollectionType(List.class, Map.class));
                for (int i = 0; i < learningPath.size(); i++) {
                    Map<String, Object> node = learningPath.get(i);
                    Map<String, Object> kp = (Map<String, Object>) node.get("knowledgePoint");
                    if (kp != null && rollbackId.equals(kp.get("id"))) {
                        progress.setCurrentNodeIndex(i);
                        break;
                    }
                }
            } catch (JsonProcessingException e) {
                // keep current index
            }
            progress.setCurrentNodeState("explain");
        }

        learnProgressMapper.update(progress);
        return reflectionResult;
    }

    public Map<String, Object> markLearned(LearnMarkLearnedRequest req) {
        Long userId = UserContext.getUserId();
        LearnProgress progress = learnProgressMapper.findByUserAndPdf(userId, req.getPdfImportId());
        if (progress == null) throw new RuntimeException("No learning progress found");

        // Update state: explain -> quiz
        progress.setCurrentNodeState("quiz");

        // Get pre-matched question IDs from the learning path for this knowledge point
        Question question = null;
        try {
            List<Map<String, Object>> learningPath = objectMapper.readValue(
                    progress.getLearningPathJson(),
                    objectMapper.getTypeFactory().constructCollectionType(List.class, Map.class));
            int idx = progress.getCurrentNodeIndex() != null ? progress.getCurrentNodeIndex() : 0;
            if (idx < learningPath.size()) {
                Map<String, Object> node = learningPath.get(idx);
                List<Object> questionIds = (List<Object>) node.get("questionIds");
                if (questionIds != null && !questionIds.isEmpty()) {
                    // Pick the first unmatched question for this node
                    for (Object qidObj : questionIds) {
                        Long qid = Long.valueOf(String.valueOf(qidObj));
                        Question q = questionMapper.findById(qid);
                        if (q != null) {
                            question = q;
                            break;
                        }
                    }
                }
            }
        } catch (Exception e) {
            // fallback to random
        }

        // Fallback: query any question from this PDF's batch
        if (question == null) {
            List<Question> batchQuestions = questionMapper.findByBatchId(req.getPdfImportId());
            if (batchQuestions != null && !batchQuestions.isEmpty()) {
                question = batchQuestions.get(new Random().nextInt(batchQuestions.size()));
            }
        }

        Map<String, Object> qMap = new HashMap<>();
        if (question != null) {
            qMap.put("id", question.getId());
            qMap.put("type", question.getType());
            qMap.put("content", question.getContent());
            try {
                String optionsJson = question.getOptions();
                if (optionsJson != null && !optionsJson.isEmpty()) {
                    qMap.put("options", objectMapper.readValue(optionsJson, List.class));
                }
            } catch (JsonProcessingException e) {
                qMap.put("options", new ArrayList<>());
            }
            qMap.put("correctAnswer", question.getCorrectAnswer());
            qMap.put("knowledgePointIds", question.getKnowledgePointIds());
            qMap.put("difficulty", question.getDifficulty());

            // Save question ID so refresh can restore it
            progress.setCurrentQuestionId(question.getId());
        }

        learnProgressMapper.update(progress);

        Map<String, Object> wrapper = new HashMap<>();
        wrapper.put("question", qMap);
        return wrapper;
    }

    private Map<String, Object> questionToMap(Question q) {
        Map<String, Object> qMap = new HashMap<>();
        qMap.put("id", q.getId());
        qMap.put("type", q.getType());
        qMap.put("content", q.getContent());
        try {
            String opts = q.getOptions();
            if (opts != null && !opts.isEmpty()) {
                qMap.put("options", objectMapper.readValue(opts, List.class));
            }
        } catch (Exception e) {
            qMap.put("options", new ArrayList<>());
        }
        qMap.put("correctAnswer", q.getCorrectAnswer());
        qMap.put("knowledgePointIds", q.getKnowledgePointIds());
        qMap.put("difficulty", q.getDifficulty());
        return qMap;
    }

    public Map<String, Object> generateTest(Long pdfImportId) {
        Long userId = UserContext.getUserId();
        LearnProgress progress = learnProgressMapper.findByUserAndPdf(userId, pdfImportId);
        if (progress == null) throw new RuntimeException("No learning progress found");

        try {
            List<Map<String, Object>> learningPath = objectMapper.readValue(
                    progress.getLearningPathJson(),
                    objectMapper.getTypeFactory().constructCollectionType(List.class, Map.class));

            // Build knowledgePoints summary with questionIds
            List<Map<String, Object>> kpSummary = new ArrayList<>();
            int totalQ = 0;
            for (Map<String, Object> node : learningPath) {
                Map<String, Object> kp = new HashMap<>();
                Map<String, Object> kpObj = (Map<String, Object>) node.get("knowledgePoint");
                kp.put("name", kpObj != null ? kpObj.get("name") : "");
                kp.put("questionIds", node.get("questionIds"));
                kpSummary.add(kp);
                List<Object> qids = (List<Object>) node.get("questionIds");
                if (qids != null) totalQ += qids.size();
            }

            Map<String, Object> req = new HashMap<>();
            req.put("knowledgePoints", kpSummary);
            req.put("totalQuestions", totalQ);
            Map<String, Object> result = aiClient.generateTest(req);

            // Fetch full question data for selected IDs
            List<Object> selectedIds = (List<Object>) result.get("selectedIds");
            List<Map<String, Object>> testQuestions = new ArrayList<>();
            if (selectedIds != null) {
                for (Object qidObj : selectedIds) {
                    Long qid = Long.valueOf(String.valueOf(qidObj));
                    Question q = questionMapper.findById(qid);
                    if (q != null) {
                        Map<String, Object> qMap = new HashMap<>();
                        qMap.put("id", q.getId());
                        qMap.put("type", q.getType());
                        qMap.put("content", q.getContent());
                        try {
                            String opts = q.getOptions();
                            if (opts != null && !opts.isEmpty()) {
                                qMap.put("options", objectMapper.readValue(opts, List.class));
                            }
                        } catch (Exception e) {
                            qMap.put("options", new ArrayList<>());
                        }
                        qMap.put("correctAnswer", q.getCorrectAnswer());
                        qMap.put("difficulty", q.getDifficulty());
                        testQuestions.add(qMap);
                    }
                }
            }

            Map<String, Object> response = new HashMap<>();
            response.put("testQuestions", testQuestions);
            return response;
        } catch (Exception e) {
            throw new RuntimeException("Failed to generate test", e);
        }
    }

    public Map<String, Object> evaluateTest(Long pdfImportId, List<Map<String, Object>> answers, double threshold) {
        Long userId = UserContext.getUserId();
        LearnProgress progress = learnProgressMapper.findByUserAndPdf(userId, pdfImportId);
        if (progress == null) throw new RuntimeException("No learning progress found");

        try {
            List<Map<String, Object>> learningPath = objectMapper.readValue(
                    progress.getLearningPathJson(),
                    objectMapper.getTypeFactory().constructCollectionType(List.class, Map.class));

            // Build KP summary
            List<Map<String, Object>> kpSummary = new ArrayList<>();
            for (Map<String, Object> node : learningPath) {
                Map<String, Object> kp = new HashMap<>();
                Map<String, Object> kpObj = (Map<String, Object>) node.get("knowledgePoint");
                kp.put("name", kpObj != null ? kpObj.get("name") : "");
                kp.put("questionIds", node.get("questionIds"));
                kpSummary.add(kp);
            }

            Map<String, Object> req = new HashMap<>();
            req.put("answers", answers);
            req.put("knowledgePoints", kpSummary);
            req.put("threshold", threshold);
            Map<String, Object> evalResult = aiClient.evaluateTest(req);

            // If not passed, save new learning path
            Boolean passed = (Boolean) evalResult.get("passed");
            if (passed == null || !passed) {
                List<Map<String, Object>> newPath = (List<Map<String, Object>>) evalResult.get("newLearningPath");
                if (newPath != null && !newPath.isEmpty()) {
                    // Assign question IDs from original KPs to the new path where names match
                    for (Map<String, Object> newNode : newPath) {
                        Map<String, Object> kp = (Map<String, Object>) newNode.get("knowledgePoint");
                        String name = kp != null ? (String) kp.get("name") : "";
                        for (Map<String, Object> origNode : learningPath) {
                            Map<String, Object> origKp = (Map<String, Object>) origNode.get("knowledgePoint");
                            if (origKp != null && name.equals(origKp.get("name"))) {
                                newNode.put("questionIds", origNode.get("questionIds"));
                                break;
                            }
                        }
                    }
                    progress.setLearningPathJson(objectMapper.writeValueAsString(newPath));
                    progress.setCurrentNodeIndex(0);
                    progress.setCurrentNodeState("explain");
                    progress.setReflectionLogJson("[]");
                    learnProgressMapper.update(progress);
                }
            }

            return evalResult;
        } catch (Exception e) {
            throw new RuntimeException("Failed to evaluate test", e);
        }
    }

    public void deleteProgress(Long pdfImportId) {
        Long userId = UserContext.getUserId();
        learnProgressMapper.deleteByUserAndPdf(userId, pdfImportId);
    }
}
