-- Adminer 4.8.1 MySQL 8.0.31-0ubuntu0.22.04.1 dump

SET NAMES utf8;
SET time_zone = '+00:00';
SET foreign_key_checks = 0;
SET sql_mode = 'NO_AUTO_VALUE_ON_ZERO';

SET NAMES utf8mb4;

DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(225) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `email` varchar(225) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `password` varchar(225) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `role` enum('1','2') NOT NULL DEFAULT '2',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `user` (`id`, `name`, `email`, `password`, `role`) VALUES
(16,	'admin',	'admin@gmail.com',	'$5$rounds=535000$8j1QrGmBP9AJkJLU$Yf4z545wyEZryviNZfaPPdCyRzlQtlFJAOSHxCV9F.0',	'1'),
(17,	'test',	'test@gmail.com',	'$5$rounds=535000$kXKvP8gevuhMdzHK$9SG.LPCXPQ1fvmSJwhjtvZIzAA2BBfmEy2kjrKZ9RT7',	'2');

-- 2022-11-27 12:12:11
