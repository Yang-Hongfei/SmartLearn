package com.smartlearn.config;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class JwtUtilTest {
    private final JwtUtil jwtUtil = new JwtUtil();

    @Test
    public void testGenerateAndParseRoundtrip() {
        String token = jwtUtil.generateToken(42L, "testuser");
        assertNotNull(token);
        assertEquals(Long.valueOf(42L), jwtUtil.getUserId(token));
    }

    @Test
    public void testValidTokenPassesValidation() {
        String token = jwtUtil.generateToken(1L, "admin");
        assertTrue(jwtUtil.validate(token));
    }

    @Test
    public void testTamperedTokenFailsValidation() {
        String token = jwtUtil.generateToken(1L, "admin");
        // Flip the last character of the payload
        String tampered = token.substring(0, token.length() - 1)
                + (token.charAt(token.length() - 1) == 'A' ? 'B' : 'A');
        assertFalse(jwtUtil.validate(tampered));
    }

    @Test
    public void testGarbledTokenFailsValidation() {
        assertFalse(jwtUtil.validate("this.is.not.a.valid.jwt"));
    }

    @Test
    public void testEmptyStringThrowsIllegalArgumentException() {
        // JWT library throws IllegalArgumentException for null/empty input
        assertThrows(IllegalArgumentException.class, () -> jwtUtil.validate(""));
    }

    @Test
    public void testNullTokenThrowsIllegalArgumentException() {
        assertThrows(IllegalArgumentException.class, () -> jwtUtil.validate(null));
    }

    @Test
    public void testExpiredTokenHasCorrectStructure() throws Exception {
        String token = jwtUtil.generateToken(1L, "admin");
        // JWT must have 3 dot-separated parts: header.payload.signature
        String[] parts = token.split("\\.");
        assertEquals(3, parts.length);
    }

    @Test
    public void testDifferentUsersGetDifferentTokens() {
        String token1 = jwtUtil.generateToken(1L, "alice");
        String token2 = jwtUtil.generateToken(2L, "bob");
        assertNotEquals(token1, token2);
        assertEquals(Long.valueOf(1L), jwtUtil.getUserId(token1));
        assertEquals(Long.valueOf(2L), jwtUtil.getUserId(token2));
    }

    @Test
    public void testTokenRoundtripIntegrity() {
        String token = jwtUtil.generateToken(7L, "student");
        assertTrue(jwtUtil.validate(token));
        assertEquals(Long.valueOf(7L), jwtUtil.getUserId(token));
    }
}
