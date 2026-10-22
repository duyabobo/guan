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

-- ── profile_attr：个人资料与期望，一个维度一行 ─────────────────────────────
CREATE TABLE IF NOT EXISTS `profile_attr` (
    `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `passport_id` BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `scope`       VARCHAR(16)     NOT NULL DEFAULT '' COMMENT 'info 个人信息 / requirement 个人期望',
    `dim_key`     VARCHAR(64)     NOT NULL DEFAULT '' COMMENT '维度键，对应代码里的 ACTIVE_DIMS',
    `value_text`  VARCHAR(512)    NOT NULL DEFAULT '' COMMENT '文本维度的值',
    `value_min`   INT             NOT NULL DEFAULT 0 COMMENT '单值，或区间下限',
    `value_max`   INT             NOT NULL DEFAULT 0 COMMENT '区间上限；单值维度为 0',
    `status`      TINYINT UNSIGNED NOT NULL DEFAULT 1,
    `create_time` DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_time` DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_passport_scope_dim` (`passport_id`, `scope`, `dim_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='个人资料与期望，一个维度一行';

-- ── identity_secret：身份密钥，业务查询不要读 ──────────────────────────────
CREATE TABLE IF NOT EXISTS `identity_secret` (
    `id`              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `passport_id`     BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `provider`        VARCHAR(32)     NOT NULL DEFAULT '' COMMENT 'wechat / national_network',
    `account_key`     VARCHAR(64)     NOT NULL DEFAULT '' COMMENT '登录主体的摘要，不存明文 openid',
    `secret_material` VARCHAR(512)    NOT NULL DEFAULT '' COMMENT '加密密钥材料。微信为 unionid。不进入会话',
    `status`          TINYINT UNSIGNED NOT NULL DEFAULT 1,
    `create_time`     DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_time`     DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_provider_account` (`provider`, `account_key`),
    UNIQUE KEY `uk_passport_provider` (`passport_id`, `provider`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='身份密钥。仅加密写入和最终核查读取';

-- ── sensitive_record：敏感信息密文 ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `sensitive_record` (
    `id`            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `passport_id`   BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `kind`          VARCHAR(16)     NOT NULL DEFAULT '' COMMENT 'voice/phone/mail/photo',
    `key_provider`  VARCHAR(32)     NOT NULL DEFAULT '' COMMENT '加密时使用的身份提供方',
    `nonce`         VARCHAR(32)     NOT NULL DEFAULT '' COMMENT 'AES-GCM nonce, base64',
    `cipher_text`   MEDIUMBLOB      NOT NULL COMMENT '密文，不含密钥',
    `content_type`  VARCHAR(64)     NOT NULL DEFAULT '',
    `plain_length`  INT UNSIGNED    NOT NULL DEFAULT 0 COMMENT '明文长度，不含内容',
    `status`        TINYINT UNSIGNED NOT NULL DEFAULT 1,
    `create_time`   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_time`   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_passport_kind` (`passport_id`, `kind`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='敏感信息密文';
