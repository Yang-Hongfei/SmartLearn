package com.smartlearn.controller;

import com.smartlearn.model.dto.*;
import com.smartlearn.model.entity.PracticeRecord;
import com.smartlearn.service.PracticeService;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/practice")
public class PracticeController {
    private final PracticeService practiceService;

    public PracticeController(PracticeService practiceService) {
        this.practiceService = practiceService;
    }

    @PostMapping("/submit")
    public ApiResponse<PracticeSubmitResultDTO> submit(@RequestBody PracticeSubmitDTO dto) {
        return ApiResponse.success(practiceService.submitAnswer(dto));
    }

    @PutMapping("/{recordId}/self-judge")
    public ApiResponse<PracticeRecord> selfJudge(@PathVariable Long recordId, @RequestBody SelfJudgeDTO dto) {
        return ApiResponse.success(practiceService.selfJudge(recordId, dto.getIsCorrect()));
    }

    @PutMapping("/{recordId}/status")
    public ApiResponse<Void> updateStatus(@PathVariable Long recordId, @RequestBody StatusUpdateDTO dto) {
        practiceService.updateStatus(recordId, dto.getStatus());
        return ApiResponse.success(null);
    }

    @GetMapping("/records")
    public ApiResponse<PageResult<PracticeRecord>> records(
            @RequestParam Long userId,
            @RequestParam(required = false) String status,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int size) {
        return ApiResponse.success(practiceService.getRecords(userId, status, page, size));
    }

    @GetMapping("/stats")
    public ApiResponse<PracticeStatsDTO> stats(@RequestParam Long userId) {
        return ApiResponse.success(practiceService.getStats(userId));
    }

    @PostMapping("/{recordId}/ai-analysis")
    public ApiResponse<Map<String, Object>> aiAnalysis(@PathVariable Long recordId) {
        return ApiResponse.success(practiceService.aiAnalysis(recordId));
    }
}
