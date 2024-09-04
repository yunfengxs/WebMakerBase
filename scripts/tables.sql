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

CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  age INT,
  status ENUM('active', 'inactive') DEFAULT 'active',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users_mul (
  id INT AUTO_INCREMENT PRIMARY KEY comment 'aaaaaaaaa',
  name VARCHAR(100) NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  age INT,
  age1 INT,
  status ENUM('active', 'inactive') DEFAULT 'active',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);