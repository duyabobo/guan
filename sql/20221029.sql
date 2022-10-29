CREATE TABLE `user_change_record` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT 'id',
  `passport_id` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT 'passport_id',
  `change_column` varchar(32) not null default '' COMMENT '修改的column名',
  `new_value` varchar(32) not null default '' comment '修改后的字段值',
  `status` tinyint(3) unsigned NOT NULL DEFAULT '1' COMMENT '逻辑删除标示: 0已删除，1有效',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最近修改时间',
  PRIMARY KEY (`id`),
  KEY `idx_passport_id` (`passport_id`)
) ENGINE=InnoDB AUTO_INCREMENT=202 DEFAULT CHARSET=utf8mb4 COMMENT='用户表变化流水记录';


CREATE TABLE `requirement_change_record` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT 'id',
  `passport_id` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT 'passport_id',
  `change_column` varchar(32) not null default '' COMMENT '修改的column名',
  `new_value` varchar(32) not null default '' comment '修改后的字段值',
  `status` tinyint(3) unsigned NOT NULL DEFAULT '1' COMMENT '逻辑删除标示: 0已删除，1有效',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最近修改时间',
  PRIMARY KEY (`id`),
  KEY `idx_passport_id` (`passport_id`)
) ENGINE=InnoDB AUTO_INCREMENT=202 DEFAULT CHARSET=utf8mb4 COMMENT='需求表变化流水记录';
