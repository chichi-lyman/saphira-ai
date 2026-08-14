import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { SaphiraMessage } from '../../types/saphira';

interface MessageItemProps {
  message: SaphiraMessage;
}

/**
 * Chat Bubble Component for Saphira AI™
 */
const MessageItem: React.FC<MessageItemProps> = ({ message }) => {
  const isUser = message.role === 'user';
  const className = `saphira-message ${isUser ? 'user' : 'model'}`;

  return (
    <div className={className}>
      {isUser ? (
        <span>{message.content}</span>
      ) : (
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
      )}
    </div>
  );
};

export default MessageItem;
