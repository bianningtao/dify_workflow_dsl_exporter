-- ============================================
-- Dify工作流导出工具 - 配置数据库表结构
-- ============================================

-- 系统配置表
CREATE TABLE IF NOT EXISTS system_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(100) NOT NULL UNIQUE COMMENT '配置键',
    config_value TEXT COMMENT '配置值（JSON格式）',
    config_type VARCHAR(50) NOT NULL DEFAULT 'string' COMMENT '配置类型：string, number, boolean, json',
    description VARCHAR(500) COMMENT '配置描述',
    is_sensitive BOOLEAN DEFAULT FALSE COMMENT '是否为敏感信息',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_config_key (config_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统配置表';

-- 目标实例配置表
CREATE TABLE IF NOT EXISTS target_instances (
    id VARCHAR(50) PRIMARY KEY COMMENT '实例ID',
    name VARCHAR(100) NOT NULL COMMENT '实例名称',
    url VARCHAR(500) NOT NULL COMMENT '实例URL',
    auth_type VARCHAR(20) NOT NULL DEFAULT 'bearer' COMMENT '认证类型：bearer, basic, api_key',
    auth_token TEXT COMMENT 'Bearer Token',
    auth_username VARCHAR(100) COMMENT '基本认证用户名',
    auth_password VARCHAR(255) COMMENT '基本认证密码',
    auth_api_key TEXT COMMENT 'API Key',
    auth_api_key_header VARCHAR(100) DEFAULT 'X-API-Key' COMMENT 'API Key Header名称',
    is_default BOOLEAN DEFAULT FALSE COMMENT '是否为默认实例',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    description TEXT COMMENT '实例描述',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_is_default (is_default),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='目标实例配置表';

-- API端点配置表
CREATE TABLE IF NOT EXISTS api_endpoints (
    id INT AUTO_INCREMENT PRIMARY KEY,
    endpoint_key VARCHAR(100) NOT NULL UNIQUE COMMENT '端点键名',
    endpoint_path VARCHAR(500) NOT NULL COMMENT '端点路径',
    description VARCHAR(500) COMMENT '端点描述',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_endpoint_key (endpoint_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='API端点配置表';

-- 数据库连接配置表
CREATE TABLE IF NOT EXISTS database_connections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    connection_name VARCHAR(100) NOT NULL UNIQUE COMMENT '连接名称',
    db_type VARCHAR(20) NOT NULL DEFAULT 'postgresql' COMMENT '数据库类型',
    host VARCHAR(255) NOT NULL COMMENT '主机地址',
    port INT NOT NULL DEFAULT 5432 COMMENT '端口',
    database_name VARCHAR(100) NOT NULL COMMENT '数据库名',
    username VARCHAR(100) NOT NULL COMMENT '用户名',
    password VARCHAR(255) COMMENT '密码',
    ssl_mode VARCHAR(20) DEFAULT 'prefer' COMMENT 'SSL模式',
    pool_size INT DEFAULT 10 COMMENT '连接池大小',
    max_overflow INT DEFAULT 20 COMMENT '最大溢出连接数',
    pool_timeout INT DEFAULT 30 COMMENT '连接池超时（秒）',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_connection_name (connection_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='数据库连接配置表';

-- 数据库表映射配置
CREATE TABLE IF NOT EXISTS database_table_mappings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    connection_id INT NOT NULL COMMENT '数据库连接ID',
    table_key VARCHAR(100) NOT NULL COMMENT '表键名',
    table_name VARCHAR(100) NOT NULL COMMENT '实际表名',
    description VARCHAR(500) COMMENT '表描述',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (connection_id) REFERENCES database_connections(id) ON DELETE CASCADE,
    UNIQUE KEY uk_connection_table (connection_id, table_key),
    INDEX idx_table_key (table_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='数据库表映射配置';

-- 插入默认系统配置
INSERT INTO system_config (config_key, config_value, config_type, description, is_sensitive) VALUES
('data_source', '"api"', 'string', '数据源类型：api 或 database', FALSE),
('api_base_url', '""', 'string', 'API基础URL', FALSE),
('api_auth_type', '"bearer"', 'string', 'API认证类型', FALSE),
('api_timeout', '30', 'number', 'API请求超时时间（秒）', FALSE),
('api_retry_count', '3', 'number', 'API重试次数', FALSE),
('api_retry_delay', '1', 'number', 'API重试延迟（秒）', FALSE),
('export_default_format', '"yaml"', 'string', '默认导出格式', FALSE),
('logging_level', '"INFO"', 'string', '日志级别', FALSE),
('logging_file', '"logs/app.log"', 'string', '日志文件路径', FALSE),
('logging_max_size', '"10MB"', 'string', '日志文件最大大小', FALSE),
('logging_backup_count', '5', 'number', '日志备份数量', FALSE),
('cache_enabled', 'true', 'boolean', '是否启用缓存', FALSE),
('cache_ttl', '300', 'number', '缓存过期时间（秒）', FALSE),
('pagination_default_page_size', '20', 'number', '默认分页大小', FALSE),
('pagination_max_page_size', '100', 'number', '最大分页大小', FALSE),
('pagination_api_page_size', '50', 'number', 'API分页大小', FALSE)
ON DUPLICATE KEY UPDATE config_value=VALUES(config_value);

-- 插入默认API端点配置
INSERT INTO api_endpoints (endpoint_key, endpoint_path, description) VALUES
('apps_list', '/console/api/apps', '获取应用列表'),
('app_detail', '/console/api/apps/{app_id}', '获取单个应用详情'),
('app_export', '/console/api/apps/{app_id}/export', '应用导出'),
('app_import', '/console/api/apps/imports', '应用导入'),
('workflow_draft', '/console/api/apps/{app_id}/workflows/draft', '获取工作流草稿'),
('workflow_detail', '/console/api/workflows/{workflow_id}', '获取工作流详情'),
('environment_variables', '/console/api/apps/{app_id}/variables', '应用环境变量'),
('import_status', '/console/api/apps/imports/{import_id}', '获取导入状态'),
('import_confirm', '/console/api/apps/imports/{import_id}/confirm', '确认导入'),
('check_dependencies', '/console/api/apps/imports/{import_id}/check-dependencies', '检查依赖')
ON DUPLICATE KEY UPDATE endpoint_path=VALUES(endpoint_path);

-- 插入默认目标实例（示例，实际使用时需要配置真实信息）
INSERT INTO target_instances (id, name, url, auth_type, is_default, description) VALUES
('default', '默认实例', '', 'bearer', TRUE, '默认Dify实例，需要配置URL和认证信息')
ON DUPLICATE KEY UPDATE name=VALUES(name);

