alter table user add column school_id bigint unsigned not null default 0 comment '学校id';
alter table user add column company_id bigint unsigned not null default 0 comment '公司id';
alter table user add column education_level smallint unsigned not null default 0 comment '学历：EDUCATION_LEVEL';
alter table requirement add column school_id bigint unsigned not null default 0 comment '学校id';
alter table requirement add column company_id bigint unsigned not null default 0 comment '公司id';
alter table requirement add column education_level smallint unsigned not null default 0 comment '学历：EDUCATION_LEVEL';
alter table work drop column region_id;
alter table work modify column seq smallint unsigned not null default 0 comment '序号越小越靠前';
alter table education drop column region_id;
alter table education modify column seq smallint unsigned not null default 0 comment '序号越小越靠前';
alter table education drop index uk_edu;
alter table education drop column school;
alter table education drop column level;
alter table education add column category varchar(32) not null default '' comment '专业门类';
alter table education add column disciplines varchar(32) not null default '' comment '专业类(学科）';

create table school (
    `id` bigint unsigned NOT NULL AUTO_INCREMENT COMMENT 'id',
    `region_id` bigint unsigned not null default 0 comment '地址id',
    `name` varchar(128) not null default '' comment '学校名(每个校区有一个记录)',
    `seq`  smallint unsigned not null default 0 comment '序号越小越靠前',
    `status` tinyint unsigned NOT NULL DEFAULT '1' COMMENT '逻辑删除标示: 0已删除，1有效',
    `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最近修改时间',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学校';

create table company (
    `id` bigint unsigned NOT NULL AUTO_INCREMENT COMMENT 'id',
    `region_id` bigint unsigned not null default 0 comment '地址id',
    `name` varchar(128) not null default '' comment '公司名(每个分公司有一个记录)',
    `seq`  smallint unsigned not null default 0 comment '序号越小越靠前',
    `status` tinyint unsigned NOT NULL DEFAULT '1' COMMENT '逻辑删除标示: 0已删除，1有效',
    `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最近修改时间',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='公司';
