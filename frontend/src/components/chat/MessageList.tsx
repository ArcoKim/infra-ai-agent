import { useRef, useEffect, memo } from 'react';
import type { Message, ChartData } from '../../types/chat';
import { MessageItem, StreamingMessage } from './MessageItem';
import { TypingIndicator } from '../common/Loading';

interface MessageListProps {
  messages: Message[];
  streamingContent?: string;
  streamingChartData?: ChartData | null;
  isStreaming?: boolean;
}

export const MessageList = memo<MessageListProps>(function MessageList({
  messages,
  streamingContent = '',
  streamingChartData = null,
  isStreaming = false,
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const hasContent = messages.length > 0 || isStreaming;

  // Auto scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingContent]);

  return (
    <div className={`flex-1 min-h-0 p-4 space-y-6 bg-gray-50 dark:bg-gray-900 transition-colors ${hasContent ? 'overflow-y-auto' : 'overflow-hidden'}`}>
      {messages.length === 0 && !isStreaming && (
        <div className="flex flex-col items-center justify-center h-full text-center">
          <div className="w-16 h-16 bg-primary-100 dark:bg-primary-900/30 rounded-full flex items-center justify-center mb-4">
            <svg className="w-8 h-8 text-primary-600 dark:text-primary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">반도체 Infra AI Agent</h3>
          <p className="text-gray-500 dark:text-gray-400 max-w-md">
            센서 데이터 조회, 그래프 생성, 장비 상태 분석 등을 도와드립니다.
            <br />
            예: "온도 센서 그래프 보여줘", "최근 압력 통계 알려줘"
          </p>
        </div>
      )}

      {messages.map((message) => (
        <MessageItem key={message.id} message={message} />
      ))}

      {/* Streaming message */}
      {isStreaming && streamingContent && (
        <StreamingMessage content={streamingContent} chartData={streamingChartData} />
      )}

      {/* Typing indicator */}
      {isStreaming && !streamingContent && (
        <div className="flex gap-4 items-center">
          <div className="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center bg-gray-700 dark:bg-gray-600">
            <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
          <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl rounded-bl-md">
            <TypingIndicator />
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
});
