<template>
  <div class="auth-page">
    <div class="auth-card">
      <h2>{{ mode === 'login' ? '登录' : '注册' }}</h2>

      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="username">用户名</label>
          <input
            id="username"
            v-model.trim="form.username"
            type="text"
            maxlength="16"
            autocomplete="username"
            placeholder="请输入用户名（4-16 位字母或数字）"
            required
          />
        </div>

        <div class="form-group">
          <label for="password">密码</label>
          <input
            id="password"
            v-model.trim="form.password"
            type="password"
            maxlength="16"
            autocomplete="current-password"
            placeholder="请输入密码（4-16 位字母或数字）"
            required
          />
        </div>

        <div v-if="mode === 'register'" class="form-group">
          <label for="confirmPassword">确认密码</label>
          <input
            id="confirmPassword"
            v-model.trim="form.confirmPassword"
            type="password"
            maxlength="16"
            autocomplete="new-password"
            placeholder="请再次输入密码"
            required
          />
        </div>

        <div v-if="error" class="error">{{ error }}</div>

        <button class="btn btn-primary full" type="submit" :disabled="loading">
          {{ loading ? '处理中...' : mode === 'login' ? '登录' : '注册' }}
        </button>
      </form>

      <div class="switch-mode">
        <span>{{ mode === 'login' ? '还没有账号？' : '已经有账号？' }}</span>
        <button class="link" type="button" @click="toggleMode">
          {{ mode === 'login' ? '立即注册' : '返回登录' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user';
import { register, login } from '@/services/user';

const router = useRouter();
const userStore = useUserStore();

const mode = ref('login');
const loading = ref(false);
const error = ref('');

const form = reactive({
  username: '',
  password: '',
  confirmPassword: '',
});

const resetForm = () => {
  form.username = '';
  form.password = '';
  form.confirmPassword = '';
  error.value = '';
};

const toggleMode = () => {
  mode.value = mode.value === 'login' ? 'register' : 'login';
  resetForm();
};

const validateInput = () => {
  const pattern = /^[A-Za-z0-9]{4,16}$/;
  if (!pattern.test(form.username) || !pattern.test(form.password)) {
    error.value = '用户名和密码需为 4-16 位字母或数字组成';
    return false;
  }
  if (mode.value === 'register') {
    if (!pattern.test(form.confirmPassword)) {
      error.value = '确认密码需为 4-16 位字母或数字组成';
      return false;
    }
    if (form.password !== form.confirmPassword) {
      error.value = '两次输入的密码不一致';
      return false;
    }
  }
  return true;
};

const handleSubmit = async () => {
  if (!validateInput()) {
    return;
  }
  loading.value = true;
  error.value = '';

  try {
    const payload = {
      username: form.username,
      password: form.password,
    };

    let response;
    if (mode.value === 'register') {
      response = await register({ ...payload, confirm_password: form.confirmPassword });
    } else {
      response = await login(payload);
    }

    const user = response?.user;
    if (!user?.id) {
      throw new Error('未能获取用户信息');
    }

    userStore.setSession({
      profile: user,
      token: user.id,
    });
    localStorage.setItem('userId', user.id);
    localStorage.setItem('username', user.username);

    await router.push({ name: 'Home' });
  } catch (err) {
    error.value = err?.response?.data?.detail || err?.message || '请求失败，请稍后再试';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.auth-page {
  min-height: calc(100vh - 160px);
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #eef2ff 0%, #f8f9ff 100%);
}

.auth-card {
  width: min(420px, 90vw);
  background: #fff;
  border-radius: 16px;
  padding: 2.5rem 2rem;
  box-shadow: 0 24px 60px rgba(76, 90, 167, 0.15);
}

.auth-card h2 {
  text-align: center;
  margin-bottom: 2rem;
  color: #314065;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #394b6f;
}

.form-group input {
  width: 100%;
  padding: 0.85rem 1rem;
  border-radius: 10px;
  border: 1px solid #d6dcf5;
  font-size: 1rem;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.form-group input:focus {
  outline: none;
  border-color: #6c7ae0;
  box-shadow: 0 0 0 3px rgba(108, 122, 224, 0.15);
}

.error {
  background: rgba(255, 125, 125, 0.15);
  color: #c53030;
  border-radius: 8px;
  padding: 0.75rem 1rem;
  margin-bottom: 1.2rem;
  font-size: 0.95rem;
}

.btn.full {
  width: 100%;
  padding: 0.85rem;
  border-radius: 10px;
  margin-top: 0.5rem;
}

.switch-mode {
  margin-top: 1.75rem;
  text-align: center;
  color: #5f6a95;
  font-size: 0.95rem;
}

.switch-mode .link {
  background: none;
  border: none;
  color: #5366f4;
  margin-left: 0.5rem;
  cursor: pointer;
  text-decoration: underline;
}

.switch-mode .link:hover {
  color: #3244c5;
}
</style>
