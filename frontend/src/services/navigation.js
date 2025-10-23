import apiClient from './api';

export const navigationService = {
  // Search for a location
  async searchLocation(query, city = null) {
    const response = await apiClient.post('/navigation/search', { query, city });
    return response.data;
  },

  // Get route between two locations
  async getRoute(origin, destination, mode = 'transit') {
    const response = await apiClient.post('/navigation/route', {
      origin,
      destination,
      mode,
    });
    return response.data;
  },
};
