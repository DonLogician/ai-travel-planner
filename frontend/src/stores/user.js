import { defineStore } from 'pinia';

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
        clearSession() {
            this.profile = null;
            this.token = null;
        },
        setLoading(value) {
            this.loading = value;
        },
        setError(message) {
            this.error = message;
        },
    },
});
