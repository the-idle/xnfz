<template>
  <div class="page-container">
    <div class="header">
      <div class="left-panel">
        <h2>考核场次管理</h2>
        <!-- 增加空值判断，防止 platformList 为空时报错 -->
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
      <!-- 这里的点击只是打开弹窗，不发请求 -->
      <el-button type="primary" @click="openCreateDialog">发布新考核</el-button>
    </div>

    <!-- 表格区域 -->
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
      
      <el-table-column label="所属平台" width="200" align="center">
        <template #default="{ row }">
          <!-- 安全获取平台信息 -->
          <el-tag effect="plain" type="info" v-if="getPlatformInfo(row.question_bank_id)">
             {{ getPlatformInfo(row.question_bank_id)?.name }} 
             <span style="font-weight: bold; margin-left: 5px;">(ID: {{ getPlatformInfo(row.question_bank_id)?.id }})</span>
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
          <div v-if="platformList.length === 0" style="color: #E6A23C; font-size: 12px;">
            提示：当前没有任何平台，无法发布考核。请先去【平台管理】创建。
          </div>
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
const editingId = ref<number>(0);

const dateRange = ref<[string, string] | null>(null);
const form = ref<Omit<AssessmentCreate, 'start_time' | 'end_time'>>({
  title: '',
  question_bank_id: undefined as unknown as number
});

// --- 初始化 ---
const initData = async () => {
  loading.value = true;
  try {
    // 1. 获取考核列表和平台列表
    // 这里使用 Promise.allSettled 防止其中一个接口失败导致整个页面卡死
    const results = await Promise.allSettled([
      request.get<any, Assessment[]>('/assessments/'),
      request.get<any, Platform[]>('/platforms/')
    ]);

    // 处理 Assessment 结果
    if (results[0].status === 'fulfilled') {
      allAssessments.value = results[0].value || [];
      displayedList.value = allAssessments.value;
    } else {
      console.error("加载考核列表失败", results[0].reason);
      allAssessments.value = [];
    }

    // 处理 Platform 结果
    if (results[1].status === 'fulfilled') {
      platformList.value = results[1].value || [];
    } else {
      console.error("加载平台列表失败", results[1].reason);
      platformList.value = [];
    }

    // 2. 构建映射表 (如果平台列表为空，则不执行)
    if (platformList.value.length > 0) {
      const map: Record<number, Platform> = {};
      // 逐个获取题库，构建映射
      for (const p of platformList.value) {
        try {
          const banks = await request.get<any, QuestionBank[]>(`/platforms/${p.id}/question-banks/`);
          if (banks && banks.length > 0) {
            banks.forEach(b => { map[b.id] = p; });
          }
        } catch (err) {
          // 忽略单个平台获取失败，不影响整体
        }
      }
      bankToPlatformMap.value = map;
    }

  } catch (e) {
    console.error(e);
    ElMessage.error('初始化数据异常');
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

// --- 弹窗逻辑：纯前端操作，不会触发网络请求 ---
const openCreateDialog = () => {
  openDialog('create');
};

const openDialog = async (type: 'create' | 'edit', row?: Assessment) => {
  dialogType.value = type;
  
  if (type === 'edit' && row) {
    editingId.value = row.id;
    form.value.title = row.title;
    form.value.question_bank_id = row.question_bank_id;
    dateRange.value = [row.start_time, row.end_time];

    // 回显平台和题库
    const platform = bankToPlatformMap.value[row.question_bank_id];
    if (platform) {
      createPlatformId.value = platform.id;
      try {
        const res = await request.get<any, QuestionBank[]>(`/platforms/${platform.id}/question-banks/`);
        currentBankList.value = res || [];
      } catch(e) { console.error(e) }
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
  
  // 最后显示弹窗
  dialogVisible.value = true;
};

const handleCreatePlatformChange = async (val: number) => {
  form.value.question_bank_id = undefined as unknown as number;
  try {
    const res = await request.get<any, QuestionBank[]>(`/platforms/${val}/question-banks/`);
    currentBankList.value = res || [];
  } catch(e) { console.error(e) }
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