-- 首页按附近地点取候选场次：address_id IN (...) AND state=? AND start_time>now
-- 现有 idx_state_start 会先扫该状态下全部未来场次再滤地点；空闲未来场次多时代价高。
ALTER TABLE `activity` ADD INDEX `idx_addr_state_start` (`address_id`, `state`, `start_time`);
