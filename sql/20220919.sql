alter table address add column thumbnails_img varchar(32) not null default '' comment '缩略图';
alter table address modify column thumbnails_img varchar(128) not null default '' comment '缩略图';
alter table address modify column img varchar(128) not null default '' comment '图片url';