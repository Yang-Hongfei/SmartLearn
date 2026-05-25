package com.smartlearn.mapper;

import com.smartlearn.model.entity.User;
import org.apache.ibatis.annotations.*;

@Mapper
public interface UserMapper {

    @Select("SELECT * FROM users WHERE id = #{id}")
    User findById(Long id);

    @Select("SELECT * FROM users WHERE username = #{username}")
    User findByUsername(String username);

    @Insert("INSERT INTO users (username, password_hash, nickname, role, created_at, updated_at) " +
            "VALUES (#{username}, #{passwordHash}, #{nickname}, #{role}, NOW(), NOW())")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(User user);
}
