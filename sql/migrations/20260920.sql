-- 自然语言输入字段（NULL 可选，无需 DEFAULT）
ALTER TABLE `user`
    ADD COLUMN `profile_desc` TEXT NULL COMMENT '自然语言个人描述原文' AFTER `info_has_filled`;

ALTER TABLE `requirement`
    ADD COLUMN `requirement_desc` TEXT NULL COMMENT '自然语言期望描述原文' AFTER `martial_status`;

-- 移除无业务逻辑写入的字段
ALTER TABLE `user`
    DROP COLUMN `is_fall_in_love`,
    DROP COLUMN `work_level`,
    DROP COLUMN `company_id`;

ALTER TABLE `requirement`
    DROP COLUMN `company_id`;
