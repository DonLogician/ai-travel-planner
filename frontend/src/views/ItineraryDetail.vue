<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useItineraryStore } from '../stores/itinerary';
import { itineraryService } from '../services/itinerary';

const route = useRoute();
const router = useRouter();
const itineraryStore = useItineraryStore();

const budgetStatus = ref(null);

onMounted(async () => {
  const id = route.params.id;
  if (id && id !== 'new') {
    await itineraryStore.fetchItinerary(id);
    fetchBudgetStatus(id);
  }
});

const fetchBudgetStatus = async (id) => {
  try {
    budgetStatus.value = await itineraryService.getBudgetStatus(id);
  } catch (error) {
    console.error('Error fetching budget status:', error);
  }
};

const itinerary = computed(() => itineraryStore.currentItinerary);

const formatDate = (dateString) => {
  if (!dateString) return '';
  return new Date(dateString).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
};

const formatTime = (timeString) => {
  if (!timeString) return '';
  return timeString;
};
</script>

<template>
  <div class="container">
    <div v-if="itineraryStore.loading" class="loading">
      <p>行程加载中...</p>
    </div>

    <div v-else-if="itinerary" class="itinerary-detail">
      <div class="header">
        <div>
          <h1>{{ itinerary.destination }}</h1>
          <p class="dates">
            {{ formatDate(itinerary.start_date) || '日期待定' }} -
            {{ formatDate(itinerary.end_date) || '日期待定' }}
          </p>
        </div>
        <router-link to="/itineraries" class="btn btn-secondary">返回列表</router-link>
      </div>

      <div class="budget-overview card">
        <h2>预算总览</h2>
        <div class="budget-stats">
          <div class="stat">
            <span class="label">计划预算</span>
            <span class="value">¥{{ itinerary.budget?.toLocaleString() }}</span>
          </div>
          <div class="stat">
            <span class="label">预估花费</span>
            <span class="value">¥{{ itinerary.total_estimated_cost?.toLocaleString() }}</span>
          </div>
          <div v-if="budgetStatus" class="stat">
            <span class="label">实际支出</span>
            <span class="value">¥{{ budgetStatus.actual_spent?.toLocaleString() }}</span>
          </div>
          <div v-if="budgetStatus" class="stat">
            <span class="label">剩余预算</span>
            <span class="value" :class="{ negative: budgetStatus.remaining < 0 }">
              ¥{{ budgetStatus.remaining?.toLocaleString() }}
            </span>
          </div>
        </div>
      </div>

      <div class="recommendations card" v-if="itinerary.recommendations">
        <h2>💡 行程建议</h2>
        <p>{{ itinerary.recommendations }}</p>
      </div>

      <div class="daily-itinerary">
        <h2>每日安排</h2>
        <div
          v-for="day in itinerary.daily_itinerary"
          :key="day.day"
          class="day-card card"
        >
          <div class="day-header">
            <h3>第 {{ day.day }} 天 · {{ formatDate(day.date) || '日期待定' }}</h3>
            <span class="day-cost">¥{{ day.total_estimated_cost?.toLocaleString() }}</span>
          </div>

          <div class="activities">
            <div
              v-for="(activity, index) in day.activities"
              :key="index"
              class="activity"
            >
              <div class="activity-time">{{ formatTime(activity.time) }}</div>
              <div class="activity-content">
                <h4>{{ activity.activity }}</h4>
                <p class="location">📍 {{ activity.location }}</p>
                <p v-if="activity.notes" class="notes">{{ activity.notes }}</p>
                <p v-if="activity.estimated_cost" class="cost">
                  💰 ¥{{ activity.estimated_cost?.toLocaleString() }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="error">
      <p>未找到行程</p>
      <router-link to="/itineraries" class="btn btn-primary">返回行程列表</router-link>
    </div>
  </div>
</template>

<style scoped>
.itinerary-detail {
  max-width: 900px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
}

.header h1 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.dates {
  color: #6c757d;
  font-size: 1.1rem;
}

.budget-overview h2,
.recommendations h2,
.daily-itinerary h2 {
  color: #667eea;
  margin-bottom: 1.5rem;
}

.budget-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1.5rem;
}

.stat {
  display: flex;
  flex-direction: column;
}

.stat .label {
  color: #6c757d;
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}

.stat .value {
  font-size: 1.5rem;
  font-weight: bold;
  color: #2c3e50;
}

.stat .value.negative {
  color: #dc3545;
}

.recommendations {
  margin-bottom: 2rem;
}

.recommendations p {
  line-height: 1.8;
  color: #495057;
}

.day-card {
  margin-bottom: 1.5rem;
}

.day-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 1rem;
  margin-bottom: 1rem;
  border-bottom: 2px solid #f0f0f0;
}

.day-header h3 {
  color: #2c3e50;
  margin: 0;
}

.day-cost {
  font-size: 1.25rem;
  font-weight: bold;
  color: #667eea;
}

.activities {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.activity {
  display: grid;
  grid-template-columns: 80px 1fr;
  gap: 1rem;
}

.activity-time {
  font-weight: bold;
  color: #667eea;
  font-size: 1.1rem;
}

.activity-content h4 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.activity-content p {
  margin-bottom: 0.25rem;
  color: #6c757d;
}

.location {
  font-size: 0.95rem;
}

.notes {
  font-style: italic;
  font-size: 0.9rem;
}

.cost {
  font-weight: bold;
  color: #28a745;
}
</style>
