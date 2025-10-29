<script setup>
import { computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useItineraryStore } from '../stores/itinerary';

const router = useRouter();
const itineraryStore = useItineraryStore();

const fallbackItineraries = [
  {
    id: 'sample-tokyo',
    title: '东京 5 日亲子行',
    dateRange: '2025/04/01 - 2025/04/05',
    highlights: ['吉卜力美术馆', '台场海滨公园', '筑地海鲜市场'],
  },
  {
    id: 'sample-bali',
    title: '巴厘岛 放松度假',
    dateRange: '2025/06/10 - 2025/06/15',
    highlights: ['水明漾海滩', '乌布文化体验', '悬崖海神庙'],
  },
  {
    id: 'sample-paris',
    title: '巴黎 文艺周末',
    dateRange: '2025/03/08 - 2025/03/10',
    highlights: ['卢浮宫', '塞纳河夜游', '凡尔赛宫'],
  },
];

const featuredItineraries = computed(() => {
  if (itineraryStore.itineraries.length) {
    return itineraryStore.itineraries.slice(0, 3).map((item) => ({
      id: item.id,
      title: item.title || item.destination || '未命名行程',
      dateRange: item.date_range || `${item.start_date || ''} — ${item.end_date || ''}`,
      highlights: Array.isArray(item.highlights)
        ? item.highlights
        : Array.isArray(item.daily_summary)
          ? item.daily_summary
          : typeof item.daily_summary === 'string'
            ? item.daily_summary.split(/；|;|\n/).filter(Boolean)
            : [],
    }));
  }
  return fallbackItineraries;
});

const isBackendUnavailable = computed(() => Boolean(itineraryStore.error));

const quickActions = [
  {
    label: '快速规划',
    description: '输入目的地与偏好，几秒钟生成 AI 行程',
    action: () => router.push('/itineraries/create'),
  },
  {
    label: '查看费用',
    description: '实时掌握预算与开销，对比计划与实际',
    action: () => router.push('/expenses'),
  },
  {
    label: '语音助手',
    description: '通过科大讯飞语音快速录入需求与消费',
    action: () => router.push('/itineraries/create'),
  },
];

onMounted(() => {
  itineraryStore.fetchItineraries();
});
</script>

<template>
  <div class="home">
    <div class="container">
      <section class="hero">
        <p class="hero-tag">智能旅行助手 · 云端同步</p>
        <h1>一次对话，搞定你的下一次旅行</h1>
        <p class="hero-subtitle">
          通过 AI 自动生成行程，掌握预算收支，语音随时更新旅行计划
        </p>
        <div class="hero-actions">
          <router-link to="/itineraries/create" class="btn btn-primary">立即开始规划</router-link>
          <router-link to="/itineraries" class="btn btn-secondary">查看我的行程</router-link>
        </div>
      </section>

      <section class="quick-actions">
        <h2>快速入口</h2>
        <div class="quick-grid">
          <button
            v-for="action in quickActions"
            :key="action.label"
            class="action-card"
            type="button"
            @click="action.action"
          >
            <h3>{{ action.label }}</h3>
            <p>{{ action.description }}</p>
            <span class="action-link">立即前往 →</span>
          </button>
        </div>
      </section>

      <section class="recent-itineraries">
        <div class="section-header">
          <div>
            <h2>最近的旅行灵感</h2>
            <p>从行程范例中获取灵感，或继续完善你的计划</p>
          </div>
          <router-link to="/itineraries" class="link">全部行程 →</router-link>
        </div>

        <div v-if="isBackendUnavailable" class="notice">
          后端暂未连接，当前展示示例行程。
        </div>

        <div class="itinerary-grid">
          <article v-for="item in featuredItineraries" :key="item.id" class="itinerary-card">
            <h3>{{ item.title }}</h3>
            <p class="date">{{ item.dateRange || '日期待定' }}</p>
            <ul>
              <li v-for="highlight in item.highlights" :key="highlight">{{ highlight }}</li>
            </ul>
            <router-link
              v-if="!item.id.startsWith('sample-')"
              class="link"
              :to="`/itineraries/${item.id}`"
            >查看详情 →</router-link>
          </article>
        </div>
      </section>

      <section class="features">
        <h2>核心功能</h2>
        <div class="feature-grid">
          <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <h3>智能行程规划</h3>
            <p>依据目的地、预算与偏好生成天级行程表，包含交通、餐饮与住宿建议。</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">💰</div>
            <h3>预算与费用管理</h3>
            <p>AI 协助估算预算，实时记录消费，对比计划与实际，防止超支。</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">🗺️</div>
            <h3>地图导航联动</h3>
            <p>基于高德地图提供地点搜索与路线规划，实时展示行程地图。</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">🎤</div>
            <h3>语音输入</h3>
            <p>接入科大讯飞语音识别，支持中文语音录入需求与开销。</p>
          </div>
        </div>
      </section>

      <section class="how-it-works">
        <h2>如何使用</h2>
        <div class="steps">
          <div class="step">
            <div class="step-number">1</div>
            <h3>告诉我们需求</h3>
            <p>输入目的地、时间、预算与偏好，也可语音描述。</p>
          </div>
          <div class="step">
            <div class="step-number">2</div>
            <h3>生成专属行程</h3>
            <p>AI 秒级输出每日安排、预算估算与必去亮点。</p>
          </div>
          <div class="step">
            <div class="step-number">3</div>
            <h3>同步与跟进</h3>
            <p>云端保存多个行程，随时更新费用，实时掌控。</p>
          </div>
          <div class="step">
            <div class="step-number">4</div>
            <h3>轻松出发</h3>
            <p>在旅途中查看地图导航，语音记录灵感与消费。</p>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.home {
  background: linear-gradient(180deg, rgba(102, 126, 234, 0.08) 0%, rgba(245, 247, 250, 1) 30%);
  padding: 2rem 0 4rem;
}

