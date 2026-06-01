import { jwtDecode } from 'jwt-decode';

export const formatPrice = (price) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(price);
};

export const decodeToken = (token) => {
  try {
    return jwtDecode(token);
  } catch (error) {
    return null;
  }
};

export const getUserRole = (user) => {
  return user?.role || 'user';
};

export const isAdmin = (user) => {
  return getUserRole(user) === 'admin';
};
