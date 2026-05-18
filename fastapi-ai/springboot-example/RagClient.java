package com.smartlearn.client;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

/**
 * FastAPI AI 服务调用客户端
 * 核心接口: POST /api/analysis/submit-answer
 */
@Component
public class AiServiceClient {

    private final RestClient restClient;
    private final ObjectMapper objectMapper;

    public AiServiceClient(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
        this.restClient = RestClient.builder()
                .baseUrl("http://localhost:8000")
                .build();
    }

    // ==================== 核心：答案分析（SpringBoot -> FastAPI） ====================

    /**
     * 提交用户答题结果，获取错题解析 + 薄弱点分析 + 学习路径
     * POST /api/analysis/submit-answer
     */
    public AnswerAnalysisResponse submitAnswer(SubmitAnswerRequest request) {
        try {
            String body = objectMapper.writeValueAsString(request);
            return restClient.post()
                    .uri("/api/analysis/submit-answer")
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(body)
                    .retrieve()
                    .body(AnswerAnalysisResponse.class);
        } catch (JsonProcessingException e) {
            throw new RuntimeException("序列化请求失败", e);
        }
    }

    /**
     * 便捷方法：直接传参
     */
    public AnswerAnalysisResponse submitAnswer(
            String userId,
            String questionId,
            String questionType,
            String questionContent,
            String[] options,
            String correctAnswer,
            String userAnswer,
            String[] knowledgePointIds,
            int difficulty
    ) {
        SubmitAnswerRequest req = new SubmitAnswerRequest(
                userId,
                new QuestionItem(questionId, questionType, questionContent,
                        options, correctAnswer, knowledgePointIds, difficulty),
                userAnswer
        );
        return submitAnswer(req);
    }

    // ==================== RAG 问答 ====================

    public RagResponse queryRag(String question, String userId) {
        String body = String.format("""
            {"question": "%s", "user_id": "%s", "top_k": 5}
            """, escapeJson(question), escapeJson(userId));
        return restClient.post()
                .uri("/api/rag/query")
                .contentType(MediaType.APPLICATION_JSON)
                .body(body)
                .retrieve()
                .body(RagResponse.class);
    }

    // ==================== 知识图谱 ====================

    public KnowledgePoint[] searchKnowledge(String keyword) {
        String body = String.format("""
            {"keyword": "%s", "limit": 10}
            """, escapeJson(keyword));
        return restClient.post()
                .uri("/api/knowledge/search")
                .contentType(MediaType.APPLICATION_JSON)
                .body(body)
                .retrieve()
                .body(KnowledgePoint[].class);
    }

    // ==================== 健康检查 ====================

    public boolean healthCheck() {
        try {
            String result = restClient.get()
                    .uri("/api/health")
                    .retrieve()
                    .body(String.class);
            return result != null && result.contains("ok");
        } catch (Exception e) {
            return false;
        }
    }

    private String escapeJson(String s) {
        if (s == null) return "";
        return s.replace("\\", "\\\\")
                .replace("\"", "\\\"")
                .replace("\n", "\\n")
                .replace("\r", "\\r")
                .replace("\t", "\\t");
    }

    // ==================== DTO: 答案分析 ====================

    public record SubmitAnswerRequest(
            String user_id,
            QuestionItem question,
            String user_answer
    ) {}

    public record QuestionItem(
            String id,
            String type,
            String content,
            String[] options,
            String correct_answer,
            String[] knowledge_point_ids,
            int difficulty
    ) {}

    public record AnswerAnalysisResponse(
            String user_id,
            String question_id,
            boolean is_correct,
            ErrorAnalysis error_analysis,
            WeakPointAnalysis[] weak_point_analysis,
            LearningPathNode[] learning_path,
            String generated_at
    ) {}

    public record ErrorAnalysis(
            String user_answer,
            String correct_answer,
            String explanation,
            String error_type,
            String error_detail
    ) {}

    public record WeakPointAnalysis(
            String knowledge_point_id,
            String knowledge_point_name,
            double current_mastery,
            String reason
    ) {}

    // ==================== DTO: 通用 ====================

    public record RagResponse(
            String answer,
            RagSource[] sources,
            String[] related_knowledge_points
    ) {}

    public record RagSource(
            String title,
            String content_snippet,
            double score,
            String knowledge_point_id
    ) {}

    public record KnowledgePoint(
            String id,
            String name,
            String description,
            int difficulty,
            String category
    ) {}

    public record LearningPathNode(
            int order,
            KnowledgePoint knowledge_point,
            String reason
    ) {}
}
