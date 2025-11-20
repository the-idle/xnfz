<template>
  <!-- ... 保持模板不变 ... -->
  <div class="page-container">
    <div class="header">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/platforms' }">平台</el-breadcrumb-item>
        <el-breadcrumb-item @click="$router.back()" style="cursor: pointer">题库</el-breadcrumb-item>
        <el-breadcrumb-item>工序管理</el-breadcrumb-item>
      </el-breadcrumb>
      <div style="margin-top: 15px;">
        <el-button type="primary" @click="openDialog('create')">新建工序</el-button>
      </div>
    </div>

    <el-table :data="list" border style="margin-top: 20px;">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="工序名称" />
      <el-table-column label="操作" width="250">
        <template #default="{ row }">
          <el-button size="small" type="success" @click="enterQuestions(row.id)">管理题目</el-button>
          <el-button size="small" type="primary" @click="openDialog('edit', row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="dialogType === 'create' ? '新建工序' : '编辑工序'" width="400px">
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
const bankId = route.params.bankId;

const list = ref([]);
const dialogVisible = ref(false);
const dialogType = ref('create');
const form = ref({ id: 0, name: '' });

const fetchData = async () => {
  try {
    const res = await request.get(`/question-banks/${bankId}/procedures/`);
    list.value = res || [];
  } catch (e) { console.error(e); }
};

const openDialog = (type: string, row?: any) => {
  dialogType.value = type;
  form.value = type === 'edit' ? { ...row } : { id: 0, name: '' };
  dialogVisible.value = true;
};

// --- 修复重点：路径参数确保正确 ---
const handleSubmit = async () => {
  try {
    if (dialogType.value === 'create') {
      await request.post(`/question-banks/${bankId}/procedures/`, { name: form.value.name });
    } else {
      // 这里的路径必须和后端 api/endpoints/procedures.py 里的路径一致
      // 通常是 PUT /question-banks/{bank_id}/procedures/{procedure_id}
      await request.put(`/question-banks/${bankId}/procedures/${form.value.id}`, { name: form.value.name });
    }
    ElMessage.success('操作成功');
    dialogVisible.value = false;
    fetchData();
  } catch (e) { 
    console.error(e); 
    // 如果是 500，不用 ElMessage 报出来，request.ts 拦截器通常会报
  }
};

const handleDelete = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定删除？这会同时删除该工序下的所有题目！', '警告', { type: 'warning' });
    // 这里的路径同上
    await request.delete(`/question-banks/${bankId}/procedures/${id}`);
    ElMessage.success('删除成功');
    fetchData();
  } catch (e) { console.error(e); }
};

const enterQuestions = (id: number) => router.push(`/procedures/${id}/questions`);

onMounted(fetchData);
</script>