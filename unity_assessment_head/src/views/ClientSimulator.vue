<template>
  <div class="page-container">
    <div class="header">
      <h2>模拟考生终端 (Debug)</h2>
      <el-alert title="用于模拟客户端答题流程，验证数据生成与计分逻辑" type="info" show-icon :closable="false" />
    </div>

    <!-- 美化步骤条：去掉了 simple 属性，换了更好看的图标 -->
    <el-steps :active="activeStep" finish-status="success" align-center style="margin: 40px 0">
      <el-step title="身份录入" :icon="UserFilled" />
      <el-step title="选择考核" :icon="Monitor" />
      <el-step title="正在答题" :icon="EditPen" />
      <el-step title="完成" :icon="Trophy" />
    </el-steps>

    <!-- 步骤1: 身份录入 -->
    <div v-if="activeStep === 0" class="step-wrapper">
      <el-card class="center-card">
        <template #header>
          <div class="card-header">
            <span>考生登录</span>
          </div>
        </template>
        <el-form label-position="top" size="large">
          <el-form-item label="考生/设备标识">
            <el-input v-model="examineeId" placeholder="请输入唯一标识 (如 Worker_01)" :prefix-icon="User" />
          </el-form-item>
          <el-button type="primary" style="width: 100%; margin-top: 10px;" @click="activeStep = 1" :disabled="!examineeId">
            下一步
          </el-button>
        </el-form>
      </el-card>
    </div>

    <!-- 步骤2: 获取近期考核 -->
    <div v-if="activeStep === 1" class="step-wrapper">
      <div class="filter-bar">
        <el-input v-model.number="platformId" placeholder="平台ID" style="width: 150px;" />
        <el-button type="primary" @click="fetchUpcoming" :loading="loading" :icon="Search">查询</el-button>
        <el-button @click="activeStep = 0" :icon="Back">返回</el-button>
      </div>
      
      <el-table :data="upcomingList" border style="width: 100%; margin-top: 20px;" empty-text="暂无进行中的考核" stripe>
        <el-table-column prop="id" label="考核ID" width="80" align="center" />
        <el-table-column prop="title" label="考核标题" />
        <el-table-column label="时间范围">
          <template #default="{row}">
            {{ new Date(row.start_time).toLocaleDateString() }} - {{ new Date(row.end_time).toLocaleDateString() }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" align="center">
          <template #default="{ row }">
            <el-button type="success" size="small" @click="startSession(row)" round>开始答题</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 步骤3: 答题界面 -->
    <div v-if="activeStep === 2 && blueprint" class="exam-wrapper">
      <div class="exam-header">
        <h3>{{ assessmentTitle }}</h3>
        <el-tag type="warning" effect="dark">考试中</el-tag>
      </div>
      
      <div v-if="blueprint.procedures.length === 0" class="empty-state">
        <el-empty description="试卷加载异常或为空" />
      </div>

      <div class="paper-content">
        <div v-for="(proc, pIndex) in blueprint.procedures" :key="pIndex" class="procedure-section">
          <div class="procedure-title">
            <span class="proc-badge">工序 {{ pIndex + 1 }}</span>
            {{ proc.name }}
          </div>
          
          <div v-for="(q, qIndex) in proc.questions" :key="q.id" class="question-card">
            <div class="q-title-row">
              <span class="q-num">{{ qIndex + 1 }}.</span>
              <div class="q-text">
                {{ q.prompt }}
                <span class="q-score">({{ q.score }}分)</span>
                <el-tag size="small" effect="plain" style="margin-left: 8px;">
                  {{ getTypeText(q.question_type) }}
                </el-tag>
              </div>
            </div>

            <!-- 图片显示 -->
            <div v-if="q.image_url" class="q-image">
              <el-image 
                :src="resolveImageUrl(q.image_url)" 
                :preview-src-list="[resolveImageUrl(q.image_url)]"
                fit="contain"
                style="max-height: 200px; border-radius: 8px;"
              />
            </div>

            <!-- 选项区域 -->
            <div class="q-options-area">
              <!-- 单选/扣分单选 -->
              <el-radio-group 
                v-if="['SINGLE_CHOICE', 'DEDUCTION_SINGLE_CHOICE'].includes(q.question_type.toUpperCase())" 
                v-model="answers[q.id]"
                class="vertical-options"
                :disabled="isQuestionSubmitted(q.id)"
              >
                <el-radio 
                  v-for="opt in q.options" 
                  :key="opt.id" 
                  :label="opt.id" 
                  border
                  class="option-item"
                >
                  {{ opt.option_text }}
                </el-radio>
              </el-radio-group>

              <!-- 多选 -->
              <el-checkbox-group 
                v-if="q.question_type.toUpperCase() === 'MULTIPLE_CHOICE'" 
                v-model="answers[q.id]"
                class="vertical-options"
                :disabled="isQuestionSubmitted(q.id)"
              >
                <el-checkbox 
                  v-for="opt in q.options" 
                  :key="opt.id" 
                  :label="opt.id" 
                  border
                  class="option-item"
                >
                  {{ opt.option_text }}
                </el-checkbox>
              </el-checkbox-group>
            </div>

            <!-- 底部操作栏 -->
            <div class="q-footer">
              <transition name="el-fade-in">
                <div v-if="isQuestionSubmitted(q.id)" class="status-done">
                  <el-icon><CircleCheckFilled /></el-icon> 
                  <span style="margin-left: 5px;">已提交 (不可修改)</span>
                </div>
                <div v-else>
                  <el-button type="primary" plain size="small" @click="submitSingleAnswer(proc.id, q.id)">
                    确认提交
                  </el-button>
                </div>
              </transition>
            </div>
          </div>
        </div>
      </div>

      <div class="exam-footer-bar">
        <div class="progress-info">
          已完成 {{ submittedCount }} / {{ totalQuestionCount }} 题
        </div>
        <el-button type="danger" size="large" @click="finishExam" :icon="Finished">
          交卷结束
        </el-button>
      </div>
    </div>

    <!-- 步骤4: 完成 -->
    <div v-if="activeStep === 3" class="step-wrapper center-card">
      <el-result icon="success" title="考试结束" sub-title="答案已上传，请前往后台[成绩记录]查看判分结果">
        <template #extra>
          <el-button type="primary" @click="reset">返回首页</el-button>
          <!-- 修复：跳转到本次考试的详情页 -->
          <el-button @click="viewCurrentResult">去查看成绩</el-button>
        </template>
      </el-result>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import request from '@/utils/request';
import { ElMessage } from 'element-plus';
// 引入了更美观的图标
import { 
  User, UserFilled, Monitor, EditPen, Trophy, 
  Search, Back, CircleCheckFilled, Finished 
} from '@element-plus/icons-vue';

const router = useRouter();
const activeStep = ref(0);
const examineeId = ref('WebTester_01');
const platformId = ref(1);
const upcomingList = ref<any[]>([]); 
const blueprint = ref<any>(null);
const assessmentTitle = ref('');
const currentResultId = ref<number | null>(null); 
const answers = ref<Record<number, any>>({}); 
const submittedStatus = ref<Record<number, boolean>>({});
const loading = ref(false);

// 计算属性
const totalQuestionCount = computed(() => {
  if (!blueprint.value) return 0;
  let count = 0;
  blueprint.value.procedures.forEach((p: any) => count += p.questions.length);
  return count;
});

const submittedCount = computed(() => {
  return Object.values(submittedStatus.value).filter(val => val).length;
});

const getTypeText = (type: string) => {
  const map: Record<string, string> = {
    'SINGLE_CHOICE': '单选',
    'MULTIPLE_CHOICE': '多选',
    'DEDUCTION_SINGLE_CHOICE': '扣分单选'
  };
  return map[type.toUpperCase()] || type;
};

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
    if (e.code === 404) {
        ElMessage.warning('该平台下暂无正在进行的考核');
    } else {
        console.error(e);
    }
  } finally {
    loading.value = false;
  }
};

