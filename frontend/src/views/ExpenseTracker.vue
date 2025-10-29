<script setup>
import { ref, onMounted, computed } from 'vue';
import { useExpenseStore } from '../stores/expense';

const expenseStore = useExpenseStore();

const showAddForm = ref(false);
const editingExpense = ref(null);

const form = ref({
  category: 'food',
  amount: '',
  description: '',
  location: '',
  itinerary_id: null,
});

const categories = [
  { value: 'accommodation', label: '🏨 住宿', color: '#e74c3c' },
  { value: 'food', label: '🍽️ 餐饮', color: '#f39c12' },
  { value: 'transportation', label: '🚗 交通', color: '#3498db' },
  { value: 'activities', label: '🎯 活动体验', color: '#9b59b6' },
  { value: 'shopping', label: '🛍️ 购物', color: '#1abc9c' },
  { value: 'other', label: '📝 其他', color: '#95a5a6' },
];

onMounted(() => {
  expenseStore.fetchExpenses();
  expenseStore.fetchExpenseSummary();
});

const resetForm = () => {
  form.value = {
    category: 'food',
    amount: '',
    description: '',
    location: '',
    itinerary_id: null,
  };
  editingExpense.value = null;
  showAddForm.value = false;
};

const handleSubmit = async () => {
  try {
    if (editingExpense.value) {
      await expenseStore.updateExpense(editingExpense.value.id, form.value);
    } else {
      await expenseStore.createExpense(form.value);
    }
    await expenseStore.fetchExpenseSummary();
    resetForm();
  } catch (error) {
    alert('保存支出失败，请稍后重试');
  }
};

const handleEdit = (expense) => {
  editingExpense.value = expense;
  form.value = {
    category: expense.category,
    amount: expense.amount,
    description: expense.description,
    location: expense.location || '',
    itinerary_id: expense.itinerary_id,
  };
  showAddForm.value = true;
};

const handleDelete = async (id) => {
  if (confirm('确定要删除这条支出记录吗？')) {
    try {
      await expenseStore.deleteExpense(id);
      await expenseStore.fetchExpenseSummary();
    } catch (error) {
      alert('删除支出失败，请稍后重试');
    }
  }
};

const getCategoryInfo = (categoryValue) => {
  return categories.find((c) => c.value === categoryValue) || categories[categories.length - 1];
};

const formatDate = (dateString) => {
  if (!dateString) return '';
  return new Date(dateString).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  });
};
</script>

