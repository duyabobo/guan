-- ADD COLUMN：全新库（列不存在）→ 成功；已存在 → 1060 幂等忽略
ALTER TABLE `user`
    ADD COLUMN `profile_desc` TEXT NULL COMMENT '自然语言个人描述原文' AFTER `info_has_filled`;

ALTER TABLE `requirement`
    ADD COLUMN `requirement_desc` TEXT NULL COMMENT '自然语言期望描述原文' AFTER `martial_status`;

-- MODIFY COLUMN：修正旧库里 NOT NULL 遗留问题（列已存在时强制改 NULL）
ALTER TABLE `user`
    MODIFY COLUMN `profile_desc` TEXT NULL COMMENT '自然语言个人描述原文';

ALTER TABLE `requirement`
    MODIFY COLUMN `requirement_desc` TEXT NULL COMMENT '自然语言期望描述原文';

-- 移除无业务写入的冗余字段（已存在则删，不存在则 1091 幂等忽略）
ALTER TABLE `user`
    DROP COLUMN `is_fall_in_love`;

ALTER TABLE `user`
    DROP COLUMN `work_level`;

ALTER TABLE `user`
    DROP COLUMN `company_id`;

ALTER TABLE `requirement`
    DROP COLUMN `company_id`;
