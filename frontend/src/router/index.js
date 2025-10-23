import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/Home.vue';
import CreateItinerary from '../views/CreateItinerary.vue';
import ItineraryList from '../views/ItineraryList.vue';
import ItineraryDetail from '../views/ItineraryDetail.vue';
import ExpenseTracker from '../views/ExpenseTracker.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
  },
  {
    path: '/itineraries',
    name: 'ItineraryList',
    component: ItineraryList,
  },
  {
    path: '/itineraries/create',
    name: 'CreateItinerary',
    component: CreateItinerary,
  },
  {
    path: '/itineraries/:id',
    name: 'ItineraryDetail',
    component: ItineraryDetail,
  },
  {
    path: '/expenses',
    name: 'ExpenseTracker',
    component: ExpenseTracker,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
