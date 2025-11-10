import { defineStore } from 'pinia';
import { clearAuthHeader } from '@/services/api';

export const useUserStore = defineStore('user', {
    state: () => ({
        profile: null,
        token: null,
        loading: false,
        error: null,
    }),
    actions: {
        setSession({ profile, token }) {
            this.profile = profile;
            this.token = token;
        },
        hydrateFromStorage() {
            const userId = localStorage.getItem('userId');
            const username = localStorage.getItem('username');
            if (userId && username) {
                this.profile = { id: userId, username };
                this.token = userId;
            }
        },
        clearSession() {
            this.profile = null;
            this.token = null;
            clearAuthHeader();
        },
        setLoading(value) {
            this.loading = value;
        },
        setError(message) {
            this.error = message;
        },
    },
});
