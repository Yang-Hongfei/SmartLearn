package com.smartlearn.model.entity;

import java.time.LocalDateTime;

public class Question {
    private Long id;
    private String type;
    private String content;
    private String options;
    private String correctAnswer;
    private String knowledgePointIds;
    private Integer difficulty;
    private String topic;
    private String sourcePdfName;
    private Long importBatchId;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getType() { return type; }
    public void setType(String type) { this.type = type; }
    public String getContent() { return content; }
    public void setContent(String content) { this.content = content; }
    public String getOptions() { return options; }
    public void setOptions(String options) { this.options = options; }
    public String getCorrectAnswer() { return correctAnswer; }
    public void setCorrectAnswer(String correctAnswer) { this.correctAnswer = correctAnswer; }
    public String getKnowledgePointIds() { return knowledgePointIds; }
    public void setKnowledgePointIds(String knowledgePointIds) { this.knowledgePointIds = knowledgePointIds; }
    public Integer getDifficulty() { return difficulty; }
    public void setDifficulty(Integer difficulty) { this.difficulty = difficulty; }
    public String getTopic() { return topic; }
    public void setTopic(String topic) { this.topic = topic; }
    public String getSourcePdfName() { return sourcePdfName; }
    public void setSourcePdfName(String sourcePdfName) { this.sourcePdfName = sourcePdfName; }
    public Long getImportBatchId() { return importBatchId; }
    public void setImportBatchId(Long importBatchId) { this.importBatchId = importBatchId; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
    public LocalDateTime getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(LocalDateTime updatedAt) { this.updatedAt = updatedAt; }
}
