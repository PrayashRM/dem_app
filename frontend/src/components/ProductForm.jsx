import { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import MessageBox from './MessageBox';
import './ProductForm.css';

const ProductForm = ({ product, onSubmit, onClose }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    price: '',
    stock: '',
    category: ''
  });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (product) {
      setFormData({
        name: product.name || '',
        description: product.description || '',
        price: product.price || '',
        stock: product.stock || '',
        category: product.category || ''
      });
    }
  }, [product]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const payload = {
        ...formData,
        price: parseFloat(formData.price),
        stock: parseInt(formData.stock, 10)
      };
      await onSubmit(payload);
    } catch (err) {
      if (err.response?.status === 422 && err.response.data.details) {
        setError(err.response.data.details.map(d => d.message).join(' | '));
      } else {
        setError(err.response?.data?.message || 'An error occurred');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content glass-panel animate-fade-in">
        <div className="modal-header">
          <h2>{product ? 'Edit Product' : 'Create Product'}</h2>
          <button className="close-btn" onClick={onClose}><X size={20} /></button>
        </div>
        
        {error && <MessageBox type="error" message={error} />}
        
        <form onSubmit={handleSubmit} className="product-form">
          <div className="form-group">
            <label className="form-label">Name *</label>
            <input type="text" name="name" value={formData.name} onChange={handleChange} className="form-input" required minLength={2} maxLength={100} />
          </div>
          
          <div className="form-group">
            <label className="form-label">Description</label>
            <textarea name="description" value={formData.description} onChange={handleChange} className="form-input" rows="3" maxLength={500} />
          </div>
          
          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Price *</label>
              <input type="number" name="price" value={formData.price} onChange={handleChange} className="form-input" required min="0.01" step="0.01" />
            </div>
            
            <div className="form-group">
              <label className="form-label">Stock *</label>
              <input type="number" name="stock" value={formData.stock} onChange={handleChange} className="form-input" required min="0" step="1" />
            </div>
          </div>
          
          <div className="form-group">
            <label className="form-label">Category</label>
            <input type="text" name="category" value={formData.category} onChange={handleChange} className="form-input" maxLength={50} />
          </div>
          
          <div className="modal-actions">
            <button type="button" onClick={onClose} className="btn-secondary">Cancel</button>
            <button type="submit" disabled={loading} className="btn-primary">
              {loading ? 'Saving...' : 'Save Product'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ProductForm;
