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
      <el-button type="primary" @click="openCreateDialog">发布新考核</el-button>
    </div>

    <el-table :data="displayedList" border stripe style="width: 100%; margin-top: 20px" v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="title" label="考核标题" show-overflow-tooltip />
      
      <el-table-column label="时间范围 (本地时间)" width="260">
        <template #default="{ row }">
          <div style="font-size: 12px; color: #666;">
            <!-- 这里的 formatDate 会把 UTC 转为本地显示 -->
            <div>起: {{ formatDate(row.start_time) }}</div>
            <div style="text-align: center; line-height: 1.2;">↓</div>
            <div>止: {{ formatDate(row.end_time) }}</div>
          </div>
        </template>
      </el-table-column>
      
      <el-table-column label="所属平台" width="200" align="center">
        <template #default="{ row }">
          <el-tag effect="plain" type="info" v-if="getPlatformInfo(row.question_bank_id)">
             {{ getPlatformInfo(row.question_bank_id)?.name }} 
             <span style="font-weight: bold; margin-left: 5px;">/ ID: {{ getPlatformInfo(row.question_bank_id)?.id }}</span>
          </el-tag>
          <span v-else style="color: #ccc;">未知/已删除</span>
        </template>
      </el-table-column>

      <el-table-column prop="question_bank_id" label="关联题库ID" width="100" align="center" />
      
      <el-table-column label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row)" size="small">{{ getStatusText(row) }}</el-tag>
        </template>
      </el-table-column>

      <el-table-column label="操作" width="260" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="success" @click="viewResults(row.id)">查看成绩</el-button>
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
            no-data-text="暂无平台，请先去创建"
          >
            <el-option v-for="p in platformList" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
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
          <!-- 核心：value-format 指定为这种格式，后端校验器会将其识别为 Beijing Time 并转 UTC -->
          <el-date-picker
            v-model="dateRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            value-format="YYYY-MM-DD HH:mm:ss" 
            style="width: 100%"
          />
          <div style="font-size: 12px; color: #999;">请选择北京时间，系统会自动处理时区。</div>
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

const loading = ref(false);
const allAssessments = ref<Assessment[]>([]);
const displayedList = ref<Assessment[]>([]);
const platformList = ref<Platform[]>([]);
const currentBankList = ref<QuestionBank[]>([]);
const bankToPlatformMap = ref<Record<number, Platform>>({});

const filterPlatformId = ref<number | null>(null);
const createPlatformId = ref<number | null>(null);
const dialogVisible = ref(false);
const dialogType = ref<'create' | 'edit'>('create');
const editingId = ref<number>(0);

const dateRange = ref<[string, string] | null>(null);
const form = ref<Omit<AssessmentCreate, 'start_time' | 'end_time'>>({
  title: '',
  question_bank_id: undefined as unknown as number
});

// --- 工具函数：UTC 转 本地时间字符串 (用于编辑回显) ---
// 输入: "2025-11-20T10:00:00" (UTC)
// 输出: "2025-11-20 18:00:00" (Local String)
const utcToLocalString = (utcStr: string) => {
  if (!utcStr) return '';
  const date = new Date(utcStr); // 浏览器会自动将 UTC 转换为本地 Date 对象
  const year = date.getFullYear();
  const month = (date.getMonth() + 1).toString().padStart(2, '0');
  const day = date.getDate().toString().padStart(2, '0');
  const hours = date.getHours().toString().padStart(2, '0');
  const minutes = date.getMinutes().toString().padStart(2, '0');
  const seconds = date.getSeconds().toString().padStart(2, '0');
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
};

// --- 工具函数：列表展示格式化 ---
const formatDate = (isoStr: string) => {
  if (!isoStr) return '-';
  // new Date() 会自动处理时区
  return isoStr.replace('T', ' ');
};

// --- 初始化 ---
const initData = async () => {
  loading.value = true;
  try {
    const results = await Promise.allSettled([
      request.get<any, Assessment[]>('/assessments/'),
      request.get<any, Platform[]>('/platforms/')
    ]);

    if (results[0].status === 'fulfilled') {
      allAssessments.value = results[0].value || [];
      displayedList.value = allAssessments.value;
    }
    if (results[1].status === 'fulfilled') {
      platformList.value = results[1].value || [];
    }

    if (platformList.value.length > 0) {
      const map: Record<number, Platform> = {};
      for (const p of platformList.value) {
        try {
          const banks = await request.get<any, QuestionBank[]>(`/platforms/${p.id}/question-banks/`);
          if (banks && banks.length > 0) {
            banks.forEach(b => { map[b.id] = p; });
          }
        } catch (err) {}
      }
      bankToPlatformMap.value = map;
    }
  } catch (e) { console.error(e); } 
  finally { loading.value = false; }
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

const openCreateDialog = () => openDialog('create');

const openDialog = async (type: 'create' | 'edit', row?: Assessment) => {
  dialogType.value = type;
  
  if (type === 'edit' && row) {
    editingId.value = row.id;
    form.value.title = row.title;
    form.value.question_bank_id = row.question_bank_id;
    
    // --- 核心修改：直接回显，不要转时区 ---
    // 因为后端现在存的就是你选的时间，直接用即可
    // Element Plus 会自动识别 "2025-11-22T10:00:00" 这种格式
    if (row.start_time && row.end_time) {
        dateRange.value = [row.start_time, row.end_time];
    } else {
        dateRange.value = null;
    }

    const platform = bankToPlatformMap.value[row.question_bank_id];
    if (platform) {
      createPlatformId.value = platform.id;
      try {
        const res = await request.get<any, QuestionBank[]>(`/platforms/${platform.id}/question-banks/`);
        currentBankList.value = res || [];
      } catch(e) {}
    } else {
      createPlatformId.value = null;
      currentBankList.value = [];
    }

  } else {
    form.value = { title: '', question_bank_id: undefined as unknown as number };
    createPlatformId.value = null;
    currentBankList.value = [];
    dateRange.value = null;
  }
  
  dialogVisible.value = true;
};

const handleCreatePlatformChange = async (val: number) => {
  form.value.question_bank_id = undefined as unknown as number;
  try {
    const res = await request.get<any, QuestionBank[]>(`/platforms/${val}/question-banks/`);
    currentBankList.value = res || [];
  } catch(e) {}
};

const handleSubmit = async () => {
  if (!dateRange.value) return ElMessage.warning('请选择考核时间');
  if (!form.value.question_bank_id) return ElMessage.warning('请选择一个题库');

  // 直接发送 dateRange 里的字符串（例如 "2025-11-22 18:00:00"）
  // 后端的 validator 会把它视为北京时间，并自动转换为 UTC 存入数据库
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