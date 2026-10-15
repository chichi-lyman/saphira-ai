import React, { useRef, useState, type KeyboardEvent } from 'react';
import Button from '../ui/Button';
import { useUser } from '../../context/UserContext';
import { useChat } from '../../context/ChatContext';

/**
 * Chat composer for Saphira AI™
 */
const ChatInput: React.FC = () => {
  const { user } = useUser();
  const { sendMessage, isStreaming } = useChat();
  const [text, setText] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = async () => {
    const trimmed = text.trim();
    if (!trimmed || isStreaming) return;
    setText('');
    await sendMessage(trimmed);
    textareaRef.current?.focus();
  };

  const onKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      void handleSubmit();
    }
  };

  const displayName = user?.name;
  const placeholder =
    displayName && displayName !== 'Guest'
      ? `Message Saphira, ${displayName}…`
      : 'Message Saphira…';

  return (
    <div className="saphira-chat-input">
      <textarea
        ref={textareaRef}
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={onKeyDown}
        placeholder={placeholder}
        rows={1}
        disabled={isStreaming}
        aria-label="Chat message input"
      />
      <Button type="button" onClick={() => void handleSubmit()} disabled={isStreaming || !text.trim()}>
        {isStreaming ? 'Sending…' : 'Send'}
      </Button>
    </div>
  );
};

export default ChatInput;
