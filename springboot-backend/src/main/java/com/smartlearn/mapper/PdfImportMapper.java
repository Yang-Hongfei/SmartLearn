package com.smartlearn.mapper;

import com.smartlearn.model.entity.PdfImport;
import org.apache.ibatis.annotations.*;

import java.util.List;

@Mapper
public interface PdfImportMapper {

    @Insert("INSERT INTO pdf_imports (filename, file_size, total_pages, total_chunks, chunks_completed, questions_extracted, status, error_message, raw_text_snippet, created_at) " +
            "VALUES (#{filename}, #{fileSize}, #{totalPages}, #{totalChunks}, #{chunksCompleted}, #{questionsExtracted}, #{status}, #{errorMessage}, #{rawTextSnippet}, NOW())")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(PdfImport pdfImport);

    @Select("SELECT * FROM pdf_imports WHERE id = #{id}")
    PdfImport findById(Long id);

    @Select("SELECT * FROM pdf_imports ORDER BY created_at DESC LIMIT #{size} OFFSET #{offset}")
    List<PdfImport> findAll(@Param("offset") int offset, @Param("size") int size);

    @Select("SELECT COUNT(*) FROM pdf_imports")
    long count();

    @Update("UPDATE pdf_imports SET questions_extracted = #{questionsExtracted}, status = #{status}, error_message = #{errorMessage} WHERE id = #{id}")
    int updateResult(@Param("id") Long id, @Param("questionsExtracted") int questionsExtracted,
                     @Param("status") String status, @Param("errorMessage") String errorMessage);

    @Update("UPDATE pdf_imports SET chunks_completed = #{chunksCompleted}, status = #{status} WHERE id = #{id}")
    int updateChunkProgress(@Param("id") Long id, @Param("chunksCompleted") int chunksCompleted,
                            @Param("status") String status);

    @Delete("DELETE FROM pdf_imports WHERE id = #{id}")
    int deleteById(Long id);
}
