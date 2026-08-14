/**
 * Saphira AI™ Active Conversation State Provider
 */

import React, {
  createContext,
  useContext,
  useMemo,
  useState,
  useCallback,
  ReactNode,
} from 'react';
import type { SaphiraMessage, SaphiraThread } from '../types/saphira';

interface ChatContextValue {
  messages: SaphiraMessage[];
  threads: SaphiraThread[];
  activeThreadId: string | null;
  addMessage: (message: SaphiraMessage) => void;
  setMessages: (messages: SaphiraMessage[]) => void;
  clearMessages: () => void;
  setThreads: (threads: SaphiraThread[]) => void;
  setActiveThreadId: (id: string | null) => void;
}

const ChatContext = createContext<ChatContextValue | undefined>(undefined);

export function ChatProvider({ children }: { children: ReactNode }) {
  const [messages, setMessages] = useState<SaphiraMessage[]>([]);
  const [threads, setThreads] = useState<SaphiraThread[]>([]);
  const [activeThreadId, setActiveThreadId] = useState<string | null>(null);

  const addMessage = useCallback((message: SaphiraMessage) => {
    setMessages((prev) => [...prev, message]);
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  const value = useMemo(
    () => ({
      messages,
      threads,
      activeThreadId,
      addMessage,
      setMessages,
      clearMessages,
      setThreads,
      setActiveThreadId,
    }),
    [messages, threads, activeThreadId, addMessage, clearMessages]
  );

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
}

export function useChat(): ChatContextValue {
  const ctx = useContext(ChatContext);
  if (!ctx) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return ctx;
}
