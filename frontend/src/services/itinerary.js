import apiClient from './api';

export const itineraryService = {
  // Create a new itinerary
  async createItinerary(data) {
    const response = await apiClient.post('/itineraries/', data);
    return response.data;
  },

  // Create itinerary from natural language text
  async createItineraryFromText(data) {
    const response = await apiClient.post('/itineraries/from-text', data);
    return response.data;
  },

  // Get all itineraries
  async getItineraries(limit = 20) {
    const response = await apiClient.get('/itineraries/', { params: { limit } });
    return response.data;
  },

  // Get a specific itinerary
  async getItinerary(id) {
    const response = await apiClient.get(`/itineraries/${id}`);
    return response.data;
  },

  // Delete an itinerary
  async deleteItinerary(id) {
    await apiClient.delete(`/itineraries/${id}`);
  },

  // Get budget status for an itinerary
  async getBudgetStatus(id) {
    const response = await apiClient.get(`/itineraries/${id}/budget-status`);
    return response.data;
  },
};
