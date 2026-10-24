-- 见面提醒、爽约记录、单次见面支付。已有库补索引和表。

ALTER TABLE `activity` ADD KEY `idx_state_start` (`state`, `start_time`);

CREATE TABLE IF NOT EXISTS `subscribe_grant` (
    `id`            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `passport_id`   BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `template_id`   VARCHAR(64)     NOT NULL DEFAULT '' COMMENT '订阅模板',
    `openid_nonce`  VARCHAR(32)     NOT NULL DEFAULT '' COMMENT 'AES-GCM nonce, base64',
    `openid_cipher` VARBINARY(255)  NOT NULL COMMENT 'openid 密文',
    `remain`        INT UNSIGNED    NOT NULL DEFAULT 0 COMMENT '还可发送的次数',
    `status`        TINYINT UNSIGNED NOT NULL DEFAULT 1,
    `create_time`   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_time`   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_passport_template` (`passport_id`, `template_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='小程序订阅消息额度';

CREATE TABLE IF NOT EXISTS `notice_sent` (
    `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `activity_id` BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `passport_id` BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `scene`       VARCHAR(32)     NOT NULL DEFAULT '' COMMENT 'meet_soon / decide / list_expire',
    `status`      TINYINT UNSIGNED NOT NULL DEFAULT 1,
    `create_time` DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_time` DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_activity_passport_scene` (`activity_id`, `passport_id`, `scene`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='已发出的到点提醒';

CREATE TABLE IF NOT EXISTS `meet_no_show` (
    `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `passport_id` BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `activity_id` BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `status`      TINYINT UNSIGNED NOT NULL DEFAULT 1,
    `create_time` DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_time` DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_passport_activity` (`passport_id`, `activity_id`),
    KEY `idx_passport` (`passport_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='爽约记录';

CREATE TABLE IF NOT EXISTS `meet_fee_order` (
    `id`                BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `passport_id`       BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `activity_id`       BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `out_trade_no`      VARCHAR(32)     NOT NULL DEFAULT '' COMMENT '商户订单号',
    `amount_fen`        INT UNSIGNED    NOT NULL DEFAULT 0 COMMENT '金额，分',
    `pay_status`        TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '0待支付 1已支付 2已核销 3待退款 4已退款 5已关闭',
    `prepay_id`         VARCHAR(64)     NOT NULL DEFAULT '',
    `wx_transaction_id` VARCHAR(64)     NOT NULL DEFAULT '',
    `status`            TINYINT UNSIGNED NOT NULL DEFAULT 1,
    `create_time`       DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_time`       DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_out_trade_no` (`out_trade_no`),
    KEY `idx_passport_activity` (`passport_id`, `activity_id`, `pay_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='单次见面支付单';
