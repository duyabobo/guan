-- 活动地点按经纬度框选。门店多了以后全表扫会慢。
ALTER TABLE `address` ADD INDEX `idx_lng_lat` (`longitude`, `latitude`);
