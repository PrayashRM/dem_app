import api from './axios';

export const productApi = {
  getAll: (params) => {
    return api.get('/products', { params });
  },
  getOne: (id) => {
    return api.get(`/products/${id}`);
  },
  create: (data) => {
    return api.post('/products', data);
  },
  update: (id, data) => {
    return api.put(`/products/${id}`, data);
  },
  patch: (id, data) => {
    return api.patch(`/products/${id}`, data);
  },
  delete: (id) => {
    return api.delete(`/products/${id}`);
  }
};
