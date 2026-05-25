package com.smartlearn.controller;

import com.smartlearn.config.UserContext;
import com.smartlearn.model.dto.ApiResponse;
import com.smartlearn.model.dto.PageResult;
import com.smartlearn.model.entity.PdfImport;
import com.smartlearn.service.PdfImportService;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;

@RestController
@RequestMapping("/api/pdf")
public class PdfImportController {
    private final PdfImportService pdfImportService;

    public PdfImportController(PdfImportService pdfImportService) {
        this.pdfImportService = pdfImportService;
    }

    @PostMapping("/upload")
    public ApiResponse<PdfImport> upload(@RequestParam("file") MultipartFile file) {
        if (file.isEmpty()) return ApiResponse.error(400, "文件为空");
        String filename = file.getOriginalFilename();
        if (filename == null || !filename.toLowerCase().endsWith(".pdf")) {
            return ApiResponse.error(400, "仅支持PDF文件");
        }
        return ApiResponse.success(pdfImportService.uploadAndParse(file, UserContext.getUserId()));
    }

    @GetMapping("/imports")
    public ApiResponse<PageResult<PdfImport>> imports(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size) {
        Long userId = UserContext.getUserId();
        List<PdfImport> records = pdfImportService.getImports(userId, page, size);
        long total = pdfImportService.countImports(userId);
        return ApiResponse.success(new PageResult<>(records, total, page, size));
    }

    @GetMapping("/imports/{id}")
    public ApiResponse<PdfImport> importDetail(@PathVariable Long id) {
        return ApiResponse.success(pdfImportService.getImport(id));
    }

    @DeleteMapping("/imports/{id}")
    public ApiResponse<Void> deleteImport(@PathVariable Long id) {
        pdfImportService.deleteImport(id);
        return ApiResponse.success(null);
    }
}
