package com.smartlearn.controller;

import com.smartlearn.config.UserContext;
import com.smartlearn.model.dto.ApiResponse;
import com.smartlearn.model.dto.PageResult;
import com.smartlearn.model.entity.Question;
import com.smartlearn.service.QuestionService;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/questions")
public class QuestionController {
    private final QuestionService questionService;

    public QuestionController(QuestionService questionService) {
        this.questionService = questionService;
    }

    @GetMapping
    public ApiResponse<PageResult<Question>> list(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int size) {
        return ApiResponse.success(questionService.findAll(page, size));
    }

    @GetMapping("/{id}")
    public ApiResponse<Question> getById(@PathVariable Long id) {
        Question q = questionService.findById(id);
        if (q == null) return ApiResponse.error(404, "题目不存在");
        return ApiResponse.success(q);
    }

    @GetMapping("/random")
    public ApiResponse<Question> random() {
        Long userId = UserContext.getUserId();
        Question q = questionService.getRandom(userId);
        if (q == null) return ApiResponse.error(404, "题库为空");
        return ApiResponse.success(q);
    }

    @GetMapping("/next")
    public ApiResponse<Question> next(@RequestParam Long currentId,
                                       @RequestParam(required = false) String topic) {
        Question q;
        if (topic != null && !topic.isEmpty()) {
            q = questionService.getNextByTopic(currentId, topic);
        } else {
            q = questionService.getNext(currentId);
        }
        if (q == null) return ApiResponse.error(404, "已是最后一题");
        return ApiResponse.success(q);
    }

    @GetMapping("/prev")
    public ApiResponse<Question> prev(@RequestParam Long currentId,
                                       @RequestParam(required = false) String topic) {
        Question q;
        if (topic != null && !topic.isEmpty()) {
            q = questionService.getPrevByTopic(currentId, topic);
        } else {
            q = questionService.getPrev(currentId);
        }
        if (q == null) return ApiResponse.error(404, "已是第一题");
        return ApiResponse.success(q);
    }

    @GetMapping("/count")
    public ApiResponse<Long> count() {
        return ApiResponse.success(questionService.countAll());
    }

    @GetMapping("/topics")
    public ApiResponse<List<String>> topics() {
        return ApiResponse.success(questionService.getAllTopics());
    }

    @GetMapping("/incorrect")
    public ApiResponse<List<Question>> incorrect() {
        Long userId = UserContext.getUserId();
        return ApiResponse.success(questionService.getIncorrectQuestions(userId));
    }

    @DeleteMapping("/{id}")
    public ApiResponse<Void> delete(@PathVariable Long id) {
        questionService.deleteById(id);
        return ApiResponse.success(null);
    }
}
