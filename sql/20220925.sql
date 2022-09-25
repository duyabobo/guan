alter table address drop column thumbnails_img ;
alter table address drop column img ;
alter table address add column img_obj_name varchar(128) not null default '' comment '配图oss存储的对象名';