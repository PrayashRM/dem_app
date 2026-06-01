import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { useProducts } from '../hooks/useProducts';
import { productApi } from '../api/productApi';
import Navbar from '../components/Navbar';
import ProductCard from '../components/ProductCard';
import ProductForm from '../components/ProductForm';
import ProductDetails from '../components/ProductDetails';
import Pagination from '../components/Pagination';
import MessageBox from '../components/MessageBox';
import { isAdmin } from '../utils/helpers';
import { Plus, Search } from 'lucide-react';
import './Products.css';

const Products = () => {
  const { user } = useAuth();
  const isUserAdmin = isAdmin(user);
  
  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [actionMessage, setActionMessage] = useState(null);
  const [viewingProductId, setViewingProductId] = useState(null);
  
  const [queryParams, setQueryParams] = useState({ page: 1, limit: 10 });
  const { products, pagination, loading, error, fetchProducts } = useProducts(queryParams);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchTerm);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchTerm]);

  useEffect(() => {
    setQueryParams(prev => ({
      ...prev,
      page: 1, // Reset to first page on search change
      search: debouncedSearch || undefined
    }));
  }, [debouncedSearch]);

  const handlePageChange = (newPage) => {
    setQueryParams(prev => ({ ...prev, page: newPage }));
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const showMessage = (type, message) => {
    setActionMessage({ type, message });
    setTimeout(() => setActionMessage(null), 5000);
  };

  const handleOpenCreateForm = () => {
    setEditingProduct(null);
    setIsFormOpen(true);
  };

  const handleOpenEditForm = (product) => {
    setEditingProduct(product);
    setIsFormOpen(true);
  };

  const handleViewDetails = (id) => {
    setViewingProductId(id);
  };

  const handlePatchStock = async (id, patchData) => {
    try {
      await productApi.patch(id, patchData);
      showMessage('success', 'Stock updated successfully');
      fetchProducts(queryParams);
    } catch (err) {
      showMessage('error', err.message || 'Failed to patch stock');
    }
  };

  const handleFormSubmit = async (formData) => {
    try {
      if (editingProduct) {
        await productApi.update(editingProduct.id, formData);
        showMessage('success', 'Product updated successfully');
      } else {
        await productApi.create(formData);
        showMessage('success', 'Product created successfully');
      }
      setIsFormOpen(false);
      fetchProducts(queryParams); // Refresh the current page
    } catch (err) {
      throw err; // Let the form handle the error display
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this product?')) {
      try {
        await productApi.delete(id);
        showMessage('success', 'Product deleted successfully');
        fetchProducts(queryParams); // Refresh
      } catch (err) {
        showMessage('error', err.message || 'Failed to delete product');
      }
    }
  };

  return (
    <div className="page-wrapper">
      <Navbar />
      <div className="page-container animate-fade-in">
        
        <div className="products-header">
          <div className="products-title">
            <h1>Products Management</h1>
            <p>Manage your inventory and catalog</p>
          </div>
          
          <button onClick={handleOpenCreateForm} className="btn-primary">
            <Plus size={18} />
            <span>Add Product (POST)</span>
          </button>
        </div>

        {actionMessage && (
          <MessageBox type={actionMessage.type} message={actionMessage.message} />
        )}

        <div className="products-toolbar">
          <div className="search-bar">
            <Search size={18} className="search-icon" />
            <input 
              type="text" 
              placeholder="Search products by name or description..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input form-input"
            />
          </div>
        </div>

        {loading ? (
          <div className="loading-state">Loading products...</div>
        ) : error ? (
          <MessageBox type="error" message={error} />
        ) : products.length === 0 ? (
          <div className="empty-state glass-panel">
            <p>No products found matching your criteria.</p>
          </div>
        ) : (
          <>
            <div className="products-grid">
              {products.map(product => (
                <ProductCard 
                  key={product.id} 
                  product={product} 
                  isAdmin={isUserAdmin}
                  onEdit={handleOpenEditForm}
                  onDelete={handleDelete}
                  onView={handleViewDetails}
                  onPatch={handlePatchStock}
                />
              ))}
            </div>
            
            <Pagination 
              pagination={pagination} 
              onPageChange={handlePageChange} 
            />
          </>
        )}

      </div>

      {isFormOpen && (
        <ProductForm 
          product={editingProduct}
          onSubmit={handleFormSubmit}
          onClose={() => setIsFormOpen(false)}
        />
      )}

      {viewingProductId && (
        <ProductDetails 
          productId={viewingProductId}
          onClose={() => setViewingProductId(null)}
        />
      )}
    </div>
  );
};

export default Products;
