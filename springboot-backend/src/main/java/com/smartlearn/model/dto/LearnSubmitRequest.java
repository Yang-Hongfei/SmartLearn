package com.smartlearn.model.dto;

import java.util.Map;

public class LearnSubmitRequest {
    private Long pdfImportId;
    private String knowledgePointId;
    private String questionId;
    private String userAnswer;
    private Map<String, Object> question;
    private String correctAnswer;

    public Long getPdfImportId() { return pdfImportId; }
    public void setPdfImportId(Long pdfImportId) { this.pdfImportId = pdfImportId; }
    public String getKnowledgePointId() { return knowledgePointId; }
    public void setKnowledgePointId(String knowledgePointId) { this.knowledgePointId = knowledgePointId; }
    public String getQuestionId() { return questionId; }
    public void setQuestionId(String questionId) { this.questionId = questionId; }
    public String getUserAnswer() { return userAnswer; }
    public void setUserAnswer(String userAnswer) { this.userAnswer = userAnswer; }
    public Map<String, Object> getQuestion() { return question; }
    public void setQuestion(Map<String, Object> question) { this.question = question; }
    public String getCorrectAnswer() { return correctAnswer; }
    public void setCorrectAnswer(String correctAnswer) { this.correctAnswer = correctAnswer; }
}
