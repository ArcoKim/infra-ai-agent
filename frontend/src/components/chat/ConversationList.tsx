import React from 'react';
import { Plus, MessageSquare, Trash2, Sun, Moon, LogOut, User, PanelLeftClose } from 'lucide-react';
import type { ConversationListItem } from '../../types/chat';
import { useTheme } from '../../contexts/ThemeContext';
import { useAuth } from '../../contexts/AuthContext';

interface ConversationListProps {
  conversations: ConversationListItem[];
  currentId?: string;
  onSelect: (id: string) => void;
  onNew: () => void;
  onDelete: (id: string) => void;
  onCloseSidebar?: () => void;
  isLoading?: boolean;
}

// Sidebar Bottom Component - User info & Settings
export const SidebarBottom: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  const { user, logout } = useAuth();

  return (
    <div className="p-3 bg-gray-100 dark:bg-gray-900">
      {/* Theme toggle */}
      <button
        onClick={toggleTheme}
        className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-800 transition-colors mb-2"
        aria-label={theme === 'dark' ? '라이트 모드로 전환' : '다크 모드로 전환'}
      >
        {theme === 'dark' ? (
          <Sun className="w-5 h-5 text-yellow-500" aria-hidden="true" />
        ) : (
          <Moon className="w-5 h-5 text-gray-600" aria-hidden="true" />
        )}
        <span className="text-sm text-gray-900 dark:text-white">{theme === 'dark' ? '라이트 모드' : '다크 모드'}</span>
      </button>

      {/* User info */}
      {user && (
        <div className="flex items-center gap-3 px-3 py-2 rounded-lg bg-gray-200 dark:bg-gray-800" role="region" aria-label="사용자 정보">
          <div className="w-8 h-8 rounded-full bg-primary-600 flex items-center justify-center" role="img" aria-label="사용자 아바타">
            <User className="w-4 h-4 text-white" aria-hidden="true" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate text-gray-900 dark:text-white">{user.name}</p>
            <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{user.email}</p>
          </div>
          <button
            onClick={logout}
            className="p-2 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-700 transition-colors"
            aria-label="로그아웃"
          >
            <LogOut className="w-4 h-4 text-gray-500 dark:text-gray-400" aria-hidden="true" />
          </button>
        </div>
      )}
    </div>
  );
};

export const ConversationList: React.FC<ConversationListProps> = ({
  conversations,
  currentId,
  onSelect,
  onNew,
  onDelete,
  onCloseSidebar,
  isLoading = false,
}) => {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));

    if (diffDays === 0) {
      return '오늘';
    } else if (diffDays === 1) {
      return '어제';
    } else if (diffDays < 7) {
      return `${diffDays}일 전`;
    } else {
      return date.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' });
    }
  };

  return (
    <nav className="flex flex-col h-full bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-white transition-colors" aria-label="대화 목록">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-2 mb-3">
          <button
            onClick={onNew}
            className="flex-1 flex items-center gap-3 px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 hover:bg-gray-200 dark:hover:bg-gray-800 transition-colors"
            aria-label="새 대화 시작"
          >
            <Plus className="w-5 h-5" aria-hidden="true" />
            <span>새 대화</span>
          </button>
          {onCloseSidebar && (
            <button
              onClick={onCloseSidebar}
              className="p-3 rounded-lg border border-gray-300 dark:border-gray-600 hover:bg-gray-200 dark:hover:bg-gray-800 transition-colors"
              aria-label="사이드바 닫기"
            >
              <PanelLeftClose className="w-5 h-5" aria-hidden="true" />
            </button>
          )}
        </div>
      </div>

      {/* Conversation list */}
      <div className="flex-1 overflow-y-auto p-2">
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-6 w-6 border-2 border-gray-400 dark:border-gray-500 border-t-primary-600 dark:border-t-white" />
          </div>
        ) : conversations.length === 0 ? (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p className="text-sm">대화 기록이 없습니다</p>
          </div>
        ) : (
          <ul className="space-y-1" role="list">
            {conversations.map((conv) => (
              <li key={conv.id}>
                <button
                  className={`group w-full flex items-center gap-2 p-3 rounded-lg cursor-pointer transition-colors text-left ${
                    currentId === conv.id
                      ? 'bg-gray-200 dark:bg-gray-700'
                      : 'hover:bg-gray-200 dark:hover:bg-gray-800'
                  }`}
                  onClick={() => onSelect(conv.id)}
                  aria-current={currentId === conv.id ? 'true' : undefined}
                  aria-label={`대화: ${conv.title}`}
                >
                  <MessageSquare className="w-4 h-4 flex-shrink-0 text-gray-500 dark:text-gray-400" aria-hidden="true" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm truncate">{conv.title}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      <time dateTime={conv.updated_at}>{formatDate(conv.updated_at)}</time>
                    </p>
                  </div>
                  <span
                    role="button"
                    tabIndex={0}
                    onClick={(e) => {
                      e.stopPropagation();
                      onDelete(conv.id);
                    }}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.stopPropagation();
                        onDelete(conv.id);
                      }
                    }}
                    className="opacity-0 group-hover:opacity-100 focus:opacity-100 p-1 hover:bg-gray-300 dark:hover:bg-gray-600 rounded transition-all"
                    aria-label={`${conv.title} 대화 삭제`}
                  >
                    <Trash2 className="w-4 h-4 text-gray-500 dark:text-gray-400 hover:text-red-500 dark:hover:text-red-400" aria-hidden="true" />
                  </span>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </nav>
  );
};
