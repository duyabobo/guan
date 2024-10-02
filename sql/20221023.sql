alter table activity add index idx_start_time (`start_time`);
alter table passport add index idx_openid (`openid`);
alter table user drop index idx_home_study;
alter table user add index idx_study_region_id (`study_region_id`);
alter table user add index idx_work_region_id (`work_region_id`);
