import api from './index';
import type { ConversationListItem, ConversationWithMessages, Conversation } from '../types/chat';

export const chatApi = {
  getConversations: async (): Promise<ConversationListItem[]> => {
    const response = await api.get<ConversationListItem[]>('/conversations/');
    return response.data;
  },

  getConversation: async (id: string): Promise<ConversationWithMessages> => {
    const response = await api.get<ConversationWithMessages>(`/conversations/${id}`);
    return response.data;
  },

  createConversation: async (): Promise<Conversation> => {
    const response = await api.post<Conversation>('/conversations/');
    return response.data;
  },

  updateTitle: async (id: string, title: string): Promise<Conversation> => {
    const response = await api.patch<Conversation>(`/conversations/${id}/title`, { title });
    return response.data;
  },

  deleteConversation: async (id: string): Promise<void> => {
    await api.delete(`/conversations/${id}`);
  },
};
