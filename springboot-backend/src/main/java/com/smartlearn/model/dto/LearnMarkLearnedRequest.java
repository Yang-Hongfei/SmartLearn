package com.smartlearn.model.dto;

public class LearnMarkLearnedRequest {
    private Long pdfImportId;
    private String knowledgePointId;

    public Long getPdfImportId() { return pdfImportId; }
    public void setPdfImportId(Long pdfImportId) { this.pdfImportId = pdfImportId; }
    public String getKnowledgePointId() { return knowledgePointId; }
    public void setKnowledgePointId(String knowledgePointId) { this.knowledgePointId = knowledgePointId; }
}
