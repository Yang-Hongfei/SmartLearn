package com.smartlearn.service;

import com.smartlearn.mapper.QuestionMapper;
import com.smartlearn.model.entity.Question;
import com.smartlearn.model.dto.PageResult;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class QuestionService {
    private final QuestionMapper questionMapper;

    public QuestionService(QuestionMapper questionMapper) {
        this.questionMapper = questionMapper;
    }

    public PageResult<Question> findAll(int page, int size) {
        int offset = (page - 1) * size;
        List<Question> records = questionMapper.findAll(offset, size);
        long total = questionMapper.count();
        return new PageResult<>(records, total, page, size);
    }

    public Question findById(Long id) {
        return questionMapper.findById(id);
    }

    public Question getRandom(Long userId) {
        if (userId != null) {
            return questionMapper.findRandomExcludeLearned(userId);
        }
        return questionMapper.findRandom();
    }

    public Question getNext(Long currentId) {
        return questionMapper.findNext(currentId);
    }

    public Question getPrev(Long currentId) {
        return questionMapper.findPrev(currentId);
    }

    public int deleteById(Long id) {
        return questionMapper.deleteById(id);
    }

    public long countAll() {
        return questionMapper.countAll();
    }

    public Question getNextByTopic(Long currentId, String topic) {
        return questionMapper.findNextByTopic(currentId, topic);
    }

    public Question getPrevByTopic(Long currentId, String topic) {
        return questionMapper.findPrevByTopic(currentId, topic);
    }

    public List<String> getAllTopics() {
        return questionMapper.findAllTopics();
    }

    public List<Question> getIncorrectQuestions(Long userId) {
        return questionMapper.findIncorrectByUser(userId);
    }
}
