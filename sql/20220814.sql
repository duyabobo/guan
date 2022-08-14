create table work (
    `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT 'id',
    `profession` varchar(128) not null default '' comment '行业',
    `major` varchar(128) not null default '' comment '方向',
    `position` varchar(64) not null default '' comment '职位',
    `status` tinyint unsigned NOT NULL DEFAULT '1' COMMENT '逻辑删除标示: 0已删除，1有效',
    `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最近修改时间',
    PRIMARY KEY (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='工作信息';
