<script setup>
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useItineraryStore } from '../stores/itinerary';
import VoiceRecorder from '../components/VoiceRecorder.vue';
import ItineraryMap from '../components/ItineraryMap.vue';

const router = useRouter();
const itineraryStore = useItineraryStore();

const form = ref({
  destination: '',
  start_date: '',
  end_date: '',
  budget: '',
  preferences: [],
  additional_notes: '',
});

const preferenceOptions = [
  { value: 'cultural', label: '文化探索' },
  { value: 'adventure', label: '冒险体验' },
  { value: 'relaxation', label: '轻松休闲' },
  { value: 'food', label: '特色美食' },
  { value: 'shopping', label: '购物血拼' },
  { value: 'nature', label: '自然风光' },
  { value: 'nightlife', label: '夜生活' },
];

const loading = ref(false);
const error = ref(null);
const aiLoading = ref(false);
const aiError = ref(null);
const aiResult = ref(null);

const togglePreference = (value) => {
  const index = form.value.preferences.indexOf(value);
  if (index > -1) {
    form.value.preferences.splice(index, 1);
  } else {
    form.value.preferences.push(value);
  }
};

const handleSubmit = async () => {
  loading.value = true;
  error.value = null;

  try {
    const itinerary = await itineraryStore.createItinerary(form.value);
    router.push(`/itineraries/${itinerary.id || 'new'}`);
  } catch (err) {
    error.value = err?.response?.data?.detail || err.message || '创建行程失败，请稍后重试。';
  } finally {
    loading.value = false;
  }
};

const handleVoiceSubmit = async (text) => {
  if (!text) {
    return;
  }

  aiLoading.value = true;
  aiError.value = null;

  try {
    const result = await itineraryStore.createItineraryFromText({
      text,
      language: 'zh',
    });
    aiResult.value = result;
  } catch (err) {
    aiError.value = err?.response?.data?.detail || err.message || '生成行程失败，请稍后重试。';
  } finally {
    aiLoading.value = false;
  }
};

const clearAiResult = () => {
  aiResult.value = null;
};

const formatDate = (dateString) => {
  if (!dateString) return '日期待定';
  return new Date(dateString).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

const formatCurrency = (value) => {
  const numeric = Number(value);
  if (Number.isNaN(numeric)) {
    return '—';
  }
  return numeric.toLocaleString('zh-CN', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  });
};

const mapDestination = computed(
  () => aiResult.value?.itinerary?.destination || form.value.destination || ''
);

const mapDailyItinerary = computed(
  () => aiResult.value?.itinerary?.daily_itinerary || []
);
</script>

