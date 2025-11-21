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
      <div style="display: flex; gap: 10px; margin-bottom: 20px;">
        <el-input v-model.number="platformId" placeholder="输入平台ID (例如 1)" style="width: 200px;" />
        <el-button type="primary" @click="fetchUpcoming" :loading="loading">查询待考场次</el-button>
      </div>
      
      <el-table :data="upcomingList" border style="width: 100%" empty-text="暂无进行中的考核">
        <el-table-column prop="id" label="考核ID" width="80" />
        <el-table-column prop="title" label="标题" />
        <el-table-column label="操作" width="150" align="center">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="startSession(row)">开始/继续考试</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 步骤3: 答题界面 -->
    <div v-if="activeStep === 2 && blueprint" class="step-content">
      <div class="exam-paper">
        <h3>考核进行中</h3>
        
        <div v-if="blueprint.procedures.length === 0" style="text-align: center; padding: 40px;">
          <el-result icon="success" title="已完成" sub-title="所有工序均已完成，请点击下方交卷">
          </el-result>
        </div>

        <div v-for="(proc, pIndex) in blueprint.procedures" :key="pIndex" class="procedure-block">
          <h4>工序: {{ proc.name }}</h4>
          
          <div v-for="(q, qIndex) in proc.questions" :key="q.id" class="question-block">
            <p><strong>{{ qIndex + 1 }}. {{ q.prompt }}</strong> <span style="color: #999;">({{ q.score }}分)</span></p>
            
            <!-- 单选 / 扣分单选 -->
            <!-- 使用 toUpperCase() 兼容大小写 -->
            <el-radio-group 
              v-if="['SINGLE_CHOICE', 'DEDUCTION_SINGLE_CHOICE'].includes(q.question_type.toUpperCase())" 
              v-model="answers[q.id]"
            >
              <el-radio v-for="opt in q.options" :key="opt.id" :label="opt.id" border style="margin-bottom: 10px; display: block;">
                {{ opt.option_text }}
              </el-radio>
            </el-radio-group>

            <!-- 多选 -->
            <el-checkbox-group 
              v-if="q.question_type.toUpperCase() === 'MULTIPLE_CHOICE'" 
              v-model="answers[q.id]"
            >
              <el-checkbox v-for="opt in q.options" :key="opt.id" :label="opt.id" border style="margin-bottom: 10px; display: block;">
                {{ opt.option_text }}
              </el-checkbox>
            </el-checkbox-group>

            <div style="margin-top: 15px;">
              <!-- 修复：传入 proc.id -->
              <el-button size="small" type="primary" plain @click="submitSingleAnswer(proc.id, q.id)">提交本题答案</el-button>
              <span v-if="q.selected_option_ids" style="color: #67C23A; font-size: 12px; margin-left: 10px;">
                <el-icon><Check /></el-icon> 已保存
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
import { useRouter } from 'vue-router';
import request from '@/utils/request';
import { ElMessage } from 'element-plus';
import { Check } from '@element-plus/icons-vue';

const router = useRouter();
const activeStep = ref(0);
const examineeId = ref('WebTester_01');
const platformId = ref(1);
const upcomingList = ref<any[]>([]); 
const blueprint = ref<any>(null);
const currentResultId = ref<number | null>(null); 
const answers = ref<Record<number, any>>({}); 
const loading = ref(false);

// 1. 获取待考列表
const fetchUpcoming = async () => {
  loading.value = true;
  upcomingList.value = []; 
  try {
    const res: any = await request.get(`/client/platforms/${platformId.value}/assessments/upcoming`);
    if (res && res.id) {
      upcomingList.value = [res];
    }
  } catch (e: any) {
    if (e.response && e.response.status === 404) {
      ElMessage.warning('该平台下暂无正在进行的考核，请检查平台ID或考核时间');
    } else {
      console.error(e);
      ElMessage.error('查询失败，请检查网络');
    }
  } finally {
    loading.value = false;
  }
};

// 2. 开始/继续考试
const startSession = async (row: any) => {
  if (!examineeId.value) return ElMessage.warning('请先输入考生标识');
  
  try {
    const res: any = await request.post(`/client/assessments/${row.id}/session`, {
      examinee_identifier: examineeId.value
    });
    
    blueprint.value = res;
    currentResultId.value = res.assessment_result_id; 

    // 断点续考回显
    if (res.procedures) {
        res.procedures.forEach((p: any) => {
          p.questions.forEach((q: any) => {
            // 初始化
            if (q.question_type.toUpperCase() === 'MULTIPLE_CHOICE') {
              answers.value[q.id] = [];
            } else {
              answers.value[q.id] = null;
            }

            // 回显逻辑
            if (q.selected_option_ids && q.selected_option_ids.length > 0) {
              if (q.question_type.toUpperCase() === 'MULTIPLE_CHOICE') {
                answers.value[q.id] = q.selected_option_ids;
              } else {
                answers.value[q.id] = q.selected_option_ids[0];
              }
            }
          });
        });
    }

    activeStep.value = 2;
    ElMessage.success('考试会话已就绪');
  } catch (e) { console.error(e); }
};

// 3. 提交单题答案 (核心修复：添加 procedure_id)
const submitSingleAnswer = async (procedureId: number, questionId: number) => {
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
      examinee_identifier: examineeId.value,
      // ⚠️ 核心修复：增加 procedure_id，因为后端必填
      procedure_id: procedureId 
    });
    ElMessage.success('答案已保存');
  } catch (e: any) { 
    console.error(e); 
    const msg = e.response?.data?.detail || '提交失败';
    // 如果 detail 是数组（比如字段缺失），转成字符串显示
    ElMessage.error(typeof msg === 'string' ? msg : JSON.stringify(msg));
  }
};

// 4. 交卷
const finishExam = async () => {
  try {
    await request.post(`/client/assessment-results/${currentResultId.value}/finish`, {
      examinee_identifier: examineeId.value 
    });
    activeStep.value = 3;
  } catch (e) { console.error(e); }
};

const reset = () => {
  activeStep.value = 0;
  blueprint.value = null;
  answers.value = {};
  upcomingList.value = [];
};
</script>

<style scoped>
.step-content { max-width: 800px; margin: 40px auto; }
.procedure-block { margin-bottom: 30px; border: 1px solid #eee; padding: 20px; border-radius: 8px; }
.question-block { margin-bottom: 20px; padding-bottom: 20px; border-bottom: 1px dashed #eee; }
.footer-actions { text-align: center; margin-top: 40px; padding-bottom: 40px; }
</style>