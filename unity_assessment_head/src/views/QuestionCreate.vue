<template>
    <div class="page-container">
      <div class="header">
        <el-page-header @back="goBack">
          <template #content>
            <span class="text-large font-600 mr-3"> {{ isEditMode ? '编辑题目' : '录入新题目' }} </span>
          </template>
        </el-page-header>
      </div>
  
      <el-card style="margin: 40px auto; max-width: 900px;" v-loading="loadingData">
        <el-form :model="qForm" label-width="100px">
          
          <el-form-item label="题目类型">
            <el-radio-group v-model="qForm.question_type" @change="handleTypeChange">
              <el-radio-button label="SINGLE_CHOICE">单选题</el-radio-button>
              <el-radio-button label="MULTIPLE_CHOICE">多选题</el-radio-button>
              <el-radio-button label="DEDUCTION_SINGLE_CHOICE">扣分单选题</el-radio-button>
            </el-radio-group>
          </el-form-item>
  
          <el-form-item label="题干内容">
            <el-input type="textarea" v-model="qForm.prompt" :rows="3" placeholder="请输入题目描述" />
          </el-form-item>
  
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="题目分值">
                <el-input-number v-model="qForm.score" :min="1" :max="100" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="场景标识">
                <el-input v-model="qForm.scene_identifier" placeholder="可选，留空则不设置" />
              </el-form-item>
            </el-col>
          </el-row>
  
          <el-form-item label="题目配图">
            <div v-if="existingImageUrl && !imageFile" style="margin-bottom: 10px;">
              <el-image 
                :src="resolveImageUrl(existingImageUrl)" 
                style="width: 100px; height: 100px; border-radius: 6px; border: 1px solid #eee;"
                fit="cover"
              />
              <div style="font-size: 12px; color: #666;">当前图片 (上传新图将覆盖)</div>
            </div>
  
            <el-upload
              action="#"
              :auto-upload="false"
              :limit="1"
              list-type="picture-card"
              :on-change="handleFileChange"
              :on-remove="handleRemoveFile"
            >
              <el-icon><Plus /></el-icon>
            </el-upload>
          </el-form-item>
  
          <el-divider content-position="left">选项配置</el-divider>
          
          <div v-for="(opt, index) in qForm.options" :key="index" class="option-row">
            <div class="opt-label">选项 {{ String.fromCharCode(65 + index) }}</div>
            
            <el-input v-model="opt.option_text" placeholder="选项内容" style="flex: 1; margin-right: 10px;" />
            
            <div class="opt-check">
              <el-switch 
                v-model="opt.is_correct" 
                active-text="正确答案" 
                inline-prompt
                style="margin-right: 10px;"
                @change="handleCorrectChange(index)"
              />
              <el-button type="danger" circle size="small" @click="removeOption(index)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
  
          <div style="margin-top: 10px; margin-left: 50px;">
            <el-button type="primary" plain @click="addOption">+ 添加选项</el-button>
          </div>
  
          <el-divider />
  
          <div style="text-align: center; margin-top: 30px;">
            <el-button size="large" @click="goBack">取消</el-button>
            <el-button type="primary" size="large" @click="submitQuestion" :loading="submitting">
              {{ isEditMode ? '保存修改' : '提交题目' }}
            </el-button>
          </div>
  
        </el-form>
      </el-card>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, onMounted, computed } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import request from '@/utils/request';
  import { ElMessage } from 'element-plus';
  import { Plus, Delete } from '@element-plus/icons-vue';
  
  const route = useRoute();
  const router = useRouter();
  const procedureId = route.params.procedureId;
  const questionId = route.params.questionId;
  
  const isEditMode = computed(() => !!questionId);
  
  const loadingData = ref(false);
  const submitting = ref(false);
  const imageFile = ref<File | null>(null);
  const existingImageUrl = ref('');
  
  // 定义选项接口
  interface Option {
    id?: number; 
    option_text: string;
    is_correct: boolean;
  }
  
  const qForm = ref({
    prompt: '',
    question_type: 'SINGLE_CHOICE',
    scene_identifier: '',
    score: 10,
    options: [
      { option_text: '', is_correct: false },
      { option_text: '', is_correct: false }
    ] as Option[]
  });
  
  const initData = async () => {
    if (isEditMode.value) {
      loadingData.value = true;
      try {
        const res: any = await request.get(`/procedures/${procedureId}/questions/${questionId}`);
        
        qForm.value.prompt = res.prompt;
        qForm.value.question_type = res.question_type ? res.question_type.toUpperCase() : 'SINGLE_CHOICE';
        qForm.value.score = res.score;
        qForm.value.scene_identifier = res.scene_identifier || ''; 
        
        if (res.options && res.options.length > 0) {
          qForm.value.options = res.options
            .map((o: any) => ({
              id: o.id, 
              option_text: o.option_text,
              is_correct: o.is_correct
            }))
            .sort((a: any, b: any) => a.id - b.id);
        }
  
        existingImageUrl.value = res.image_url || '';
      } catch (e) {
        console.error(e);
        ElMessage.error('获取题目详情失败');
      } finally {
        loadingData.value = false;
      }
    }
  };
  
  const addOption = () => {
    qForm.value.options.push({ option_text: '', is_correct: false });
  };
  
  const removeOption = (index: number) => {
    if (qForm.value.options.length <= 1) return ElMessage.warning('至少保留一个选项');
    qForm.value.options.splice(index, 1);
  };
  
  const handleCorrectChange = (changedIndex: number) => {
    const type = qForm.value.question_type;
    if ((type === 'SINGLE_CHOICE' || type === 'DEDUCTION_SINGLE_CHOICE') && qForm.value.options[changedIndex].is_correct) {
      qForm.value.options.forEach((opt, i) => {
        if (i !== changedIndex) opt.is_correct = false;
      });
    }
  };
  
  const handleTypeChange = (val: string) => {
    if (val !== 'MULTIPLE_CHOICE') {
      const hasMultiple = qForm.value.options.filter(o => o.is_correct).length > 1;
      if (hasMultiple) {
        qForm.value.options.forEach(o => o.is_correct = false);
        ElMessage.info('切换为单选类型，请重新指定正确答案');
      }
    }
  };
  
  const handleFileChange = (uploadFile: any) => {
    imageFile.value = uploadFile.raw;
  };
  
  const handleRemoveFile = () => {
    imageFile.value = null;
  };
  
  const resolveImageUrl = (url: string) => {
    if (!url) return '';
    if (url.startsWith('http')) return url;
    return `http://127.0.0.1:8000${url}`;
  };
  
  const submitQuestion = async () => {
  if (!qForm.value.prompt || !qForm.value.prompt.trim()) {
    return ElMessage.warning('请填写题干');
  }

  // 1. 先过滤出有效选项（去掉空内容的）
  const validOptions = qForm.value.options.filter(o => o.option_text && o.option_text.trim() !== '');
  
  // 2. 校验数量
  if (qForm.value.question_type === 'MULTIPLE_CHOICE') {
    if (validOptions.length < 2) {
      return ElMessage.warning('多选题至少需要两个有效选项');
    }
  } else {
    if (validOptions.length < 1) {
      return ElMessage.warning('至少填写一个有效选项');
    }
  }
  
  // 3. 校验答案 (注意：要在有效选项里找正确答案)
  const hasCorrect = validOptions.some(o => o.is_correct);
  if (!hasCorrect) return ElMessage.warning('请至少设置一个正确答案');

  submitting.value = true;
  try {
    const formData = new FormData();
    const finalIdentifier = qForm.value.scene_identifier ? qForm.value.scene_identifier.trim() : '';

    const payload = {
      prompt: qForm.value.prompt,
      question_type: qForm.value.question_type,
      scene_identifier: finalIdentifier, 
      score: qForm.value.score,
      // --- 核心修复：只发送过滤后的 validOptions，而不是原始的 qForm.value.options ---
      options: validOptions 
    };
    
    formData.append('question_data', JSON.stringify(payload));

    if (imageFile.value) {
      formData.append('image_file', imageFile.value);
    }

    if (isEditMode.value) {
      await request.put(`/procedures/${procedureId}/questions/${questionId}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      ElMessage.success('修改保存成功');
    } else {
      await request.post(`/procedures/${procedureId}/questions/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      ElMessage.success('创建成功');
    }

    goBack();
  } catch (e: any) {
    console.error(e);
    const msg = e.response?.data?.detail || '提交失败';
    // 优化报错显示：如果是数组（字段验证错误），转字符串
    ElMessage.error(typeof msg === 'string' ? msg : JSON.stringify(msg));
  } finally {
    submitting.value = false;
  }
};
  
  const goBack = () => {
    router.back();
  };
  
  onMounted(initData);
  </script>
  
  <style scoped>
  .option-row { display: flex; align-items: center; margin-bottom: 15px; background: #f8f9fa; padding: 10px; border-radius: 4px; }
  .opt-label { width: 60px; font-weight: bold; text-align: center; color: #666; }
  .opt-check { display: flex; align-items: center; }
  </style>