<template>
  <div class="container">
    <div class="create-itinerary">
      <div class="create-itinerary__layout">
        <div class="create-itinerary__content">
          <h1>创建专属行程</h1>
          <p class="subtitle">
            填写旅行需求或直接语音描述，AI 会为你生成个性化的每日行程与预算建议
          </p>

          <section class="ai-section card">
            <div class="section-header">
              <div>
                <h2>语音 / 文本快速创建</h2>
                <p>按下录音或直接输入文字，让 AI 帮你一键生成行程计划。</p>
              </div>
            </div>

            <VoiceRecorder :disabled="aiLoading" @submit-text="handleVoiceSubmit" />

            <p v-if="aiError" class="error">{{ aiError }}</p>
            <p v-if="aiLoading" class="loading">AI 正在生成行程，请稍候...</p>

            <div v-if="aiResult?.itinerary" class="ai-result">
              <div class="ai-result__header">
                <div>
                  <h3>{{ aiResult.itinerary.destination }}</h3>
                  <p class="ai-result__dates">
                    {{ formatDate(aiResult.itinerary.start_date) }} -
                    {{ formatDate(aiResult.itinerary.end_date) }}
                  </p>
                </div>
                <div class="ai-result__budget">
                  <p>计划预算</p>
                  <strong>¥{{ formatCurrency(aiResult.itinerary.budget) }}</strong>
                </div>
              </div>

              <div class="ai-result__summary">
                <div>
                  <span>预估花费</span>
                  <strong>¥{{ formatCurrency(aiResult.itinerary.total_estimated_cost) }}</strong>
                </div>
                <div>
                  <span>行程天数</span>
                  <strong>{{ aiResult.itinerary.daily_itinerary?.length || 0 }} 天</strong>
                </div>
              </div>

              <div v-if="aiResult.itinerary.recommendations" class="ai-result__recommendations">
                <h4>行程建议</h4>
                <p>{{ aiResult.itinerary.recommendations }}</p>
              </div>

              <div class="ai-result__days">
                <div
                  v-for="day in aiResult.itinerary.daily_itinerary"
                  :key="day.day"
                  class="ai-result__day"
                >
                  <div class="ai-result__day-header">
                    <h4>第 {{ day.day }} 天 · {{ formatDate(day.date) }}</h4>
                    <span>预计 ¥{{ formatCurrency(day.total_estimated_cost) }}</span>
                  </div>
                  <ul class="ai-result__activities">
                    <li v-for="(activity, index) in day.activities" :key="index">
                      <span class="time">{{ activity.time || '时间待定' }}</span>
                      <div class="content">
                        <p class="title">{{ activity.activity }}</p>
                        <p class="meta">📍 {{ activity.location }}</p>
                        <p v-if="activity.notes" class="notes">{{ activity.notes }}</p>
                        <p v-if="activity.estimated_cost" class="cost">
                          约 ¥{{ formatCurrency(activity.estimated_cost) }}
                        </p>
                      </div>
                    </li>
                  </ul>
                </div>
              </div>

              <details v-if="aiResult.prompt" class="ai-result__prompt">
                <summary>查看生成 Prompt</summary>
                <pre>{{ aiResult.prompt }}</pre>
              </details>

              <div class="ai-result__actions">
                <router-link
                  v-if="aiResult.itinerary.id"
                  class="btn btn-primary"
                  :to="`/itineraries/${aiResult.itinerary.id}`"
                >
                  查看完整行程
                </router-link>
                <button type="button" class="btn btn-secondary" @click="clearAiResult">
                  清除结果
                </button>
              </div>
            </div>
          </section>

          <div v-if="error" class="error">{{ error }}</div>

          <form @submit.prevent="handleSubmit" class="card manual-form">
            <div class="form-group">
              <label for="destination">目的地 *</label>
              <input
                id="destination"
                v-model="form.destination"
                type="text"
                placeholder="例如：北京、巴黎、东京"
                required
              />
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="start_date">出发日期 *</label>
                <input id="start_date" v-model="form.start_date" type="date" required />
              </div>

              <div class="form-group">
                <label for="end_date">返回日期 *</label>
                <input id="end_date" v-model="form.end_date" type="date" required />
              </div>
            </div>

            <div class="form-group">
              <label for="budget">预算 (¥) *</label>
              <input
                id="budget"
                v-model.number="form.budget"
                type="number"
                min="0"
                step="0.01"
                placeholder="例如：5000"
                required
              />
            </div>

            <div class="form-group">
              <label>旅行偏好</label>
              <div class="preference-chips">
                <button
                  v-for="option in preferenceOptions"
                  :key="option.value"
                  type="button"
                  class="chip"
                  :class="{ active: form.preferences.includes(option.value) }"
                  @click="togglePreference(option.value)"
                >
                  {{ option.label }}
                </button>
              </div>
            </div>

            <div class="form-group">
              <label for="additional_notes">补充说明</label>
              <textarea
                id="additional_notes"
                v-model="form.additional_notes"
                placeholder="如有特殊需求或更多偏好，请在此补充..."
              ></textarea>
            </div>

            <div class="form-actions">
              <button type="submit" class="btn btn-primary" :disabled="loading">
                {{ loading ? '正在生成行程...' : '生成行程' }}
              </button>
              <router-link to="/itineraries" class="btn btn-secondary">取消</router-link>
            </div>
          </form>
        </div>
        <aside class="create-itinerary__map">
          <ItineraryMap
            :destination="mapDestination"
            :daily-itinerary="mapDailyItinerary"
            min-height="640px"
          />
        </aside>
      </div>
    </div>
  </div>
