package com.smartlearn.controller;

import com.smartlearn.client.AiServiceClient;
import com.smartlearn.model.dto.ApiResponse;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/config")
public class ConfigController {
    private final AiServiceClient aiClient;

    public ConfigController(AiServiceClient aiClient) {
        this.aiClient = aiClient;
    }

    @GetMapping("/api-key")
    public ApiResponse<Map<String, Object>> getApiKeyStatus() {
        return ApiResponse.success(aiClient.getApiKeyStatus());
    }

    @PostMapping("/api-key")
    public ApiResponse<Map<String, Object>> setApiKey(@RequestBody Map<String, String> req) {
        String apiKey = req.get("apiKey");
        if (apiKey == null) apiKey = req.get("api_key");
        if (apiKey == null || apiKey.trim().isEmpty()) {
            return ApiResponse.error(400, "API Key 不能为空");
        }
        return ApiResponse.success(aiClient.setApiKey(apiKey.trim()));
    }
}
