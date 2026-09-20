-- 关关雎鸠 初始化 DDL
-- 幂等：所有建表语句使用 CREATE TABLE IF NOT EXISTS
-- 字符集：utf8mb4（支持 emoji）

SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- ── region：省市区 ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `region` (
    `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'id',
    `province`    VARCHAR(128)    NOT NULL DEFAULT '' COMMENT '省',
    `city`        VARCHAR(128)    NOT NULL DEFAULT '' COMMENT '市',
    `area`        VARCHAR(128)    NOT NULL DEFAULT '' COMMENT '区/县',
    `status`      TINYINT UNSIGNED NOT NULL DEFAULT 1 COMMENT '逻辑删除: 0删除 1有效',
    `create_time` DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_time` DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='省市区';

-- ── education：专业信息 ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `education` (
    `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'id',
    `category`    VARCHAR(128)    NOT NULL DEFAULT '' COMMENT '专业门类',
    `disciplines` VARCHAR(128)    NOT NULL DEFAULT '' COMMENT '专业类(学科)',
    `major`       VARCHAR(128)    NOT NULL DEFAULT '' COMMENT '专业',
    `seq`         INT             NOT NULL DEFAULT 0  COMMENT '排序',
    `status`      TINYINT UNSIGNED NOT NULL DEFAULT 1,
    `create_time` DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_time` DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='专业信息';

-- ── work：工作信息 ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `work` (
    `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'id',
    `profession`  VARCHAR(128)    NOT NULL DEFAULT '' COMMENT '行业',
    `industry`    VARCHAR(128)    NOT NULL DEFAULT '' COMMENT '方向',
    `position`    VARCHAR(128)    NOT NULL DEFAULT '' COMMENT '职位',
    `seq`         INT             NOT NULL DEFAULT 0,
    `status`      TINYINT UNSIGNED NOT NULL DEFAULT 1,
    `create_time` DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_time` DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='工作信息';

-- company 表已移除（work 相关功能暂未启用，company_id 字段无业务写入）

-- ── school：学校 ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `school` (
    `id`               BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'id',
    `region_id`        BIGINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '所在省市区id',
    `name`             VARCHAR(256)    NOT NULL DEFAULT '' COMMENT '学校名',
    `logo`             VARCHAR(512)    NOT NULL DEFAULT '' COMMENT '学校logo',
    `nature_name`      VARCHAR(64)     NOT NULL DEFAULT '' COMMENT '公办/民办',
    `school_type_name` VARCHAR(64)     NOT NULL DEFAULT '' COMMENT '专科/本科',
    `seq`              INT             NOT NULL DEFAULT 0,
    `status`           TINYINT UNSIGNED NOT NULL DEFAULT 1,
    `create_time`      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_time`      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学校信息';

-- ── address：见面地点 ───────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `address` (
    `id`           BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'id',
    `name`         VARCHAR(256)    NOT NULL DEFAULT '' COMMENT '地点名',
    `description`  VARCHAR(512)    NOT NULL DEFAULT '' COMMENT '地点描述',
    `region_id`    BIGINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '省市区id',
    `longitude`    DOUBLE          NOT NULL DEFAULT 0 COMMENT '经度',
    `latitude`     DOUBLE          NOT NULL DEFAULT 0 COMMENT '纬度',
    `img_obj_name` VARCHAR(512)    NOT NULL DEFAULT '' COMMENT '七牛对象名',
    `status`       TINYINT UNSIGNED NOT NULL DEFAULT 1,
    `create_time`  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_time`  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='见面地点';

-- ── passport：账号 ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `passport` (
    `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'id',
    `phone`       VARCHAR(32)     NOT NULL DEFAULT '' COMMENT '手机号',
    `openid`      VARCHAR(64)     NOT NULL DEFAULT '' COMMENT '微信openid(md5)',
    `status`      TINYINT UNSIGNED NOT NULL DEFAULT 1,
    `create_time` DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_time` DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    INDEX `idx_openid` (`openid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='账号';

-- ── user：用户信息 ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `user` (
    `id`              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `passport_id`     BIGINT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'passport_id',
    `allow_location`  TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '是否允许获取位置',
    `sex`             TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '性别: 0未知 1男 2女',
    `verify_type`     TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '认证类型: 0无 1学校 2工作',
    `has_head_img`    TINYINT          NOT NULL DEFAULT -1 COMMENT '自定义头像: -1未选 0否 1是',
    `head_img_version` INT             NOT NULL DEFAULT 0,
    `birth_year`      SMALLINT        NOT NULL DEFAULT 0,
    `height`          SMALLINT        NOT NULL DEFAULT 0 COMMENT '身高cm',
    `weight`          SMALLINT        NOT NULL DEFAULT 0 COMMENT '体重kg',
    `home_region_id`  BIGINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '籍贯',
    `study_from_year` SMALLINT        NOT NULL DEFAULT 0 COMMENT '入学年份',
    `study_region_id` BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `school_id`       BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `education_level` TINYINT UNSIGNED NOT NULL DEFAULT 0,
    `education_id`    BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `work_region_id`  BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `work_id`         BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `month_pay`       INT             NOT NULL DEFAULT 0 COMMENT '月收入(元)',
    `martial_status`  TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '婚姻: 0未知 1未婚 2离异',
    `info_has_filled` TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '是否完善信息',
    `profile_desc`    TEXT             NULL               COMMENT '自然语言个人描述原文',
    `status`          TINYINT UNSIGNED NOT NULL DEFAULT 1,
    `create_time`     DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_time`     DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    INDEX `idx_passport_id` (`passport_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户信息';

-- ── requirement：期望条件 ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `requirement` (
    `id`                  BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `passport_id`         BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `verify_type`         TINYINT UNSIGNED NOT NULL DEFAULT 0,
    `sex`                 TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '期望对方性别',
    `min_birth_year`      SMALLINT        NOT NULL DEFAULT 0,
    `max_birth_year`      SMALLINT        NOT NULL DEFAULT 0,
    `min_weight`          SMALLINT        NOT NULL DEFAULT 0,
    `max_weight`          SMALLINT        NOT NULL DEFAULT 0,
    `min_height`          SMALLINT        NOT NULL DEFAULT 0,
    `max_height`          SMALLINT        NOT NULL DEFAULT 0,
    `home_region_id`      BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `min_study_from_year` SMALLINT        NOT NULL DEFAULT 0,
    `max_study_from_year` SMALLINT        NOT NULL DEFAULT 0,
    `study_region_id`     BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `school_id`           BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `education_level`     TINYINT UNSIGNED NOT NULL DEFAULT 0,
    `education_id`        BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `work_region_id`      BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `work_id`             BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `max_month_pay`       INT             NOT NULL DEFAULT 0,
    `min_month_pay`       INT             NOT NULL DEFAULT 0,
    `martial_status`      TINYINT UNSIGNED NOT NULL DEFAULT 0,
    `requirement_desc`    TEXT             NULL      COMMENT '自然语言期望描述原文',
    `status`              TINYINT UNSIGNED NOT NULL DEFAULT 1,
    `create_time`         DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_time`         DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    INDEX `idx_passport_id` (`passport_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='期望条件';

-- ── verify：认证信息 ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `verify` (
    `id`                  BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `passport_id`         BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `mail`                VARCHAR(256)    NOT NULL DEFAULT '' COMMENT '验证邮箱(加密)',
    `mail_type`           TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '邮箱类型: 0无 1学校 2工作',
    `mail_verify_status`  TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '认证状态: 0未认证 1已认证',
    `status`              TINYINT UNSIGNED NOT NULL DEFAULT 1,
    `create_time`         DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_time`         DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    INDEX `idx_passport_id` (`passport_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='认证信息';

-- ── activity：见面活动 ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `activity` (
    `id`               BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `address_id`       BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `start_time`       DATETIME        NOT NULL DEFAULT '1970-01-01 00:00:00' COMMENT '见面时间',
    `girl_passport_id` BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `boy_passport_id`  BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `state`            TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '状态: 0空闲 1邀请中 100已成功',
    `girl_meet_result` TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '女方见面结果: 0未知 1合适 100不合适',
    `boy_meet_result`  TINYINT UNSIGNED NOT NULL DEFAULT 0,
    `status`           TINYINT UNSIGNED NOT NULL DEFAULT 1,
    `create_time`      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_time`      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='见面活动';

-- ── activity_change_record：活动流水 ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `activity_change_record` (
    `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `activity_id` BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `passport_id` BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `change_type` TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '变化: 1发出邀请 2接受 3邀请者取消 4接受者取消',
    `status`      TINYINT UNSIGNED NOT NULL DEFAULT 1,
    `create_time` DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_time` DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='活动流水记录';

-- ── user_change_record：用户信息变更流水 ────────────────────────────────────
CREATE TABLE IF NOT EXISTS `user_change_record` (
    `id`            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `passport_id`   BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `change_column` VARCHAR(64)     NOT NULL DEFAULT '',
    `new_value`     VARCHAR(512)    NOT NULL DEFAULT '',
    `status`        TINYINT UNSIGNED NOT NULL DEFAULT 1,
    `create_time`   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_time`   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户信息变更流水';

-- ── requirement_change_record：期望变更流水 ─────────────────────────────────
CREATE TABLE IF NOT EXISTS `requirement_change_record` (
    `id`            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `passport_id`   BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `change_column` VARCHAR(64)     NOT NULL DEFAULT '',
    `new_value`     VARCHAR(512)    NOT NULL DEFAULT '',
    `status`        TINYINT UNSIGNED NOT NULL DEFAULT 1,
    `create_time`   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_time`   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='期望条件变更流水';

-- ── share：分享记录 ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `share` (
    `id`                BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `share_passport_id` BIGINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '分享人',
    `accept_passport_id` BIGINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '接受人',
    `status`            TINYINT UNSIGNED NOT NULL DEFAULT 1,
    `create_time`       DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_time`       DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='分享记录';
