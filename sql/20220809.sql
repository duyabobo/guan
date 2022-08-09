alter table education add column region_id bigint unsigned not null default 0 comment '学校所在区id，如果需要分校区的话，多个校区算多个记录' after id;
alter table education add index idx_region_id (`region_id`), add unique key uk_edu (`school`, `level`, `major`);
alter table education add column seq int unsigned not null default 0 comment '序号越小越靠前。10位从高到低分配规则：1～6位支持429495个学校，7位支持9种学历类型，8-10位支持1000个专业' after major;
