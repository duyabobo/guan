alter table address drop column thumbnails_img ;
alter table address drop column img ;
alter table address add column img varchar(128) not null default '' comment '配图url（七牛）';