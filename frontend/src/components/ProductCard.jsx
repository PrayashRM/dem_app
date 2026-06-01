import { Edit, Trash2, Info, Plus, Minus } from 'lucide-react';
import { formatPrice } from '../utils/helpers';
import './ProductCard.css';

const ProductCard = ({ product, isAdmin, onEdit, onDelete, onView, onPatch }) => {
  return (
    <div className="product-card glass-panel">
      <div className="product-header">
        <h3 className="product-title">{product.name}</h3>
        <span className="product-category">{product.category || 'Uncategorized'}</span>
      </div>
      <p className="product-desc">{product.description || 'No description available.'}</p>
      
      <div className="product-footer">
        <div className="product-stats">
          <span className="product-price">{formatPrice(product.price)}</span>
          <span className={`product-stock ${product.stock > 0 ? 'in-stock' : 'out-of-stock'}`}>
            {product.stock > 0 ? `${product.stock} in stock` : 'Out of stock'}
          </span>
        </div>
      </div>

      <div className="product-actions-full">
        <button onClick={() => onView(product.id)} className="btn-secondary btn-sm" style={{ width: '100%', justifyContent: 'center' }}>
          <Info size={16} /> View Details (GET)
        </button>
        
        <div className="admin-actions-row">
          <div className="patch-actions">
            <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>PATCH Stock:</span>
            <button onClick={() => onPatch(product.id, { stock: Math.max(0, product.stock - 1) })} className="patch-btn" title="Decrease Stock" disabled={product.stock <= 0}>
              <Minus size={14} />
            </button>
            <button onClick={() => onPatch(product.id, { stock: product.stock + 1 })} className="patch-btn" title="Increase Stock">
              <Plus size={14} />
            </button>
          </div>
          <div className="crud-actions">
            <button onClick={() => onEdit(product)} className="action-btn edit-btn" title="Full Update (PUT)">
              <Edit size={16} />
            </button>
            <button onClick={() => onDelete(product.id)} className="action-btn delete-btn" title="Delete (DELETE)">
              <Trash2 size={16} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductCard;
