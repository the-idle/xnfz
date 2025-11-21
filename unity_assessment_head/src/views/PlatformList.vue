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
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入平台描述" />
        </el-form-item>
        
        <!-- 密码字段优化 -->
        <el-form-item label="访问密码">
          <el-input 
            v-model="form.password" 
            type="password" 
            show-password 
            :placeholder="dialogType === 'create' ? '请输入密码 (至少6位)' : '留空则不修改'"
            autocomplete="new-password" 
          />
          <div style="font-size: 12px; color: #999; line-height: 1.4; margin-top: 5px;">
            <span v-if="dialogType === 'create'" style="color: #f56c6c;">* 必填项，至少6位字符。</span>
            <span v-else>如需修改，请输入新密码（至少6位）；否则留空。</span>
          </div>
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

const form = ref({ 
  id: 0, 
  name: '', 
  description: '',
  password: '' 
});

const fetchPlatforms = async () => {
  try {
    const data = await request.get<any, Platform[]>('/platforms/'); 
    platformList.value = data || [];
  } catch (e) { console.error(e); }
};

const openDialog = (type: 'create' | 'edit', row?: Platform) => {
  dialogType.value = type;
  
  if (type === 'edit' && row) {
    form.value = { 
      id: row.id, 
      name: row.name, 
      description: row.description || '',
      password: '' // 编辑模式默认清空密码框
    };
  } else {
    form.value = { id: 0, name: '', description: '', password: '' };
  }
  dialogVisible.value = true;
};

// --- 核心修复：handleSubmit ---
const handleSubmit = async () => {
  if (!form.value.name) return ElMessage.warning('平台名称不能为空');

  // 1. 校验密码长度
  if (dialogType.value === 'create') {
    // 新建模式：密码必填且 >= 6
    if (!form.value.password || form.value.password.length < 6) {
      return ElMessage.warning('新建平台时，密码必须填写且至少6位');
    }
  } else {
    // 编辑模式：如果填了密码，必须 >= 6
    if (form.value.password && form.value.password.length < 6) {
      return ElMessage.warning('新密码长度至少6位');
    }
  }

  // 2. 构造 Payload
  const payload: any = {
    name: form.value.name,
    description: form.value.description
  };
  
  // 只有当输入了密码时才发送 password 字段
  if (form.value.password) {
    payload.password = form.value.password;
  }

  try {
    if (dialogType.value === 'create') {
      await request.post('/platforms/', payload);
      ElMessage.success('创建成功');
    } else {
      await request.put(`/platforms/${form.value.id}`, payload);
      ElMessage.success('更新成功');
    }

    dialogVisible.value = false;
    fetchPlatforms(); 
  } catch (e: any) {
    console.error(e);
    // 后端如果还报 422，会被 request.ts 捕获或在这里处理
  }
};

const handleDelete = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定删除该平台吗？', '警告', { type: 'warning' });
    await request.delete(`/platforms/${id}`);
    ElMessage.success('删除成功');
    fetchPlatforms();
  } catch (e) {}
};

const goToBanks = (id: number) => {
  router.push(`/platforms/${id}/banks`);
};

onMounted(fetchPlatforms);
</script>