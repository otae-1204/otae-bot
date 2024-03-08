/*
 Navicat Premium Data Transfer

 Source Server         : Server
 Source Server Type    : MySQL
 Source Server Version : 80200
 Source Host           : mcs1-otae.top:3306
 Source Schema         : db_otaebot

 Target Server Type    : MySQL
 Target Server Version : 80200
 File Encoding         : 65001

 Date: 23/01/2024 00:45:38
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for bulletdata
-- ----------------------------
DROP TABLE IF EXISTS `bulletdata`;
CREATE TABLE `bulletdata`  (
  `id` int(0) NOT NULL AUTO_INCREMENT COMMENT '子弹Id',
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '子弹名',
  `caliber` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '口径',
  `weight` double NULL DEFAULT NULL COMMENT '重量',
  `stackMaxSize` int(0) NULL DEFAULT NULL COMMENT '最大堆叠数量',
  `tracer` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '是否曳光',
  `tracerColor` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '曳光颜色',
  `damage` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '伤害',
  `armorDamage` double NULL DEFAULT NULL COMMENT '损甲百分比',
  `fragmentationChance` double NULL DEFAULT NULL COMMENT '碎弹率',
  `ricochetChance` double NULL DEFAULT NULL COMMENT '跳弹率',
  `penetrationPower` int(0) NULL DEFAULT NULL COMMENT '穿透值',
  `accuracyModifier` double NULL DEFAULT NULL COMMENT '精度修正',
  `recoilModifier` double NULL DEFAULT NULL COMMENT '后座修正',
  `lightBleedModifier` double NULL DEFAULT NULL COMMENT '小出血修正',
  `heavyBleedModifier` double NULL DEFAULT NULL COMMENT '大出血修正',
  `img` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '图片',
  `marketSale` int(0) NULL DEFAULT NULL COMMENT '是否禁售',
  `apiID` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT 'API中的ID值',
  `projectileCount` int(0) NULL DEFAULT NULL COMMENT '单次射击弹丸数',
  `initialSpeed` double NULL DEFAULT NULL COMMENT '子弹飞行速度',
  `staminaBurnPerDamage` double NULL DEFAULT NULL COMMENT '受伤掉耐',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for traders_peacekeeper
-- ----------------------------
DROP TABLE IF EXISTS `traders_peacekeeper`;
CREATE TABLE `traders_peacekeeper`  (
  `id` int(0) NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '物品名',
  `price` int(0) NULL DEFAULT NULL COMMENT '价格',
  `currency` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '货币类型',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 12 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = DYNAMIC;

SET FOREIGN_KEY_CHECKS = 1;
