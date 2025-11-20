<template>
    <div class="page-container">
      <div class="header">
        <h2>模拟考生终端 (Debug)</h2>
        <el-alert title="此页面用于模拟 Unity 客户端行为，测试数据生成与计分逻辑" type="info" show-icon :closable="false" />
      </div>
  
      <!-- 步骤条 -->
      <el-steps :active="activeStep" finish-status="success" simple style="margin: 20px 0">
        <el-step title="身份录入" />
        <el-step title="选择考核" />
        <el-step title="正在答题" />
        <el-step title="完成" />
      </el-steps>
  
      <!-- 步骤1: 身份录入 -->
      <div v-if="activeStep === 0" class="step-content">
        <el-form label-width="120px">
          <el-form-item label="考生/设备标识">
            <el-input v-model="examineeId" placeholder="例如：Worker_001 或 Device_A" />
          </el-form-item>
          <el-button type="primary" @click="activeStep = 1" :disabled="!examineeId">下一步</el-button>
        </el-form>
      </div>
  
      <!-- 步骤2: 获取近期考核 -->
      <div v-if="activeStep === 1" class="step-content">
        <el-input v-model.number="platformId" placeholder="输入平台ID (例如 1)" style="margin-bottom: 10px; width: 200px;" />
        <el-button @click="fetchUpcoming">查询待考场次</el-button>
        
        <el-table :data="upcomingList" border style="margin-top: 10px;">
          <el-table-column prop="id" label="考核ID" width="80" />
          <el-table-column prop="title" label="标题" />
          <el-table-column label="操作">
            <template #default="{ row }">
              <el-button type="primary" link @click="startSession(row)">开始/继续考试</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
  
      <!-- 步骤3: 答题界面 -->
      <div v-if="activeStep === 2 && blueprint" class="step-content">
        <div class="exam-paper">
          <h3>考核进行中</h3>
          
          <div v-if="blueprint.procedures.length === 0">
            <el-result icon="success" title="已完成" sub-title="所有工序均已完成，请点击下方交卷">
            </el-result>
          </div>
  
          <div v-for="(proc, pIndex) in blueprint.procedures" :key="pIndex" class="procedure-block">
            <h4>工序: {{ proc.name }}</h4>
            
            <div v-for="(q, qIndex) in proc.questions" :key="q.id" class="question-block">
              <p><strong>{{ qIndex + 1 }}. {{ q.prompt }}</strong> ({{ q.score }}分)</p>
              
              <!-- 单选 / 扣分单选 -->
              <el-radio-group 
                v-if="['SINGLE_CHOICE', 'DEDUCTION_SINGLE_CHOICE'].includes(q.question_type)" 
                v-model="answers[q.id]"
              >
                <el-radio v-for="opt in q.options" :key="opt.id" :label="opt.id" border>
                  {{ opt.option_text }}
                </el-radio>
              </el-radio-group>
  
              <!-- 多选 -->
              <el-checkbox-group 
                v-if="q.question_type === 'MULTIPLE_CHOICE'" 
                v-model="answers[q.id]"
              >
                <el-checkbox v-for="opt in q.options" :key="opt.id" :label="opt.id" border>
                  {{ opt.option_text }}
                </el-checkbox>
              </el-checkbox-group>
  
              <div style="margin-top: 10px;">
                <el-button size="small" @click="submitSingleAnswer(q.id)">提交本题答案</el-button>
                <span v-if="q.selected_option_ids" style="color: #67C23A; font-size: 12px; margin-left: 10px;">
                  (已自动加载上次记录)
                </span>
              </div>
            </div>
          </div>
  
          <div class="footer-actions">
            <el-button type="danger" size="large" @click="finishExam">交卷 (Finish)</el-button>
          </div>
        </div>
      </div>
  
      <!-- 步骤4: 完成 -->
      <div v-if="activeStep === 3" class="step-content" style="text-align: center;">
        <el-result icon="success" title="考试结束" sub-title="答案已上传，请前往后台[成绩记录]查看判分结果">
          <template #extra>
            <el-button type="primary" @click="reset">再测一次</el-button>
            <el-button @click="$router.push('/assessments')">去查看成绩</el-button>
          </template>
        </el-result>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref } from 'vue';
  import request from '@/utils/request';
  import { ElMessage } from 'element-plus';
  
  const activeStep = ref(0);
  const examineeId = ref('WebTester_01');
  const platformId = ref(1);
  const upcomingList = ref([]);
  const blueprint = ref<any>(null);
  const currentResultId = ref<number | null>(null); 
  const answers = ref<Record<number, any>>({}); 
  
