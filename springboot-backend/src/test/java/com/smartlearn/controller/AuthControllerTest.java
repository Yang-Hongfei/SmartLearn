package com.smartlearn.controller;

import com.smartlearn.config.JwtUtil;
import com.smartlearn.config.UserContext;
import com.smartlearn.mapper.UserMapper;
import com.smartlearn.model.dto.ApiResponse;
import com.smartlearn.model.dto.LoginRequest;
import com.smartlearn.model.dto.RegisterRequest;
import com.smartlearn.model.entity.User;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.Map;

public class AuthControllerTest {

    private final JwtUtil jwtUtil = new JwtUtil();
    private final StubUserMapper userMapper = new StubUserMapper();
    private final AuthController controller = new AuthController(userMapper, jwtUtil);

    @AfterEach
    void tearDown() {
        UserContext.clear();
        userMapper.reset();
    }

    // --- Register ---

    @Test
    public void testRegisterSuccess() {
        RegisterRequest req = new RegisterRequest();
        req.setUsername("testuser");
        req.setPassword("123456");
        req.setNickname("Test User");

        ApiResponse<Map<String, Object>> resp = controller.register(req);
        assertEquals(200, resp.getCode());
        assertNotNull(resp.getData().get("token"));
        assertEquals("testuser", resp.getData().get("username"));
        assertEquals("Test User", resp.getData().get("nickname"));
    }

    @Test
    public void testRegisterDuplicateUsername() {
        RegisterRequest req = new RegisterRequest();
        req.setUsername("existing");
        req.setPassword("123456");

        // First registration succeeds
        controller.register(req);
        // Second registration with same username fails
        ApiResponse<Map<String, Object>> resp = controller.register(req);
        assertEquals(400, resp.getCode());
        assertTrue(resp.getMessage().contains("用户名已存在"));
    }

    @Test
    public void testRegisterEmptyUsername() {
        RegisterRequest req = new RegisterRequest();
        req.setUsername("");
        req.setPassword("123456");

        ApiResponse<Map<String, Object>> resp = controller.register(req);
        assertEquals(400, resp.getCode());
    }

    @Test
    public void testRegisterNullUsername() {
        RegisterRequest req = new RegisterRequest();
        req.setUsername(null);
        req.setPassword("123456");

        ApiResponse<Map<String, Object>> resp = controller.register(req);
        assertEquals(400, resp.getCode());
    }

    @Test
    public void testRegisterShortPassword() {
        RegisterRequest req = new RegisterRequest();
        req.setUsername("newuser");
        req.setPassword("12345"); // 5 chars, need >= 6

        ApiResponse<Map<String, Object>> resp = controller.register(req);
        assertEquals(400, resp.getCode());
        assertTrue(resp.getMessage().contains("密码至少6位"));
    }

    @Test
    public void testRegisterNullPassword() {
        RegisterRequest req = new RegisterRequest();
        req.setUsername("newuser");
        req.setPassword(null);

        ApiResponse<Map<String, Object>> resp = controller.register(req);
        assertEquals(400, resp.getCode());
    }

    @Test
    public void testRegisterDefaultNickname() {
        RegisterRequest req = new RegisterRequest();
        req.setUsername("nonick");
        req.setPassword("123456");
        // nickname not set → should default to username

        ApiResponse<Map<String, Object>> resp = controller.register(req);
        assertEquals(200, resp.getCode());
        assertEquals("nonick", resp.getData().get("nickname"));
    }

    @Test
    public void testRegisterTrimsWhitespace() {
        RegisterRequest req = new RegisterRequest();
        req.setUsername("  spaced  ");
        req.setPassword("123456");

        ApiResponse<Map<String, Object>> resp = controller.register(req);
        assertEquals(200, resp.getCode());
        assertEquals("spaced", resp.getData().get("username"));
    }

    // --- Login ---

    @Test
    public void testLoginSuccess() {
        // Register first
        RegisterRequest reg = new RegisterRequest();
        reg.setUsername("loginuser");
        reg.setPassword("123456");
        controller.register(reg);

        // Then login
        LoginRequest req = new LoginRequest();
        req.setUsername("loginuser");
        req.setPassword("123456");

        ApiResponse<Map<String, Object>> resp = controller.login(req);
        assertEquals(200, resp.getCode());
        assertNotNull(resp.getData().get("token"));
        assertEquals("loginuser", resp.getData().get("username"));
    }

    @Test
    public void testLoginWrongPassword() {
        RegisterRequest reg = new RegisterRequest();
        reg.setUsername("loginuser2");
        reg.setPassword("123456");
        controller.register(reg);

        LoginRequest req = new LoginRequest();
        req.setUsername("loginuser2");
        req.setPassword("wrongpassword");

        ApiResponse<Map<String, Object>> resp = controller.login(req);
        assertEquals(401, resp.getCode());
    }

    @Test
    public void testLoginNonexistentUser() {
        LoginRequest req = new LoginRequest();
        req.setUsername("nobody");
        req.setPassword("123456");

        ApiResponse<Map<String, Object>> resp = controller.login(req);
        assertEquals(401, resp.getCode());
    }

    // --- Me ---

    @Test
    public void testMeReturnsCurrentUser() {
        // Register a user
        RegisterRequest reg = new RegisterRequest();
        reg.setUsername("meuser");
        reg.setPassword("123456");
        ApiResponse<Map<String, Object>> regResp = controller.register(reg);
        Long userId = ((Number) regResp.getData().get("userId")).longValue();

        // Set context to simulate authenticated request
        UserContext.set(userId, "meuser");

        ApiResponse<Map<String, Object>> resp = controller.me();
        assertEquals(200, resp.getCode());
        assertEquals("meuser", resp.getData().get("username"));
    }

    // --- In-memory stub for UserMapper ---

    static class StubUserMapper implements UserMapper {
        private java.util.Map<Long, User> byId = new java.util.HashMap<>();
        private java.util.Map<String, User> byUsername = new java.util.HashMap<>();
        private long nextId = 1;

        @Override
        public User findById(Long id) {
            return byId.get(id);
        }

        @Override
        public User findByUsername(String username) {
            return byUsername.get(username);
        }

        @Override
        public int insert(User user) {
            user.setId(nextId++);
            byId.put(user.getId(), user);
            byUsername.put(user.getUsername(), user);
            return 1;
        }

        void reset() {
            byId.clear();
            byUsername.clear();
            nextId = 1;
        }
    }
}
