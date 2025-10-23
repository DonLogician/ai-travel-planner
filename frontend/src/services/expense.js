import apiClient from './api';

export const expenseService = {
  // Create a new expense
  async createExpense(data) {
    const response = await apiClient.post('/expenses/', data);
    return response.data;
  },

  // Get all expenses
  async getExpenses(params = {}) {
    const response = await apiClient.get('/expenses/', { params });
    return response.data;
  },

  // Get a specific expense
  async getExpense(id) {
    const response = await apiClient.get(`/expenses/${id}`);
    return response.data;
  },

  // Update an expense
  async updateExpense(id, data) {
    const response = await apiClient.put(`/expenses/${id}`, data);
    return response.data;
  },

  // Delete an expense
  async deleteExpense(id) {
    await apiClient.delete(`/expenses/${id}`);
  },

  // Get expense summary
  async getExpenseSummary(itineraryId = null) {
    const params = itineraryId ? { itinerary_id: itineraryId } : {};
    const response = await apiClient.get('/expenses/summary', { params });
    return response.data;
  },
};
