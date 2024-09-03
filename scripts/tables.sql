CREATE TABLE IF NOT EXISTS `child`
(
    `id`                  VARCHAR(128) PRIMARY KEY comment 'ID',
    `updated_at`          VARCHAR(255) NOT NULL comment '刷新时间',
    `execute_status`      VARCHAR(128) NOT NULL comment '执行状态',
    `execute_result`      INTEGER DEFAULT 0 comment '结果',
    `converted_model_size` REAL DEFAULT 0.0 comment '转换模型大小',
    `max_totalpss`      INTEGER DEFAULT 0 comment '最大物理内存',
    `max_sysmem`        INTEGER DEFAULT 0 comment '最大系统内存',
    `status` ENUM('active', 'inactive', 'banned') NOT NULL DEFAULT 'active' comment '状态',
    `status_test` ENUM('active', 'inactive') NOT NULL DEFAULT 'active' comment '状态测试',
    `testsssss`        INTEGER DEFAULT 0 comment '最大系统内存'
);

CREATE TABLE IF NOT EXISTS `father`
(
    `id`                  VARCHAR(128) PRIMARY KEY comment 'ID',
    `updated_at`          VARCHAR(255) NOT NULL comment '刷新时间',
    `execute_status`      VARCHAR(128) NOT NULL comment '执行状态',
    `execute_result`      INTEGER DEFAULT 0 comment '结果',
    `converted_model_size` REAL DEFAULT 0.0 comment '转换模型大小',
    `max_totalpss`      INTEGER DEFAULT 0 comment '最大物理内存',
    `max_sysmem`        INTEGER DEFAULT 0 comment '最大系统内存',
    `status` ENUM('active', 'inactive', 'banned') NOT NULL DEFAULT 'active' comment '状态'
);