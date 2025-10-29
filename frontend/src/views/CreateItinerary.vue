<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useItineraryStore } from '../stores/itinerary';

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
  error.value = err.message || '创建行程失败，请稍后重试。';
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="container">
    <div class="create-itinerary">
      <h1>创建专属行程</h1>
      <p class="subtitle">
        填写旅行需求，AI 会为你生成个性化的每日行程与预算建议
      </p>

      <div v-if="error" class="error">{{ error }}</div>

      <form @submit.prevent="handleSubmit" class="card">
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
  </div>
</template>

<style scoped>
.create-itinerary {
  max-width: 800px;
  margin: 0 auto;
}

.create-itinerary h1 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #6c757d;
  margin-bottom: 2rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
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
</style>
