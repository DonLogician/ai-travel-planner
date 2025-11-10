<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useItineraryStore } from '../stores/itinerary';
import { useExpenseStore } from '../stores/expense';
import { itineraryService } from '../services/itinerary';
import ItineraryMap from '../components/ItineraryMap.vue';

const route = useRoute();
const itineraryStore = useItineraryStore();
const expenseStore = useExpenseStore();
const budgetStatus = ref(null);

const categoryLabels = {
  accommodation: '住宿',
  food: '餐饮',
  transportation: '交通',
  activities: '活动体验',
  shopping: '购物',
  other: '其他',
};

const fetchBudgetStatus = async (id) => {
  try {
    budgetStatus.value = await itineraryService.getBudgetStatus(id);
  } catch (error) {
    console.error('Error fetching budget status:', error);
  }
};

const loadItineraryData = async (id) => {
  if (!id || id === 'new') {
    return;
  }

  try {
    await Promise.all([
      itineraryStore.fetchItinerary(id),
      expenseStore.fetchExpenses({ itinerary_id: id }),
    ]);
  } finally {
    await fetchBudgetStatus(id);
  }
};

onMounted(() => {
  loadItineraryData(route.params.id);
});

const itinerary = computed(() => itineraryStore.currentItinerary);

const structuredDays = computed(() => {
  if (!itinerary.value?.daily_itinerary) {
    return [];
  }

  return itinerary.value.daily_itinerary.map((day, index) => {
    const activities = Array.isArray(day.activities) ? day.activities : [];

    return {
      day: day.day || index + 1,
      date: day.date,
      total_estimated_cost: day.total_estimated_cost ?? 0,
      activities: activities.map((activity) => ({
        time: activity.time || '',
        activity: activity.activity || activity.title || '行程待补充',
        location: activity.location || activity.place || '地点待定',
        estimated_cost: activity.estimated_cost ?? null,
        notes: activity.notes || activity.description || '',
      })),
    };
  });
});

const budgetOverview = computed(() => {
  const planned = itinerary.value?.budget ?? 0;
  const estimated = itinerary.value?.total_estimated_cost ?? 0;
  const actual = budgetStatus.value?.actual_spent ?? null;
  const remaining = budgetStatus.value?.remaining ?? (planned ? planned - (actual ?? 0) : null);
  const spentPercentage = budgetStatus.value?.spent_percentage ?? (
    planned ? ((actual ?? 0) / planned) * 100 : 0
  );

  return {
    planned,
    estimated,
    actual,
    remaining,
    spentPercentage,
  };
});

const mapDailyItinerary = computed(() => itinerary.value?.daily_itinerary || []);

const mapDestination = computed(() => itinerary.value?.destination || '');

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

const formatCurrency = (value) => {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return '—';
  }
  return Number(value).toLocaleString('zh-CN', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  });
};

const formatAmount = (value) => {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return '0.00';
  }
  return Number(value).toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
};

const itineraryExpenses = computed(() => expenseStore.expenses || []);

const expensesLoading = computed(() => expenseStore.loading);

const expenseBreakdown = computed(() => budgetStatus.value?.expense_breakdown || {});

const getCategoryLabel = (category) => categoryLabels[category] || category;

watch(
  () => route.params.id,
  (id) => {
    loadItineraryData(id);
  }
);
</script>

