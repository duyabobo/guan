alter table user drop column home_province,drop column home_city, drop column home_area,drop column province, drop column city, drop column school, drop column major, drop column education;
alter table requirement drop column home_province,drop column home_city, drop column home_area,drop column province, drop column city, drop column school, drop column major, drop column study_from_year, drop column school_type;
alter table user add column home_region_id bigint unsigned not null default 0 comment '籍贯地点id' after weight, add column study_region_id bigint unsigned not null default 0 comment '学习地点id' after home_region_id, add column education_id bigint unsigned not null default 0 comment '学习信息id' after study_region_id;
alter table requirement add column home_region_id bigint unsigned not null default 0 comment '籍贯地点id' after max_height, add column study_region_id bigint unsigned not null default 0 comment '学习地点id' after home_region_id, add column education_id bigint unsigned not null default 0 comment '学习信息id' after study_region_id, add column min_study_from_year smallint not null default 0 comment '最早入学年份' after education_id, add column max_study_from_year smallint not null default 0 comment '最晚入学年份';
alter table address drop column province, drop column city, drop column area;
alter table address add column region_id bigint unsigned not null default 0 comment '省市区id';

create table education (
    `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT 'id',
    `school` varchar(128) not null default '' comment '学校',
    `level` varchar(32) not null default '' comment '学历枚举：EDUCATION_CHOICE_LIST',
    `major` varchar(32) not null default '' comment '专业',
    `status` tinyint unsigned NOT NULL DEFAULT '1' COMMENT '逻辑删除标示: 0已删除，1有效',
    `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最近修改时间',
    PRIMARY KEY (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='专业信息';

create table region (
    `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT 'id',
    `province` varchar(128) not null default '' comment '省',
    `city` varchar(128) not null default '' comment '市',
    `area` varchar(128) not null default '' comment '区/县',
    `status` tinyint unsigned NOT NULL DEFAULT '1' COMMENT '逻辑删除标示: 0已删除，1有效',
    `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最近修改时间',
    PRIMARY KEY (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='省市区信息';

alter table user drop column has_fill_finish;
alter table requirement add column verify_type tinyint unsigned not null default 0 comment '认证类型：MODEL_VERIFY_TYPE' after id;
alter table requirement drop column min_education, drop column max_education;
alter table user drop column sex, add column sex tinyint unsigned not null default 0 comment '性别：MODEL_SEX_ENUMERATE' after id, drop column martial_status, add column martial_status tinyint unsigned not null default 0 comment '婚姻状态：MODEL_MARTIAL_STATUS_ENUMERATE' after study_from_year;
alter table requirement drop column sex, add column sex tinyint unsigned not null default 0 comment '性别：MODEL_SEX_ENUMERATE' after id, drop column martial_status, add column martial_status tinyint unsigned not null default 0 comment '婚姻状态：MODEL_MARTIAL_STATUS_ENUMERATE' after max_month_pay;