alter table user add column has_head_img tinyint unsigned not null default 0 comment '是否有自定义头像：0没有，1有' after sex;