<template>
  <div class="container">
    <div v-if="itineraryStore.loading" class="loading">
      <p>行程加载中...</p>
    </div>

    <div v-else-if="itinerary" class="itinerary-detail">
      <div class="itinerary-detail__layout">
        <div class="itinerary-detail__content">
          <div class="header">
            <div>
              <h1>{{ itinerary.destination || '行程详情' }}</h1>
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
                <span class="value">¥{{ formatCurrency(budgetOverview.planned) }}</span>
              </div>
              <div class="stat">
                <span class="label">预估花费</span>
                <span class="value">¥{{ formatCurrency(budgetOverview.estimated) }}</span>
              </div>
              <div class="stat">
                <span class="label">实际支出</span>
                <span class="value">¥{{ formatCurrency(budgetOverview.actual) }}</span>
              </div>
              <div class="stat">
                <span class="label">剩余预算</span>
                <span class="value" :class="{ negative: (budgetOverview.remaining ?? 0) < 0 }">
                  ¥{{ formatCurrency(budgetOverview.remaining) }}
                </span>
              </div>
            </div>
            <div class="budget-progress" v-if="budgetOverview.spentPercentage">
              <div
                class="budget-progress-bar"
                :style="{ width: `${Math.min(budgetOverview.spentPercentage, 100)}%` }"
              ></div>
            </div>
          </div>

          <div class="expenses card">
            <div class="expenses-header">
              <h2>支出明细</h2>
              <span class="expenses-total">
                累计支出
                <strong>{{ budgetOverview.actual !== null ? `¥${formatAmount(budgetOverview.actual)}` : '—' }}</strong>
              </span>
            </div>
            <div v-if="expensesLoading" class="expenses-loading">支出加载中...</div>
            <div v-else>
              <div v-if="!itineraryExpenses.length" class="empty-state">
                该行程暂无支出记录，可在「旅行账本」页面新增支出。
              </div>
              <div v-else class="expenses-list">
                <div
                  v-for="expense in itineraryExpenses"
                  :key="expense.id"
                  class="expenses-item"
                >
                  <div class="expenses-item__info">
                    <p class="expenses-item__description">{{ expense.description }}</p>
                    <p class="expenses-item__meta">
                      {{ formatDate(expense.date) }} · {{ getCategoryLabel(expense.category) }}
                    </p>
                  </div>
                  <span class="expenses-item__amount">¥{{ formatAmount(expense.amount) }}</span>
                </div>
              </div>
              <div v-if="Object.keys(expenseBreakdown).length" class="expenses-breakdown">
                <h3>分类汇总</h3>
                <div class="expenses-breakdown__grid">
                  <div v-for="(amount, category) in expenseBreakdown" :key="category" class="expenses-breakdown__item">
                    <span class="label">{{ getCategoryLabel(category) }}</span>
                    <span class="amount">¥{{ formatAmount(amount) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="recommendations card" v-if="itinerary.recommendations">
            <h2>💡 行程建议</h2>
            <p>{{ itinerary.recommendations }}</p>
          </div>

          <div class="daily-itinerary card">
            <h2>每日安排</h2>
            <div v-if="!structuredDays.length" class="empty-state">
              暂无详细行程，稍后可在此补充每日规划。
            </div>
            <div
              v-for="day in structuredDays"
              :key="day.day"
              class="day-card"
            >
              <div class="day-header">
                <h3>第 {{ day.day }} 天 · {{ formatDate(day.date) || '日期待定' }}</h3>
                <span class="day-cost">¥{{ formatCurrency(day.total_estimated_cost) }}</span>
              </div>

              <div class="activities">
                <div
                  v-for="(activity, index) in day.activities"
                  :key="index"
                  class="activity"
                >
                  <div class="activity-time">{{ formatTime(activity.time) || '时间待定' }}</div>
                  <div class="activity-content">
                    <h4>{{ activity.activity }}</h4>
                    <p class="location">📍 {{ activity.location }}</p>
                    <p v-if="activity.notes" class="notes">{{ activity.notes }}</p>
                    <p v-if="activity.estimated_cost" class="cost">
                      💰 ¥{{ formatCurrency(activity.estimated_cost) }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <aside class="itinerary-detail__map">
          <ItineraryMap
            :destination="mapDestination"
            :daily-itinerary="mapDailyItinerary"
            min-height="720px"
          />
        </aside>
      </div>
    </div>

    <div v-else class="error">
      <p>未找到行程</p>
      <router-link to="/itineraries" class="btn btn-primary">返回行程列表</router-link>
    </div>
  </div>
</template>

<style scoped>
.container {
  max-width: 1240px;
  margin: 0 auto;
  padding: 2rem 1.5rem 3rem;
}

.loading,
.error {
  text-align: center;
  padding: 4rem 2rem;
  background: #fff;
  border-radius: 1rem;
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.08);
}

.loading p,
.error p {
  font-size: 1.1rem;
  color: #666;
}

.itinerary-detail {
  width: 100%;
}

.itinerary-detail__layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(320px, 420px);
  gap: 2.5rem;
  align-items: flex-start;
}

.itinerary-detail__content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.itinerary-detail__map {
  position: sticky;
  top: 1.5rem;
  height: fit-content;
}

.card {
  background: #fff;
  border-radius: 1rem;
  padding: 1.5rem 2rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.06);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1.5rem;
}

