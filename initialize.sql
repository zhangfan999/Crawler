/*
Navicat MySQL Data Transfer
Source Server         : 本地服务器
Source Server Version : 50717
Source Host           : localhost:3306
Source Database       : spider
Target Server Type    : MYSQL
Target Server Version : 50717
File Encoding         : 65001
Date: 2019-01-21 13:59:31
*/
SET FOREIGN_KEY_CHECKS=0;
-- ----------------------------
-- Table structure for cellbank_production
-- ----------------------------
-- DROP TABLE IF EXISTS `cellbank_production`;
CREATE TABLE `cellbank_production` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `KCLBNo` varchar(100) DEFAULT NULL,
  `ProductName` varchar(100) DEFAULT NULL,
  `Distributibility` varchar(100) DEFAULT NULL,
  `CellLineSTRProfile` varchar(255) DEFAULT NULL,
  `Origin` varchar(200) DEFAULT NULL,
  `Species` varchar(100) DEFAULT NULL,
  `Strain` varchar(200) DEFAULT NULL,
  `VirusSusceptibilit` varchar(500) DEFAULT NULL,
  `VirusResistance` varchar(500) DEFAULT NULL,
  `Reversetranscritase` varchar(500) DEFAULT NULL,
  `Tumorigenecity` varchar(200) DEFAULT NULL,
  `Isoenzyme` varchar(255) DEFAULT NULL,
  `Karyology` varchar(400) DEFAULT NULL,
  `CellularMorphology` varchar(100) DEFAULT NULL,
  `Production` varchar(500) DEFAULT NULL,
  `Histocompatibility` varchar(255) DEFAULT NULL,
  `GrowthPattern` varchar(100) DEFAULT NULL,
  `Histopathology` varchar(200) DEFAULT NULL,
  `Differentiation` varchar(255) DEFAULT NULL,
  `FreezingMedia` varchar(150) DEFAULT NULL,
  `OriginalMedia` varchar(300) DEFAULT NULL,
  `KCLBMedia` varchar(500) DEFAULT NULL,
  `Depositor` varchar(500) DEFAULT NULL,
  `Subculture` varchar(500) DEFAULT NULL,
  `Reference` varchar(500) DEFAULT NULL,
  `Note` varchar(1500) DEFAULT NULL,
  `Hit` varchar(100) DEFAULT NULL,
  `SplitRatio` varchar(100) DEFAULT NULL,
  `MediaChange` varchar(300) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=844 DEFAULT CHARSET=utf8;

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for cellbank_failed_arc_url
-- ----------------------------
-- DROP TABLE IF EXISTS `cellbank_failed_arc_url`;
CREATE TABLE `cellbank_failed_arc_url` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `url` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for cellbank_failed_list_url
-- ----------------------------
DROP TABLE IF EXISTS `cellbank_failed_list_url`;
CREATE TABLE `cellbank_failed_list_url` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `url` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;