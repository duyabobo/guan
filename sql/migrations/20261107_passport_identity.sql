-- 身份收进通行证：unionid 查找值、手机号密文。openid 不再入库。
-- identity_secret 先留着，启动封存读完明文材料后再删。

ALTER TABLE `passport` ADD COLUMN `unionid` VARCHAR(64) NULL DEFAULT NULL COMMENT '身份密钥材料的 HMAC，不存明文';

UPDATE `passport` p
INNER JOIN `identity_secret` s
    ON s.passport_id = p.id AND s.provider = 'wechat' AND s.status = 1 AND s.account_key <> ''
SET p.unionid = s.account_key
WHERE p.unionid IS NULL OR p.unionid = '';

UPDATE `passport` SET `unionid` = NULL WHERE `unionid` = '';

ALTER TABLE `passport` ADD UNIQUE KEY `uk_unionid` (`unionid`);

ALTER TABLE `passport` MODIFY COLUMN `phone` VARCHAR(128) NOT NULL DEFAULT '' COMMENT '手机号密文，用 unionid 材料加密；空表示未绑定';

ALTER TABLE `passport` DROP INDEX `idx_openid`;

ALTER TABLE `passport` DROP COLUMN `openid`;
