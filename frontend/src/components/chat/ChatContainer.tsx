import React, { useState, useEffect, useCallback } from 'react';
import { PanelLeft } from 'lucide-react';
import type { Message, ConversationListItem, ChartData } from '../../types/chat';
import { chatApi } from '../../api/chat';
import { useSSE } from '../../hooks/useSSE';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';
import { ConversationList, SidebarBottom } from './ConversationList';

export const ChatContainer: React.FC = () => {
  const [conversations, setConversations] = useState<ConversationListItem[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoadingConversations, setIsLoadingConversations] = useState(true);
  const [isLoadingMessages, setIsLoadingMessages] = useState(false);
  const [isDeletingId, setIsDeletingId] = useState<string | null>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  const {
    streamingContent,
    chartData,
    isStreaming,
    startStream,
    stopStream,
    resetStream,
  } = useSSE({
    onDone: async (convId) => {
      // Reload messages after streaming completes
      if (convId) {
        setCurrentConversationId(convId);
        await loadMessages(convId);
        await loadConversations();
      }
      resetStream();
    },
    onError: (error) => {
      console.error('Stream error:', error);
      resetStream();
    },
  });

  // Load conversations
  const loadConversations = useCallback(async () => {
    try {
      const data = await chatApi.getConversations();
      setConversations(data);
    } catch (error) {
      console.error('Failed to load conversations:', error);
    } finally {
      setIsLoadingConversations(false);
    }
  }, []);

  // Load messages for a conversation
  const loadMessages = useCallback(async (conversationId: string) => {
    setIsLoadingMessages(true);
    try {
      const data = await chatApi.getConversation(conversationId);
      setMessages(data.messages);
    } catch (error) {
      console.error('Failed to load messages:', error);
      setMessages([]);
    } finally {
      setIsLoadingMessages(false);
    }
  }, []);

  // Initial load
  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  // Load messages when conversation changes
  useEffect(() => {
    if (currentConversationId) {
      loadMessages(currentConversationId);
    } else {
      setMessages([]);
    }
  }, [currentConversationId, loadMessages]);

  // Handle sending a message
  const handleSend = (message: string) => {
    // Add user message to UI immediately
    const tempUserMessage: Message = {
      id: `temp-${Date.now()}`,
      conversation_id: currentConversationId || '',
      role: 'user',
      content: message,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMessage]);

    // Start streaming
    startStream(message, currentConversationId || undefined);
  };

  // Handle new conversation
  const handleNewConversation = () => {
    setCurrentConversationId(null);
    setMessages([]);
    resetStream();
  };

  // Handle delete conversation
  const handleDeleteConversation = async (id: string) => {
    if (isDeletingId) return; // Prevent multiple deletions

    setIsDeletingId(id);
    try {
      await chatApi.deleteConversation(id);
      setConversations((prev) => prev.filter((c) => c.id !== id));
      if (currentConversationId === id) {
        setCurrentConversationId(null);
        setMessages([]);
      }
    } catch (error) {
      console.error('Failed to delete conversation:', error);
    } finally {
      setIsDeletingId(null);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
      {/* Top area - Sidebar + Messages */}
      <div className="flex flex-1 min-h-0">
        {/* Sidebar Top */}
        <div
          className={`flex-shrink-0 transition-all duration-300 border-r border-gray-300 dark:border-gray-600 ${
            isSidebarOpen ? 'w-80' : 'w-0 border-r-0'
          } overflow-hidden`}
        >
          <div className="w-80 h-full">
            <ConversationList
              conversations={conversations}
              currentId={currentConversationId || undefined}
              onSelect={setCurrentConversationId}
              onNew={handleNewConversation}
              onDelete={handleDeleteConversation}
              onCloseSidebar={() => setIsSidebarOpen(false)}
              isLoading={isLoadingConversations}
              deletingId={isDeletingId}
            />
          </div>
        </div>

        {/* Main chat area */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Header with sidebar toggle */}
          {!isSidebarOpen && (
            <div className="flex items-center gap-2 p-2 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 transition-colors">
              <button
                onClick={() => setIsSidebarOpen(true)}
                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                title="사이드바 열기"
              >
                <PanelLeft className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              </button>
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                반도체 Infra AI Agent
              </span>
            </div>
          )}

          {/* Messages */}
          <MessageList
            messages={messages}
            streamingContent={streamingContent}
            streamingChartData={chartData as ChartData | null}
            isStreaming={isStreaming}
          />
        </div>
      </div>

      {/* Bottom area - unified border-t */}
      <div className="flex border-t border-gray-200 dark:border-gray-700">
        {/* Sidebar Bottom */}
        <div
          className={`flex-shrink-0 transition-all duration-300 border-r border-gray-300 dark:border-gray-600 ${
            isSidebarOpen ? 'w-80' : 'w-0 border-r-0'
          } overflow-hidden`}
        >
          <div className="w-80">
            <SidebarBottom />
          </div>
        </div>

        {/* Chat Input */}
        <div className="flex-1 min-w-0">
          <ChatInput
            onSend={handleSend}
            onStop={stopStream}
            disabled={isLoadingMessages}
            isStreaming={isStreaming}
          />
        </div>
      </div>
    </div>
  );
};
