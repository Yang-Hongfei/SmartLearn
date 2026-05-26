package com.smartlearn.service;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class PracticeServiceTest {

    // autoJudge is package-private, accessible from same package
    // We create a minimal instance since autoJudge is a pure function
    // that doesn't touch any of the injected dependencies.

    private final PracticeService service = new PracticeService(null, null, null, null);

    // --- single_choice ---

    @Test
    public void testSingleChoiceExactMatch() {
        assertTrue(service.autoJudge("single_choice", "A", "A"));
    }

    @Test
    public void testSingleChoiceCaseInsensitive() {
        assertTrue(service.autoJudge("single_choice", "a", "A"));
    }

    @Test
    public void testSingleChoiceWrongAnswer() {
        assertFalse(service.autoJudge("single_choice", "B", "A"));
    }

    @Test
    public void testSingleChoiceWithWhitespace() {
        assertTrue(service.autoJudge("single_choice", "  A  ", "A"));
    }

    // --- true_false ---

    @Test
    public void testTrueFalseCorrect() {
        assertTrue(service.autoJudge("true_false", "True", "True"));
    }

    @Test
    public void testTrueFalseCaseDiff() {
        assertTrue(service.autoJudge("true_false", "true", "True"));
    }

    @Test
    public void testTrueFalseWrong() {
        assertFalse(service.autoJudge("true_false", "False", "True"));
    }

    // --- fill_blank ---

    @Test
    public void testFillBlankExactMatch() {
        assertTrue(service.autoJudge("fill_blank", "start()", "start()"));
    }

    @Test
    public void testFillBlankCaseInsensitive() {
        assertTrue(service.autoJudge("fill_blank", "START", "start"));
    }

    @Test
    public void testFillBlankWrongAnswer() {
        assertFalse(service.autoJudge("fill_blank", "run()", "start()"));
    }

    // --- essay ---

    @Test
    public void testEssayAlwaysReturnsFalse() {
        // autoJudge cannot reliably score essays; returns false so user self-judges.
        assertFalse(service.autoJudge("essay",
                "Polymorphism allows one interface to be used for different types.",
                "Polymorphism allows one interface to be used for different types."));
    }

    // --- null safety ---

    @Test
    public void testNullUserAnswerReturnsFalse() {
        assertFalse(service.autoJudge("single_choice", null, "A"));
    }
}
