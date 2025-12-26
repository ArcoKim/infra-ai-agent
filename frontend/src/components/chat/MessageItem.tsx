import { memo } from 'react';
import ReactMarkdown from 'react-markdown';
import { User, Bot } from 'lucide-react';
import type { Message, ChartData } from '../../types/chat';
import { ChartRenderer } from '../chart/ChartRenderer';

interface MessageBubbleProps {
  content: string;
  isUser?: boolean;
  isStreaming?: boolean;
  chartData?: ChartData | null;
  timestamp?: string;
}

const MessageBubble = memo<MessageBubbleProps>(function MessageBubble({
  content,
  isUser = false,
  isStreaming = false,
  chartData = null,
  timestamp,
}) {
  return (
    <div className={`flex gap-4 ${isUser ? 'flex-row-reverse' : ''}`}>
      {/* Avatar */}
      <div
        className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
          isUser ? 'bg-primary-600' : 'bg-gray-700 dark:bg-gray-600'
        }`}
        role="img"
        aria-label={isUser ? '사용자' : 'AI 어시스턴트'}
      >
        {isUser ? (
          <User className="w-5 h-5 text-white" aria-hidden="true" />
        ) : (
          <Bot className="w-5 h-5 text-white" aria-hidden="true" />
        )}
      </div>

      {/* Content */}
      <div className={`flex-1 max-w-3xl ${isUser ? 'text-right' : ''}`}>
        <div
          className={`inline-block px-4 py-3 rounded-2xl ${
            isUser
              ? 'bg-primary-600 rounded-br-md'
              : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-bl-md'
          }`}
        >
          {/* Message content */}
          <div className={`prose prose-sm max-w-none ${isUser ? 'text-white [&_*]:text-white' : 'text-gray-900 dark:text-gray-100 dark:prose-invert'}`}>
            <ReactMarkdown
              components={{
                img: () => null,
              }}
            >
              {content}
            </ReactMarkdown>
          </div>

          {/* Streaming indicator */}
          {isStreaming && !isUser && (
            <span
              className="inline-block w-2 h-4 bg-gray-400 dark:bg-gray-500 animate-pulse ml-1"
              aria-label="응답 생성 중"
            />
          )}
        </div>

        {/* Chart */}
        {chartData && (
          <div className="mt-4 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4">
            <ChartRenderer chartData={chartData} height={350} />
          </div>
        )}

        {/* Timestamp */}
        {timestamp && (
          <div className={`text-xs text-gray-400 dark:text-gray-500 mt-1 ${isUser ? 'text-right' : ''}`}>
            <time dateTime={timestamp}>
              {new Date(timestamp).toLocaleTimeString('ko-KR', {
                hour: '2-digit',
                minute: '2-digit',
              })}
            </time>
          </div>
        )}
      </div>
    </div>
  );
});

interface MessageItemProps {
  message: Message;
}

export const MessageItem = memo<MessageItemProps>(function MessageItem({ message }) {
  return (
    <MessageBubble
      content={message.content}
      isUser={message.role === 'user'}
      chartData={message.chart_data}
      timestamp={message.created_at}
    />
  );
});

interface StreamingMessageProps {
  content: string;
  chartData?: ChartData | null;
}

export const StreamingMessage = memo<StreamingMessageProps>(function StreamingMessage({ content, chartData }) {
  return (
    <MessageBubble
      content={content}
      isUser={false}
      isStreaming={true}
      chartData={chartData}
    />
  );
});
