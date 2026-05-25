package com.smartlearn.model.entity;

import java.time.LocalDateTime;

public class LearnProgress {
    private Long id;
    private Long userId;
    private Long pdfImportId;
    private String learningPathJson;
    private Integer currentNodeIndex;
    private String currentNodeState;
    private Long currentQuestionId;
    private String completedNodes;
    private String reflectionLogJson;
    private String quizHistoryJson;
    private LocalDateTime updatedAt;
    private LocalDateTime createdAt;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public Long getUserId() { return userId; }
    public void setUserId(Long userId) { this.userId = userId; }
    public Long getPdfImportId() { return pdfImportId; }
    public void setPdfImportId(Long pdfImportId) { this.pdfImportId = pdfImportId; }
    public String getLearningPathJson() { return learningPathJson; }
    public void setLearningPathJson(String learningPathJson) { this.learningPathJson = learningPathJson; }
    public Integer getCurrentNodeIndex() { return currentNodeIndex; }
    public void setCurrentNodeIndex(Integer currentNodeIndex) { this.currentNodeIndex = currentNodeIndex; }
    public String getCurrentNodeState() { return currentNodeState; }
    public void setCurrentNodeState(String currentNodeState) { this.currentNodeState = currentNodeState; }
    public Long getCurrentQuestionId() { return currentQuestionId; }
    public void setCurrentQuestionId(Long currentQuestionId) { this.currentQuestionId = currentQuestionId; }
    public String getCompletedNodes() { return completedNodes; }
    public void setCompletedNodes(String completedNodes) { this.completedNodes = completedNodes; }
    public String getReflectionLogJson() { return reflectionLogJson; }
    public void setReflectionLogJson(String reflectionLogJson) { this.reflectionLogJson = reflectionLogJson; }
    public String getQuizHistoryJson() { return quizHistoryJson; }
    public void setQuizHistoryJson(String quizHistoryJson) { this.quizHistoryJson = quizHistoryJson; }
    public LocalDateTime getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(LocalDateTime updatedAt) { this.updatedAt = updatedAt; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
}
