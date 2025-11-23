/*
Navicat MySQL Data Transfer

Source Server         : localhost
Source Server Version : 80012
Source Host           : localhost:3306
Source Database       : unity_assessment_v1.0

Target Server Type    : MYSQL
Target Server Version : 80012
File Encoding         : 65001

Date: 2025-11-23 22:39:10
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
-- Records of answer_logs
-- ----------------------------
INSERT INTO `answer_logs` VALUES ('1', '1', '37', '[115]', '0');
INSERT INTO `answer_logs` VALUES ('2', '2', '1', '[1]', '5');
INSERT INTO `answer_logs` VALUES ('3', '2', '2', '[3]', '2');
INSERT INTO `answer_logs` VALUES ('4', '2', '3', '[6]', '5');
INSERT INTO `answer_logs` VALUES ('5', '2', '4', '[9]', '5');
INSERT INTO `answer_logs` VALUES ('6', '2', '39', '[119]', '5');
INSERT INTO `answer_logs` VALUES ('7', '3', '1', '[1]', '5');
INSERT INTO `answer_logs` VALUES ('8', '3', '2', '[2]', '0');
INSERT INTO `answer_logs` VALUES ('9', '3', '3', '[5]', '0');
INSERT INTO `answer_logs` VALUES ('10', '3', '4', '[10]', '0');

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
-- Records of assessments
-- ----------------------------
INSERT INTO `assessments` VALUES ('1', '2025第四季度安全考核', '2025-11-22 00:00:00', '2025-11-24 00:00:00', '1');

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
-- Records of assessment_results
-- ----------------------------
INSERT INTO `assessment_results` VALUES ('1', '1', '1', '0', '2025-11-22 01:21:45', '2025-11-22 01:21:58');
INSERT INTO `assessment_results` VALUES ('2', '1', '2', '22', '2025-11-23 02:03:49', '2025-11-23 02:13:45');
INSERT INTO `assessment_results` VALUES ('3', '1', '3', '5', '2025-11-23 02:15:15', null);

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
-- Records of examinees
-- ----------------------------
INSERT INTO `examinees` VALUES ('2', 'LAPTOP-JLFS5U6M');
INSERT INTO `examinees` VALUES ('3', 'LAPTOP-JLFS5U6M1');
INSERT INTO `examinees` VALUES ('1', 'WebTester_01');

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
-- Records of options
-- ----------------------------
INSERT INTO `options` VALUES ('1', '1', '已了解，立即开启任务', '1');
INSERT INTO `options` VALUES ('2', '2', '正常', '0');
INSERT INTO `options` VALUES ('3', '2', '异常', '1');
INSERT INTO `options` VALUES ('4', '3', '标识卡信息不全', '0');
INSERT INTO `options` VALUES ('5', '3', '标识卡信息有误', '0');
INSERT INTO `options` VALUES ('6', '3', '物料配送错误', '1');
INSERT INTO `options` VALUES ('7', '3', '物料包装错误', '0');
INSERT INTO `options` VALUES ('8', '4', '让班组物料员把错发物料搬到班组暂存区，在班组台账上登记 “待核查”，计划交接班时跟下一班班长交接，后续再找时间联系质量和仓储部门。', '0');
INSERT INTO `options` VALUES ('9', '4', '安排班组员工将错发物料移至车间 “可疑物料隔离区”，挂上 “可疑物料待质量部处置” 标识牌，填写《班组物料异常报告单》（注明物料信息、异常情况），同步提交给质量主管和仓储班长启动处置流程。', '1');
INSERT INTO `options` VALUES ('10', '4', '叮嘱本工序员工先别碰这批物料，自己去仓库临时调一批正确的物料保障生产，错发的物料先放在现场原地，等仓库调货后再处理。', '0');
INSERT INTO `options` VALUES ('11', '4', '电话联系配送员，要求尽快送正确物料到一工序，同时让班组物料员清点错发物料，放在现场等配送员来更换。', '0');
INSERT INTO `options` VALUES ('12', '5', '正常', '0');
INSERT INTO `options` VALUES ('13', '5', '异常', '1');
INSERT INTO `options` VALUES ('14', '6', '员工未佩戴安全帽', '0');
INSERT INTO `options` VALUES ('15', '6', '员工未佩戴手套', '0');
INSERT INTO `options` VALUES ('16', '6', '员工未佩戴防护眼镜', '1');
INSERT INTO `options` VALUES ('17', '7', '让员工暂停操作，戴好防护眼镜再操作，同时讲解安全风险。', '1');
INSERT INTO `options` VALUES ('18', '7', '让员工把当前零件加工完再去戴防护眼镜，同时讲解安全风险。', '0');
INSERT INTO `options` VALUES ('19', '7', '让员工去戴防护眼镜，自己临时盯设备，待员工回来讲解安全风险。', '0');
INSERT INTO `options` VALUES ('20', '7', '让员工先干活，下班前检查防护眼镜佩戴，别停工。', '0');
INSERT INTO `options` VALUES ('21', '8', '正常', '0');
INSERT INTO `options` VALUES ('22', '8', '异常', '1');
INSERT INTO `options` VALUES ('23', '9', '设备存在故障未报修', '0');
INSERT INTO `options` VALUES ('24', '9', '操作区域物料堆放杂乱，通道堵塞', '1');
INSERT INTO `options` VALUES ('25', '9', '操作人员未按规定进行设备日常点检', '1');
INSERT INTO `options` VALUES ('26', '9', '有非本工序人员在操作区域逗留', '1');
INSERT INTO `options` VALUES ('27', '10', '自己简单整理下物料，让操作人员继续干活，不管非本工序人员。', '0');
INSERT INTO `options` VALUES ('28', '10', '告诉操作人员等这批活儿干完再清理物料和补做点检，对非本工序人员口头提醒一下。', '0');
INSERT INTO `options` VALUES ('29', '10', '立即安排人员清理物料，保持通道畅通；督促操作人员补做点检记录；劝离非本工序人员并强调区域规定。', '1');
INSERT INTO `options` VALUES ('30', '10', '只让操作人员注意别影响工作，物料和非本工序人员问题先不管。', '0');
INSERT INTO `options` VALUES ('31', '11', '正常', '0');
INSERT INTO `options` VALUES ('32', '11', '异常', '1');
INSERT INTO `options` VALUES ('33', '12', '设备运行监测图波动异常，可能存在故障隐患', '1');
INSERT INTO `options` VALUES ('34', '12', '产品目前能正常加工，无质量问题', '0');
INSERT INTO `options` VALUES ('35', '12', '设备运行监测图波动异常，但在管控范围内', '0');
INSERT INTO `options` VALUES ('36', '12', '通过监测图示无法判断是否有异常', '0');
INSERT INTO `options` VALUES ('37', '13', '要求立即停止设备运行，通知维修人员检查设备。', '0');
INSERT INTO `options` VALUES ('38', '13', '检查产品质量，确认产品正常后继续加工。', '0');
INSERT INTO `options` VALUES ('39', '13', '要求在加工件完成后停止设备运行，通知维修人员到现场确认是否故障。', '1');
INSERT INTO `options` VALUES ('40', '13', '提醒操作人员注意观察波动，如果再持续波动再通知维修人员。', '0');
INSERT INTO `options` VALUES ('41', '14', '正常', '0');
INSERT INTO `options` VALUES ('42', '14', '异常', '1');
INSERT INTO `options` VALUES ('43', '15', '交接班记录填写不完整，重要信息描述不清晰', '1');
INSERT INTO `options` VALUES ('44', '15', '工作未完成交接', '1');
INSERT INTO `options` VALUES ('45', '15', '没有异常，记录清晰', '0');
INSERT INTO `options` VALUES ('46', '15', '记录有误', '1');
INSERT INTO `options` VALUES ('47', '16', '立即要求在岗作业员重新确认各工艺参数，纠正加工风险，清晰传达生产指令；同时记录上一班交接记录的问题。', '1');
INSERT INTO `options` VALUES ('48', '16', '让他们自己去完善记录和沟通，先不管遗留故障。', '0');
INSERT INTO `options` VALUES ('49', '16', '简单提醒一下要完善记录，工作衔接和故障问题等出现问题再说。', '0');
INSERT INTO `options` VALUES ('50', '16', '关注任务衔接和今天要交付的急单，记录和潜在故障问题先暂不处理。', '0');
INSERT INTO `options` VALUES ('51', '17', '正常', '0');
INSERT INTO `options` VALUES ('52', '17', '异常', '1');
INSERT INTO `options` VALUES ('53', '18', '部分安全警示标识损坏或丢失', '1');
INSERT INTO `options` VALUES ('54', '18', '设备处于故障状态未进行报修处理', '0');
INSERT INTO `options` VALUES ('55', '18', '操作人员未按警示要求佩戴护目镜等防护用品', '1');
INSERT INTO `options` VALUES ('56', '18', '安全通道被该废料轻微堵塞', '1');
INSERT INTO `options` VALUES ('57', '19', '马上安排更换或补充安全警示标识；督促操作人员佩戴好防护用品；清理安全通道废料。', '1');
INSERT INTO `options` VALUES ('58', '19', '告诉操作人员等会再戴防护用品，标识和通道问题等有空再弄。', '0');
INSERT INTO `options` VALUES ('59', '19', '自己简单提醒一下防护用品，标识和通道问题不管。', '0');
INSERT INTO `options` VALUES ('60', '19', '只关注通道清理，标识和防护用品问题之后再说。', '0');
INSERT INTO `options` VALUES ('61', '20', '正常', '0');
INSERT INTO `options` VALUES ('62', '20', '异常', '1');
INSERT INTO `options` VALUES ('63', '21', '生产进度与计划偏差较大，未及时上报', '1');
INSERT INTO `options` VALUES ('64', '21', '操作人员私自调整加工顺序，影响整体节奏', '0');
INSERT INTO `options` VALUES ('65', '21', '看板信息更新不及时，数据不准确', '0');
INSERT INTO `options` VALUES ('66', '21', '看板显示的零件名称有误', '0');
INSERT INTO `options` VALUES ('67', '22', '立即与相关人员沟通了解进度偏差原因并上报；评估生产进度延误带来的影响，快速制定对策。', '1');
INSERT INTO `options` VALUES ('68', '22', '让操作人员自己注意进度和顺序，晚点再更新看板。', '0');
INSERT INTO `options` VALUES ('69', '22', '询问进度情况，要求下班后留下加班继续生产，直至完成计划产量。', '0');
INSERT INTO `options` VALUES ('70', '22', '只关注看板更新，进度和加工顺序问题之后再说。', '0');
INSERT INTO `options` VALUES ('71', '23', '正常', '0');
INSERT INTO `options` VALUES ('72', '23', '异常', '1');
INSERT INTO `options` VALUES ('73', '24', '设备处于故障状态未进行报修', '1');
INSERT INTO `options` VALUES ('74', '24', '设备维护保养记录不完整（缺少部分日期的清洁、润滑记录）', '0');
INSERT INTO `options` VALUES ('75', '24', '设备维护保养记录与实际不符', '1');
INSERT INTO `options` VALUES ('76', '24', '设备防护盖板未归位，存在安全隐患', '0');
INSERT INTO `options` VALUES ('77', '25', '立即要求员工补充完整维护保养记录，即时教育，提醒记录的重要性。', '0');
INSERT INTO `options` VALUES ('78', '25', '要求员工对在加工的产品加工完后立即停止作业，共同排查设备故障及报修，同时要求员工对设备进行清洁，并对工作不实的行为严肃教育。', '1');
INSERT INTO `options` VALUES ('79', '25', '提醒设备的维护保养重要性，要求下班后将设备的清洁再重新做一遍。', '0');
INSERT INTO `options` VALUES ('80', '25', '立即要求停机处理设备故障。', '0');
INSERT INTO `options` VALUES ('81', '26', '正常', '0');
INSERT INTO `options` VALUES ('82', '26', '异常', '1');
INSERT INTO `options` VALUES ('83', '27', '灭火器实际状态与点检表判定不一致', '0');
INSERT INTO `options` VALUES ('84', '27', '灭火器点检表超前日期点检', '1');
INSERT INTO `options` VALUES ('85', '27', '无异常', '0');
INSERT INTO `options` VALUES ('86', '28', '要求点检负责人重新按照正确日期进行点检，并对其进行教育。', '1');
INSERT INTO `options` VALUES ('87', '28', '对超前日期点检原因展开调查，对点检负责人进行处罚。', '0');
INSERT INTO `options` VALUES ('88', '28', '让点检负责人修改超前的日期，提醒下次不能再犯。', '0');
INSERT INTO `options` VALUES ('89', '28', '找到点检负责人进行教育，提醒下次不能再犯。', '0');
INSERT INTO `options` VALUES ('90', '29', '正常', '0');
INSERT INTO `options` VALUES ('91', '29', '异常', '1');
INSERT INTO `options` VALUES ('92', '30', '零件放置方向错误，加工面存在被滑道磨花伤风险', '0');
INSERT INTO `options` VALUES ('93', '30', '零件未放置容器内传递，存在相互撞击和加工面划伤风险', '1');
INSERT INTO `options` VALUES ('94', '30', '零件未及时取用加工，生产节拍不均衡', '0');
INSERT INTO `options` VALUES ('95', '31', '将零件放入零件盒后再继续传送，对操作员工进行教育。', '0');
INSERT INTO `options` VALUES ('96', '31', '找到操作者询问零件未放入容器传递的原因，共同讨论如何不再犯错。', '0');
INSERT INTO `options` VALUES ('97', '31', '检查所传递的零件是否有损伤，对操作者进行教育和绩效评价。', '0');
INSERT INTO `options` VALUES ('98', '31', '要求操作者立即纠正，将零件放入零件盒后再继续传送，对已传送零件检查是否有损伤。', '1');
INSERT INTO `options` VALUES ('99', '32', '正常', '0');
INSERT INTO `options` VALUES ('100', '32', '异常', '1');
INSERT INTO `options` VALUES ('101', '33', '成品区零件未做标识', '0');
INSERT INTO `options` VALUES ('102', '33', '成品零件数量不完整', '0');
INSERT INTO `options` VALUES ('103', '33', '有未加工完的产品混放在成品中', '1');
INSERT INTO `options` VALUES ('104', '34', '标识并通知对应工序操作者取零件返工，再次检查成品区是否仍有类似情况。', '1');
INSERT INTO `options` VALUES ('105', '34', '把未加工完的产品先放在一边，标识隔离，对对应的工序操作者进行教育。', '0');
INSERT INTO `options` VALUES ('106', '34', '标记未加工完的产品，通知对应的操作者到成品区取回返工。', '0');
INSERT INTO `options` VALUES ('107', '34', '标识并找到对应工序操作者展开教育，要求立即取零件返工。', '0');
INSERT INTO `options` VALUES ('108', '35', '正常', '0');
INSERT INTO `options` VALUES ('109', '35', '异常', '1');
INSERT INTO `options` VALUES ('110', '36', '物料错装', '0');
INSERT INTO `options` VALUES ('111', '36', '物料混装', '0');
INSERT INTO `options` VALUES ('112', '36', '物料标识不全', '1');
INSERT INTO `options` VALUES ('113', '37', '补充缺失的物料标识牌，对所有物料标识进行复查，确保准确性。', '1');
INSERT INTO `options` VALUES ('114', '37', '记录标识不全的物料，打电话通知物流人员补贴标识牌。', '0');
INSERT INTO `options` VALUES ('115', '37', '补充缺失的物料标识牌，对责任人进行绩效考核。', '0');
INSERT INTO `options` VALUES ('116', '37', '调查物料标识牌缺失原因，对责任人进行教育。', '0');
INSERT INTO `options` VALUES ('119', '39', '321', '1');

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
-- Records of platforms
-- ----------------------------
INSERT INTO `platforms` VALUES ('1', '虚拟实训考核平台1.0', '用于班组长现场管理虚拟仿真考核', '$2b$12$om92DDNFQi5vpF4PXJg0I.1FLvF5XoteBnPB2tSW4V/0qaApCOIQ2');

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
-- Records of procedures
-- ----------------------------
INSERT INTO `procedures` VALUES ('1', '班组园地', '1');
INSERT INTO `procedures` VALUES ('2', 'Area01', '1');
INSERT INTO `procedures` VALUES ('3', 'Area02', '1');
INSERT INTO `procedures` VALUES ('4', 'Area03', '1');
INSERT INTO `procedures` VALUES ('5', 'Area04', '1');
INSERT INTO `procedures` VALUES ('6', 'Area05', '1');
INSERT INTO `procedures` VALUES ('7', 'Area06', '1');
INSERT INTO `procedures` VALUES ('8', 'Area07', '1');
INSERT INTO `procedures` VALUES ('9', 'Area08', '1');
INSERT INTO `procedures` VALUES ('10', '灭火器检查场景', '1');
INSERT INTO `procedures` VALUES ('11', '工序间零件传递场景', '1');
INSERT INTO `procedures` VALUES ('12', '成品区场景', '1');
INSERT INTO `procedures` VALUES ('13', '物料区场景', '1');

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
-- Records of questions
-- ----------------------------
INSERT INTO `questions` VALUES ('1', '1', '现场管理巡查表领取', null, 'SINGLE_CHOICE', null, '5');
INSERT INTO `questions` VALUES ('2', '2', '物料标识卡是否存在问题？', '/assets/images/工序一/物料标识卡.jpg', 'SINGLE_CHOICE', null, '2');
INSERT INTO `questions` VALUES ('3', '2', '你发现了什么问题？', null, 'SINGLE_CHOICE', null, '5');
INSERT INTO `questions` VALUES ('4', '2', '你该如何处理这个问题？', null, 'SINGLE_CHOICE', null, '5');
INSERT INTO `questions` VALUES ('5', '3', '班长，有什么事吗？', null, 'SINGLE_CHOICE', null, '2');
INSERT INTO `questions` VALUES ('6', '3', '你发现了什么问题？', null, 'SINGLE_CHOICE', null, '5');
INSERT INTO `questions` VALUES ('7', '3', '你该如何处理这个问题？', null, 'SINGLE_CHOICE', null, '5');
INSERT INTO `questions` VALUES ('8', '4', '当前工序是否存在问题？', null, 'SINGLE_CHOICE', null, '2');
INSERT INTO `questions` VALUES ('9', '4', '你发现了什么问题？', null, 'MULTIPLE_CHOICE', null, '9');
INSERT INTO `questions` VALUES ('10', '4', '你该如何处理这个问题？', null, 'SINGLE_CHOICE', null, '5');
INSERT INTO `questions` VALUES ('11', '5', '当前工序是否存在问题？', '/assets/images/工序四/运行监测图表.jpg', 'SINGLE_CHOICE', null, '2');
INSERT INTO `questions` VALUES ('12', '5', '你发现了什么问题？', null, 'SINGLE_CHOICE', null, '3');
INSERT INTO `questions` VALUES ('13', '5', '你该如何处理这个问题？', null, 'SINGLE_CHOICE', null, '5');
INSERT INTO `questions` VALUES ('14', '6', '交接班记录是否存在问题？', null, 'SINGLE_CHOICE', null, '2');
INSERT INTO `questions` VALUES ('15', '6', '你发现了什么问题？', null, 'MULTIPLE_CHOICE', null, '9');
INSERT INTO `questions` VALUES ('16', '6', '你该如何处理这个问题？', null, 'SINGLE_CHOICE', null, '5');
INSERT INTO `questions` VALUES ('17', '7', '安全警示标识是否存在问题？', null, 'SINGLE_CHOICE', null, '2');
INSERT INTO `questions` VALUES ('18', '7', '你发现了什么问题？', null, 'MULTIPLE_CHOICE', null, '9');
INSERT INTO `questions` VALUES ('19', '7', '你该如何处理这个问题？', null, 'SINGLE_CHOICE', null, '5');
INSERT INTO `questions` VALUES ('20', '8', '生产进度看板是否存在问题？', null, 'SINGLE_CHOICE', null, '2');
INSERT INTO `questions` VALUES ('21', '8', '你发现了什么问题？', null, 'SINGLE_CHOICE', null, '3');
INSERT INTO `questions` VALUES ('22', '8', '你该如何处理这个问题？', null, 'SINGLE_CHOICE', null, '5');
INSERT INTO `questions` VALUES ('23', '9', '设备维护记录是否存在问题？', null, 'SINGLE_CHOICE', null, '2');
INSERT INTO `questions` VALUES ('24', '9', '你发现了什么问题？', null, 'MULTIPLE_CHOICE', null, '6');
INSERT INTO `questions` VALUES ('25', '9', '你该如何处理这个问题？', null, 'SINGLE_CHOICE', null, '5');
INSERT INTO `questions` VALUES ('26', '10', '灭火器点检表是否存在问题？', '/assets/images/场景/灭火器点检表.jpg', 'SINGLE_CHOICE', null, '2');
INSERT INTO `questions` VALUES ('27', '10', '你发现了什么问题？', null, 'SINGLE_CHOICE', null, '5');
INSERT INTO `questions` VALUES ('28', '10', '你该如何处理这个问题？', null, 'SINGLE_CHOICE', null, '5');
INSERT INTO `questions` VALUES ('29', '11', '工序间滑道上零件是否存在问题？', '/assets/images/场景/工序间滑道零件.jpg', 'SINGLE_CHOICE', null, '2');
INSERT INTO `questions` VALUES ('30', '11', '你发现了什么问题？', null, 'SINGLE_CHOICE', null, '5');
INSERT INTO `questions` VALUES ('31', '11', '你该如何处理这个问题？', null, 'SINGLE_CHOICE', null, '5');
INSERT INTO `questions` VALUES ('32', '12', '成品区是否存在问题？', '/assets/images/场景/成品区.jpg', 'SINGLE_CHOICE', null, '2');
INSERT INTO `questions` VALUES ('33', '12', '你发现了什么问题？', null, 'SINGLE_CHOICE', null, '5');
INSERT INTO `questions` VALUES ('34', '12', '你该如何处理这个问题？', null, 'SINGLE_CHOICE', null, '5');
INSERT INTO `questions` VALUES ('35', '13', '物料区物料标识是否存在问题？', '/assets/images/场景/物料区标识.jpg', 'SINGLE_CHOICE', null, '2');
INSERT INTO `questions` VALUES ('36', '13', '你发现了什么问题？', null, 'SINGLE_CHOICE', null, '5');
INSERT INTO `questions` VALUES ('37', '13', '你该如何处理这个问题？', null, 'SINGLE_CHOICE', null, '5');
INSERT INTO `questions` VALUES ('39', '1', '123', null, 'SINGLE_CHOICE', '', '5');

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
-- Records of question_banks
-- ----------------------------
INSERT INTO `question_banks` VALUES ('1', '虚拟实训考核平台1.0题库', '1');

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

-- ----------------------------
-- Records of users
-- ----------------------------
INSERT INTO `users` VALUES ('1', 'admin', '$2b$12$e8wsNXgBV.WB06xJ.eV.quz8WVpxqHHe5VmgMpWOahluzMLA/eqru', '1');
INSERT INTO `users` VALUES ('4', 'admin1', '$2b$12$XQZCpMVjVbOyn3HkxjXzH./KLjzJJMz3WcbZpyP41Ufk1Rg5KIUoG', '1');
