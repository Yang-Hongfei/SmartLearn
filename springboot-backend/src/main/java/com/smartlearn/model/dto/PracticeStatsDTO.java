package com.smartlearn.model.dto;

import java.util.Map;

public class PracticeStatsDTO {
    private long total;
    private long learned;
    private long unanswered;
    private long incorrect;

    public PracticeStatsDTO() {}
    public PracticeStatsDTO(long total, long learned, long unanswered, long incorrect) {
        this.total = total; this.learned = learned;
        this.unanswered = unanswered; this.incorrect = incorrect;
    }

    public long getTotal() { return total; }
    public void setTotal(long total) { this.total = total; }
    public long getLearned() { return learned; }
    public void setLearned(long learned) { this.learned = learned; }
    public long getUnanswered() { return unanswered; }
    public void setUnanswered(long unanswered) { this.unanswered = unanswered; }
    public long getIncorrect() { return incorrect; }
    public void setIncorrect(long incorrect) { this.incorrect = incorrect; }
}
