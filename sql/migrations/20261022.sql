-- 身份密钥与敏感信息密文。密钥和密文分表，业务查询不读密钥表。

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
