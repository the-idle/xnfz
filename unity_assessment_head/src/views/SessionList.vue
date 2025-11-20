<template>
    <div class="page-container">
      <div class="header">
        <el-page-header @back="$router.push('/assessments')">
          <template #content>
            <span class="text-large font-600 mr-3"> 考核成绩单 </span>
          </template>
        </el-page-header>
      </div>
  
      <el-empty v-if="!assessmentId" description="请先在「场次发布」页面选择一个考核查看成绩" />
  
      <div v-else style="margin-top: 20px;">
        <el-table :data="sessionList" border style="width: 100%" v-loading="loading">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="examinee_identifier" label="考生/设备标识" />
          
          <el-table-column prop="total_score" label="得分" sortable width="120" align="center">
            <template #default="{ row }">
              <span :class="getScoreClass(row.total_score)" style="font-size: 16px;">
                {{ row.total_score }}
              </span>
            </template>
          </el-table-column>
          
          <el-table-column label="状态" width="120" align="center">
            <template #default="{ row }">
              <el-tag :type="row.end_time ? 'success' : 'warning'">
                {{ row.end_time ? '已交卷' : '进行中' }}
              </el-tag>
            </template>
          </el-table-column>
  
          <el-table-column label="交卷时间">
            <template #default="{ row }">
              {{ row.end_time ? new Date(row.end_time).toLocaleString() : '-' }}
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="150" align="center">
            <template #default="{ row }">
              <!-- 修复：启用了查看详情按钮 -->
              <el-button type="primary" size="small" @click="viewDetail(row.id)" :disabled="!row.end_time">
                查看详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, onMounted } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import request from '@/utils/request';
  import type { AssessmentSession } from '@/types/api';
  
  const route = useRoute();
  const router = useRouter();
  const assessmentId = route.query.assessmentId;
  const loading = ref(false);
  const sessionList = ref<AssessmentSession[]>([]);
  
  const fetchResults = async () => {
    if (!assessmentId) return;
    loading.value = true;
    try {
      const res = await request.get<any, AssessmentSession[]>(`/admin/assessments/${assessmentId}/results/`);
      sessionList.value = res || [];
    } catch (error) {
      console.error(error);
    } finally {
      loading.value = false;
    }
  };
  
  const viewDetail = (sessionId: number) => {
    // 跳转到详情页
    router.push(`/sessions/${sessionId}`);
  };
  
  const getScoreClass = (score: number) => {
    if (score >= 90) return 'text-success';
    if (score < 60) return 'text-danger';
    return 'text-warning';
  };
  
  onMounted(fetchResults);
  </script>
  
  <style scoped>
  .text-success { color: #67C23A; font-weight: bold; }
  .text-danger { color: #F56C6C; font-weight: bold; }
  .text-warning { color: #E6A23C; font-weight: bold; }
  </style>