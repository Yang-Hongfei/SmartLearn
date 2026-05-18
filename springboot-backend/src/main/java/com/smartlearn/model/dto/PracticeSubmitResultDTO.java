package com.smartlearn.model.dto;

import java.util.Map;

public class PracticeSubmitResultDTO {
    private Long recordId;
    private Boolean isCorrect;
    private String judgeMode;
    private String correctAnswer;
    private String status;
    // AI analysis fields (populated when judgeMode=ai)
    private Map<String, Object> aiAnalysis;

    public Long getRecordId() { return recordId; }
    public void setRecordId(Long recordId) { this.recordId = recordId; }
    public Boolean getIsCorrect() { return isCorrect; }
    public void setIsCorrect(Boolean isCorrect) { this.isCorrect = isCorrect; }
    public String getJudgeMode() { return judgeMode; }
    public void setJudgeMode(String judgeMode) { this.judgeMode = judgeMode; }
    public String getCorrectAnswer() { return correctAnswer; }
    public void setCorrectAnswer(String correctAnswer) { this.correctAnswer = correctAnswer; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    public Map<String, Object> getAiAnalysis() { return aiAnalysis; }
    public void setAiAnalysis(Map<String, Object> aiAnalysis) { this.aiAnalysis = aiAnalysis; }
}
