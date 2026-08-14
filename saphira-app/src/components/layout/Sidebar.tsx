import React from 'react';
import { useChat } from '../../context/ChatContext';

/**
 * Navigation & History Panel for Saphira AI™
 * Displays past chat threads, saved context, and settings toggles.
 */
const Sidebar: React.FC = () => {
  const { threads, activeThreadId, setActiveThreadId, clearMessages } = useChat();

  const handleNewChat = () => {
    setActiveThreadId(null);
    clearMessages();
  };

  return (
    <aside className="saphira-sidebar">
      <button
        type="button"
        className="saphira-btn"
        style={{ width: '100%', marginBottom: '1.25rem' }}
        onClick={handleNewChat}
      >
        New chat
      </button>
      <h2>Recent</h2>
      {threads.length === 0 ? (
        <p style={{ fontSize: '0.85rem', color: 'var(--saphira-muted)' }}>
          No conversations yet
        </p>
      ) : (
        threads.map((t) => (
          <div
            key={t.id}
            className={`saphira-thread-item${activeThreadId === t.id ? ' active' : ''}`}
            onClick={() => setActiveThreadId(t.id)}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') setActiveThreadId(t.id);
            }}
          >
            {t.title || 'Untitled'}
          </div>
        ))
      )}
    </aside>
  );
};

export default Sidebar;
