package com.smartlearn.controller;

import com.smartlearn.model.dto.*;
import com.smartlearn.service.LearnService;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/learn")
public class LearnController {
    private final LearnService learnService;

    public LearnController(LearnService learnService) {
        this.learnService = learnService;
    }

    @PostMapping("/plan")
    public ApiResponse<Map<String, Object>> generatePlan(@RequestBody LearnPlanRequest req) {
        return ApiResponse.success(learnService.generatePlan(req.getPdfImportId()));
    }

    @GetMapping("/progress")
    public ApiResponse<Map<String, Object>> getProgress(@RequestParam Long pdfImportId) {
        Map<String, Object> progress = learnService.getProgress(pdfImportId);
        if (progress == null) return ApiResponse.error(404, "未找到学习进度");
        return ApiResponse.success(progress);
    }

    @GetMapping("/progress-list")
    public ApiResponse<List<Map<String, Object>>> listProgress() {
        return ApiResponse.success(learnService.listProgress());
    }

    @PostMapping("/submit")
    public ApiResponse<Map<String, Object>> submitAnswer(@RequestBody LearnSubmitRequest req) {
        return ApiResponse.success(learnService.submitAnswer(req));
    }

    @PostMapping("/mark-learned")
    public ApiResponse<Map<String, Object>> markLearned(@RequestBody LearnMarkLearnedRequest req) {
        return ApiResponse.success(learnService.markLearned(req));
    }

    @DeleteMapping("/progress/{pdfImportId}")
    public ApiResponse<Void> deleteProgress(@PathVariable Long pdfImportId) {
        learnService.deleteProgress(pdfImportId);
        return ApiResponse.success(null);
    }

    @PostMapping("/generate-test")
    public ApiResponse<Map<String, Object>> generateTest(@RequestBody LearnPlanRequest req) {
        return ApiResponse.success(learnService.generateTest(req.getPdfImportId()));
    }

    @PostMapping("/evaluate-test")
    public ApiResponse<Map<String, Object>> evaluateTest(@RequestBody Map<String, Object> req) {
        Long pdfImportId = Long.valueOf(String.valueOf(req.get("pdfImportId")));
        List<Map<String, Object>> answers = (List<Map<String, Object>>) req.get("answers");
        double threshold = req.get("threshold") != null ? Double.parseDouble(String.valueOf(req.get("threshold"))) : 0.7;
        return ApiResponse.success(learnService.evaluateTest(pdfImportId, answers, threshold));
    }
}