</template>

<style scoped>
.create-itinerary {
  max-width: 1240px;
  margin: 0 auto;
  padding: 0 0 2rem;
}

.create-itinerary__layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(320px, 420px);
  gap: 2.5rem;
  align-items: flex-start;
}

.create-itinerary__content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.create-itinerary__map {
  position: sticky;
  top: 1.5rem;
  height: fit-content;
  display: block;
}

.create-itinerary h1 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #6c757d;
  margin-bottom: 0;
}

.ai-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.section-header h2 {
  margin: 0;
  color: #2c3e50;
}

.section-header p {
  margin: 0.5rem 0 0;
  color: #6c757d;
}

.loading {
  color: #4c51bf;
  font-weight: 600;
}

.ai-result {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  background: #f9fafc;
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid rgba(102, 126, 234, 0.2);
}

.ai-result__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.ai-result__header h3 {
  margin: 0;
  color: #4c51bf;
}

.ai-result__dates {
  margin: 0.35rem 0 0;
  color: #6c757d;
}

.ai-result__budget {
  text-align: right;
  color: #2c3e50;
}

.ai-result__budget strong {
  display: block;
  font-size: 1.5rem;
}

.ai-result__summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 1rem;
}

.ai-result__summary span {
  color: #6c757d;
}

.ai-result__summary strong {
  font-size: 1.2rem;
  color: #2c3e50;
}

.ai-result__recommendations {
  background: white;
  border-radius: 10px;
  padding: 1rem 1.25rem;
  border-left: 4px solid #667eea;
}

.ai-result__recommendations h4 {
  margin: 0 0 0.5rem;
  color: #2c3e50;
}

.ai-result__days {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.ai-result__day {
  background: white;
  border-radius: 10px;
  padding: 1rem;
  border: 1px solid rgba(102, 126, 234, 0.15);
}

.ai-result__day-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  color: #2c3e50;
}

.ai-result__day-header span {
  color: #4c51bf;
  font-weight: 600;
}

.ai-result__activities {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.ai-result__activities li {
  display: grid;
  grid-template-columns: 90px 1fr;
  gap: 0.75rem;
  align-items: flex-start;
}

.ai-result__activities .time {
  font-weight: 600;
  color: #4c51bf;
}

.ai-result__activities .content {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.ai-result__activities .title {
  margin: 0;
  color: #2c3e50;
}

.ai-result__activities .meta {
  margin: 0;
  color: #6c757d;
  font-size: 0.95rem;
}

.ai-result__activities .notes {
  margin: 0;
  font-size: 0.9rem;
  color: #495057;
}

.ai-result__activities .cost {
  margin: 0;
  color: #16a34a;
  font-weight: 600;
}

.ai-result__prompt {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  border: 1px dashed rgba(102, 126, 234, 0.4);
}

.ai-result__prompt summary {
  cursor: pointer;
  font-weight: 600;
  color: #4c51bf;
}

.ai-result__prompt pre {
  white-space: pre-wrap;
  word-break: break-word;
  margin: 0.75rem 0 0;
  font-size: 0.9rem;
  color: #1f2937;
  background: #f8fafc;
  padding: 0.75rem;
  border-radius: 6px;
}

.ai-result__actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

.manual-form {
  margin-bottom: 2rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.error {
  color: #e53e3e;
  background: rgba(229, 62, 62, 0.08);
  padding: 0.75rem 1rem;
  border-radius: 8px;
}

.preference-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.chip {
  padding: 0.5rem 1rem;
  border: 2px solid #667eea;
  background: white;
  color: #667eea;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s;
}

.chip:hover {
  background: #f0f0f0;
}

.chip.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 1024px) {
  .create-itinerary__layout {
    grid-template-columns: 1fr;
    gap: 2rem;
  }

  .create-itinerary__map {
    position: static;
    order: -1;
  }
}
</style>
