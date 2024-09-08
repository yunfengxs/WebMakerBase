CREATE TABLE weapons (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '武器的唯一标识符',
    name VARCHAR(255) NOT NULL COMMENT '武器名称',
    quality ENUM('甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸') NOT NULL DEFAULT '癸' COMMENT '品质',
    attack_power INT NOT NULL DEFAULT 1 COMMENT '武器攻击力',
    special_effects TEXT COMMENT '武器特殊效果',
    description TEXT COMMENT '武器描述',
    image_url VARCHAR(255) COMMENT '武器图片地址',
    wear_type ENUM('单手', '双手', '远程', '盾牌') NOT NULL COMMENT '武器类型',
    can_be_destroyed BOOLEAN DEFAULT TRUE COMMENT '是否可以摧毁',
    attribute_bonus TEXT COMMENT '属性加成',
    durability INT DEFAULT 100 COMMENT '耐久度',
    level_requirement INT DEFAULT 1 COMMENT '最低使用等级',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
);
CREATE TABLE fashu (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '武器的唯一标识符',
    name VARCHAR(255) NOT NULL COMMENT '武器名称',
    quality ENUM('甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸') NOT NULL DEFAULT '癸' COMMENT '品质',
    attack_power INT NOT NULL DEFAULT 1 COMMENT '武器攻击力',
    special_effects TEXT COMMENT '武器特殊效果',
    description TEXT COMMENT '武器描述',
    image_url VARCHAR(255) COMMENT '武器图片地址',
    wear_type ENUM('单手', '双手', '远程', '盾牌') NOT NULL COMMENT '武器类型',
    can_be_destroyed BOOLEAN DEFAULT TRUE COMMENT '是否可以摧毁',
    attribute_bonus TEXT COMMENT '属性加成',
    durability INT DEFAULT 100 COMMENT '耐久度',
    level_requirement INT DEFAULT 1 COMMENT '最低使用等级',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
);