// 1. 获取待考列表
const fetchUpcoming = async () => {
  try {
    const res = await request.get<any, any[]>(`/client/platforms/${platformId.value}/assessments/upcoming`);
    upcomingList.value = res || [];
    if (upcomingList.value.length === 0) {
      ElMessage.info('该平台下暂无进行中的考核，请先去【考核场次管理】发布一个时间范围包含现在的考核');
    }
  } catch (e: any) {
    // 修复：捕获 404 错误，不让它在控制台爆红干扰调试
    console.warn("Fetch upcoming warning:", e);
    upcomingList.value = [];
    if (e.response && e.response.status === 404) {
        ElMessage.warning('当前平台没有正在进行的考核。请先创建考核场次。');
    } else {
        ElMessage.error('查询失败，请检查网络或平台ID');
    }
  }
};
  
  // 2. 开始/继续考试
  const startSession = async (row: any) => {
    try {
      const res = await request.post<any, any>(`/client/assessments/${row.id}/session`, {
        examinee_identifier: examineeId.value
      });
      
      blueprint.value = res;
      currentResultId.value = res.assessment_result_id; 
  
      // 断点续考回显
      res.procedures.forEach((p: any) => {
        p.questions.forEach((q: any) => {
          if (q.question_type === 'MULTIPLE_CHOICE') {
            answers.value[q.id] = [];
          } else {
            answers.value[q.id] = null;
          }
  
          if (q.selected_option_ids && q.selected_option_ids.length > 0) {
            if (q.question_type === 'MULTIPLE_CHOICE') {
              answers.value[q.id] = q.selected_option_ids;
            } else {
              answers.value[q.id] = q.selected_option_ids[0];
            }
          }
        });
      });
  
      activeStep.value = 2;
      ElMessage.success('考试会话已就绪');
    } catch (e) { console.error(e); }
  };
  
  // 3. 提交单题答案 (核心修复：添加 examinee_identifier)
  const submitSingleAnswer = async (questionId: number) => {
    const val = answers.value[questionId];
    if (val === null || val === undefined || (Array.isArray(val) && val.length === 0)) {
      return ElMessage.warning('请先选择选项');
    }
  
    let ids = [];
    if (Array.isArray(val)) ids = val;
    else ids = [val];
  
    try {
      await request.post(`/client/assessment-results/${currentResultId.value}/answer`, {
        question_id: questionId,
        selected_option_ids: ids,
        // ⚠️ 必填：后端新增校验
        examinee_identifier: examineeId.value 
      });
      ElMessage.success('答案已保存');
    } catch (e: any) { 
      console.error(e); 
      // 显示后端返回的具体错误（如：考试已结束、身份不匹配等）
      const msg = e.response?.data?.detail || '提交失败';
      ElMessage.error(msg);
    }
  };
  
  // 4. 交卷 (核心修复：添加 examinee_identifier)
  const finishExam = async () => {
    try {
      await request.post(`/client/assessment-results/${currentResultId.value}/finish`, {
        // ⚠️ 必填：后端新增校验
        examinee_identifier: examineeId.value 
      });
      activeStep.value = 3;
    } catch (e) { console.error(e); }
  };
  
  const reset = () => {
    activeStep.value = 0;
    blueprint.value = null;
    answers.value = {};
  };
  </script>
  
  <style scoped>
  .step-content { max-width: 800px; margin: 40px auto; }
  .procedure-block { margin-bottom: 30px; border: 1px solid #eee; padding: 20px; border-radius: 8px; }
  .question-block { margin-bottom: 20px; padding-bottom: 20px; border-bottom: 1px dashed #eee; }
  .footer-actions { text-align: center; margin-top: 40px; padding-bottom: 40px; }
  </style>