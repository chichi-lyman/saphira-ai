import React, { useEffect, useRef } from 'react';
import { useChat } from '../../context/ChatContext';
import MessageItem from './MessageItem';

/**
 * Conversation Stream Container for Saphira AI™
 * Renders the sequence of user prompts and Saphira responses
 * with markdown rendering and code block highlighting.
 */
const MessageList: React.FC = () => {
  const { messages } = useChat();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="saphira-message-list">
      {messages.length === 0 && (
        <div
          style={{
            margin: 'auto',
            textAlign: 'center',
            color: 'var(--saphira-muted)',
            maxWidth: 360,
          }}
        >
          <p style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>Saphira AI™</p>
          <p style={{ fontSize: '0.9rem' }}>
            Say what you want. Saphira understands the intent, coordinates the right
            intelligence, and responds.
          </p>
        </div>
      )}
      {messages.map((m, i) => (
        <MessageItem key={m.id ?? `msg-${i}`} message={m} />
      ))}
      <div ref={bottomRef} />
    </div>
  );
};

export default MessageList;
