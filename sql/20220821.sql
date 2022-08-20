create table share (
    `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT 'id',
    `share_passport_id` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT '分享人passportId',
    `accept_passport_id` bigint(20) unsigned not null default '0' comment '接受邀请人passportId',
    `status` tinyint unsigned NOT NULL DEFAULT '1' COMMENT '逻辑删除标示: 0已删除，1有效',
    `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最近修改时间',
    PRIMARY KEY (`id`),
    index idx_region_id (`region_id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='邀请信息';