// 2. 开始/继续考试
const startSession = async (row: any) => {
  if (!examineeId.value) return ElMessage.warning('请先输入考生标识');
  assessmentTitle.value = row.title;
  
  try {
    const res: any = await request.post(`/client/assessments/${row.id}/session`, {
      examinee_identifier: examineeId.value
    });
    
    blueprint.value = res;
    currentResultId.value = res.assessment_result_id; 
    
    submittedStatus.value = {};

    if (res.procedures) {
        res.procedures.forEach((p: any) => {
          p.questions.forEach((q: any) => {
            if (q.question_type.toUpperCase() === 'MULTIPLE_CHOICE') {
              answers.value[q.id] = [];
            } else {
              answers.value[q.id] = null;
            }

            if (q.selected_option_ids && q.selected_option_ids.length > 0) {
              submittedStatus.value[q.id] = true;
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
    ElMessage.success('试卷加载完毕');
  } catch (e: any) {
    console.error("Start Session Error:", e);
    
    // --- 核心修复：显式弹出后端返回的错误信息 ---
    // 拦截器已经把 msg 挂载到了 e.message 上
    const msg = e.message || '无法开始考试';
    
    // 如果是 403 (已考过)，用黄色警告提示，体验更好
    if (e.code === 403 || msg.includes('已完成') || msg.includes('finished')) {
        ElMessage.warning(msg);
    } else {
        // 其他错误用红色报错
        ElMessage.error(msg);
    }
  }
};

const isQuestionSubmitted = (qid: number) => {
  return !!submittedStatus.value[qid];
};

// 3. 提交单题答案
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
      procedure_id: procedureId
    });
    
    submittedStatus.value[questionId] = true;
    ElMessage.success('本题已提交并锁定');
    
  } catch (e: any) { 
    console.error(e); 
    const msg = e.response?.data?.detail || e.message || '提交失败';
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

// --- 新增：跳转查看本次成绩 ---
const viewCurrentResult = () => {
  if (currentResultId.value) {
    router.push(`/sessions/${currentResultId.value}`);
  } else {
    ElMessage.warning('未找到本次考试记录ID');
  }
};

const reset = () => {
  activeStep.value = 0;
  blueprint.value = null;
  answers.value = {};
  upcomingList.value = [];
  submittedStatus.value = {};
};

const resolveImageUrl = (url: string) => {
  if (!url) return '';
  if (url.startsWith('http')) return url;
  return `http://127.0.0.1:8000${url}`;
};
</script>

<style scoped>
/* 通用布局 */
.step-wrapper { max-width: 800px; margin: 0 auto; }
.center-card { max-width: 500px; margin: 40px auto; }
.card-header { font-weight: bold; font-size: 18px; }
.filter-bar { display: flex; gap: 10px; margin-bottom: 20px; justify-content: center; }

/* 考试界面 */
.exam-wrapper { 
  max-width: 800px; 
  margin: 0 auto 80px auto;
}

.exam-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.05);
  margin-bottom: 20px;
}

/* 题目卡片 */
.question-card {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.05);
  margin-bottom: 15px;
  border-left: 4px solid transparent;
  transition: all 0.3s;
}
.question-card:hover {
  box-shadow: 0 4px 16px 0 rgba(0,0,0,0.1);
}

/* 题干区域 */
.q-title-row {
  display: flex;
  align-items: flex-start;
  margin-bottom: 15px;
}
.q-num {
  font-size: 18px;
  font-weight: bold;
  color: #409EFF;
  margin-right: 10px;
  min-width: 25px;
}
.q-text {
  font-size: 16px;
  color: #303133;
  line-height: 1.5;
}
.q-score {
  color: #909399;
  font-size: 14px;
  margin-left: 5px;
}

/* 图片 */
.q-image {
  margin: 10px 0 10px 35px;
  background: #f5f7fa;
  padding: 5px;
  border-radius: 4px;
  display: inline-block;
}

/* 选项样式 */
.q-options-area {
  margin-left: 35px;
}
.vertical-options .el-radio,
.vertical-options .el-checkbox {
  width: 100%;
  margin-right: 0;
  margin-bottom: 12px;
  height: auto;
  padding: 12px 20px; /* 加大点击区域 */
  border-radius: 8px;
  white-space: normal;
  display: flex;
  align-items: center;
  transition: all 0.2s;
}
/* 选中态背景高亮 */
:deep(.el-radio.is-bordered.is-checked),
:deep(.el-checkbox.is-bordered.is-checked) {
  background-color: #ecf5ff;
  border-color: #409EFF;
  border-width: 2px;
}

/* 底部栏 */
.q-footer {
  margin-top: 15px;
  margin-left: 35px;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  height: 32px;
}
.status-done {
  color: #67C23A;
  font-size: 14px;
  display: flex;
  align-items: center;
  background: #f0f9eb;
  padding: 5px 10px;
  border-radius: 4px;
}

/* 悬浮进度条 */
.exam-footer-bar {
  position: fixed;
  bottom: 0;
  left: 220px; 
  right: 0;
  background: #fff;
  padding: 15px 40px;
  box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 100;
  border-top: 1px solid #ebeef5;
}
.progress-info {
  font-size: 16px;
  font-weight: bold;
  color: #606266;
}
</style>