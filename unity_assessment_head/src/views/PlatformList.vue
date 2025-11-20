<template>
    <div class="page-container">
      <div class="header">
        <h2>平台管理</h2>
        <el-button type="primary" @click="openDialog('create')">新建平台</el-button>
      </div>
  
      <el-table :data="platformList" border stripe style="width: 100%; margin-top: 20px">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="平台名称" />
        <el-table-column prop="description" label="描述" />
        
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <!-- 确保这三个按钮都在 -->
            <el-button size="small" type="success" @click="goToBanks(row.id)">管理题库</el-button>
            <el-button size="small" type="primary" @click="openDialog('edit', row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
  
      <!-- 弹窗 -->
      <el-dialog 
        v-model="dialogVisible" 
        :title="dialogType === 'create' ? '新建平台' : '编辑平台'"
        width="500px"
      >
        <el-form :model="form" label-width="80px">
          <el-form-item label="名称">
            <el-input v-model="form.name" placeholder="请输入平台名称" />
          </el-form-item>
          <el-form-item label="描述">
            <el-input v-model="form.description" type="textarea" :rows="3" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </template>
      </el-dialog>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, onMounted } from 'vue';
  import { useRouter } from 'vue-router';
  import request from '@/utils/request';
  import type { Platform } from '@/types/api';
  import { ElMessage, ElMessageBox } from 'element-plus';
  
  const router = useRouter();
  const platformList = ref<Platform[]>([]);
  const dialogVisible = ref(false);
  const dialogType = ref<'create' | 'edit'>('create');
  const form = ref({ id: 0, name: '', description: '' });
  
  const fetchPlatforms = async () => {
    const data = await request.get<any, Platform[]>('/platforms/'); 
    platformList.value = data || [];
  };
  
  const openDialog = (type: 'create' | 'edit', row?: Platform) => {
    dialogType.value = type;
    if (type === 'edit' && row) {
      form.value = { id: row.id, name: row.name, description: row.description || '' };
    } else {
      form.value = { id: 0, name: '', description: '' };
    }
    dialogVisible.value = true;
  };
  
  const handleSubmit = async () => {
    if (!form.value.name) return ElMessage.warning('平台名称不能为空');
    try {
      if (dialogType.value === 'create') {
        await request.post('/platforms/', { name: form.value.name, description: form.value.description });
      } else {
        await request.put(`/platforms/${form.value.id}`, { name: form.value.name, description: form.value.description });
      }
      ElMessage.success('操作成功');
      dialogVisible.value = false;
      fetchPlatforms();
    } catch (e) { console.error(e); }
  };
  
  const handleDelete = async (id: number) => {
    try {
      await ElMessageBox.confirm('确定删除该平台吗？', '警告', { type: 'warning' });
      await request.delete(`/platforms/${id}`);
      fetchPlatforms();
    } catch (error) {}
  };
  
  const goToBanks = (id: number) => {
    router.push(`/platforms/${id}/banks`);
  };
  
  onMounted(fetchPlatforms);
  </script>