<template>
  <div class="page-container">
    <div class="header">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/platforms' }">平台列表</el-breadcrumb-item>
        <el-breadcrumb-item>题库管理</el-breadcrumb-item>
      </el-breadcrumb>
      <div style="margin-top: 15px;">
        <el-button type="primary" @click="openDialog('create')">新建题库</el-button>
      </div>
    </div>

    <el-table :data="list" border style="margin-top: 20px;">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="题库名称" />
      <el-table-column prop="total_score" label="总分" width="100" align="center">
        <template #default="{ row }">
          <el-tag type="primary">{{ row.total_score ?? 0 }} 分</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="250">
        <template #default="{ row }">
          <el-button size="small" type="success" @click="enterProcedure(row.id)">管理工序</el-button>
          <el-button size="small" type="primary" @click="openDialog('edit', row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="dialogType === 'create' ? '新建题库' : '编辑题库'" width="400px">
      <el-form :model="form">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="handleSubmit" type="primary">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import request from '@/utils/request';
import { ElMessage, ElMessageBox } from 'element-plus';

const route = useRoute();
const router = useRouter();
const platformId = route.params.platformId;

const list = ref([]);
const dialogVisible = ref(false);
const dialogType = ref('create');
const form = ref({ id: 0, name: '' });

const fetchData = async () => {
  const res = await request.get(`/platforms/${platformId}/question-banks/`);
  list.value = res || [];
};

const openDialog = (type: string, row?: any) => {
  dialogType.value = type;
  form.value = type === 'edit' ? { ...row } : { id: 0, name: '' };
  dialogVisible.value = true;
};

const handleSubmit = async () => {
  // --- 核心修复：前端先校验，不要发空数据给后端 ---
  if (!form.value.name || !form.value.name.trim()) {
    ElMessage.warning('题库名称不能为空');
    return; // 直接中断，不发请求
  }

  try {
    if (dialogType.value === 'create') {
      await request.post(`/platforms/${platformId}/question-banks/`, form.value);
    } else {
      // 确保这里只发送 name 字段，或者后端 update schema 允许其他字段
      await request.put(`/platforms/${platformId}/question-banks/${form.value.id}`, {
        name: form.value.name
      });
    }
    ElMessage.success('操作成功');
    dialogVisible.value = false;
    fetchData();
  } catch (e: any) {
    // 如果后端还是报错，这里会捕获
    // 之前的 request.ts 已经处理了大部分报错
    console.error(e);
  }
};

const handleDelete = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定删除？', '警告', { type: 'warning' });
    await request.delete(`/platforms/${platformId}/question-banks/${id}`);
    ElMessage.success('删除成功');
    fetchData();
  } catch (e) {}
};

const enterProcedure = (id: number) => router.push(`/banks/${id}/procedures`);

onMounted(fetchData);
</script>