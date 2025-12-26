import { useState, useCallback, useRef, useEffect } from 'react';
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

  // Store options in ref to avoid dependency issues
  const optionsRef = useRef(options);
  useEffect(() => {
    optionsRef.current = options;
  }, [options]);

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
      optionsRef.current.onError?.('Not authenticated');
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
              optionsRef.current.onContent?.(chunk.content);
            }
            break;

          case 'chart':
            if (chunk.chartData) {
              setChartData(chunk.chartData);
              optionsRef.current.onChart?.(chunk.chartData);
            }
            break;

          case 'done':
            if (chunk.conversationId) {
              setConversationId(chunk.conversationId);
              optionsRef.current.onDone?.(chunk.conversationId);
            }
            eventSource.close();
            setIsStreaming(false);
            break;

          case 'error':
            optionsRef.current.onError?.(chunk.error || 'Unknown error');
            eventSource.close();
            setIsStreaming(false);
            break;
        }
      } catch (error) {
        console.error('Error parsing SSE message:', error, 'Raw data:', event.data);
      }
    };

    eventSource.onerror = () => {
      eventSource.close();
      setIsStreaming(false);
      optionsRef.current.onError?.('Connection lost');
    };
  }, []);

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
