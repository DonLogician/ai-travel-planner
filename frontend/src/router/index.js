import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/Home.vue';
import CreateItinerary from '../views/CreateItinerary.vue';
import ItineraryList from '../views/ItineraryList.vue';
import ItineraryDetail from '../views/ItineraryDetail.vue';
import ExpenseTracker from '../views/ExpenseTracker.vue';
import AuthPage from '../views/AuthPage.vue';
import { useUserStore } from '@/stores/user';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: true },
  },
  {
    path: '/itineraries',
    name: 'ItineraryList',
    component: ItineraryList,
    meta: { requiresAuth: true },
  },
  {
    path: '/itineraries/create',
    name: 'CreateItinerary',
    component: CreateItinerary,
    meta: { requiresAuth: true },
  },
  {
    path: '/itineraries/:id',
    name: 'ItineraryDetail',
    component: ItineraryDetail,
    meta: { requiresAuth: true },
  },
  {
    path: '/expenses',
    name: 'ExpenseTracker',
    component: ExpenseTracker,
    meta: { requiresAuth: true },
  },
  {
    path: '/auth',
    name: 'Auth',
    component: AuthPage,
    meta: { requiresAuth: false },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const userStore = useUserStore();

  if (!userStore.profile) {
    userStore.hydrateFromStorage();
  }

  if (to.meta.requiresAuth && !userStore.profile) {
    next({ name: 'Auth' });
    return;
  }

  if (to.name === 'Auth' && userStore.profile) {
    next({ name: 'Home' });
    return;
  }

  next();
});

export default router;
