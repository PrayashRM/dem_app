import api from './axios';

export const authApi = {
  register: (data) => {
    return api.post('/api/v1/auth/register', data);
  },
  login: (data) => {
    return api.post('/api/v1/auth/login', data);
  },
  me: () => {
    return api.get('/api/v1/auth/me');
  }
};
