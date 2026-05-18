package com.smartlearn.model.enums;

public enum PracticeStatus {
    UNANSWERED("unanswered"),
    LEARNED("learned"),
    INCORRECT("incorrect");

    private final String value;

    PracticeStatus(String value) { this.value = value; }
    public String getValue() { return value; }
}
