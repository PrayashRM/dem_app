import api from './axios';

export const productApi = {
  getAll: (params) => {
    return api.get('/api/v1/products', { params });
  },
  getOne: (id) => {
    return api.get(`/api/v1/products/${id}`);
  },
  create: (data) => {
    return api.post('/api/v1/products', data);
  },
  update: (id, data) => {
    return api.put(`/api/v1/products/${id}`, data);
  },
  patch: (id, data) => {
    return api.patch(`/api/v1/products/${id}`, data);
  },
  delete: (id) => {
    return api.delete(`/api/v1/products/${id}`);
  }
};
