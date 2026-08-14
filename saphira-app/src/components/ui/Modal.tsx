import React, { useEffect } from 'react';

interface ModalProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
}

/**
 * Dialog Container for Saphira AI™
 */
const Modal: React.FC<ModalProps> = ({ open, onClose, title, children }) => {
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div className="saphira-modal-overlay" onClick={onClose} role="presentation">
      <div
        className="saphira-modal"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby={title ? 'saphira-modal-title' : undefined}
      >
        {title && (
          <h2 id="saphira-modal-title" style={{ marginBottom: '1rem' }}>
            {title}
          </h2>
        )}
        {children}
      </div>
    </div>
  );
};

export default Modal;
