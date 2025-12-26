import React, { useState, useRef, useEffect } from 'react';
import { Send, Square } from 'lucide-react';

interface ChatInputProps {
  onSend: (message: string) => void;
  onStop?: () => void;
  disabled?: boolean;
  isStreaming?: boolean;
  placeholder?: string;
}

const INPUT_HEIGHT = 44;

export const ChatInput: React.FC<ChatInputProps> = ({
  onSend,
  onStop,
  disabled = false,
  isStreaming = false,
  placeholder = '메시지를 입력하세요...',
}) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled && !isStreaming) {
      onSend(message.trim());
      setMessage('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = `${INPUT_HEIGHT}px`;
      const scrollHeight = textareaRef.current.scrollHeight;
      if (scrollHeight > INPUT_HEIGHT) {
        textareaRef.current.style.height = `${Math.min(scrollHeight, 200)}px`;
      }
    }
  }, [message]);

  return (
    <form onSubmit={handleSubmit} className="bg-white dark:bg-gray-800 p-4 transition-colors" role="form" aria-label="메시지 입력">
      <div className="flex items-end gap-3 max-w-4xl mx-auto">
        <textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled || isStreaming}
          rows={1}
          style={{ height: INPUT_HEIGHT }}
          className="flex-1 resize-none rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 px-4 leading-[42px] focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:bg-gray-100 dark:disabled:bg-gray-600 disabled:cursor-not-allowed placeholder-gray-400 dark:placeholder-gray-500 transition-colors box-border"
          aria-label="메시지 입력창"
          aria-describedby="input-hint"
        />

        {isStreaming ? (
          <button
            type="button"
            onClick={onStop}
            style={{ height: INPUT_HEIGHT, width: INPUT_HEIGHT }}
            className="flex-shrink-0 flex items-center justify-center rounded-xl bg-red-500 text-white hover:bg-red-600 transition-colors"
            aria-label="응답 생성 중지"
          >
            <Square className="w-5 h-5 fill-current" aria-hidden="true" />
          </button>
        ) : (
          <button
            type="submit"
            disabled={!message.trim() || disabled}
            style={{ height: INPUT_HEIGHT, width: INPUT_HEIGHT }}
            className="flex-shrink-0 flex items-center justify-center rounded-xl bg-primary-600 text-white hover:bg-primary-700 disabled:bg-gray-300 dark:disabled:bg-gray-600 disabled:cursor-not-allowed transition-colors"
            aria-label="메시지 전송"
          >
            <Send className="w-5 h-5" aria-hidden="true" />
          </button>
        )}
      </div>

      <div className="text-center mt-2" id="input-hint">
        <span className="text-xs text-gray-400 dark:text-gray-500">
          Enter로 전송, Shift+Enter로 줄바꿈
        </span>
      </div>
    </form>
  );
};
