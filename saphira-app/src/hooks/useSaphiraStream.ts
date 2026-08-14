/**
 * Saphira AI™ Streaming Custom Hook
 * Handles real-time token streaming so text appears dynamically
 * word-by-word on screen as Saphira responds.
 */

import { useCallback, useRef, useState } from 'react';
import { streamChat } from '../services/saphiraApi';
import type { SaphiraMessage } from '../types/saphira';

export interface UseSaphiraStreamResult {
  isStreaming: boolean;
  streamError: string | null;
  streamedContent: string;
  startStream: (messages: SaphiraMessage[]) => Promise<string>;
  stopStream: () => void;
  resetStream: () => void;
}

export function useSaphiraStream(): UseSaphiraStreamResult {
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamError, setStreamError] = useState<string | null>(null);
  const [streamedContent, setStreamedContent] = useState('');
  const abortRef = useRef(false);

  const stopStream = useCallback(() => {
    abortRef.current = true;
    setIsStreaming(false);
  }, []);

  const resetStream = useCallback(() => {
    setStreamedContent('');
    setStreamError(null);
    abortRef.current = false;
  }, []);

  const startStream = useCallback(async (messages: SaphiraMessage[]): Promise<string> => {
    abortRef.current = false;
    setIsStreaming(true);
    setStreamError(null);
    setStreamedContent('');

    let full = '';

    try {
      for await (const chunk of streamChat(messages)) {
        if (abortRef.current) break;
        full += chunk;
        setStreamedContent(full);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Streaming failed';
      setStreamError(message);
      throw err;
    } finally {
      setIsStreaming(false);
    }

    return full;
  }, []);

  return {
    isStreaming,
    streamError,
    streamedContent,
    startStream,
    stopStream,
    resetStream,
  };
}
