import { ChevronLeft, ChevronRight } from 'lucide-react';
import './Pagination.css';

const Pagination = ({ pagination, onPageChange }) => {
  if (!pagination || pagination.total_pages <= 1) return null;

  const { page, total_pages, has_next, has_previous } = pagination;

  return (
    <div className="pagination">
      <button 
        className="page-btn" 
        onClick={() => onPageChange(page - 1)} 
        disabled={!has_previous}
      >
        <ChevronLeft size={18} />
      </button>
      
      <span className="page-info">
        Page {page} of {total_pages}
      </span>
      
      <button 
        className="page-btn" 
        onClick={() => onPageChange(page + 1)} 
        disabled={!has_next}
      >
        <ChevronRight size={18} />
      </button>
    </div>
  );
};

export default Pagination;
