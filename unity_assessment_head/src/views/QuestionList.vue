<template>
  <div class="page-container">
    <div class="header">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/platforms' }">平台</el-breadcrumb-item>
        <el-breadcrumb-item @click="$router.go(-2)" style="cursor: pointer">题库</el-breadcrumb-item>
        <el-breadcrumb-item @click="$router.back()" style="cursor: pointer">工序</el-breadcrumb-item>
        <el-breadcrumb-item>题目管理</el-breadcrumb-item>
      </el-breadcrumb>
      <div style="margin-top: 15px;">
        <el-button type="primary" @click="goToCreate">录入新题目</el-button>
      </div>
    </div>

    <el-table :data="list" border style="margin-top: 20px;">
      <el-table-column prop="id" label="ID" width="60" />
      
      <!-- 类型列 -->
      <el-table-column label="类型" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="getTypeColor(row.question_type)" effect="plain">
            {{ getTypeText(row.question_type) }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="prompt" label="题干" show-overflow-tooltip />
      <el-table-column prop="score" label="分值" width="70" align="center" />
      
      <el-table-column label="配图" width="100" align="center">
        <template #default="{ row }">
          <el-image 
            v-if="row.image_url" 
            style="width: 50px; height: 50px; border-radius: 4px;" 
            :src="resolveImageUrl(row.image_url)" 
            :preview-src-list="[resolveImageUrl(row.image_url)]" 
            fit="cover"
            preview-teleported
          >
            <template #error>
              <div style="display: flex; justify-content: center; align-items: center; height: 100%; color: #ccc; background: #f5f7fa;">无图</div>
            </template>
          </el-image>
          <span v-else style="color: #ccc; font-size: 12px;">无图</span>
        </template>
      </el-table-column>

      <el-table-column label="操作" width="180" align="center">
        <template #default="{ row }">
          <el-button size="small" type="primary" @click="goToEdit(row.id)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import request from '@/utils/request';
import { ElMessage, ElMessageBox } from 'element-plus';

const route = useRoute();
const router = useRouter();
const procedureId = route.params.procedureId;

const list = ref<any[]>([]);

const fetchData = async () => {
  const res = await request.get<any, any[]>(`/procedures/${procedureId}/questions/`);
  list.value = res || [];
};

const handleDelete = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定删除该题目？', '警告', { type: 'warning' });
    await request.delete(`/procedures/${procedureId}/questions/${id}`);
    ElMessage.success('删除成功');
    fetchData();
  } catch (e) {}
};

const goToCreate = () => router.push(`/procedures/${procedureId}/questions/create`);

const goToEdit = (questionId: number) => {
  router.push(`/procedures/${procedureId}/questions/${questionId}/edit`);
};

// --- 核心修复：处理大小写问题 ---
const getTypeText = (type: string) => {
  if (!type) return '未知';
  // 统一转大写再匹配
  const key = type.toUpperCase();
  const map: Record<string, string> = {
    'SINGLE_CHOICE': '单选题',
    'MULTIPLE_CHOICE': '多选题',
    'DEDUCTION_SINGLE_CHOICE': '扣分单选'
  };
  return map[key] || type;
};

const getTypeColor = (type: string) => {
  if (!type) return 'info'; // 默认给 info
  const key = type.toUpperCase();
  if (key === 'MULTIPLE_CHOICE') return 'warning';
  if (key === 'DEDUCTION_SINGLE_CHOICE') return 'danger';
  return 'primary'; // 默认给 primary (蓝色) 或 info
};

const resolveImageUrl = (url: string) => {
  if (!url) return '';
  if (url.startsWith('http')) return url;
  const BASE_URL = 'http://127.0.0.1:8000'; 
  return `${BASE_URL}${url}`;
};


onMounted(fetchData);
</script>