package com.smartlearn.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.smartlearn.client.AiServiceClient;
import com.smartlearn.config.ApiKeyHolder;
import com.smartlearn.config.UserContext;
import com.smartlearn.mapper.PracticeRecordMapper;
import com.smartlearn.model.dto.PracticeSubmitDTO;
import com.smartlearn.model.dto.PracticeSubmitResultDTO;
import com.smartlearn.model.entity.PracticeRecord;
import com.smartlearn.model.entity.Question;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class PracticeServiceIntegrationTest {

    private StubPracticeRecordMapper recordMapper;
    private StubQuestionService questionService;
    private StubAiServiceClient aiClient;
    private PracticeService service;
    private ObjectMapper objectMapper = new ObjectMapper();

    private static Question makeQuestion(Long id, String type, String correctAnswer) {
        Question q = new Question();
        q.setId(id);
        q.setType(type);
        q.setContent("Test question " + id);
        q.setCorrectAnswer(correctAnswer);
        q.setDifficulty(1);
        q.setOptions("[\"A\", \"B\", \"C\", \"D\"]");
        q.setKnowledgePointIds("[\"kp_basics\"]");
        return q;
    }

    @BeforeEach
    void setUp() {
        recordMapper = new StubPracticeRecordMapper();
        questionService = new StubQuestionService();
        aiClient = new StubAiServiceClient();
        service = new PracticeService(recordMapper, questionService, aiClient, objectMapper);
        UserContext.set(100L, "testuser");
        ApiKeyHolder.set("sk-test-key-for-integration-test");
    }

    @AfterEach
    void tearDown() {
        UserContext.clear();
        ApiKeyHolder.clear();
    }

    // --- auto judge mode ---

    @Test
    public void testAutoJudgeCorrectAnswer() {
        questionService.addQuestion(makeQuestion(1L, "single_choice", "A"));

        PracticeSubmitDTO dto = new PracticeSubmitDTO();
        dto.setUserId(100L);
        dto.setQuestionId(1L);
        dto.setUserAnswer("A");
        dto.setJudgeMode("auto");

        PracticeSubmitResultDTO result = service.submitAnswer(dto);
        assertTrue(result.getIsCorrect());
        assertEquals("learned", result.getStatus());
        assertEquals("auto", result.getJudgeMode());
        assertNotNull(result.getRecordId());
    }

    @Test
    public void testAutoJudgeWrongAnswer() {
        questionService.addQuestion(makeQuestion(2L, "single_choice", "A"));

        PracticeSubmitDTO dto = new PracticeSubmitDTO();
        dto.setUserId(100L);
        dto.setQuestionId(2L);
        dto.setUserAnswer("B");
        dto.setJudgeMode("auto");

        PracticeSubmitResultDTO result = service.submitAnswer(dto);
        assertFalse(result.getIsCorrect());
        assertEquals("incorrect", result.getStatus());
    }

    @Test
    public void testAutoJudgeCaseInsensitive() {
        questionService.addQuestion(makeQuestion(3L, "true_false", "True"));

        PracticeSubmitDTO dto = new PracticeSubmitDTO();
        dto.setUserId(100L);
        dto.setQuestionId(3L);
        dto.setUserAnswer("true");
        dto.setJudgeMode("auto");

        PracticeSubmitResultDTO result = service.submitAnswer(dto);
        assertTrue(result.getIsCorrect());
    }

    @Test
    public void testAutoJudgeEssayReturnsFalse() {
        questionService.addQuestion(makeQuestion(4L, "essay",
                "Polymorphism is the ability of objects to take many forms."));

        PracticeSubmitDTO dto = new PracticeSubmitDTO();
        dto.setUserId(100L);
        dto.setQuestionId(4L);
        dto.setUserAnswer("Polymorphism is the ability of objects to take many forms.");
        dto.setJudgeMode("auto");

        // Essay auto-judge should return false (cannot reliably score)
        PracticeSubmitResultDTO result = service.submitAnswer(dto);
        assertFalse(result.getIsCorrect());
    }

    // --- self judge mode ---

    @Test
    public void testSelfJudgeCreatesUnansweredRecord() {
        questionService.addQuestion(makeQuestion(5L, "single_choice", "B"));

        PracticeSubmitDTO dto = new PracticeSubmitDTO();
        dto.setUserId(100L);
        dto.setQuestionId(5L);
        dto.setUserAnswer("B");
        dto.setJudgeMode("self");

        PracticeSubmitResultDTO result = service.submitAnswer(dto);
        assertNull(result.getIsCorrect());
        assertEquals("unanswered", result.getStatus());
        assertEquals("B", result.getCorrectAnswer());
        assertEquals("self", result.getJudgeMode());
    }

    // --- ai judge mode ---

    @Test
    public void testAiJudgeCorrectAnswer() {
        questionService.addQuestion(makeQuestion(6L, "single_choice", "C"));

        PracticeSubmitDTO dto = new PracticeSubmitDTO();
        dto.setUserId(100L);
        dto.setQuestionId(6L);
        dto.setUserAnswer("C");
        dto.setJudgeMode("ai");

        PracticeSubmitResultDTO result = service.submitAnswer(dto);
        assertTrue(result.getIsCorrect());
        assertEquals("learned", result.getStatus());
        assertEquals("ai", result.getJudgeMode());
        assertNotNull(result.getAiAnalysis());
    }

    @Test
    public void testAiJudgeWrongAnswer() {
        questionService.addQuestion(makeQuestion(7L, "single_choice", "C"));

        PracticeSubmitDTO dto = new PracticeSubmitDTO();
        dto.setUserId(100L);
        dto.setQuestionId(7L);
        dto.setUserAnswer("D");
        dto.setJudgeMode("ai");

        PracticeSubmitResultDTO result = service.submitAnswer(dto);
        assertFalse(result.getIsCorrect());
        assertEquals("incorrect", result.getStatus());
    }

    // --- record lifecycle (insert vs update) ---

    @Test
    public void testSecondSubmissionUpdatesExistingRecord() {
        questionService.addQuestion(makeQuestion(8L, "single_choice", "A"));

        PracticeSubmitDTO dto = new PracticeSubmitDTO();
        dto.setUserId(100L);
        dto.setQuestionId(8L);
        dto.setUserAnswer("B");
        dto.setJudgeMode("auto");

        // First submission: insert
        PracticeSubmitResultDTO r1 = service.submitAnswer(dto);
        Long recordId = r1.getRecordId();
        assertFalse(r1.getIsCorrect());

        // Second submission: update same record
        dto.setUserAnswer("A");
        PracticeSubmitResultDTO r2 = service.submitAnswer(dto);
        assertEquals(recordId, r2.getRecordId()); // same record
        assertTrue(r2.getIsCorrect()); // now correct
    }

    // --- error handling ---

    @Test
    public void testNonexistentQuestionThrowsException() {
        PracticeSubmitDTO dto = new PracticeSubmitDTO();
        dto.setUserId(100L);
        dto.setQuestionId(999L);
        dto.setUserAnswer("A");
        dto.setJudgeMode("auto");

        assertThrows(RuntimeException.class, () -> service.submitAnswer(dto));
    }

    @Test
    public void testInvalidJudgeModeThrowsException() {
        questionService.addQuestion(makeQuestion(9L, "single_choice", "A"));

        PracticeSubmitDTO dto = new PracticeSubmitDTO();
        dto.setUserId(100L);
        dto.setQuestionId(9L);
        dto.setUserAnswer("A");
        dto.setJudgeMode("unknown");

        assertThrows(RuntimeException.class, () -> service.submitAnswer(dto));
    }

    @Test
    public void testUserIdFallsBackToUserContext() {
        questionService.addQuestion(makeQuestion(10L, "single_choice", "A"));

        PracticeSubmitDTO dto = new PracticeSubmitDTO();
        dto.setUserId(null); // should fall back to UserContext
        dto.setQuestionId(10L);
        dto.setUserAnswer("A");
        dto.setJudgeMode("auto");

        PracticeSubmitResultDTO result = service.submitAnswer(dto);
        assertTrue(result.getIsCorrect());
    }

    // --- missing API key ---

    @Test
    public void testAiJudgeWithoutApiKeyThrowsClearError() {
        ApiKeyHolder.clear(); // simulate no key configured
        questionService.addQuestion(makeQuestion(12L, "single_choice", "A"));

        PracticeSubmitDTO dto = new PracticeSubmitDTO();
        dto.setUserId(100L);
        dto.setQuestionId(12L);
        dto.setUserAnswer("A");
        dto.setJudgeMode("ai");

        RuntimeException ex = assertThrows(RuntimeException.class, () -> service.submitAnswer(dto));
        assertTrue(ex.getMessage().contains("API Key"));
    }

    // --- null answer ---

    @Test
    public void testNullUserAnswerAutoJudge() {
        questionService.addQuestion(makeQuestion(11L, "single_choice", "A"));

        PracticeSubmitDTO dto = new PracticeSubmitDTO();
        dto.setUserId(100L);
        dto.setQuestionId(11L);
        dto.setUserAnswer(null);
        dto.setJudgeMode("auto");

        PracticeSubmitResultDTO result = service.submitAnswer(dto);
        assertFalse(result.getIsCorrect());
        assertEquals("incorrect", result.getStatus());
    }

    // ==================================================================
    // Stubs
    // ==================================================================

    static class StubPracticeRecordMapper implements PracticeRecordMapper {
        private java.util.Map<Long, PracticeRecord> store = new java.util.HashMap<>();
        private long nextId = 1;

        @Override
        public PracticeRecord findByUserAndQuestion(Long userId, Long questionId) {
            return store.values().stream()
                    .filter(r -> userId.equals(r.getUserId()) && questionId.equals(r.getQuestionId()))
                    .findFirst().orElse(null);
        }

        @Override
        public int insert(PracticeRecord record) {
            record.setId(nextId++);
            store.put(record.getId(), record);
            return 1;
        }

        @Override
        public int update(PracticeRecord record) {
            if (store.containsKey(record.getId())) {
                store.put(record.getId(), record);
                return 1;
            }
            return 0;
        }

        @Override
        public PracticeRecord findById(Long id) { return store.get(id); }

        @Override
        public java.util.List<PracticeRecord> findByUserAndStatus(
                Long userId, String status, int offset, int size) { return java.util.Collections.emptyList(); }

        @Override
        public long countByUserAndStatus(Long userId, String status) { return 0; }

        @Override
        public long countByUser(Long userId) { return 0; }

        @Override
        public java.util.List<StatusCount> statsByUser(Long userId) { return java.util.Collections.emptyList(); }

        @Override
        public int updateStatus(Long id, String status) { return 0; }

        @Override
        public int selfJudge(Long id, boolean isCorrect, String status) { return 0; }

        @Override
        public int updateAiAnalysis(Long id, String json) { return 0; }
    }

    static class StubQuestionService extends QuestionService {
        private java.util.Map<Long, Question> questions = new java.util.HashMap<>();

        StubQuestionService() { super(null); }

        void addQuestion(Question q) { questions.put(q.getId(), q); }

        @Override
        public Question findById(Long id) { return questions.get(id); }
    }

    /**
     * Stub AiServiceClient that bypasses the RestTemplate constructor chain.
     *
     * The real AiServiceClient constructor dereferences config.getAiBaseUrl(),
     * so we create a minimal dummy to satisfy the constructor, then override
     * the 10-arg submitAnswer used by PracticeService.
     */
    static class StubAiServiceClient extends AiServiceClient {
        // The name "baseUrl" isn't accessible from here because it's private,
        // but the parent constructor stores it. We just need a non-null config.
        StubAiServiceClient() {
            super(new org.springframework.web.client.RestTemplate(),
                  new com.fasterxml.jackson.databind.ObjectMapper(),
                  new com.smartlearn.config.AiClientConfig() {
                      public String getAiBaseUrl() { return "http://localhost:8000"; }
                  });
        }

        @Override
        public AiServiceClient.AnswerAnalysisResponse submitAnswer(
                String userId, String questionId, String questionType,
                String questionContent, String[] options, String correctAnswer,
                String userAnswer, String[] knowledgePointIds, int difficulty) {
            AnswerAnalysisResponse resp = new AnswerAnalysisResponse();
            resp.user_id = userId;
            resp.question_id = questionId;
            resp.is_correct = correctAnswer.equalsIgnoreCase(
                    userAnswer != null ? userAnswer.trim() : "");
            resp.error_analysis = new ErrorAnalysis();
            resp.weak_point_analysis = new WeakPointAnalysis[0];
            resp.learning_path = new LearningPathNode[0];
            return resp;
        }
    }
}
