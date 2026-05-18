package com.smartlearn.mapper;

import com.smartlearn.model.entity.Question;
import org.apache.ibatis.annotations.*;

import java.util.List;

@Mapper
public interface QuestionMapper {

    @Select("SELECT * FROM questions ORDER BY id DESC LIMIT #{size} OFFSET #{offset}")
    List<Question> findAll(@Param("offset") int offset, @Param("size") int size);

    @Select("SELECT COUNT(*) FROM questions")
    long count();

    @Select("SELECT * FROM questions WHERE id = #{id}")
    Question findById(Long id);

    @Select("SELECT COUNT(*) FROM questions")
    long countAll();

    @Select("SELECT * FROM questions WHERE id > #{currentId} ORDER BY id ASC LIMIT 1")
    Question findNext(Long currentId);

    @Select("SELECT * FROM questions WHERE id < #{currentId} ORDER BY id DESC LIMIT 1")
    Question findPrev(Long currentId);

    @Select("SELECT * FROM questions WHERE id > #{currentId} AND topic = #{topic} ORDER BY id ASC LIMIT 1")
    Question findNextByTopic(@Param("currentId") Long currentId, @Param("topic") String topic);

    @Select("SELECT * FROM questions WHERE id < #{currentId} AND topic = #{topic} ORDER BY id DESC LIMIT 1")
    Question findPrevByTopic(@Param("currentId") Long currentId, @Param("topic") String topic);

    @Select("SELECT DISTINCT topic FROM questions WHERE topic != '' ORDER BY topic")
    List<String> findAllTopics();

    @Select("SELECT q.* FROM questions q INNER JOIN practice_records pr ON q.id = pr.question_id WHERE pr.user_id = #{userId} AND pr.status = 'incorrect' ORDER BY q.id")
    List<Question> findIncorrectByUser(Long userId);

    @Select("SELECT * FROM questions ORDER BY RAND() LIMIT 1")
    Question findRandom();

    @Select("SELECT * FROM questions WHERE id NOT IN (SELECT question_id FROM practice_records WHERE user_id = #{userId} AND status = 'learned') ORDER BY RAND() LIMIT 1")
    Question findRandomExcludeLearned(Long userId);

    @Insert("INSERT INTO questions (type, content, options, correct_answer, knowledge_point_ids, difficulty, topic, source_pdf_name, import_batch_id) " +
            "VALUES (#{type}, #{content}, #{options}, #{correctAnswer}, #{knowledgePointIds}, #{difficulty}, #{topic}, #{sourcePdfName}, #{importBatchId})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(Question question);

    @Delete("DELETE FROM questions WHERE id = #{id}")
    int deleteById(Long id);

    @Delete("DELETE FROM questions WHERE import_batch_id = #{batchId}")
    int deleteByBatchId(Long batchId);
}
