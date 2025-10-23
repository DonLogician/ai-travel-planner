<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useItineraryStore } from '../stores/itinerary';

const router = useRouter();
const itineraryStore = useItineraryStore();

onMounted(() => {
  itineraryStore.fetchItineraries();
});

const deleteItinerary = async (id) => {
  if (confirm('Are you sure you want to delete this itinerary?')) {
    try {
      await itineraryStore.deleteItinerary(id);
    } catch (error) {
      alert('Failed to delete itinerary');
    }
  }
};

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};
</script>

<template>
  <div class="container">
    <div class="itinerary-list">
      <div class="header">
        <h1>My Itineraries</h1>
        <router-link to="/itineraries/create" class="btn btn-primary">
          + New Itinerary
        </router-link>
      </div>

      <div v-if="itineraryStore.loading" class="loading">
        <p>Loading itineraries...</p>
      </div>

      <div v-else-if="itineraryStore.error" class="error">
        {{ itineraryStore.error }}
      </div>

      <div v-else-if="itineraryStore.itineraries.length === 0" class="empty-state">
        <p>You haven't created any itineraries yet.</p>
        <router-link to="/itineraries/create" class="btn btn-primary">
          Create Your First Itinerary
        </router-link>
      </div>

      <div v-else class="itinerary-grid">
        <div
          v-for="itinerary in itineraryStore.itineraries"
          :key="itinerary.id"
          class="itinerary-card card"
        >
          <div class="card-header">
            <h3>{{ itinerary.destination }}</h3>
            <span class="badge">
              {{ itinerary.daily_itinerary?.length || 0 }} days
            </span>
          </div>

          <div class="card-body">
            <p class="dates">
              <strong>📅</strong>
              {{ formatDate(itinerary.start_date) }} - {{ formatDate(itinerary.end_date) }}
            </p>
            <p class="budget">
              <strong>💰</strong>
              Budget: ¥{{ itinerary.budget?.toLocaleString() }}
            </p>
            <p class="estimated-cost">
              <strong>💵</strong>
              Estimated: ¥{{ itinerary.total_estimated_cost?.toLocaleString() }}
            </p>
          </div>

          <div class="card-actions">
            <button
              @click="router.push(`/itineraries/${itinerary.id}`)"
              class="btn btn-primary btn-sm"
            >
              View Details
            </button>
            <button @click="deleteItinerary(itinerary.id)" class="btn btn-danger btn-sm">
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.itinerary-list {
  max-width: 1200px;
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

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 8px;
}

.empty-state p {
  font-size: 1.2rem;
  color: #6c757d;
  margin-bottom: 1.5rem;
}

.itinerary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.itinerary-card {
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
}

.itinerary-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.card-header h3 {
  color: #667eea;
  margin: 0;
}

.badge {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.875rem;
}

.card-body p {
  margin-bottom: 0.5rem;
  color: #495057;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e9ecef;
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
}
</style>