.header h1 {
  font-size: 2rem;
  margin-bottom: 0.5rem;
  color: #2c3e50;
}

.dates {
  color: #6c757d;
  font-size: 1rem;
}

.budget-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 1.5rem;
  margin-top: 1.5rem;
}

.stat .label {
  display: block;
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

.budget-progress {
  height: 8px;
  background: #f5f5f5;
  border-radius: 999px;
  margin-top: 1rem;
  overflow: hidden;
}

.budget-progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  transition: width 0.3s ease;
}

.expenses-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.expenses-total {
  font-size: 0.95rem;
  color: #6c757d;
}

.expenses-total strong {
  margin-left: 0.25rem;
  font-size: 1.25rem;
  color: #2c3e50;
}

.expenses-loading {
  text-align: center;
  padding: 1rem;
  color: #6c757d;
}

.expenses-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.expenses-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  border-radius: 0.75rem;
  background: #f8f9ff;
  border: 1px solid rgba(102, 126, 234, 0.15);
}

.expenses-item__info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  max-width: 70%;
}

.expenses-item__description {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.35rem;
}

.expenses-item__meta {
  font-size: 0.85rem;
  color: #6c757d;
}

.expenses-item__amount {
  font-size: 1.2rem;
  font-weight: 700;
  color: #2c3e50;
}

.expenses-breakdown {
  margin-top: 1.75rem;
  border-top: 1px solid #f0f0f0;
  padding-top: 1.5rem;
}

.expenses-breakdown h3 {
  color: #2c3e50;
  font-size: 1.1rem;
  margin-bottom: 1rem;
}

.expenses-breakdown__grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 0.75rem;
}

.expenses-breakdown__item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: #f8f9fa;
  border-radius: 0.5rem;
  color: #495057;
}

.expenses-breakdown__item .amount {
  font-weight: 600;
  color: #2c3e50;
}

.recommendations {
  margin-bottom: 0;
}

.recommendations p {
  line-height: 1.8;
  color: #495057;
}

.daily-itinerary {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.empty-state {
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 0.75rem;
  color: #6c757d;
  text-align: center;
}

.day-card {
  padding: 0;
  border-radius: 0.75rem;
  border: 1px solid #f0f0f0;
  overflow: hidden;
}

.day-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
}

.day-header h3 {
  color: #2c3e50;
  margin: 0;
}

.day-cost {
  font-size: 1.1rem;
  font-weight: bold;
  color: #667eea;
}

.activities {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  padding: 1.5rem;
}

.activity {
  display: grid;
  grid-template-columns: 90px 1fr;
  gap: 1rem;
}

.activity-time {
  font-weight: bold;
  color: #667eea;
  font-size: 1rem;
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

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.6rem 1.2rem;
  border-radius: 999px;
  font-weight: 600;
  text-decoration: none;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
}

.btn-secondary {
  background: #f1f3f5;
  color: #495057;
}

@media (max-width: 1024px) {
  .itinerary-detail__layout {
    grid-template-columns: 1fr;
    gap: 2rem;
  }

  .itinerary-detail__map {
    position: static;
    order: -1;
  }
}
</style>
