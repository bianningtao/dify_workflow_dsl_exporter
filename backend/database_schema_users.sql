-- ============================================
-- 用户认证和管理数据库表结构
-- ============================================

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY COMMENT '用户ID（UUID）',
    email VARCHAR(255) NOT NULL UNIQUE COMMENT '邮箱（登录账号）',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    username VARCHAR(100) NOT NULL COMMENT '用户名',
    is_admin BOOLEAN DEFAULT FALSE COMMENT '是否为管理员',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    last_login_at TIMESTAMP NULL COMMENT '最后登录时间',
    INDEX idx_email (email),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 用户配置表（替代原来的全局配置）
CREATE TABLE IF NOT EXISTS user_system_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL COMMENT '用户ID',
    config_key VARCHAR(100) NOT NULL COMMENT '配置键',
    config_value TEXT COMMENT '配置值',
    config_type ENUM('string', 'number', 'boolean', 'json') DEFAULT 'string' COMMENT '配置类型',
    description TEXT COMMENT '配置描述',
    is_sensitive BOOLEAN DEFAULT FALSE COMMENT '是否为敏感信息',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY unique_user_config (user_id, config_key),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_config_key (config_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户系统配置表';

-- 用户目标实例表
CREATE TABLE IF NOT EXISTS user_target_instances (
    id VARCHAR(36) PRIMARY KEY COMMENT '实例ID（UUID）',
    user_id VARCHAR(36) NOT NULL COMMENT '用户ID',
    instance_name VARCHAR(100) NOT NULL COMMENT '实例名称',
    instance_url VARCHAR(500) NOT NULL COMMENT '实例URL',
    auth_type ENUM('bearer', 'basic', 'api_key') DEFAULT 'bearer' COMMENT '认证类型',
    auth_config JSON COMMENT '认证配置（JSON格式）',
    description TEXT COMMENT '实例描述',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户目标实例配置表';

-- 用户数据库连接表
CREATE TABLE IF NOT EXISTS user_database_connections (
    id VARCHAR(36) PRIMARY KEY COMMENT '连接ID（UUID）',
    user_id VARCHAR(36) NOT NULL COMMENT '用户ID',
    connection_name VARCHAR(100) NOT NULL COMMENT '连接名称',
    db_type ENUM('postgresql', 'mysql') DEFAULT 'postgresql' COMMENT '数据库类型',
    host VARCHAR(255) NOT NULL COMMENT '主机地址',
    port INT NOT NULL COMMENT '端口',
    database_name VARCHAR(100) NOT NULL COMMENT '数据库名',
    username VARCHAR(100) NOT NULL COMMENT '用户名',
    password_encrypted TEXT COMMENT '加密后的密码',
    ssl_mode VARCHAR(50) DEFAULT 'prefer' COMMENT 'SSL模式',
    pool_size INT DEFAULT 10 COMMENT '连接池大小',
    max_overflow INT DEFAULT 20 COMMENT '最大溢出连接数',
    pool_timeout INT DEFAULT 30 COMMENT '连接池超时时间',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户数据库连接配置表';

-- 会话表（用于JWT token黑名单或会话管理）
CREATE TABLE IF NOT EXISTS user_sessions (
    id VARCHAR(36) PRIMARY KEY COMMENT '会话ID（UUID）',
    user_id VARCHAR(36) NOT NULL COMMENT '用户ID',
    token_jti VARCHAR(255) NOT NULL UNIQUE COMMENT 'JWT JTI（唯一标识符）',
    expires_at TIMESTAMP NOT NULL COMMENT '过期时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_token_jti (token_jti),
    INDEX idx_expires_at (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户会话表';

