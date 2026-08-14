import React, { useState, useRef, useCallback } from 'react';
import { useChat } from '../../context/ChatContext';
import { useUser } from '../../context/UserContext';
import { useSaphiraStream } from '../../hooks/useSaphiraStream';
import type { SaphiraMessage } from '../../types/saphira';
import Button from '../ui/Button';

/**
 * Prompt Input UI Component for Saphira AI™
 * Captures user text and submits it to the Saphira API handler.
 */
const ChatInput: React.FC = () => {
  const [text, setText] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const { messages, addMessage, setMessages } = useChat();
  const { user } = useUser();
  const { isStreaming, startStream, streamedContent } = useSaphiraStream();

  // When streaming updates, keep the last model message in sync
  React.useEffect(() => {
    if (!isStreaming || !streamedContent) return;
    setMessages((prev) => {
      const next = [...prev];
      const last = next[next.length - 1];
      if (last && last.role === 'model') {
        next[next.length - 1] = { ...last, content: streamedContent };
        return next;
      }
      return next;
    });
  }, [streamedContent, isStreaming, setMessages]);

  const handleSubmit = useCallback(async () => {
    const trimmed = text.trim();
    if (!trimmed || isStreaming) return;

    const userMsg: SaphiraMessage = {
      id: `u-${Date.now()}`,
      role: 'user',
      content: trimmed,
      createdAt: new Date().toISOString(),
    };

    const modelPlaceholder: SaphiraMessage = {
      id: `m-${Date.now()}`,
      role: 'model',
      content: '',
      createdAt: new Date().toISOString(),
    };

    addMessage(userMsg);
    addMessage(modelPlaceholder);
    setText('');

    const history: SaphiraMessage[] = [...messages, userMsg];

    try {
      await startStream(history);
    } catch {
      // Error already stored in hook; ensure placeholder shows failure if empty
      setMessages((prev) => {
        const next = [...prev];
        const last = next[next.length - 1];
        if (last && last.role === 'model' && !last.content) {
          next[next.length - 1] = {
            ...last,
            content: 'Sorry, I could not complete that request. Please try again.',
          };
        }
        return next;
      });
    }
  }, [text, isStreaming, messages, addMessage, setMessages, startStream]);

  const onKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      void handleSubmit();
    }
  };

  return (
    <div className="saphira-chat-input">
      <textarea
        ref={textareaRef}
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={onKeyDown}
        placeholder={user.name !== 'Guest' ? `Message Saphira, ${user.name}…` : 'Message Saphira…'}
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
