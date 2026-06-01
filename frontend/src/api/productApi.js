import api from "./axios";

const productApi = {
  createProduct: (data) => api.post("/products", data),
  getProducts: (params = {}) => api.get("/products", { params }),
  getProductById: (id) => api.get(`/products/${id}`),
  updateProduct: (id, data) => api.put(`/products/${id}`, data),
  patchProduct: (id, data) => api.patch(`/products/${id}`, data),
  deleteProduct: (id) => api.delete(`/products/${id}`),
};

export default productApi;
