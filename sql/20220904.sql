alter table school add column email varchar(64) not null default '' comment '学校邮箱后缀' after seq;
alter table company add column email varchar(64) not null default '' comment '公司邮箱后缀' after seq;
alter table user add column work_level smallint unsigned not null default 0 comment '职级' after work_id;
alter table requirement add column work_level smallint unsigned not null default 0 comment '职级' after work_id;
