-- 不再维护学历、学校、工作、认证。已有库删表，并清掉对应资料行。

DELETE FROM `profile_attr`
WHERE `dim_key` IN (
    'education',
    'education_level',
    'school',
    'study_from_year',
    'study_region',
    'work',
    'work_region',
    'month_pay'
);

DROP TABLE IF EXISTS `education`;
DROP TABLE IF EXISTS `work`;
DROP TABLE IF EXISTS `school`;
DROP TABLE IF EXISTS `verify`;
