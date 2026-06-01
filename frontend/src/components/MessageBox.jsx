import { AlertCircle, CheckCircle } from 'lucide-react';
import './MessageBox.css';

const MessageBox = ({ type = 'success', message }) => {
  if (!message) return null;

  return (
    <div className={`message-box ${type}`}>
      {type === 'success' ? <CheckCircle size={18} /> : <AlertCircle size={18} />}
      <span>{message}</span>
    </div>
  );
};

export default MessageBox;
