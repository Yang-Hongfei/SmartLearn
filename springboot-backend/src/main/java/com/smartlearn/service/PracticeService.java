package com.smartlearn.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.smartlearn.client.AiServiceClient;
import com.smartlearn.mapper.PracticeRecordMapper;
import com.smartlearn.model.entity.PracticeRecord;
import com.smartlearn.model.entity.Question;
import com.smartlearn.model.dto.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.*;

@Service
public class PracticeService {
    private static final Logger log = LoggerFactory.getLogger(PracticeService.class);
    private final PracticeRecordMapper recordMapper;
    private final QuestionService questionService;
    private final AiServiceClient aiClient;
    private final ObjectMapper objectMapper;

    public PracticeService(PracticeRecordMapper recordMapper, QuestionService questionService,
                           AiServiceClient aiClient, ObjectMapper objectMapper) {
        this.recordMapper = recordMapper;
        this.questionService = questionService;
        this.aiClient = aiClient;
        this.objectMapper = objectMapper;
    }

    @Transactional
    public PracticeSubmitResultDTO submitAnswer(PracticeSubmitDTO dto) {
        Question question = questionService.findById(dto.getQuestionId());
        if (question == null) throw new RuntimeException("题目不存在");

        String judgeMode = dto.getJudgeMode();
        PracticeRecord record = recordMapper.findByUserAndQuestion(dto.getUserId(), dto.getQuestionId());
        boolean isNew = (record == null);

        if (isNew) {
            record = new PracticeRecord();
            record.setUserId(dto.getUserId());
            record.setQuestionId(dto.getQuestionId());
        }

        PracticeSubmitResultDTO result = new PracticeSubmitResultDTO();
        result.setJudgeMode(judgeMode);

        if ("auto".equals(judgeMode)) {
            boolean correct = autoJudge(question.getType(), dto.getUserAnswer(), question.getCorrectAnswer());
            record.setUserAnswer(dto.getUserAnswer());
            record.setIsCorrect(correct);
            record.setJudgeMode("auto");
            record.setStatus(correct ? "learned" : "incorrect");
            saveRecord(isNew, record);
            result.setRecordId(record.getId());
            result.setIsCorrect(correct);
            result.setStatus(record.getStatus());

        } else if ("self".equals(judgeMode)) {
            record.setUserAnswer(dto.getUserAnswer());
            record.setIsCorrect(null);
            record.setJudgeMode("self");
            record.setStatus("unanswered");
            saveRecord(isNew, record);
            result.setRecordId(record.getId());
            result.setCorrectAnswer(question.getCorrectAnswer());
            result.setStatus("unanswered");

        } else if ("ai".equals(judgeMode)) {
            record.setUserAnswer(dto.getUserAnswer());
            record.setJudgeMode("ai");
            String[] kpIds = parseJsonArray(question.getKnowledgePointIds());
            String[] options = parseJsonArray(question.getOptions());
            try {
                AiServiceClient.AnswerAnalysisResponse aiResult = aiClient.submitAnswer(
                        "user_" + dto.getUserId(),
                        "q_" + question.getId(),
                        question.getType(),
                        question.getContent(),
                        options,
                        question.getCorrectAnswer(),
                        dto.getUserAnswer(),
                        kpIds,
                        question.getDifficulty() != null ? question.getDifficulty() : 1
                );
                record.setIsCorrect(aiResult.is_correct);
                record.setStatus(aiResult.is_correct ? "learned" : "incorrect");
                Map<String, Object> aiMap = objectMapper.convertValue(aiResult, Map.class);
                record.setAiAnalysisJson(objectMapper.writeValueAsString(aiMap));
                saveRecord(isNew, record);
                result.setRecordId(record.getId());
                result.setIsCorrect(aiResult.is_correct);
                result.setStatus(record.getStatus());
                result.setAiAnalysis(aiMap);
            } catch (Exception e) {
                log.error("AI judging failed", e);
                record.setIsCorrect(null);
                record.setStatus("unanswered");
                saveRecord(isNew, record);
                throw new RuntimeException("AI判题失败: " + e.getMessage());
            }
        } else {
            throw new RuntimeException("无效的判题模式: " + judgeMode);
        }
        return result;
    }