.hero {
  text-align: center;
  padding: 4rem 2rem;
  background: radial-gradient(circle at top left, rgba(255, 255, 255, 0.9), rgba(102, 126, 234, 0.2));
  color: #1f2933;
  border-radius: 20px;
  margin-bottom: 3rem;
  position: relative;
  overflow: hidden;
}

.hero::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.3), rgba(118, 75, 162, 0.2));
  opacity: 0.6;
  z-index: 0;
}

.hero > * {
  position: relative;
  z-index: 1;
}

.hero-tag {
  display: inline-block;
  padding: 0.5rem 1.5rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.7);
  color: #4c51bf;
  font-weight: 600;
  margin-bottom: 1rem;
}

.hero h1 {
  font-size: clamp(2.5rem, 5vw, 3.5rem);
  margin-bottom: 1rem;
}

.hero-subtitle {
  font-size: 1.25rem;
  margin-bottom: 2rem;
  color: rgba(31, 41, 51, 0.8);
}

.hero-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.quick-actions {
  margin-bottom: 3.5rem;
}

.quick-actions h2 {
  font-size: 2rem;
  margin-bottom: 1.5rem;
  color: #2c3e50;
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.5rem;
}

.action-card {
  border: none;
  border-radius: 16px;
  background: white;
  padding: 1.75rem;
  text-align: left;
  box-shadow: 0 12px 30px -20px rgba(102, 126, 234, 0.6);
  cursor: pointer;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.action-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 20px 40px -24px rgba(118, 75, 162, 0.7);
}

.action-card h3 {
  font-size: 1.25rem;
  color: #4c51bf;
  margin-bottom: 0.5rem;
}

.action-card p {
  color: #4a5568;
  margin-bottom: 1rem;
}

.action-link {
  color: #667eea;
  font-weight: 600;
}

.recent-itineraries {
  margin-bottom: 4rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.section-header h2 {
  font-size: 2rem;
  color: #2c3e50;
  margin-bottom: 0.25rem;
}

.section-header p {
  color: #6c757d;
}

.link {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
}

.link:hover {
  text-decoration: underline;
}

.notice {
  margin-bottom: 1rem;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  background: rgba(255, 193, 7, 0.15);
  color: #8a6d3b;
}

.itinerary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.5rem;
}

.itinerary-card {
  background: white;
  border-radius: 16px;
  padding: 1.75rem;
  box-shadow: 0 18px 40px -32px rgba(102, 126, 234, 0.8);
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.itinerary-card h3 {
  font-size: 1.3rem;
  color: #1f2937;
}

.itinerary-card .date {
  color: #4c51bf;
  font-weight: 600;
}

.itinerary-card ul {
  list-style: none;
  padding: 0;
  margin: 0;
  color: #4a5568;
}

.itinerary-card li + li {
  margin-top: 0.35rem;
}

.features {
  margin-bottom: 4rem;
}

.features h2 {
  text-align: center;
  font-size: 2rem;
  margin-bottom: 2rem;
  color: #2c3e50;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.5rem;
}

.feature-card {
  background: white;
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 16px 32px -28px rgba(0, 0, 0, 0.2);
  text-align: center;
  transition: transform 0.3s;
}

.feature-card:hover {
  transform: translateY(-8px);
}

.feature-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.feature-card h3 {
  color: #4c51bf;
  margin-bottom: 0.75rem;
}

.feature-card p {
  color: #4a5568;
}

.how-it-works {
  background: white;
  border-radius: 20px;
  padding: 3rem 2rem;
  box-shadow: 0 16px 40px -30px rgba(102, 126, 234, 0.8);
}

.how-it-works h2 {
  text-align: center;
  font-size: 2rem;
  margin-bottom: 2rem;
  color: #2c3e50;
}

.steps {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2rem;
}

.step {
  text-align: center;
  padding: 1.5rem;
}

.step-number {
  width: 60px;
  height: 60px;
  margin: 0 auto 1rem;
  border-radius: 50%;
  display: grid;
  place-items: center;
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.step h3 {
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.step p {
  color: #4a5568;
}

@media (max-width: 768px) {
  .hero {
    padding: 3rem 1.5rem;
  }

  .hero-subtitle {
    font-size: 1.1rem;
  }

  .section-header {
    align-items: flex-start;
  }
}
</style>
