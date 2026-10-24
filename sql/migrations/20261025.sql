-- 见面定金：签到、一对一结算、记给对方的一笔。

CREATE TABLE IF NOT EXISTS `meet_checkin` (
    `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `passport_id` BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `slot_key`    CHAR(64)        NOT NULL DEFAULT '' COMMENT '场次盲索引',
    `order_id`    BIGINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '已核销的定金单',
    `status`      TINYINT UNSIGNED NOT NULL DEFAULT 1,
    `create_time` DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_time` DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_passport_order` (`passport_id`, `order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='见面签到';

CREATE TABLE IF NOT EXISTS `meet_deposit_settle` (
    `id`                 BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `slot_key`           CHAR(64)        NOT NULL DEFAULT '' COMMENT '场次盲索引',
    `order_low_id`       BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `order_high_id`      BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `outcome`            VARCHAR(16)     NOT NULL DEFAULT '' COMMENT 'refund / award / forfeit / skip',
    `winner_passport_id` BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `status`             TINYINT UNSIGNED NOT NULL DEFAULT 1,
    `create_time`        DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_time`        DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_slot_orders` (`slot_key`, `order_low_id`, `order_high_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='定金结算';

CREATE TABLE IF NOT EXISTS `meet_deposit_payout` (
    `id`              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `passport_id`     BIGINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '拿走这笔的人',
    `slot_key`        CHAR(64)        NOT NULL DEFAULT '' COMMENT '场次盲索引',
    `source_order_id` BIGINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '被扣下的定金单',
    `amount_fen`      INT UNSIGNED    NOT NULL DEFAULT 0,
    `pay_status`      TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '0待打款',
    `status`          TINYINT UNSIGNED NOT NULL DEFAULT 1,
    `create_time`     DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_time`     DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_source_order` (`source_order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='记给对方的定金';