<template>
  <div class="container">
    <div class="expense-tracker">
      <div class="header">
        <h1>旅行账本</h1>
        <button @click="showAddForm = !showAddForm" class="btn btn-primary">
          {{ showAddForm ? '取消' : '+ 新增支出' }}
        </button>
      </div>

      <!-- Add/Edit Form -->
      <div v-if="showAddForm" class="card expense-form">
        <h2>{{ editingExpense ? '编辑支出' : '新增支出' }}</h2>
        <form @submit.prevent="handleSubmit">
          <div class="form-row">
            <div class="form-group">
              <label for="category">支出分类</label>
              <select id="category" v-model="form.category" required>
                <option v-for="cat in categories" :key="cat.value" :value="cat.value">
                  {{ cat.label }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label for="amount">金额 (¥)</label>
              <input
                id="amount"
                v-model.number="form.amount"
                type="number"
                min="0"
                step="0.01"
                required
              />
            </div>
          </div>

          <div class="form-group">
            <label for="description">支出描述</label>
            <input
              id="description"
              v-model="form.description"
              type="text"
              placeholder="例如：本地餐厅晚餐"
              required
            />
          </div>

          <div class="form-group">
            <label for="location">地点（可选）</label>
            <input id="location" v-model="form.location" type="text" placeholder="例如：北京" />
          </div>

          <div class="form-actions">
            <button type="submit" class="btn btn-primary">
              {{ editingExpense ? '更新' : '新增' }}支出
            </button>
            <button type="button" @click="resetForm" class="btn btn-secondary">取消</button>
          </div>
        </form>
      </div>

      <!-- Summary -->
      <div v-if="expenseStore.summary" class="summary card">
        <h2>支出总览</h2>
        <div class="summary-stats">
          <div class="stat-large">
            <span class="label">累计支出</span>
            <span class="value">¥{{ expenseStore.summary.total_expenses?.toLocaleString() }}</span>
          </div>
          <div class="stat-large">
            <span class="label">记录笔数</span>
            <span class="value">{{ expenseStore.summary.count }}</span>
          </div>
        </div>

        <h3>分类汇总</h3>
        <div class="category-breakdown">
          <div
            v-for="(amount, category) in expenseStore.summary.by_category"
            :key="category"
            class="category-stat"
          >
            <span class="category-label">{{ getCategoryInfo(category).label }}</span>
            <span class="category-amount">¥{{ amount?.toLocaleString() }}</span>
          </div>
        </div>
      </div>

      <!-- Expense List -->
      <div class="expense-list">
        <h2>最新支出</h2>
        <div v-if="expenseStore.loading" class="loading">支出加载中...</div>

        <div v-else-if="expenseStore.expenses.length === 0" class="empty-state">
          <p>暂无支出记录，快来记录第一笔消费吧！</p>
        </div>

        <div v-else class="expense-items">
          <div
            v-for="expense in expenseStore.expenses"
            :key="expense.id"
            class="expense-item card"
          >
            <div class="expense-main">
              <div class="expense-icon" :style="{ backgroundColor: getCategoryInfo(expense.category).color }">
                {{ getCategoryInfo(expense.category).label.split(' ')[0] }}
              </div>
              <div class="expense-info">
                <h4>{{ expense.description }}</h4>
                <p class="expense-meta">
                  {{ getCategoryInfo(expense.category).label }}
                  <span v-if="expense.location"> • {{ expense.location }}</span>
                  <span> • {{ formatDate(expense.date) }}</span>
                </p>
              </div>
              <div class="expense-amount">¥{{ expense.amount?.toLocaleString() }}</div>
            </div>
            <div class="expense-actions">
              <button @click="handleEdit(expense)" class="btn btn-secondary btn-sm">编辑</button>
              <button @click="handleDelete(expense.id)" class="btn btn-danger btn-sm">删除</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.expense-tracker {
  max-width: 900px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.header h1 {
  color: #2c3e50;
}

.expense-form {
  margin-bottom: 2rem;
}

.expense-form h2 {
  color: #667eea;
  margin-bottom: 1.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.summary {
  margin-bottom: 2rem;
}

.summary h2,
.expense-list h2 {
  color: #667eea;
  margin-bottom: 1.5rem;
}

.summary-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.stat-large {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 8px;
}

.stat-large .label {
  font-size: 0.9rem;
  opacity: 0.9;
  margin-bottom: 0.5rem;
}

.stat-large .value {
  font-size: 2rem;
  font-weight: bold;
}

.summary h3 {
  color: #2c3e50;
  margin-bottom: 1rem;
}

.category-breakdown {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.category-stat {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 4px;
}

.category-label {
  color: #495057;
}

.category-amount {
  font-weight: bold;
  color: #2c3e50;
}

.expense-items {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.expense-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.expense-main {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
}

.expense-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: white;
}

.expense-info {
  flex: 1;
}

.expense-info h4 {
  color: #2c3e50;
  margin-bottom: 0.25rem;
}

.expense-meta {
  font-size: 0.875rem;
  color: #6c757d;
}

.expense-amount {
  font-size: 1.25rem;
  font-weight: bold;
  color: #2c3e50;
  margin-right: 1rem;
}

.expense-actions {
  display: flex;
  gap: 0.5rem;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  background: white;
  border-radius: 8px;
  color: #6c757d;
}
</style>
