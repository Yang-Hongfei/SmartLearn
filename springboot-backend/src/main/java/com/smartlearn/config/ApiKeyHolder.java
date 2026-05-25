package com.smartlearn.config;

/**
 * ThreadLocal holder for per-request API key passed via X-Api-Key header.
 * Each HTTP request carries its own key from the user's browser localStorage.
 */
public class ApiKeyHolder {
    private static final ThreadLocal<String> KEY = new ThreadLocal<>();

    public static void set(String key) { KEY.set(key); }
    public static String get() { return KEY.get(); }
    public static void clear() { KEY.remove(); }
}
