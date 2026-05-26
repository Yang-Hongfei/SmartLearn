package com.smartlearn.controller;

import com.smartlearn.config.JwtUtil;
import com.smartlearn.mapper.UserMapper;
import com.smartlearn.model.dto.ApiResponse;
import com.smartlearn.model.dto.LoginRequest;
import com.smartlearn.model.dto.RegisterRequest;
import com.smartlearn.model.entity.User;
import org.springframework.web.bind.annotation.*;

import java.security.MessageDigest;
import java.security.SecureRandom;
import java.util.Base64;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/auth")
public class AuthController {
    private final UserMapper userMapper;
    private final JwtUtil jwtUtil;

    private String hashPassword(String password) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] hash = md.digest(password.getBytes("UTF-8"));
            return Base64.getEncoder().encodeToString(hash);
        } catch (Exception e) { throw new RuntimeException(e); }
    }

    public AuthController(UserMapper userMapper, JwtUtil jwtUtil) {
        this.userMapper = userMapper;
        this.jwtUtil = jwtUtil;
    }

    @PostMapping("/register")
    public ApiResponse<Map<String, Object>> register(@RequestBody RegisterRequest req) {
        if (req.getUsername() == null || req.getUsername().trim().isEmpty())
            return ApiResponse.error(400, "用户名不能为空");
        if (req.getPassword() == null || req.getPassword().length() < 6)
            return ApiResponse.error(400, "密码至少6位");

        User existing = userMapper.findByUsername(req.getUsername().trim());
        if (existing != null) return ApiResponse.error(400, "用户名已存在");

        User user = new User();
        user.setUsername(req.getUsername().trim());
        user.setPasswordHash(hashPassword(req.getPassword()));
        user.setNickname(req.getNickname() != null ? req.getNickname().trim() : req.getUsername().trim());
        userMapper.insert(user);

        String token = jwtUtil.generateToken(user.getId(), user.getUsername());
        Map<String, Object> data = new HashMap<>();
        data.put("token", token);
        data.put("userId", user.getId());
        data.put("username", user.getUsername());
        data.put("nickname", user.getNickname());
        return ApiResponse.success(data);
    }

    @PostMapping("/login")
    public ApiResponse<Map<String, Object>> login(@RequestBody LoginRequest req) {
        User user = userMapper.findByUsername(req.getUsername());
        if (user == null || !hashPassword(req.getPassword()).equals(user.getPasswordHash()))
            return ApiResponse.error(401, "用户名或密码错误");

        String token = jwtUtil.generateToken(user.getId(), user.getUsername());
        Map<String, Object> data = new HashMap<>();
        data.put("token", token);
        data.put("userId", user.getId());
        data.put("username", user.getUsername());
        data.put("nickname", user.getNickname());
        return ApiResponse.success(data);
    }

    @GetMapping("/me")
    public ApiResponse<Map<String, Object>> me() {
        Long userId = com.smartlearn.config.UserContext.getUserId();
        User user = userMapper.findById(userId);
        Map<String, Object> data = new HashMap<>();
        data.put("userId", user.getId());
        data.put("username", user.getUsername());
        data.put("nickname", user.getNickname());
        return ApiResponse.success(data);
    }
}
