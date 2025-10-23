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
  { value: 'cultural', label: 'Cultural' },
  { value: 'adventure', label: 'Adventure' },
  { value: 'relaxation', label: 'Relaxation' },
  { value: 'food', label: 'Food' },
  { value: 'shopping', label: 'Shopping' },
  { value: 'nature', label: 'Nature' },
  { value: 'nightlife', label: 'Nightlife' },
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
    error.value = err.message || 'Failed to create itinerary. Please try again.';
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="container">
    <div class="create-itinerary">
      <h1>Plan Your Trip</h1>
      <p class="subtitle">
        Tell us about your travel plans and our AI will create a personalized itinerary for you
      </p>

      <div v-if="error" class="error">{{ error }}</div>

      <form @submit.prevent="handleSubmit" class="card">
        <div class="form-group">
          <label for="destination">Destination *</label>
          <input
            id="destination"
            v-model="form.destination"
            type="text"
            placeholder="e.g., Beijing, Paris, Tokyo"
            required
          />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="start_date">Start Date *</label>
            <input id="start_date" v-model="form.start_date" type="date" required />
          </div>

          <div class="form-group">
            <label for="end_date">End Date *</label>
            <input id="end_date" v-model="form.end_date" type="date" required />
          </div>
        </div>

        <div class="form-group">
          <label for="budget">Budget (¥) *</label>
          <input
            id="budget"
            v-model.number="form.budget"
            type="number"
            min="0"
            step="0.01"
            placeholder="e.g., 5000"
            required
          />
        </div>

        <div class="form-group">
          <label>Travel Preferences</label>
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
          <label for="additional_notes">Additional Notes</label>
          <textarea
            id="additional_notes"
            v-model="form.additional_notes"
            placeholder="Any special requirements or preferences..."
          ></textarea>
        </div>

        <div class="form-actions">
          <button type="submit" class="btn btn-primary" :disabled="loading">
            {{ loading ? 'Generating Itinerary...' : 'Generate Itinerary' }}
          </button>
          <router-link to="/itineraries" class="btn btn-secondary">Cancel</router-link>
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
