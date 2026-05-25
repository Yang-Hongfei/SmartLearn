-- SmartLearn Database Schema

CREATE DATABASE IF NOT EXISTS smartlearn DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE smartlearn;

CREATE TABLE IF NOT EXISTS users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nickname VARCHAR(100) DEFAULT '',
    role VARCHAR(20) DEFAULT 'user' COMMENT 'admin/user',
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
    user_id BIGINT DEFAULT NULL COMMENT 'NULL=admin preset, else owner',
    admin_preset TINYINT DEFAULT 0 COMMENT '1=admin preset visible to all',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS learn_progress (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL DEFAULT 1,
    pdf_import_id BIGINT NOT NULL,
    learning_path_json TEXT NOT NULL COMMENT '完整学习路径JSON',
    current_node_index INT DEFAULT 0,
    current_node_state VARCHAR(20) DEFAULT 'explain' COMMENT 'explain/quiz',
    completed_nodes TEXT NULL COMMENT '已完成节点ID JSON数组',
    reflection_log_json TEXT NULL COMMENT 'Reflection历史JSON',
    quiz_history_json TEXT NULL COMMENT '答题历史JSON',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE INDEX idx_lp_user_pdf (user_id, pdf_import_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert a default user for practice
INSERT IGNORE INTO users (id, username, password_hash, nickname, role) VALUES (1, 'admin', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', '管理员', 'admin');
-- default password: admin123
