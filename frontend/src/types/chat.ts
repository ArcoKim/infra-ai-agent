export interface Message {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  chart_data?: ChartData | null;
  created_at: string;
}

export interface Conversation {
  id: string;
  user_id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface ConversationListItem {
  id: string;
  title: string;
  updated_at: string;
  last_message?: string | null;
}

export interface ConversationWithMessages extends Conversation {
  messages: Message[];
}

export interface ChartData {
  type: 'line' | 'bar' | 'scatter' | 'gauge';
  title: string;
  options: Record<string, unknown>;
}

export interface StreamChunk {
  type: 'content' | 'chart' | 'done' | 'error';
  content?: string;
  chartData?: ChartData;
  conversationId?: string;
  error?: string;
}

export interface ChatState {
  conversations: ConversationListItem[];
  currentConversation: ConversationWithMessages | null;
  isLoading: boolean;
  isStreaming: boolean;
  streamingContent: string;
  streamingChartData: ChartData | null;
}
