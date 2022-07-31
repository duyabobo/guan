alter table user drop column home_province,drop column home_city, drop column home_area,drop column province, drop column city, drop column school, drop column major, drop column education;
alter table requirement drop column home_province,drop column home_city, drop column home_area,drop column province, drop column city, drop column school, drop column major, drop column study_from_year, drop column school_type;
alter table user add column home_address_id bigint unsigned not null default 0 comment '籍贯地点id' after weight, add column study_address_id bigint unsigned not null default 0 comment '学习地点id' after home_address_id, add column education_id bigint unsigned not null default 0 comment '学习信息id' after study_address_id;
alter table requirement add column home_address_id bigint unsigned not null default 0 comment '籍贯地点id' after max_height, add column study_address_id bigint unsigned not null default 0 comment '学习地点id' after home_address_id, add column education_id bigint unsigned not null default 0 comment '学习信息id' after study_address_id, add column min_study_from_year smallint not null default 0 comment '最早入学年份' after education_id, add column max_study_from_year smallint not null default 0 comment '最晚入学年份';

create table education (
    `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT 'id',
    `school` varchar(128) not null default '' comment '学校',
    `level` varchar(32) not null default '' comment '学历枚举：EDUCATION_CHOICE_LIST',
    `major` varchar(32) not null default '' comment '专业',
    PRIMARY KEY (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='教育信息';