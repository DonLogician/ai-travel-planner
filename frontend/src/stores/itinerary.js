import { defineStore } from 'pinia';
import { itineraryService } from '../services/itinerary';

export const useItineraryStore = defineStore('itinerary', {
  state: () => ({
    itineraries: [],
    currentItinerary: null,
    loading: false,
    error: null,
  }),

  actions: {
    async fetchItineraries() {
      this.loading = true;
      this.error = null;
      try {
        this.itineraries = await itineraryService.getItineraries();
      } catch (error) {
        this.error = error.message;
        console.error('Error fetching itineraries:', error);
      } finally {
        this.loading = false;
      }
    },

    async createItinerary(data) {
      this.loading = true;
      this.error = null;
      try {
        const newItinerary = await itineraryService.createItinerary(data);
        this.itineraries.unshift(newItinerary);
        return newItinerary;
      } catch (error) {
        this.error = error.message;
        console.error('Error creating itinerary:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchItinerary(id) {
      this.loading = true;
      this.error = null;
      try {
        this.currentItinerary = await itineraryService.getItinerary(id);
      } catch (error) {
        this.error = error.message;
        console.error('Error fetching itinerary:', error);
      } finally {
        this.loading = false;
      }
    },

    async deleteItinerary(id) {
      this.loading = true;
      this.error = null;
      try {
        await itineraryService.deleteItinerary(id);
        this.itineraries = this.itineraries.filter((i) => i.id !== id);
      } catch (error) {
        this.error = error.message;
        console.error('Error deleting itinerary:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },
  },
});
