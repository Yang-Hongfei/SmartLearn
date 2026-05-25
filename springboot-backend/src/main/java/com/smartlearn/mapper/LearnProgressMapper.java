package com.smartlearn.mapper;

import com.smartlearn.model.entity.LearnProgress;
import org.apache.ibatis.annotations.*;

import java.util.List;

@Mapper
public interface LearnProgressMapper {

    @Select("SELECT * FROM learn_progress WHERE user_id = #{userId} AND pdf_import_id = #{pdfImportId}")
    LearnProgress findByUserAndPdf(@Param("userId") Long userId, @Param("pdfImportId") Long pdfImportId);

    @Select("SELECT * FROM learn_progress WHERE user_id = #{userId}")
    List<LearnProgress> findByUser(@Param("userId") Long userId);

    @Insert("INSERT INTO learn_progress (user_id, pdf_import_id, learning_path_json, current_node_index, " +
            "current_node_state, current_question_id, completed_nodes, reflection_log_json, quiz_history_json) " +
            "VALUES (#{userId}, #{pdfImportId}, #{learningPathJson}, #{currentNodeIndex}, " +
            "#{currentNodeState}, #{currentQuestionId}, #{completedNodes}, #{reflectionLogJson}, #{quizHistoryJson})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(LearnProgress progress);

    @Update("UPDATE learn_progress SET learning_path_json = #{learningPathJson}, " +
            "current_node_index = #{currentNodeIndex}, current_node_state = #{currentNodeState}, " +
            "current_question_id = #{currentQuestionId}, " +
            "completed_nodes = #{completedNodes}, reflection_log_json = #{reflectionLogJson}, " +
            "quiz_history_json = #{quizHistoryJson} " +
            "WHERE user_id = #{userId} AND pdf_import_id = #{pdfImportId}")
    int update(LearnProgress progress);

    @Delete("DELETE FROM learn_progress WHERE id = #{id}")
    int deleteById(@Param("id") Long id);

    @Delete("DELETE FROM learn_progress WHERE user_id = #{userId} AND pdf_import_id = #{pdfImportId}")
    int deleteByUserAndPdf(@Param("userId") Long userId, @Param("pdfImportId") Long pdfImportId);
}
