<template>
  <div class="page-container" v-loading="loading">
    <div class="header">
      <el-page-header @back="$router.back()">
        <template #content>
          <span class="text-large font-600 mr-3"> 考卷详情 </span>
        </template>
      </el-page-header>
    </div>

    <div v-if="detail" style="margin-top: 20px;">
      <!-- 成绩概览卡片 -->
      <el-card shadow="never" class="score-card">
        <div class="score-summary">
          <div class="score-item">
            <div class="label">考生标识</div>
            <div class="value">{{ detail.examinee_identifier }}</div>
          </div>
          <div class="score-item">
            <div class="label">最终得分</div>
            <div class="value score-num" :class="getScoreClass(detail.total_score)">{{ detail.total_score }}</div>
          </div>
          <div class="score-item">
            <div class="label">耗时</div>
            <div class="value">{{ calcDuration(detail.start_time, detail.end_time) }}</div>
          </div>
        </div>
      </el-card>

      <!-- 答题流水 -->
      <h3 style="margin-top: 30px;">答题详情</h3>
      
      <div v-if="!logs || logs.length === 0">
        <el-empty description="暂无详细答题日志" />
      </div>

      <div v-else class="question-list">
        <el-card v-for="(log, index) in logs" :key="index" class="question-card" shadow="hover">
          <template #header>
            <div class="q-header">
              <span class="q-index">第 {{ index + 1 }} 题 
                <span style="font-size: 12px; font-weight: normal; color: #999;">(ID: {{ log.question_id }})</span>
              </span>
              
              <div class="q-status">
                <el-tag :type="log.score_awarded > 0 ? 'success' : 'danger'">
                   {{ log.score_awarded > 0 ? '得分' : '0分' }}
                </el-tag>
                <span style="margin-left: 10px; font-weight: bold;">
                  得 {{ log.score_awarded }} 分
                </span>
              </div>
            </div>
          </template>

          <div class="q-body">
            <!-- 题干显示 -->
            <div v-if="log.question" class="q-prompt">
              {{ log.question.prompt }}
              <!-- 修复：调用 getTypeText 显示中文类型 -->
              <el-tag size="small" type="info" effect="plain" style="margin-left: 10px; vertical-align: text-bottom;">
                {{ getTypeText(log.question.question_type) }}
              </el-tag>
            </div>
            <div v-else class="q-prompt-fallback">
              <el-text type="info">题目详情未找到（可能已被删除）</el-text>
            </div>

            <!-- 选项显示 -->
            <div class="q-options" v-if="log.question && log.question.options">
              <div 
                v-for="opt in log.question.options" 
                :key="opt.id"
                class="option-item"
                :class="{
                  'user-selected': isSelected(log, opt.id),
                  'is-correct': opt.is_correct
                }"
              >
                <!-- 图标逻辑 -->
                <el-icon v-if="opt.is_correct" color="#67C23A" class="opt-icon"><Check /></el-icon>
                <el-icon v-else-if="isSelected(log, opt.id)" color="#F56C6C" class="opt-icon"><Close /></el-icon>
                <span v-else class="opt-icon"></span> 
                
                {{ opt.option_text }}
                
                <span v-if="isSelected(log, opt.id)" class="tag-selected">(考生选择)</span>
              </div>
            </div>

            <!-- 降级显示 -->
            <div v-else style="margin-top: 10px; padding: 10px; background: #f9f9f9; border-radius: 4px;">
              <span style="color: #666;">考生提交的选项 ID: </span>
              <span style="font-family: monospace; font-weight: bold;">
                {{ Array.isArray(log.selected_option_ids) ? log.selected_option_ids.join(', ') : log.selected_option_ids }}
              </span>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import request from '@/utils/request';
import { Check, Close } from '@element-plus/icons-vue';

const route = useRoute();
const sessionId = route.params.id;
const loading = ref(false);
const detail = ref<any>(null);

// 兼容字段名
const logs = computed(() => {
  if (!detail.value) return [];
  return detail.value.answer_logs || detail.value.logs || [];
});

const fetchDetail = async () => {
  loading.value = true;
  try {
    const res = await request.get<any, any>(`/admin/assessment-results/${sessionId}`);
    detail.value = res;
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
};

const isSelected = (log: any, optId: number) => {
  if (!log.selected_option_ids) return false;
  return log.selected_option_ids.includes(optId);
};

// --- 新增：中文类型转换 ---
const getTypeText = (type: string) => {
  if (!type) return '未知';
  // 转大写，防止 multiple_choice 匹配失败
  const key = type.toUpperCase();
  const map: Record<string, string> = {
    'SINGLE_CHOICE': '单选题',
    'MULTIPLE_CHOICE': '多选题',
    'DEDUCTION_SINGLE_CHOICE': '扣分单选题'
  };
  return map[key] || type; // 匹配不到则显示原文
};

const getScoreClass = (score: number) => {
  if (score >= 90) return 'text-success';
  if (score < 60) return 'text-danger';
  return 'text-warning';
};

const calcDuration = (start: string, end?: string) => {
  if (!end) return '未完成';
  const diff = new Date(end).getTime() - new Date(start).getTime();
  const minutes = Math.floor(diff / 60000);
  const seconds = Math.floor((diff % 60000) / 1000);
  return `${minutes}分 ${seconds}秒`;
};

onMounted(fetchDetail);
</script>

<style scoped>
.score-card { background-color: #f8f9fa; }
.score-summary { display: flex; justify-content: space-around; text-align: center; }
.score-item .label { color: #909399; margin-bottom: 5px; }
.score-item .value { font-size: 18px; font-weight: bold; }
.score-num { font-size: 24px; }

.question-list { margin-top: 20px; }
.question-card { margin-bottom: 15px; }
.q-header { display: flex; align-items: center; justify-content: space-between; }
.q-index { font-weight: bold; font-size: 16px; }
.q-prompt { font-size: 16px; margin-bottom: 15px; font-weight: 500; }
.q-prompt-fallback { margin-bottom: 15px; }

.option-item { 
  padding: 10px; 
  border: 1px solid #dcdfe6; 
  margin-bottom: 8px; 
  border-radius: 4px; 
  display: flex; 
  align-items: center;
}
.opt-icon { width: 24px; margin-right: 8px; display: flex; align-items: center; }
.user-selected { border-color: #409EFF; background-color: #ecf5ff; }
.is-correct { border-color: #67C23A; background-color: #f0f9eb; }
.tag-selected { font-size: 12px; color: #409EFF; margin-left: auto; font-weight: bold; }
.text-success { color: #67C23A; }
.text-danger { color: #F56C6C; }
.text-warning { color: #E6A23C; }
</style>