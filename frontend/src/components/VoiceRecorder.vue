<script setup>
import { ref, computed, onBeforeUnmount } from 'vue';
import { voiceService } from '../services/voice';

const emit = defineEmits(['submit-text']);

const props = defineProps({
  language: {
    type: String,
    default: 'zh_cn',
  },
  disabled: {
    type: Boolean,
    default: false,
  },
});

const isRecording = ref(false);
const isProcessing = ref(false);
const error = ref('');
const transcript = ref('');
const fallbackText = ref('');
const chunks = [];
let mediaRecorder = null;
let mediaStream = null;

const recorderSupported = computed(() => Boolean(navigator?.mediaDevices?.getUserMedia && window?.MediaRecorder));

const toggleRecording = async () => {
  if (isRecording.value) {
    stopRecording();
    return;
  }
  await startRecording();
};

const startRecording = async () => {
  if (!recorderSupported.value || props.disabled) {
    return;
  }

  try {
    error.value = '';
    transcript.value = '';
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaStream = stream;
    mediaRecorder = new MediaRecorder(stream, {
      mimeType: 'audio/webm;codecs=opus',
    });

    mediaRecorder.ondataavailable = (event) => {
      if (event.data && event.data.size > 0) {
        chunks.push(event.data);
      }
    };

    mediaRecorder.onstop = async () => {
      const blob = new Blob(chunks.splice(0, chunks.length), { type: 'audio/webm' });
      await processAudioBlob(blob);
      cleanupStream();
    };

    mediaRecorder.start();
    isRecording.value = true;
  } catch (err) {
    error.value = err?.message || '无法访问麦克风，请检查浏览器权限设置。';
    cleanupStream();
  }
};

const stopRecording = () => {
  if (!mediaRecorder || mediaRecorder.state === 'inactive') {
    return;
  }
  mediaRecorder.stop();
  isRecording.value = false;
};

const cleanupStream = () => {
  if (mediaStream) {
    mediaStream.getTracks().forEach((track) => track.stop());
    mediaStream = null;
  }
  mediaRecorder = null;
};

const processAudioBlob = async (blob) => {
  if (!blob || !blob.size) {
    error.value = '未捕获到有效音频，请重试。';
    return;
  }

  isProcessing.value = true;
  error.value = '';

  try {
    const file = new File([blob], `voice-${Date.now()}.webm`, { type: blob.type || 'audio/webm' });
    const response = await voiceService.uploadVoice(file, props.language);
    transcript.value = response.text?.trim() || '';
    fallbackText.value = transcript.value;

    if (!transcript.value) {
      error.value = '语音识别结果为空，请重试或改用文字输入。';
    }
  } catch (err) {
    const detail = err?.response?.data?.detail || err?.message;
    error.value = detail || '语音识别失败，请稍后重试。';
  } finally {
    isProcessing.value = false;
  }
};

const submitText = () => {
  if (isProcessing.value || props.disabled) {
    return;
  }
  const text = fallbackText.value?.trim();
  if (!text) {
    error.value = '请先录音或输入旅行描述。';
    return;
  }
  error.value = '';
  emit('submit-text', text);
};

onBeforeUnmount(() => {
  cleanupStream();
});

const submitDisabled = computed(() => props.disabled || isProcessing.value);
</script>

<template>
  <div class="voice-recorder" :class="{ disabled: props.disabled }">
    <div class="voice-recorder__header">
      <h3>语音快速生成</h3>
      <p>按下录音说出旅行计划，或直接输入文字描述。</p>
    </div>

    <div class="voice-recorder__controls">
      <button
        type="button"
        class="btn btn-secondary"
        :disabled="!recorderSupported || props.disabled || isProcessing"
        @click="toggleRecording"
      >
        <span v-if="!recorderSupported">不支持录音</span>
        <span v-else-if="isRecording">停止录音</span>
        <span v-else>开始录音</span>
      </button>
      <span v-if="isRecording" class="voice-recorder__status">录音中...</span>
      <span v-else-if="isProcessing" class="voice-recorder__status">识别中...</span>
    </div>

    <div v-if="transcript" class="voice-recorder__transcript">
      <label>AI 转写结果（可修改）</label>
      <textarea
        v-model="fallbackText"
        rows="4"
        :disabled="submitDisabled"
      ></textarea>
    </div>

    <div v-else class="voice-recorder__fallback">
      <label>或直接输入旅行需求</label>
      <textarea
        v-model="fallbackText"
        rows="4"
        :placeholder="'例如：我想去日本东京玩 5 天，预算 1 万元，带孩子，喜欢美食和动漫。'"
        :disabled="submitDisabled"
      ></textarea>
    </div>

    <p v-if="error" class="voice-recorder__error">{{ error }}</p>

    <div class="voice-recorder__actions">
      <button
        type="button"
        class="btn btn-primary"
        :disabled="submitDisabled"
        @click="submitText"
      >
        使用描述生成行程
      </button>
    </div>
  </div>
</template>

<style scoped>
.voice-recorder {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.5rem;
  border-radius: 12px;
  background: white;
  box-shadow: 0 12px 32px -24px rgba(102, 126, 234, 0.65);
}

.voice-recorder.disabled {
  opacity: 0.6;
  pointer-events: none;
}

.voice-recorder__header h3 {
  margin: 0;
  color: #4c51bf;
}

.voice-recorder__header p {
  margin: 0.4rem 0 0;
  color: #6c757d;
  font-size: 0.95rem;
}

.voice-recorder__controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.voice-recorder__status {
  color: #4c51bf;
  font-weight: 600;
}

.voice-recorder__transcript label,
.voice-recorder__fallback label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #2c3e50;
}

textarea {
  width: 100%;
  border-radius: 8px;
  border: 1px solid #d1d5db;
  padding: 0.75rem;
  resize: vertical;
  min-height: 120px;
  font-size: 1rem;
}

textarea:disabled {
  background: #f8f9fa;
}

.voice-recorder__error {
  margin: 0;
  color: #e53e3e;
  font-size: 0.9rem;
}

.voice-recorder__actions {
  display: flex;
  justify-content: flex-end;
}
</style>
