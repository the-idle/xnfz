/*
Navicat MySQL Data Transfer

Source Server         : localhost
Source Server Version : 80012
Source Host           : localhost:3306
Source Database       : unity_assessment_v1.0

Target Server Type    : MYSQL
Target Server Version : 80012
File Encoding         : 65001

Date: 2025-11-23 22:40:32
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for answer_logs
-- ----------------------------
DROP TABLE IF EXISTS `answer_logs`;
CREATE TABLE `answer_logs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `result_id` int(11) DEFAULT NULL COMMENT '所属会话ID',
  `question_id` int(11) DEFAULT NULL COMMENT '题目ID',
  `selected_option_ids` json NOT NULL COMMENT '选中的选项ID列表，如 [1, 2]',
  `score_awarded` int(11) NOT NULL DEFAULT '0' COMMENT '该题得分',
  `answered_at` datetime NOT NULL COMMENT '答题时间',
  PRIMARY KEY (`id`),
  KEY `ix_answer_logs_result_id` (`result_id`),
  KEY `ix_answer_logs_question_id` (`question_id`),
  CONSTRAINT `fk_logs_question` FOREIGN KEY (`question_id`) REFERENCES `questions` (`id`),
  CONSTRAINT `fk_logs_result` FOREIGN KEY (`result_id`) REFERENCES `assessment_results` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Table structure for assessments
-- ----------------------------
DROP TABLE IF EXISTS `assessments`;
CREATE TABLE `assessments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '考核标题',
  `start_time` datetime NOT NULL COMMENT '开始时间',
  `end_time` datetime NOT NULL COMMENT '结束时间',
  `question_bank_id` int(11) NOT NULL COMMENT '使用的题库ID (1对1)',
  PRIMARY KEY (`id`),
  KEY `ix_assessments_question_bank_id` (`question_bank_id`),
  CONSTRAINT `fk_assessments_question_bank` FOREIGN KEY (`question_bank_id`) REFERENCES `question_banks` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Table structure for assessment_results
-- ----------------------------
DROP TABLE IF EXISTS `assessment_results`;
CREATE TABLE `assessment_results` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `assessment_id` int(11) DEFAULT NULL COMMENT '所属考核ID',
  `examinee_id` int(11) DEFAULT NULL COMMENT '考生ID',
  `total_score` int(11) DEFAULT '0' COMMENT '当前总分',
  `start_time` datetime NOT NULL COMMENT '开始答题时间',
  `end_time` datetime DEFAULT NULL COMMENT '交卷时间',
  PRIMARY KEY (`id`),
  KEY `ix_assessment_results_assessment_id` (`assessment_id`),
  KEY `ix_assessment_results_examinee_id` (`examinee_id`),
  CONSTRAINT `fk_results_assessment` FOREIGN KEY (`assessment_id`) REFERENCES `assessments` (`id`),
  CONSTRAINT `fk_results_examinee` FOREIGN KEY (`examinee_id`) REFERENCES `examinees` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Table structure for examinees
-- ----------------------------
DROP TABLE IF EXISTS `examinees`;
CREATE TABLE `examinees` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `identifier` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '考生唯一标识(如工号、座位号)',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_examinees_identifier` (`identifier`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Table structure for options
-- ----------------------------
DROP TABLE IF EXISTS `options`;
CREATE TABLE `options` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `question_id` int(11) DEFAULT NULL COMMENT '所属题目ID',
  `option_text` text COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '选项文字',
  `is_correct` tinyint(1) DEFAULT '0' COMMENT '是否正确答案',
  PRIMARY KEY (`id`),
  KEY `ix_options_question_id` (`question_id`),
  CONSTRAINT `fk_options_question` FOREIGN KEY (`question_id`) REFERENCES `questions` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=120 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Table structure for platforms
-- ----------------------------
DROP TABLE IF EXISTS `platforms`;
CREATE TABLE `platforms` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(191) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '平台名称，如：班组长现场管理平台 V1.0',
  `description` text COLLATE utf8mb4_unicode_ci COMMENT '平台描述',
  `hashed_password` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '平台访问密码(可选)',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Table structure for procedures
-- ----------------------------
DROP TABLE IF EXISTS `procedures`;
CREATE TABLE `procedures` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '工序名称，如：车床A点',
  `question_bank_id` int(11) DEFAULT NULL COMMENT '所属题库ID',
  PRIMARY KEY (`id`),
  KEY `ix_procedures_question_bank_id` (`question_bank_id`),
  CONSTRAINT `fk_procedures_question_bank` FOREIGN KEY (`question_bank_id`) REFERENCES `question_banks` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Table structure for questions
-- ----------------------------
DROP TABLE IF EXISTS `questions`;
CREATE TABLE `questions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `procedure_id` int(11) DEFAULT NULL COMMENT '所属工序ID',
  `prompt` text COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '题干内容',
  `image_url` varchar(512) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '题目图片URL',
  `question_type` enum('SINGLE_CHOICE','MULTIPLE_CHOICE','DEDUCTION_SINGLE_CHOICE') COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '题目类型',
  `scene_identifier` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '场景标识符(可选，非唯一)',
  `score` int(11) NOT NULL DEFAULT '0' COMMENT '分值',
  PRIMARY KEY (`id`),
  KEY `ix_questions_procedure_id` (`procedure_id`),
  CONSTRAINT `fk_questions_procedure` FOREIGN KEY (`procedure_id`) REFERENCES `procedures` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=40 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Table structure for question_banks
-- ----------------------------
DROP TABLE IF EXISTS `question_banks`;
CREATE TABLE `question_banks` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '题库名称',
  `platform_id` int(11) DEFAULT NULL COMMENT '所属平台ID',
  PRIMARY KEY (`id`),
  KEY `ix_question_banks_platform_id` (`platform_id`),
  CONSTRAINT `fk_question_banks_platform` FOREIGN KEY (`platform_id`) REFERENCES `platforms` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '登录用户名',
  `hashed_password` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '加密后的密码',
  `is_superuser` tinyint(1) DEFAULT '0' COMMENT '是否为超级管理员 (1:是, 0:否)',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
