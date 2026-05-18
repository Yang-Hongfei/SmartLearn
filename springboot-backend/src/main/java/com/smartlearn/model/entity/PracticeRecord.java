package com.smartlearn.model.entity;

import java.time.LocalDateTime;

public class PracticeRecord {
    private Long id;
    private Long userId;
    private Long questionId;
    private String userAnswer;
    private Boolean isCorrect;
    private String judgeMode;
    private String status;
    private String aiAnalysisJson;
    private LocalDateTime practicedAt;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public Long getUserId() { return userId; }
    public void setUserId(Long userId) { this.userId = userId; }
    public Long getQuestionId() { return questionId; }
    public void setQuestionId(Long questionId) { this.questionId = questionId; }
    public String getUserAnswer() { return userAnswer; }
    public void setUserAnswer(String userAnswer) { this.userAnswer = userAnswer; }
    public Boolean getIsCorrect() { return isCorrect; }
    public void setIsCorrect(Boolean isCorrect) { this.isCorrect = isCorrect; }
    public String getJudgeMode() { return judgeMode; }
    public void setJudgeMode(String judgeMode) { this.judgeMode = judgeMode; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    public String getAiAnalysisJson() { return aiAnalysisJson; }
    public void setAiAnalysisJson(String aiAnalysisJson) { this.aiAnalysisJson = aiAnalysisJson; }
    public LocalDateTime getPracticedAt() { return practicedAt; }
    public void setPracticedAt(LocalDateTime practicedAt) { this.practicedAt = practicedAt; }
}
