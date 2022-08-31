alter table user add index idx_home_study (home_region_id, study_region_id, education_id);
alter table activity add column girl_meet_result tinyint(3) unsigned NOT NULL DEFAULT '0' COMMENT '女方见面结果: MODEL_MEET_RESULT_MAP';
alter table activity add column boy_meet_result tinyint(3) unsigned NOT NULL DEFAULT '0' COMMENT '男方见面结果: MODEL_MEET_RESULT_MAP';
