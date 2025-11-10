<template>
  <div id="app">
    <nav v-if="showNav" class="navbar">
      <div class="container">
        <router-link to="/" class="nav-brand">🧳 AI 智能旅行助手</router-link>
        <div class="nav-links">
          <router-link to="/">首页</router-link>
          <router-link to="/itineraries">我的行程</router-link>
          <router-link to="/itineraries/create">创建行程</router-link>
          <router-link to="/expenses">旅行账本</router-link>
          <button class="link" v-if="userStore.profile" @click="logout">退出登录</button>
        </div>
      </div>
    </nav>

    <main class="main-content">
      <router-view />
    </main>

    <footer v-if="showNav" class="footer">
      <div class="container">
        <p>&copy; 2024 AI 智能旅行助手 · 为你打造个性化旅程体验</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

const showNav = computed(() => route.name !== 'Auth');

const logout = () => {
  userStore.clearSession();
  router.push({ name: 'Auth' });
};
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  line-height: 1.6;
  color: #333;
  background-color: #f5f7fa;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.navbar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.navbar .container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-brand {
  font-size: 1.5rem;
  font-weight: bold;
  color: white;
  text-decoration: none;
}

.nav-links {
  display: flex;
  gap: 2rem;
}

.nav-links a {
  color: white;
  text-decoration: none;
  transition: opacity 0.3s;
}

.nav-links .link {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 1rem;
  transition: opacity 0.3s;
}

.nav-links .link:hover {
  opacity: 0.8;
}

.nav-links a:hover {
  opacity: 0.8;
}

.nav-links a.router-link-active {
  border-bottom: 2px solid white;
  padding-bottom: 0.25rem;
}

.main-content {
  min-height: calc(100vh - 200px);
  padding: 2rem 0;
}

.footer {
  background-color: #2c3e50;
  color: white;
  padding: 2rem 0;
  text-align: center;
  margin-top: 4rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s;
  text-decoration: none;
  display: inline-block;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
}

.card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.form-group textarea {
  min-height: 100px;
  resize: vertical;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: #667eea;
}

.error {
  background-color: #f8d7da;
  color: #721c24;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
}
</style>
