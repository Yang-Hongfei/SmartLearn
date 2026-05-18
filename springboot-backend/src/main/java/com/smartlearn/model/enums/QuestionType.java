package com.smartlearn.model.enums;

public enum QuestionType {
    SINGLE_CHOICE("single_choice"),
    FILL_BLANK("fill_blank"),
    TRUE_FALSE("true_false"),
    ESSAY("essay");

    private final String value;

    QuestionType(String value) { this.value = value; }
    public String getValue() { return value; }
}
