import { defineStore } from 'pinia';
import { expenseService } from '../services/expense';

export const useExpenseStore = defineStore('expense', {
  state: () => ({
    expenses: [],
    summary: null,
    loading: false,
    error: null,
  }),

  actions: {
    async fetchExpenses(params = {}) {
      this.loading = true;
      this.error = null;
      try {
        this.expenses = await expenseService.getExpenses(params);
      } catch (error) {
        this.error = error.message;
        console.error('Error fetching expenses:', error);
      } finally {
        this.loading = false;
      }
    },

    async createExpense(data) {
      this.loading = true;
      this.error = null;
      try {
        const newExpense = await expenseService.createExpense(data);
        this.expenses.unshift(newExpense);
        return newExpense;
      } catch (error) {
        this.error = error.message;
        console.error('Error creating expense:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async updateExpense(id, data) {
      this.loading = true;
      this.error = null;
      try {
        const updatedExpense = await expenseService.updateExpense(id, data);
        const index = this.expenses.findIndex((e) => e.id === id);
        if (index !== -1) {
          this.expenses[index] = updatedExpense;
        }
        return updatedExpense;
      } catch (error) {
        this.error = error.message;
        console.error('Error updating expense:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async deleteExpense(id) {
      this.loading = true;
      this.error = null;
      try {
        await expenseService.deleteExpense(id);
        this.expenses = this.expenses.filter((e) => e.id !== id);
      } catch (error) {
        this.error = error.message;
        console.error('Error deleting expense:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchExpenseSummary(itineraryId = null) {
      this.loading = true;
      this.error = null;
      try {
        this.summary = await expenseService.getExpenseSummary(itineraryId);
      } catch (error) {
        this.error = error.message;
        console.error('Error fetching expense summary:', error);
      } finally {
        this.loading = false;
      }
    },
  },
});
