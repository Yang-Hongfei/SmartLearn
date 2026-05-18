-- SmartLearn Database Schema

CREATE DATABASE IF NOT EXISTS smartlearn DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE smartlearn;

CREATE TABLE IF NOT EXISTS users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nickname VARCHAR(100) DEFAULT '',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS questions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    type VARCHAR(20) NOT NULL COMMENT 'single_choice/fill_blank/true_false/essay',
    content TEXT NOT NULL,
    options TEXT NULL COMMENT 'JSON array',
    correct_answer TEXT NOT NULL,
    knowledge_point_ids TEXT NULL COMMENT 'JSON array',
    difficulty INT DEFAULT 1 COMMENT '1-5',
    topic VARCHAR(200) DEFAULT '',
    source_pdf_name VARCHAR(255) NULL,
    import_batch_id BIGINT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_questions_type (type),
    INDEX idx_questions_topic (topic),
    INDEX idx_questions_import_batch (import_batch_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS practice_records (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    question_id BIGINT NOT NULL,
    user_answer TEXT NULL,
    is_correct BOOLEAN NULL,
    judge_mode VARCHAR(10) DEFAULT 'auto' COMMENT 'self/ai/auto',
    status VARCHAR(20) DEFAULT 'unanswered' COMMENT 'unanswered/learned/incorrect',
    ai_analysis_json TEXT NULL,
    practiced_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE INDEX idx_pr_user_question (user_id, question_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS pdf_imports (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_size BIGINT DEFAULT 0,
    total_pages INT DEFAULT 0,
    total_chunks INT DEFAULT 0,
    chunks_completed INT DEFAULT 0,
    questions_extracted INT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending' COMMENT 'pending/processing/completed/failed',
    error_message TEXT NULL,
    raw_text_snippet TEXT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert a default user for practice
INSERT IGNORE INTO users (id, username, password_hash, nickname) VALUES (1, 'default', '', '学习者');
