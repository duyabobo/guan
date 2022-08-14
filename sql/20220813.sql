alter table passport add index idx_openid (`openid`);
alter table activity add state tinyint not null default 0 comment '活动状态：MODEL_ACTIVITY_STATE' after boy_passport_id;
