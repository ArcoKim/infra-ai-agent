import { useState, useCallback, useRef } from 'react';
import type { StreamChunk, ChartData } from '../types/chat';
import { getAccessToken } from '../utils/token';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

interface UseSSEOptions {
  onContent?: (content: string) => void;
  onChart?: (chartData: ChartData) => void;
  onDone?: (conversationId: string) => void;
  onError?: (error: string) => void;
}

export const useSSE = (options: UseSSEOptions = {}) => {
  const [streamingContent, setStreamingContent] = useState('');
  const [chartData, setChartData] = useState<ChartData | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  const startStream = useCallback((message: string, existingConversationId?: string) => {
    // Close existing connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    // Reset state
    setStreamingContent('');
    setChartData(null);
    setIsStreaming(true);

    const token = getAccessToken();
    if (!token) {
      options.onError?.('Not authenticated');
      setIsStreaming(false);
      return;
    }

    // Build URL with query parameters
    const params = new URLSearchParams({
      message,
      token,
    });
    if (existingConversationId) {
      params.append('conversation_id', existingConversationId);
    }

    const url = `${API_BASE_URL}/chat/stream?${params.toString()}`;
    const eventSource = new EventSource(url);
    eventSourceRef.current = eventSource;

    eventSource.onmessage = (event) => {
      try {
        const chunk: StreamChunk = JSON.parse(event.data);

        switch (chunk.type) {
          case 'content':
            if (chunk.content) {
              setStreamingContent(prev => prev + chunk.content);
              options.onContent?.(chunk.content);
            }
            break;

          case 'chart':
            if (chunk.chartData) {
              setChartData(chunk.chartData);
              options.onChart?.(chunk.chartData);
            }
            break;

          case 'done':
            if (chunk.conversationId) {
              setConversationId(chunk.conversationId);
              options.onDone?.(chunk.conversationId);
            }
            eventSource.close();
            setIsStreaming(false);
            break;

          case 'error':
            options.onError?.(chunk.error || 'Unknown error');
            eventSource.close();
            setIsStreaming(false);
            break;
        }
      } catch (e) {
        console.error('Error parsing SSE message:', e);
      }
    };

    eventSource.onerror = () => {
      eventSource.close();
      setIsStreaming(false);
      options.onError?.('Connection lost');
    };
  }, [options]);

  const stopStream = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setIsStreaming(false);
  }, []);

  const resetStream = useCallback(() => {
    setStreamingContent('');
    setChartData(null);
    setConversationId(null);
  }, []);

  return {
    streamingContent,
    chartData,
    isStreaming,
    conversationId,
    startStream,
    stopStream,
    resetStream,
  };
};
