import apiClient from './api';

export const register = (payload) =>
    apiClient.post('/auth/register', payload).then((res) => res.data);

export const login = (payload) =>
    apiClient.post('/auth/login', payload).then((res) => res.data);
