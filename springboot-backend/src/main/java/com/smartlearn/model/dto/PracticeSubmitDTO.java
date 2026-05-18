package com.smartlearn.model.dto;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;

public class PracticeSubmitDTO {
    @NotNull private Long userId;
    @NotNull private Long questionId;
    private String userAnswer;
    @NotBlank private String judgeMode;

    public Long getUserId() { return userId; }
    public void setUserId(Long userId) { this.userId = userId; }
    public Long getQuestionId() { return questionId; }
    public void setQuestionId(Long questionId) { this.questionId = questionId; }
    public String getUserAnswer() { return userAnswer; }
    public void setUserAnswer(String userAnswer) { this.userAnswer = userAnswer; }
    public String getJudgeMode() { return judgeMode; }
    public void setJudgeMode(String judgeMode) { this.judgeMode = judgeMode; }
}
