package com.smartlearn.config;

public class UserContext {
    private static final ThreadLocal<Long> USER_ID = new ThreadLocal<>();
    private static final ThreadLocal<String> USERNAME = new ThreadLocal<>();

    public static void set(Long userId, String username) {
        USER_ID.set(userId);
        USERNAME.set(username);
    }

    public static Long getUserId() {
        Long id = USER_ID.get();
        return id != null ? id : 1L; // fallback to admin for backward compat
    }

    public static String getUsername() { return USERNAME.get(); }

    public static void clear() {
        USER_ID.remove();
        USERNAME.remove();
    }
}
