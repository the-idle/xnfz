<template>
    <div class="page-container">
      <div class="header">
        <div class="left-panel">
          <h2>考核场次管理</h2>
          <el-select 
            v-model="filterPlatformId" 
            placeholder="筛选：请选择所属平台" 
            style="width: 240px; margin-left: 20px;"
            clearable
            @change="handleFilterChange"
          >
            <el-option v-for="p in platformList" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </div>
        <el-button type="primary" @click="openDialog('create')">发布新考核</el-button>
      </div>
  
      <el-table :data="displayedList" border stripe style="width: 100%; margin-top: 20px" v-loading="loading">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="title" label="考核标题" show-overflow-tooltip />
        
        <el-table-column label="时间范围" width="260">
          <template #default="{ row }">
            <div style="font-size: 12px; color: #666;">
              <div>{{ formatDate(row.start_time) }}</div>
              <div style="text-align: center; line-height: 1.2;">↓</div>
              <div>{{ formatDate(row.end_time) }}</div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="所属平台" width="160" align="center">
          <template #default="{ row }">
            <el-tag effect="plain" type="info" v-if="getPlatformInfo(row.question_bank_id)">
               {{ getPlatformInfo(row.question_bank_id)?.name }}
            </el-tag>
            <span v-else style="color: #ccc;">未知</span>
          </template>
        </el-table-column>
  
        <el-table-column prop="question_bank_id" label="关联题库ID" width="100" align="center" />
        
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row)" size="small">{{ getStatusText(row) }}</el-tag>
          </template>
        </el-table-column>
  
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="success" @click="viewResults(row.id)">查看成绩</el-button>
            <!-- 新增编辑按钮 -->
            <el-button size="small" type="primary" @click="openDialog('edit', row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
  
      <!-- 弹窗 -->
      <el-dialog v-model="dialogVisible" :title="dialogType === 'create' ? '发布新考核' : '编辑考核'" width="550px">
        <el-form :model="form" label-width="100px">
          <el-form-item label="考核标题">
            <el-input v-model="form.title" placeholder="例如：2025第一季度安全考核" />
          </el-form-item>
  
          <el-form-item label="所属平台">
            <el-select 
              v-model="createPlatformId" 
              placeholder="请先选择平台" 
              style="width: 100%" 
              @change="handleCreatePlatformChange"
              :disabled="dialogType === 'edit'" 
            >
              <!-- 编辑模式下暂不支持跨平台修改题库，避免逻辑过于复杂，如下拉框数据源问题 -->
              <el-option v-for="p in platformList" :key="p.id" :label="p.name" :value="p.id" />
            </el-select>
            <div v-if="dialogType === 'edit'" style="font-size: 12px; color: #999;">编辑模式下暂不支持修改所属平台</div>
          </el-form-item>
  
          <el-form-item label="选择题库">
            <el-select 
              v-model="form.question_bank_id" 
              placeholder="请选择该平台下的题库" 
              style="width: 100%"
              :disabled="!createPlatformId"
              no-data-text="该平台下暂无题库"
            >
              <el-option v-for="b in currentBankList" :key="b.id" :label="b.name" :value="b.id" />
            </el-select>
          </el-form-item>
  
          <el-form-item label="有效时间">
            <el-date-picker
              v-model="dateRange"
              type="datetimerange"
              range-separator="至"
              start-placeholder="开始"
              end-placeholder="结束"
              value-format="YYYY-MM-DDTHH:mm:ss"
              style="width: 100%"
            />
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
  import type { Assessment, AssessmentCreate, Platform, QuestionBank } from '@/types/api';
  import { ElMessage, ElMessageBox } from 'element-plus';
  
  const router = useRouter();
  
  // 数据源
  const loading = ref(false);
  const allAssessments = ref<Assessment[]>([]);
  const displayedList = ref<Assessment[]>([]);
  const platformList = ref<Platform[]>([]);
  const currentBankList = ref<QuestionBank[]>([]);
  
  // 映射表
  const bankToPlatformMap = ref<Record<number, Platform>>({});
  
  // 状态
  const filterPlatformId = ref<number | null>(null);
  const createPlatformId = ref<number | null>(null);
  const dialogVisible = ref(false);
  const dialogType = ref<'create' | 'edit'>('create');
  const editingId = ref<number>(0); // 记录正在编辑的ID
  
  const dateRange = ref<[string, string] | null>(null);
  const form = ref<Omit<AssessmentCreate, 'start_time' | 'end_time'>>({
    title: '',
    question_bank_id: undefined as unknown as number
  });
  
  // --- 初始化 ---
  const initData = async () => {
    loading.value = true;
    try {
      const [assessRes, platRes] = await Promise.all([
        request.get<any, Assessment[]>('/assessments/'),
        request.get<any, Platform[]>('/platforms/')
      ]);
      
      allAssessments.value = assessRes || [];
      platformList.value = platRes || [];
      displayedList.value = allAssessments.value;
  
      const map: Record<number, Platform> = {};
      await Promise.all(platformList.value.map(async (p) => {
        try {
          const banks = await request.get<any, QuestionBank[]>(`/platforms/${p.id}/question-banks/`);
          if (banks && banks.length > 0) {
            banks.forEach(b => { map[b.id] = p; });
          }
        } catch (err) {}
      }));
      bankToPlatformMap.value = map;
    } catch (e) {
      console.error(e);
      ElMessage.error('数据加载失败');
    } finally {
      loading.value = false;
    }
  };
  
  const getPlatformInfo = (bankId: number) => bankToPlatformMap.value[bankId];
  
  const handleFilterChange = async (val: number | null) => {
    if (!val) {
      displayedList.value = allAssessments.value;
      return;
    }
    displayedList.value = allAssessments.value.filter(item => {
      const p = bankToPlatformMap.value[item.question_bank_id];
      return p && p.id === val;
    });
  };
  
  // --- 创建/编辑 逻辑 ---
  const openDialog = async (type: 'create' | 'edit', row?: Assessment) => {
    dialogType.value = type;
    dialogVisible.value = true;
  
    if (type === 'edit' && row) {
      // 编辑模式：回显数据
      editingId.value = row.id;
      form.value.title = row.title;
      form.value.question_bank_id = row.question_bank_id;
      dateRange.value = [row.start_time, row.end_time];
  
      // 关键：反查平台ID，并加载该平台的题库列表，以便回显题库名称
      const platform = bankToPlatformMap.value[row.question_bank_id];
      if (platform) {
        createPlatformId.value = platform.id;
        // 加载题库列表
        const res = await request.get<any, QuestionBank[]>(`/platforms/${platform.id}/question-banks/`);
        currentBankList.value = res || [];
      } else {
        createPlatformId.value = null;
        currentBankList.value = [];
      }
  
    } else {
      // 新建模式
      form.value = { title: '', question_bank_id: undefined as unknown as number };
      createPlatformId.value = null;
      currentBankList.value = [];
      dateRange.value = null;
    }
  };
  
  const handleCreatePlatformChange = async (val: number) => {
    form.value.question_bank_id = undefined as unknown as number;
    const res = await request.get<any, QuestionBank[]>(`/platforms/${val}/question-banks/`);
    currentBankList.value = res || [];
  };
  
  const handleSubmit = async () => {
    if (!dateRange.value) return ElMessage.warning('请选择考核时间');
    if (!form.value.question_bank_id) return ElMessage.warning('请选择一个题库');
  
    const payload = {
      ...form.value,
      start_time: dateRange.value[0],
      end_time: dateRange.value[1]
    };
  
    try {
      if (dialogType.value === 'create') {
        await request.post('/assessments/', payload);
        ElMessage.success('发布成功');
      } else {
        await request.put(`/assessments/${editingId.value}`, payload);
        ElMessage.success('更新成功');
      }
      dialogVisible.value = false;
      await initData(); 
    } catch (e) { console.error(e); }
  };
  
  const handleDelete = async (id: number) => {
    try {
      await ElMessageBox.confirm('确定删除此考核吗？', '警告', { type: 'warning' });
      await request.delete(`/assessments/${id}`);
      ElMessage.success('删除成功');
      await initData();
    } catch (e) {}
  };
  
  const viewResults = (id: number) => router.push({ name: 'SessionList', query: { assessmentId: id } });
  
  const formatDate = (isoStr: string) => {
    if (!isoStr) return '-';
    const d = new Date(isoStr);
    return `${d.getFullYear()}-${(d.getMonth()+1).toString().padStart(2,'0')}-${d.getDate().toString().padStart(2,'0')} ${d.getHours().toString().padStart(2,'0')}:${d.getMinutes().toString().padStart(2,'0')}`;
  };
  
  const getStatus = (row: Assessment) => {
    const now = new Date().getTime();
    const start = new Date(row.start_time).getTime();
    const end = new Date(row.end_time).getTime();
    if (now < start) return 'not_started';
    if (now > end) return 'ended';
    return 'active';
  };
  const getStatusText = (row: Assessment) => ({ not_started: '未开始', active: '进行中', ended: '已结束' }[getStatus(row)]);
  const getStatusType = (row: Assessment) => ({ not_started: 'info', active: 'success', ended: 'danger' }[getStatus(row)]);
  
  onMounted(initData);
  </script>
  
  <style scoped>
  .header { display: flex; justify-content: space-between; align-items: center; }
  .left-panel { display: flex; align-items: center; }
  </style>