    public PracticeRecord selfJudge(Long recordId, boolean isCorrect) {
        PracticeRecord record = recordMapper.findById(recordId);
        if (record == null) throw new RuntimeException("记录不存在");
        String status = isCorrect ? "learned" : "incorrect";
        recordMapper.selfJudge(recordId, isCorrect, status);
        record.setIsCorrect(isCorrect);
        record.setStatus(status);
        return record;
    }

    public void updateStatus(Long recordId, String status) {
        recordMapper.updateStatus(recordId, status);
    }

    public PageResult<PracticeRecord> getRecords(Long userId, String status, int page, int size) {
        int offset = (page - 1) * size;
        List<PracticeRecord> records;
        long total;
        if (status != null && !status.isEmpty()) {
            records = recordMapper.findByUserAndStatus(userId, status, offset, size);
            total = recordMapper.countByUserAndStatus(userId, status);
        } else {
            records = recordMapper.findByUserAndStatus(userId, null, offset, size);
            total = recordMapper.countByUser(userId);
        }
        return new PageResult<PracticeRecord>(records, total, page, size);
    }

    public PracticeStatsDTO getStats(Long userId) {
        List<PracticeRecordMapper.StatusCount> counts = recordMapper.statsByUser(userId);
        long total = recordMapper.countByUser(userId);
        long learned = 0, unanswered = 0, incorrect = 0;
        for (PracticeRecordMapper.StatusCount sc : counts) {
            String s = sc.getStatus();
            if ("learned".equals(s)) learned = sc.getCnt();
            else if ("unanswered".equals(s)) unanswered = sc.getCnt();
            else if ("incorrect".equals(s)) incorrect = sc.getCnt();
        }
        return new PracticeStatsDTO(total, learned, unanswered, incorrect);
    }

    @Transactional
    public Map<String, Object> aiAnalysis(Long recordId) {
        PracticeRecord record = recordMapper.findById(recordId);
        if (record == null) throw new RuntimeException("记录不存在");
        Question question = questionService.findById(record.getQuestionId());
        if (question == null) throw new RuntimeException("题目不存在");

        String[] kpIds = parseJsonArray(question.getKnowledgePointIds());
        String[] options = parseJsonArray(question.getOptions());
        try {
            AiServiceClient.AnswerAnalysisResponse aiResult = aiClient.submitAnswer(
                    "user_" + record.getUserId(),
                    "q_" + question.getId(),
                    question.getType(),
                    question.getContent(),
                    options,
                    question.getCorrectAnswer(),
                    record.getUserAnswer(),
                    kpIds,
                    question.getDifficulty() != null ? question.getDifficulty() : 1
            );
            Map<String, Object> aiMap = objectMapper.convertValue(aiResult, Map.class);
            recordMapper.updateAiAnalysis(recordId, objectMapper.writeValueAsString(aiMap));
            recordMapper.selfJudge(recordId, aiResult.is_correct,
                    aiResult.is_correct ? "learned" : "incorrect");
            return aiMap;
        } catch (JsonProcessingException e) {
            throw new RuntimeException("序列化失败", e);
        }
    }

    private void saveRecord(boolean isNew, PracticeRecord record) {
        if (isNew) recordMapper.insert(record);
        else recordMapper.update(record);
    }

    private boolean autoJudge(String type, String userAnswer, String correctAnswer) {
        if (userAnswer == null) return false;
        return userAnswer.trim().equalsIgnoreCase(correctAnswer.trim());
    }

    private String[] parseJsonArray(String json) {
        if (json == null || json.trim().isEmpty()) return new String[0];
        try {
            return objectMapper.readValue(json, String[].class);
        } catch (Exception e) {
            return new String[0];
        }
    }
}
