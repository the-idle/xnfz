<template>
    <div class="page-container">
      <div class="header">
        <h2>用户管理</h2>
        <el-button type="primary" @click="openDialog('create')">新建用户</el-button>
      </div>
  
      <el-table :data="list" border stripe style="margin-top: 20px">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column label="权限" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_superuser ? 'warning' : 'info'">
              {{ row.is_superuser ? '超级管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button size="small" type="warning" @click="openDialog('edit', row)">重置密码</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
  
      <el-dialog v-model="dialogVisible" :title="dialogType === 'create' ? '新建用户' : '重置密码'" width="400px">
        <el-form :model="form" label-width="100px">
          <el-form-item label="用户名">
            <el-input v-model="form.username" :disabled="dialogType === 'edit'" placeholder="请输入登录用户名" />
          </el-form-item>
          
          <el-form-item label="密码">
            <el-input v-model="form.password" type="password" show-password placeholder="请输入密码 (至少6位)" />
          </el-form-item>
  
          <el-form-item label="管理员权限" v-if="dialogType === 'create'">
            <el-switch v-model="form.is_superuser" active-text="是" inactive-text="否" />
            <div style="font-size: 12px; color: #999; line-height: 1.2; margin-top: 5px;">开启后该用户可登录后台进行管理</div>
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
  import request from '@/utils/request';
  import { ElMessage, ElMessageBox } from 'element-plus';
  
  const list = ref([]);
  const dialogVisible = ref(false);
  const dialogType = ref<'create' | 'edit'>('create');
  const form = ref({ id: 0, username: '', password: '', is_superuser: false });
  
  const fetchList = async () => {
    const res = await request.get('/users/');
    list.value = res || [];
  };
  
  const openDialog = (type: 'create' | 'edit', row?: any) => {
    dialogType.value = type;
    if (type === 'edit' && row) {
      form.value = { id: row.id, username: row.username, password: '', is_superuser: row.is_superuser };
    } else {
      form.value = { id: 0, username: '', password: '', is_superuser: true };
    }
    dialogVisible.value = true;
  };
  
  const handleSubmit = async () => {
    // 基础非空校验
    if (!form.value.username) return ElMessage.warning('用户名不能为空');
    
    // --- 修复：密码校验逻辑 ---
    if (dialogType.value === 'create') {
      // 新建时密码必填且需 >= 6
      if (!form.value.password || form.value.password.length < 6) {
        return ElMessage.warning('新建用户密码长度不能少于6位');
      }
    } else {
      // 修改时，如果填了密码，就要校验长度
      if (form.value.password && form.value.password.length < 6) {
        return ElMessage.warning('新密码长度不能少于6位');
      }
    }
  
    try {
      if (dialogType.value === 'create') {
        await request.post('/users/', {
          username: form.value.username,
          password: form.value.password,
          is_superuser: form.value.is_superuser,
          email: `${form.value.username}@local.com`, 
          full_name: form.value.username
        });
      } else {
        // 如果是重置密码，只传 password 字段
        const payload: any = {};
        if (form.value.password) payload.password = form.value.password;
        
        // 如果没填密码直接点确定，提示一下或不发请求
        if (!payload.password) {
           dialogVisible.value = false;
           return;
        }
  
        await request.put(`/users/${form.value.id}`, payload);
      }
      ElMessage.success('操作成功');
      dialogVisible.value = false;
      fetchList();
    } catch (e: any) {
    // 👇 重点在这里 👇
    
    // 1. 获取后端返回的错误详情
    // 你的拦截器可能已经把 response.data 返回了，或者 error.response 存在
    const errorDetail = e.response?.data?.detail || e.message;

    // 2. 友好提示
    if (errorDetail === "Username already registered.") {
      ElMessage.warning('用户名已存在，请更换一个');
      // 此时控制台依然会有红色网络报错，这是正常的，只要界面弹出了黄色警告即可。
    } else {
      ElMessage.error(typeof errorDetail === 'string' ? errorDetail : '操作失败');
    }
    
    // 如果你不想在控制台看到 Uncaught (in promise)，这就已经防住了。
    // 但网络请求本身的 400 红色记录是消除不掉的。
  }
};
  
  const handleDelete = async (id: number) => {
    try {
      await ElMessageBox.confirm('确定删除该用户吗？', '警告', { type: 'warning' });
      await request.delete(`/users/${id}`);
      ElMessage.success('已删除');
      fetchList();
    } catch (e) {}
  };
  
  onMounted(fetchList);
  </script>