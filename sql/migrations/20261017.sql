-- 个人资料与个人期望：一个维度一行。新增维度只加目录和记录，不加字段。
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
