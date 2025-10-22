/*
 Navicat Premium Dump SQL

 Source Server         : 本地
 Source Server Type    : MySQL
 Source Server Version : 80027 (8.0.27)
 Source Host           : localhost:3306
 Source Schema         : dify_workflow_config

 Target Server Type    : MySQL
 Target Server Version : 80027 (8.0.27)
 File Encoding         : 65001

 Date: 21/10/2025 21:45:37
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for api_endpoints
-- ----------------------------
DROP TABLE IF EXISTS `api_endpoints`;
CREATE TABLE `api_endpoints` (
  `id` int NOT NULL AUTO_INCREMENT,
  `endpoint_key` varchar(100) NOT NULL COMMENT '端点键名',
  `endpoint_path` varchar(500) NOT NULL COMMENT '端点路径',
  `description` varchar(500) DEFAULT NULL COMMENT '端点描述',
  `is_active` tinyint(1) DEFAULT NULL COMMENT '是否启用',
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `endpoint_key` (`endpoint_key`),
  KEY `idx_endpoint_key` (`endpoint_key`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='API端点配置表';

-- ----------------------------
-- Records of api_endpoints
-- ----------------------------
BEGIN;
INSERT INTO `api_endpoints` (`id`, `endpoint_key`, `endpoint_path`, `description`, `is_active`, `created_at`, `updated_at`) VALUES (1, 'apps_list', '/console/api/apps', '获取应用列表', 1, '2025-10-17 09:14:55', '2025-10-17 09:14:55');
INSERT INTO `api_endpoints` (`id`, `endpoint_key`, `endpoint_path`, `description`, `is_active`, `created_at`, `updated_at`) VALUES (2, 'app_detail', '/console/api/apps/{app_id}', '获取单个应用详情', 1, '2025-10-17 09:14:55', '2025-10-17 09:14:55');
INSERT INTO `api_endpoints` (`id`, `endpoint_key`, `endpoint_path`, `description`, `is_active`, `created_at`, `updated_at`) VALUES (3, 'app_export', '/console/api/apps/{app_id}/export', '应用导出', 1, '2025-10-17 09:14:55', '2025-10-17 09:14:55');
INSERT INTO `api_endpoints` (`id`, `endpoint_key`, `endpoint_path`, `description`, `is_active`, `created_at`, `updated_at`) VALUES (4, 'app_import', '/console/api/apps/imports', '应用导入', 1, '2025-10-17 09:14:55', '2025-10-17 09:14:55');
INSERT INTO `api_endpoints` (`id`, `endpoint_key`, `endpoint_path`, `description`, `is_active`, `created_at`, `updated_at`) VALUES (5, 'workflow_draft', '/console/api/apps/{app_id}/workflows/draft', '获取工作流草稿', 1, '2025-10-17 09:14:55', '2025-10-17 09:14:55');
INSERT INTO `api_endpoints` (`id`, `endpoint_key`, `endpoint_path`, `description`, `is_active`, `created_at`, `updated_at`) VALUES (6, 'workflow_detail', '/console/api/workflows/{workflow_id}', '获取工作流详情', 1, '2025-10-17 09:14:55', '2025-10-17 09:14:55');
INSERT INTO `api_endpoints` (`id`, `endpoint_key`, `endpoint_path`, `description`, `is_active`, `created_at`, `updated_at`) VALUES (7, 'environment_variables', '/console/api/apps/{app_id}/variables', '应用环境变量', 1, '2025-10-17 09:14:55', '2025-10-17 09:14:55');
INSERT INTO `api_endpoints` (`id`, `endpoint_key`, `endpoint_path`, `description`, `is_active`, `created_at`, `updated_at`) VALUES (8, 'import_status', '/console/api/apps/imports/{import_id}', '获取导入状态', 1, '2025-10-17 09:14:55', '2025-10-17 09:14:55');
INSERT INTO `api_endpoints` (`id`, `endpoint_key`, `endpoint_path`, `description`, `is_active`, `created_at`, `updated_at`) VALUES (9, 'import_confirm', '/console/api/apps/imports/{import_id}/confirm', '确认导入', 1, '2025-10-17 09:14:55', '2025-10-17 09:14:55');
INSERT INTO `api_endpoints` (`id`, `endpoint_key`, `endpoint_path`, `description`, `is_active`, `created_at`, `updated_at`) VALUES (10, 'check_dependencies', '/console/api/apps/imports/{import_id}/check-dependencies', '检查依赖', 1, '2025-10-17 09:14:55', '2025-10-17 09:14:55');
COMMIT;

-- ----------------------------
-- Table structure for database_connections
-- ----------------------------
DROP TABLE IF EXISTS `database_connections`;
CREATE TABLE `database_connections` (
  `id` int NOT NULL AUTO_INCREMENT,
  `connection_name` varchar(100) NOT NULL COMMENT '连接名称',
  `db_type` varchar(20) NOT NULL COMMENT '数据库类型',
  `host` varchar(255) NOT NULL COMMENT '主机地址',
  `port` int NOT NULL COMMENT '端口',
  `database_name` varchar(100) NOT NULL COMMENT '数据库名',
  `username` varchar(100) NOT NULL COMMENT '用户名',
  `password` varchar(255) DEFAULT NULL COMMENT '密码',
  `ssl_mode` varchar(20) DEFAULT NULL COMMENT 'SSL模式',
  `pool_size` int DEFAULT NULL COMMENT '连接池大小',
  `max_overflow` int DEFAULT NULL COMMENT '最大溢出连接数',
  `pool_timeout` int DEFAULT NULL COMMENT '连接池超时（秒）',
  `is_active` tinyint(1) DEFAULT NULL COMMENT '是否启用',
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `connection_name` (`connection_name`),
  KEY `idx_connection_name` (`connection_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='数据库连接配置表';

-- ----------------------------
-- Records of database_connections
-- ----------------------------
BEGIN;
COMMIT;

-- ----------------------------
-- Table structure for database_table_mappings
-- ----------------------------
DROP TABLE IF EXISTS `database_table_mappings`;
CREATE TABLE `database_table_mappings` (
  `id` int NOT NULL AUTO_INCREMENT,
  `connection_id` int NOT NULL COMMENT '数据库连接ID',
  `table_key` varchar(100) NOT NULL COMMENT '表键名',
  `table_name` varchar(100) NOT NULL COMMENT '实际表名',
  `description` varchar(500) DEFAULT NULL COMMENT '表描述',
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `connection_id` (`connection_id`),
  KEY `idx_table_key` (`table_key`),
  CONSTRAINT `database_table_mappings_ibfk_1` FOREIGN KEY (`connection_id`) REFERENCES `database_connections` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='数据库表映射配置';

-- ----------------------------
-- Records of database_table_mappings
-- ----------------------------
BEGIN;
COMMIT;

-- ----------------------------
-- Table structure for system_config
-- ----------------------------
DROP TABLE IF EXISTS `system_config`;
CREATE TABLE `system_config` (
  `id` int NOT NULL AUTO_INCREMENT,
  `config_key` varchar(100) NOT NULL COMMENT '配置键',
  `config_value` text COMMENT '配置值（JSON格式）',
  `config_type` varchar(50) NOT NULL COMMENT '配置类型：string, number, boolean, json',
  `description` varchar(500) DEFAULT NULL COMMENT '配置描述',
  `is_sensitive` tinyint(1) DEFAULT NULL COMMENT '是否为敏感信息',
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `config_key` (`config_key`),
  KEY `idx_config_key` (`config_key`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='系统配置表';

-- ----------------------------
-- Records of system_config
-- ----------------------------
BEGIN;
INSERT INTO `system_config` (`id`, `config_key`, `config_value`, `config_type`, `description`, `is_sensitive`, `created_at`, `updated_at`) VALUES (1, 'data_source', '\"api\"', 'string', '数据源类型', 0, '2025-10-17 09:14:54', '2025-10-17 09:14:54');
INSERT INTO `system_config` (`id`, `config_key`, `config_value`, `config_type`, `description`, `is_sensitive`, `created_at`, `updated_at`) VALUES (2, 'api_base_url', '\"https://dify.jototech.cn/\"', 'string', 'API基础URL', 0, '2025-10-17 09:14:54', '2025-10-17 09:14:54');
INSERT INTO `system_config` (`id`, `config_key`, `config_value`, `config_type`, `description`, `is_sensitive`, `created_at`, `updated_at`) VALUES (3, 'api_auth_type', '\"bearer\"', 'string', 'API认证类型', 0, '2025-10-17 09:14:54', '2025-10-17 09:14:54');
INSERT INTO `system_config` (`id`, `config_key`, `config_value`, `config_type`, `description`, `is_sensitive`, `created_at`, `updated_at`) VALUES (4, 'api_timeout', '30', 'number', 'API超时时间', 0, '2025-10-17 09:14:54', '2025-10-17 09:14:54');
INSERT INTO `system_config` (`id`, `config_key`, `config_value`, `config_type`, `description`, `is_sensitive`, `created_at`, `updated_at`) VALUES (5, 'api_retry_count', '3', 'number', 'API重试次数', 0, '2025-10-17 09:14:54', '2025-10-17 09:14:54');
INSERT INTO `system_config` (`id`, `config_key`, `config_value`, `config_type`, `description`, `is_sensitive`, `created_at`, `updated_at`) VALUES (6, 'api_retry_delay', '1', 'number', 'API重试延迟', 0, '2025-10-17 09:14:54', '2025-10-17 09:14:54');
INSERT INTO `system_config` (`id`, `config_key`, `config_value`, `config_type`, `description`, `is_sensitive`, `created_at`, `updated_at`) VALUES (7, 'pagination_default_page_size', '20', 'number', '默认分页大小', 0, '2025-10-17 09:14:54', '2025-10-17 09:14:54');
INSERT INTO `system_config` (`id`, `config_key`, `config_value`, `config_type`, `description`, `is_sensitive`, `created_at`, `updated_at`) VALUES (8, 'pagination_max_page_size', '100', 'number', '最大分页大小', 0, '2025-10-17 09:14:54', '2025-10-17 09:14:54');
INSERT INTO `system_config` (`id`, `config_key`, `config_value`, `config_type`, `description`, `is_sensitive`, `created_at`, `updated_at`) VALUES (9, 'pagination_api_page_size', '50', 'number', 'API分页大小', 0, '2025-10-17 09:14:54', '2025-10-17 09:14:54');
INSERT INTO `system_config` (`id`, `config_key`, `config_value`, `config_type`, `description`, `is_sensitive`, `created_at`, `updated_at`) VALUES (10, 'export_default_format', '\"yaml\"', 'string', '默认导出格式', 0, '2025-10-17 09:14:54', '2025-10-17 09:14:54');
INSERT INTO `system_config` (`id`, `config_key`, `config_value`, `config_type`, `description`, `is_sensitive`, `created_at`, `updated_at`) VALUES (11, 'logging_level', '\"INFO\"', 'string', '日志级别', 0, '2025-10-17 09:14:54', '2025-10-17 09:14:54');
INSERT INTO `system_config` (`id`, `config_key`, `config_value`, `config_type`, `description`, `is_sensitive`, `created_at`, `updated_at`) VALUES (12, 'logging_file', '\"logs/app.log\"', 'string', '日志文件路径', 0, '2025-10-17 09:14:54', '2025-10-17 09:14:54');
INSERT INTO `system_config` (`id`, `config_key`, `config_value`, `config_type`, `description`, `is_sensitive`, `created_at`, `updated_at`) VALUES (13, 'logging_max_size', '\"10MB\"', 'string', '日志文件最大大小', 0, '2025-10-17 09:14:54', '2025-10-17 09:14:54');
INSERT INTO `system_config` (`id`, `config_key`, `config_value`, `config_type`, `description`, `is_sensitive`, `created_at`, `updated_at`) VALUES (14, 'logging_backup_count', '5', 'number', '日志备份数量', 0, '2025-10-17 09:14:54', '2025-10-17 09:14:54');
INSERT INTO `system_config` (`id`, `config_key`, `config_value`, `config_type`, `description`, `is_sensitive`, `created_at`, `updated_at`) VALUES (15, 'cache_enabled', 'true', 'boolean', '是否启用缓存', 0, '2025-10-17 09:14:55', '2025-10-17 09:14:55');
INSERT INTO `system_config` (`id`, `config_key`, `config_value`, `config_type`, `description`, `is_sensitive`, `created_at`, `updated_at`) VALUES (16, 'cache_ttl', '300', 'number', '缓存过期时间', 0, '2025-10-17 09:14:55', '2025-10-17 09:14:55');
INSERT INTO `system_config` (`id`, `config_key`, `config_value`, `config_type`, `description`, `is_sensitive`, `created_at`, `updated_at`) VALUES (17, 'api_bearer_token', '\"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjI2OWYzNmUtNDgxYS00NDZiLTliYmItYjcyM2NiMTZkMjc2IiwiZXhwIjoxNzYwOTI5OTAzLCJpc3MiOiJTRUxGX0hPU1RFRCIsInN1YiI6IkNvbnNvbGUgQVBJIFBhc3Nwb3J0In0.UpcBppDbUOIJ9NzEplXSpr8gzHZlvs7I_T67Vj60kfU\"', 'string', '​Bearer Token', 1, '2025-10-20 02:23:55', '2025-10-20 02:23:55');
INSERT INTO `system_config` (`id`, `config_key`, `config_value`, `config_type`, `description`, `is_sensitive`, `created_at`, `updated_at`) VALUES (18, 'api_basic_username', '\"\"', 'string', 'Basic认证用户名', 0, '2025-10-20 02:23:55', '2025-10-20 02:23:55');
INSERT INTO `system_config` (`id`, `config_key`, `config_value`, `config_type`, `description`, `is_sensitive`, `created_at`, `updated_at`) VALUES (19, 'api_key_header', '\"X-API-Key\"', 'string', 'API Key Header名称', 0, '2025-10-20 02:23:55', '2025-10-20 02:23:55');
COMMIT;

-- ----------------------------
-- Table structure for target_instances
-- ----------------------------
DROP TABLE IF EXISTS `target_instances`;
CREATE TABLE `target_instances` (
  `id` varchar(50) NOT NULL COMMENT '实例ID',
  `name` varchar(100) NOT NULL COMMENT '实例名称',
  `url` varchar(500) NOT NULL COMMENT '实例URL',
  `auth_type` varchar(20) NOT NULL COMMENT '认证类型：bearer, basic, api_key',
  `auth_token` text COMMENT 'Bearer Token',
  `auth_username` varchar(100) DEFAULT NULL COMMENT '基本认证用户名',
  `auth_password` varchar(255) DEFAULT NULL COMMENT '基本认证密码',
  `auth_api_key` text COMMENT 'API Key',
  `auth_api_key_header` varchar(100) DEFAULT NULL COMMENT 'API Key Header名称',
  `is_default` tinyint(1) DEFAULT NULL COMMENT '是否为默认实例',
  `is_active` tinyint(1) DEFAULT NULL COMMENT '是否启用',
  `description` text COMMENT '实例描述',
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_is_default` (`is_default`),
  KEY `idx_is_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='目标实例配置表';

-- ----------------------------
-- Records of target_instances
-- ----------------------------
BEGIN;
INSERT INTO `target_instances` (`id`, `name`, `url`, `auth_type`, `auth_token`, `auth_username`, `auth_password`, `auth_api_key`, `auth_api_key_header`, `is_default`, `is_active`, `description`, `created_at`, `updated_at`) VALUES ('default', '本地Dify实例', 'https://dify.jototech.cn/', 'bearer', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjI2OWYzNmUtNDgxYS00NDZiLTliYmItYjcyM2NiMTZkMjc2IiwiZXhwIjoxNzYwOTI5OTAzLCJpc3MiOiJTRUxGX0hPU1RFRCIsInN1YiI6IkNvbnNvbGUgQVBJIFBhc3Nwb3J0In0.UpcBppDbUOIJ9NzEplXSpr8gzHZlvs7I_T67Vj60kfU', NULL, NULL, NULL, 'X-API-Key', 1, 1, '', '2025-10-17 09:14:55', '2025-10-20 02:12:33');
INSERT INTO `target_instances` (`id`, `name`, `url`, `auth_type`, `auth_token`, `auth_username`, `auth_password`, `auth_api_key`, `auth_api_key_header`, `is_default`, `is_active`, `description`, `created_at`, `updated_at`) VALUES ('production', '生产环境Dify', 'https://prod-dify.company.com/', 'bearer', 'prod_console_api_token_here', NULL, NULL, NULL, 'X-API-Key', 0, 1, '', '2025-10-17 09:14:55', '2025-10-17 09:14:55');
COMMIT;

-- ----------------------------
-- Table structure for user_database_connections
-- ----------------------------
DROP TABLE IF EXISTS `user_database_connections`;
CREATE TABLE `user_database_connections` (
  `id` varchar(36) NOT NULL COMMENT '连接ID（UUID）',
  `user_id` varchar(36) NOT NULL COMMENT '用户ID',
  `connection_name` varchar(100) NOT NULL COMMENT '连接名称',
  `db_type` enum('postgresql','mysql') DEFAULT 'postgresql' COMMENT '数据库类型',
  `host` varchar(255) NOT NULL COMMENT '主机地址',
  `port` int NOT NULL COMMENT '端口',
  `database_name` varchar(100) NOT NULL COMMENT '数据库名',
  `username` varchar(100) NOT NULL COMMENT '用户名',
  `password_encrypted` text COMMENT '加密后的密码',
  `ssl_mode` varchar(50) DEFAULT 'prefer' COMMENT 'SSL模式',
  `pool_size` int DEFAULT '10' COMMENT '连接池大小',
  `max_overflow` int DEFAULT '20' COMMENT '最大溢出连接数',
  `pool_timeout` int DEFAULT '30' COMMENT '连接池超时时间',
  `is_active` tinyint(1) DEFAULT '1' COMMENT '是否启用',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_is_active` (`is_active`),
  CONSTRAINT `user_database_connections_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='用户数据库连接配置表';

-- ----------------------------
-- Records of user_database_connections
-- ----------------------------
BEGIN;
COMMIT;

-- ----------------------------
-- Table structure for user_sessions
-- ----------------------------
DROP TABLE IF EXISTS `user_sessions`;
CREATE TABLE `user_sessions` (
  `id` varchar(36) NOT NULL COMMENT '会话ID（UUID）',
  `user_id` varchar(36) NOT NULL COMMENT '用户ID',
  `token_jti` varchar(255) NOT NULL COMMENT 'JWT JTI（唯一标识符）',
  `expires_at` timestamp NOT NULL COMMENT '过期时间',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `token_jti` (`token_jti`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_token_jti` (`token_jti`),
  KEY `idx_expires_at` (`expires_at`),
  CONSTRAINT `user_sessions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='用户会话表';

-- ----------------------------
-- Records of user_sessions
-- ----------------------------
BEGIN;
INSERT INTO `user_sessions` (`id`, `user_id`, `token_jti`, `expires_at`, `created_at`) VALUES ('4a260957-3b51-4e17-b970-379bebf2c973', '3184c55d-98ec-493f-a240-acf4cfb3327f', '1e7bda10-5ff2-4374-a543-b910e5ebc16f', '2025-10-21 03:42:07', '2025-10-20 11:42:06');
INSERT INTO `user_sessions` (`id`, `user_id`, `token_jti`, `expires_at`, `created_at`) VALUES ('63f368a4-2195-4af8-919b-85e7a23a5a00', '3184c55d-98ec-493f-a240-acf4cfb3327f', '46c016b8-7d16-49b0-8389-6c8610331426', '2025-10-27 04:24:27', '2025-10-20 12:24:27');
INSERT INTO `user_sessions` (`id`, `user_id`, `token_jti`, `expires_at`, `created_at`) VALUES ('af6fd4eb-b2ad-49ba-855e-fc8de9264112', '3184c55d-98ec-493f-a240-acf4cfb3327f', '9efb733f-acf5-4c7f-97b8-f4c44eafbc40', '2025-10-27 04:27:25', '2025-10-20 12:27:25');
INSERT INTO `user_sessions` (`id`, `user_id`, `token_jti`, `expires_at`, `created_at`) VALUES ('b3c9656d-214b-4128-a24c-a78fece2fb73', '3184c55d-98ec-493f-a240-acf4cfb3327f', '75687e86-71d6-4200-a5f1-ab7d5c9db30c', '2025-10-27 14:53:00', '2025-10-20 22:53:00');
INSERT INTO `user_sessions` (`id`, `user_id`, `token_jti`, `expires_at`, `created_at`) VALUES ('de0c284b-133b-495a-a582-9c8b6f4524bf', '3184c55d-98ec-493f-a240-acf4cfb3327f', '5f3d1e43-ab17-4fa9-9009-79b95b3c9428', '2025-10-21 03:41:25', '2025-10-20 11:41:25');
INSERT INTO `user_sessions` (`id`, `user_id`, `token_jti`, `expires_at`, `created_at`) VALUES ('eb19af2a-5bdc-4d6c-a451-dd0734e4c4c0', '5fac7c68-561d-42e1-ba1b-fb81b9873d27', 'b01b7247-e273-4bd7-bc57-dc607d81e130', '2025-10-28 10:13:48', '2025-10-21 18:13:47');
COMMIT;

-- ----------------------------
-- Table structure for user_system_config
-- ----------------------------
DROP TABLE IF EXISTS `user_system_config`;
CREATE TABLE `user_system_config` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` varchar(36) NOT NULL COMMENT '用户ID',
  `config_key` varchar(100) NOT NULL COMMENT '配置键',
  `config_value` text COMMENT '配置值',
  `config_type` enum('string','number','boolean','json') DEFAULT 'string' COMMENT '配置类型',
  `description` text COMMENT '配置描述',
  `is_sensitive` tinyint(1) DEFAULT '0' COMMENT '是否为敏感信息',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_user_config` (`user_id`,`config_key`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_config_key` (`config_key`),
  CONSTRAINT `user_system_config_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='用户系统配置表';

-- ----------------------------
-- Records of user_system_config
-- ----------------------------
BEGIN;
INSERT INTO `user_system_config` (`id`, `user_id`, `config_key`, `config_value`, `config_type`, `description`, `is_sensitive`, `created_at`, `updated_at`) VALUES (1, '3184c55d-98ec-493f-a240-acf4cfb3327f', 'api_base_url', 'https://dify.jototech.cn', 'string', 'API基础URL', 0, '2025-10-20 22:34:45', '2025-10-20 23:02:27');
INSERT INTO `user_system_config` (`id`, `user_id`, `config_key`, `config_value`, `config_type`, `description`, `is_sensitive`, `created_at`, `updated_at`) VALUES (2, '3184c55d-98ec-493f-a240-acf4cfb3327f', 'api_auth_type', 'bearer', 'string', 'API认证类型', 0, '2025-10-20 22:34:45', '2025-10-20 23:02:27');
INSERT INTO `user_system_config` (`id`, `user_id`, `config_key`, `config_value`, `config_type`, `description`, `is_sensitive`, `created_at`, `updated_at`) VALUES (3, '3184c55d-98ec-493f-a240-acf4cfb3327f', 'api_bearer_token', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjI2OWYzNmUtNDgxYS00NDZiLTliYmItYjcyM2NiMTZkMjc2IiwiZXhwIjoxNzYwOTczOTMxLCJpc3MiOiJTRUxGX0hPU1RFRCIsInN1YiI6IkNvbnNvbGUgQVBJIFBhc3Nwb3J0In0.4M85OCLaie35jJRhRWU2nxTBfvRmkDGP6-NIzHA1DFo', 'string', 'Bearer Token', 0, '2025-10-20 22:34:45', '2025-10-20 23:02:27');
INSERT INTO `user_system_config` (`id`, `user_id`, `config_key`, `config_value`, `config_type`, `description`, `is_sensitive`, `created_at`, `updated_at`) VALUES (4, '3184c55d-98ec-493f-a240-acf4cfb3327f', 'api_timeout', '30', 'number', 'API超时时间', 0, '2025-10-20 22:34:45', '2025-10-20 23:02:27');
INSERT INTO `user_system_config` (`id`, `user_id`, `config_key`, `config_value`, `config_type`, `description`, `is_sensitive`, `created_at`, `updated_at`) VALUES (5, '3184c55d-98ec-493f-a240-acf4cfb3327f', 'api_retry_count', '3', 'number', 'API重试次数', 0, '2025-10-20 22:34:45', '2025-10-20 23:02:27');
INSERT INTO `user_system_config` (`id`, `user_id`, `config_key`, `config_value`, `config_type`, `description`, `is_sensitive`, `created_at`, `updated_at`) VALUES (6, '3184c55d-98ec-493f-a240-acf4cfb3327f', 'api_retry_delay', '1', 'number', 'API重试延迟', 0, '2025-10-20 22:34:45', '2025-10-20 23:02:27');
INSERT INTO `user_system_config` (`id`, `user_id`, `config_key`, `config_value`, `config_type`, `description`, `is_sensitive`, `created_at`, `updated_at`) VALUES (7, '3184c55d-98ec-493f-a240-acf4cfb3327f', 'data_source', 'api', 'string', '数据源类型', 0, '2025-10-20 22:34:45', '2025-10-20 23:02:27');
INSERT INTO `user_system_config` (`id`, `user_id`, `config_key`, `config_value`, `config_type`, `description`, `is_sensitive`, `created_at`, `updated_at`) VALUES (8, '3184c55d-98ec-493f-a240-acf4cfb3327f', 'export_default_format', 'yaml', 'string', '默认导出格式', 0, '2025-10-20 22:34:45', '2025-10-20 23:02:27');
INSERT INTO `user_system_config` (`id`, `user_id`, `config_key`, `config_value`, `config_type`, `description`, `is_sensitive`, `created_at`, `updated_at`) VALUES (9, '3184c55d-98ec-493f-a240-acf4cfb3327f', 'pagination_default_page_size', '20', 'number', '默认分页大小', 0, '2025-10-20 22:34:45', '2025-10-20 23:02:27');
INSERT INTO `user_system_config` (`id`, `user_id`, `config_key`, `config_value`, `config_type`, `description`, `is_sensitive`, `created_at`, `updated_at`) VALUES (10, '3184c55d-98ec-493f-a240-acf4cfb3327f', 'pagination_max_page_size', '100', 'number', '最大分页大小', 0, '2025-10-20 22:34:45', '2025-10-20 23:02:27');
INSERT INTO `user_system_config` (`id`, `user_id`, `config_key`, `config_value`, `config_type`, `description`, `is_sensitive`, `created_at`, `updated_at`) VALUES (11, '3184c55d-98ec-493f-a240-acf4cfb3327f', 'pagination_api_page_size', '50', 'number', 'API分页大小', 0, '2025-10-20 22:34:45', '2025-10-20 23:02:27');
INSERT INTO `user_system_config` (`id`, `user_id`, `config_key`, `config_value`, `config_type`, `description`, `is_sensitive`, `created_at`, `updated_at`) VALUES (12, '3184c55d-98ec-493f-a240-acf4cfb3327f', 'cache_enabled', 'true', 'boolean', '是否启用缓存', 0, '2025-10-20 22:34:45', '2025-10-20 23:02:27');
INSERT INTO `user_system_config` (`id`, `user_id`, `config_key`, `config_value`, `config_type`, `description`, `is_sensitive`, `created_at`, `updated_at`) VALUES (13, '3184c55d-98ec-493f-a240-acf4cfb3327f', 'cache_ttl', '300', 'number', '缓存过期时间', 0, '2025-10-20 22:34:45', '2025-10-20 23:02:27');
INSERT INTO `user_system_config` (`id`, `user_id`, `config_key`, `config_value`, `config_type`, `description`, `is_sensitive`, `created_at`, `updated_at`) VALUES (14, '5fac7c68-561d-42e1-ba1b-fb81b9873d27', 'api_base_url', 'https://dify.jototech.cn/', 'string', 'API基础URL', 0, '2025-10-21 18:14:50', '2025-10-21 18:15:56');
INSERT INTO `user_system_config` (`id`, `user_id`, `config_key`, `config_value`, `config_type`, `description`, `is_sensitive`, `created_at`, `updated_at`) VALUES (15, '5fac7c68-561d-42e1-ba1b-fb81b9873d27', 'api_auth_type', 'bearer', 'string', 'API认证类型', 0, '2025-10-21 18:14:51', '2025-10-21 18:15:56');
INSERT INTO `user_system_config` (`id`, `user_id`, `config_key`, `config_value`, `config_type`, `description`, `is_sensitive`, `created_at`, `updated_at`) VALUES (16, '5fac7c68-561d-42e1-ba1b-fb81b9873d27', 'api_bearer_token', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjI2OWYzNmUtNDgxYS00NDZiLTliYmItYjcyM2NiMTZkMjc2IiwiZXhwIjoxNzYxMDQ1MjYzLCJpc3MiOiJTRUxGX0hPU1RFRCIsInN1YiI6IkNvbnNvbGUgQVBJIFBhc3Nwb3J0In0.yxA298yrQdFUNJAbIRUytC7G9DooKLWUYFfcOpTP0lQ', 'string', 'Bearer Token', 0, '2025-10-21 18:14:51', '2025-10-21 18:15:56');
INSERT INTO `user_system_config` (`id`, `user_id`, `config_key`, `config_value`, `config_type`, `description`, `is_sensitive`, `created_at`, `updated_at`) VALUES (17, '5fac7c68-561d-42e1-ba1b-fb81b9873d27', 'api_timeout', '30', 'number', 'API超时时间', 0, '2025-10-21 18:14:51', '2025-10-21 18:15:56');
INSERT INTO `user_system_config` (`id`, `user_id`, `config_key`, `config_value`, `config_type`, `description`, `is_sensitive`, `created_at`, `updated_at`) VALUES (18, '5fac7c68-561d-42e1-ba1b-fb81b9873d27', 'api_retry_count', '3', 'number', 'API重试次数', 0, '2025-10-21 18:14:51', '2025-10-21 18:15:56');
INSERT INTO `user_system_config` (`id`, `user_id`, `config_key`, `config_value`, `config_type`, `description`, `is_sensitive`, `created_at`, `updated_at`) VALUES (19, '5fac7c68-561d-42e1-ba1b-fb81b9873d27', 'api_retry_delay', '1', 'number', 'API重试延迟', 0, '2025-10-21 18:14:51', '2025-10-21 18:15:56');
INSERT INTO `user_system_config` (`id`, `user_id`, `config_key`, `config_value`, `config_type`, `description`, `is_sensitive`, `created_at`, `updated_at`) VALUES (20, '5fac7c68-561d-42e1-ba1b-fb81b9873d27', 'data_source', 'api', 'string', '数据源类型', 0, '2025-10-21 18:14:51', '2025-10-21 18:15:56');
INSERT INTO `user_system_config` (`id`, `user_id`, `config_key`, `config_value`, `config_type`, `description`, `is_sensitive`, `created_at`, `updated_at`) VALUES (21, '5fac7c68-561d-42e1-ba1b-fb81b9873d27', 'export_default_format', 'yaml', 'string', '默认导出格式', 0, '2025-10-21 18:14:51', '2025-10-21 18:15:56');
INSERT INTO `user_system_config` (`id`, `user_id`, `config_key`, `config_value`, `config_type`, `description`, `is_sensitive`, `created_at`, `updated_at`) VALUES (22, '5fac7c68-561d-42e1-ba1b-fb81b9873d27', 'pagination_default_page_size', '20', 'number', '默认分页大小', 0, '2025-10-21 18:14:51', '2025-10-21 18:15:56');
INSERT INTO `user_system_config` (`id`, `user_id`, `config_key`, `config_value`, `config_type`, `description`, `is_sensitive`, `created_at`, `updated_at`) VALUES (23, '5fac7c68-561d-42e1-ba1b-fb81b9873d27', 'pagination_max_page_size', '100', 'number', '最大分页大小', 0, '2025-10-21 18:14:51', '2025-10-21 18:15:56');
INSERT INTO `user_system_config` (`id`, `user_id`, `config_key`, `config_value`, `config_type`, `description`, `is_sensitive`, `created_at`, `updated_at`) VALUES (24, '5fac7c68-561d-42e1-ba1b-fb81b9873d27', 'pagination_api_page_size', '50', 'number', 'API分页大小', 0, '2025-10-21 18:14:51', '2025-10-21 18:15:56');
INSERT INTO `user_system_config` (`id`, `user_id`, `config_key`, `config_value`, `config_type`, `description`, `is_sensitive`, `created_at`, `updated_at`) VALUES (25, '5fac7c68-561d-42e1-ba1b-fb81b9873d27', 'cache_enabled', 'true', 'boolean', '是否启用缓存', 0, '2025-10-21 18:14:51', '2025-10-21 18:15:56');
INSERT INTO `user_system_config` (`id`, `user_id`, `config_key`, `config_value`, `config_type`, `description`, `is_sensitive`, `created_at`, `updated_at`) VALUES (26, '5fac7c68-561d-42e1-ba1b-fb81b9873d27', 'cache_ttl', '300', 'number', '缓存过期时间', 0, '2025-10-21 18:14:51', '2025-10-21 18:15:56');
COMMIT;

-- ----------------------------
-- Table structure for user_target_instances
-- ----------------------------
DROP TABLE IF EXISTS `user_target_instances`;
CREATE TABLE `user_target_instances` (
  `id` varchar(36) NOT NULL COMMENT '实例ID（UUID）',
  `user_id` varchar(36) NOT NULL COMMENT '用户ID',
  `instance_name` varchar(100) NOT NULL COMMENT '实例名称',
  `instance_url` varchar(500) NOT NULL COMMENT '实例URL',
  `auth_type` enum('bearer','basic','api_key') DEFAULT 'bearer' COMMENT '认证类型',
  `auth_config` json DEFAULT NULL COMMENT '认证配置（JSON格式）',
  `description` text COMMENT '实例描述',
  `is_active` tinyint(1) DEFAULT '1' COMMENT '是否启用',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_is_active` (`is_active`),
  CONSTRAINT `user_target_instances_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='用户目标实例配置表';

-- ----------------------------
-- Records of user_target_instances
-- ----------------------------
BEGIN;
INSERT INTO `user_target_instances` (`id`, `user_id`, `instance_name`, `instance_url`, `auth_type`, `auth_config`, `description`, `is_active`, `created_at`, `updated_at`) VALUES ('instance-1761041701159', '5fac7c68-561d-42e1-ba1b-fb81b9873d27', 'dify-1', 'https://dify.jototech.cn/', 'bearer', '{\"token\": \"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjI2OWYzNmUtNDgxYS00NDZiLTliYmItYjcyM2NiMTZkMjc2IiwiZXhwIjoxNzYxMDQ1MjYzLCJpc3MiOiJTRUxGX0hPU1RFRCIsInN1YiI6IkNvbnNvbGUgQVBJIFBhc3Nwb3J0In0.yxA298yrQdFUNJAbIRUytC7G9DooKLWUYFfcOpTP0lQ\"}', '', 1, '2025-10-21 18:15:56', '2025-10-21 18:15:56');
COMMIT;

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` varchar(36) NOT NULL COMMENT '用户ID（UUID）',
  `email` varchar(255) NOT NULL COMMENT '邮箱（登录账号）',
  `password_hash` varchar(255) NOT NULL COMMENT '密码哈希',
  `username` varchar(100) NOT NULL COMMENT '用户名',
  `is_admin` tinyint(1) DEFAULT '0' COMMENT '是否为管理员',
  `is_active` tinyint(1) DEFAULT '1' COMMENT '是否启用',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `last_login_at` timestamp NULL DEFAULT NULL COMMENT '最后登录时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  KEY `idx_email` (`email`),
  KEY `idx_is_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='用户表';

-- ----------------------------
-- Records of users
-- ----------------------------
BEGIN;
INSERT INTO `users` (`id`, `email`, `password_hash`, `username`, `is_admin`, `is_active`, `created_at`, `updated_at`, `last_login_at`) VALUES ('3184c55d-98ec-493f-a240-acf4cfb3327f', 'admin@example.com', '$2b$12$269MGWK/gNFiY7mIZl98ceYCmM6eksW5PV.aGVfQOv9z8wX7XiMtC', '系统管理员', 1, 1, '2025-10-20 11:30:06', '2025-10-20 22:55:32', '2025-10-20 22:55:32');
INSERT INTO `users` (`id`, `email`, `password_hash`, `username`, `is_admin`, `is_active`, `created_at`, `updated_at`, `last_login_at`) VALUES ('5fac7c68-561d-42e1-ba1b-fb81b9873d27', 'abian@abian.com', '$2b$12$GmwY5PK.LYaOYZoFbEAUCe2/Nz9chjSoQIxVkFEZgU6G.xgDa/NDK', 'abian@abian.com', 0, 1, '2025-10-21 18:13:35', '2025-10-21 18:13:47', '2025-10-21 18:13:48');
COMMIT;

SET FOREIGN_KEY_CHECKS = 1;
