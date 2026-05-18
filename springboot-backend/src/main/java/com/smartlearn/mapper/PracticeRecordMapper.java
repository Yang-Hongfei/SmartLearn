package com.smartlearn.mapper;

import com.smartlearn.model.entity.PracticeRecord;
import org.apache.ibatis.annotations.*;

import java.util.List;

@Mapper
public interface PracticeRecordMapper {

    @Select("SELECT * FROM practice_records WHERE user_id = #{userId} AND question_id = #{questionId}")
    PracticeRecord findByUserAndQuestion(@Param("userId") Long userId, @Param("questionId") Long questionId);

    @Insert("INSERT INTO practice_records (user_id, question_id, user_answer, is_correct, judge_mode, status, ai_analysis_json, practiced_at) " +
            "VALUES (#{userId}, #{questionId}, #{userAnswer}, #{isCorrect}, #{judgeMode}, #{status}, #{aiAnalysisJson}, NOW())")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(PracticeRecord record);

    @Update("UPDATE practice_records SET user_answer = #{userAnswer}, is_correct = #{isCorrect}, " +
            "judge_mode = #{judgeMode}, status = #{status}, ai_analysis_json = #{aiAnalysisJson}, practiced_at = NOW() " +
            "WHERE id = #{id}")
    int update(PracticeRecord record);

    @Select("SELECT * FROM practice_records WHERE id = #{id}")
    PracticeRecord findById(Long id);

    @Select("<script>SELECT * FROM practice_records WHERE user_id = #{userId}" +
            "<if test='status != null'> AND status = #{status}</if>" +
            " ORDER BY practiced_at DESC LIMIT #{size} OFFSET #{offset}</script>")
    List<PracticeRecord> findByUserAndStatus(@Param("userId") Long userId, @Param("status") String status,
                                              @Param("offset") int offset, @Param("size") int size);

    @Select("<script>SELECT COUNT(*) FROM practice_records WHERE user_id = #{userId}" +
            "<if test='status != null'> AND status = #{status}</if></script>")
    long countByUserAndStatus(@Param("userId") Long userId, @Param("status") String status);

    @Select("SELECT COUNT(*) FROM practice_records WHERE user_id = #{userId}")
    long countByUser(Long userId);

    @Select("SELECT status, COUNT(*) as cnt FROM practice_records WHERE user_id = #{userId} GROUP BY status")
    List<StatusCount> statsByUser(Long userId);

    @Update("UPDATE practice_records SET status = #{status} WHERE id = #{id}")
    int updateStatus(@Param("id") Long id, @Param("status") String status);

    @Update("UPDATE practice_records SET is_correct = #{isCorrect}, status = #{status} WHERE id = #{id}")
    int selfJudge(@Param("id") Long id, @Param("isCorrect") boolean isCorrect, @Param("status") String status);

    @Update("UPDATE practice_records SET ai_analysis_json = #{json} WHERE id = #{id}")
    int updateAiAnalysis(@Param("id") Long id, @Param("json") String json);

    class StatusCount {
        private String status;
        private long cnt;
        public String getStatus() { return status; }
        public void setStatus(String status) { this.status = status; }
        public long getCnt() { return cnt; }
        public void setCnt(long cnt) { this.cnt = cnt; }
    }
}
