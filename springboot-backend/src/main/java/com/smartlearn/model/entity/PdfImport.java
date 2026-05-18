package com.smartlearn.model.entity;

import java.time.LocalDateTime;

public class PdfImport {
    private Long id;
    private String filename;
    private Long fileSize;
    private Integer totalPages;
    private Integer totalChunks;
    private Integer chunksCompleted;
    private Integer questionsExtracted;
    private String status;
    private String errorMessage;
    private String rawTextSnippet;
    private LocalDateTime createdAt;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getFilename() { return filename; }
    public void setFilename(String filename) { this.filename = filename; }
    public Long getFileSize() { return fileSize; }
    public void setFileSize(Long fileSize) { this.fileSize = fileSize; }
    public Integer getTotalPages() { return totalPages; }
    public void setTotalPages(Integer totalPages) { this.totalPages = totalPages; }
    public Integer getTotalChunks() { return totalChunks; }
    public void setTotalChunks(Integer totalChunks) { this.totalChunks = totalChunks; }
    public Integer getChunksCompleted() { return chunksCompleted; }
    public void setChunksCompleted(Integer chunksCompleted) { this.chunksCompleted = chunksCompleted; }
    public Integer getQuestionsExtracted() { return questionsExtracted; }
    public void setQuestionsExtracted(Integer questionsExtracted) { this.questionsExtracted = questionsExtracted; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    public String getErrorMessage() { return errorMessage; }
    public void setErrorMessage(String errorMessage) { this.errorMessage = errorMessage; }
    public String getRawTextSnippet() { return rawTextSnippet; }
    public void setRawTextSnippet(String rawTextSnippet) { this.rawTextSnippet = rawTextSnippet; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
}
