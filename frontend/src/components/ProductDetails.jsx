import { useState, useEffect } from 'react';
import { X, Package, DollarSign, Tag, Clock } from 'lucide-react';
import productApi from '../api/productApi';
import { formatPrice } from '../utils/helpers';
import MessageBox from './MessageBox';

const ProductDetails = ({ productId, onClose }) => {
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDetails = async () => {
      try {
        const response = await productApi.getProductById(productId);
        if (response.data.success && response.data.data) {
          setProduct(response.data.data);
        }
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to load product details');
      } finally {
        setLoading(false);
      }
    };
    fetchDetails();
  }, [productId]);

  return (
    <div className="modal-overlay">
      <div className="modal-content glass-panel animate-fade-in" style={{ maxWidth: '600px' }}>
        <div className="modal-header">
          <h2>Product Details</h2>
          <button className="close-btn" onClick={onClose}><X size={20} /></button>
        </div>

        {loading ? (
          <div style={{ padding: '40px', textAlign: 'center' }}>Loading details...</div>
        ) : error ? (
          <MessageBox type="error" message={error} />
        ) : product ? (
          <div className="product-details-body" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div>
              <h1 style={{ fontSize: '1.8rem', marginBottom: '8px' }}>{product.name}</h1>
              <span className="product-category" style={{ fontSize: '0.9rem', padding: '6px 12px' }}>
                <Tag size={14} style={{ display: 'inline', marginRight: '4px', verticalAlign: 'middle' }}/>
                {product.category || 'Uncategorized'}
              </span>
            </div>
            
            <p style={{ color: 'var(--text-secondary)', lineHeight: '1.6', fontSize: '1.05rem' }}>
              {product.description || 'No detailed description available.'}
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', background: 'var(--bg-tertiary)', padding: '20px', borderRadius: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{ background: 'rgba(99, 102, 241, 0.1)', padding: '12px', borderRadius: '50%', color: 'var(--accent-primary)' }}>
                  <DollarSign size={24} />
                </div>
                <div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Price</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 'bold' }}>{formatPrice(product.price)}</div>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{ background: 'rgba(16, 185, 129, 0.1)', padding: '12px', borderRadius: '50%', color: 'var(--success)' }}>
                  <Package size={24} />
                </div>
                <div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Current Stock</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 'bold', color: product.stock > 0 ? 'inherit' : 'var(--danger)' }}>
                    {product.stock} units
                  </div>
                </div>
              </div>
            </div>

            <div style={{ fontSize: '0.8rem', color: 'var(--text-tertiary)', display: 'flex', alignItems: 'center', gap: '6px', marginTop: '12px' }}>
              <Clock size={14} />
              Last Updated: {new Date(product.updated_at || product.created_at).toLocaleString()}
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
};

export default ProductDetails;
