import React from 'react';
import { Sun, Moon } from 'lucide-react';
import { RegisterForm } from '../components/auth/RegisterForm';
import { useTheme } from '../contexts/ThemeContext';

export const RegisterPage: React.FC = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-500 to-primary-700 dark:from-gray-800 dark:to-gray-900 p-4 transition-colors">
      {/* Theme toggle button */}
      <button
        onClick={toggleTheme}
        className="fixed top-4 right-4 p-2 rounded-lg bg-white/20 hover:bg-white/30 dark:bg-gray-700/50 dark:hover:bg-gray-600/50 transition-colors"
        title={theme === 'dark' ? '라이트 모드' : '다크 모드'}
      >
        {theme === 'dark' ? (
          <Sun className="w-5 h-5 text-yellow-300" />
        ) : (
          <Moon className="w-5 h-5 text-white" />
        )}
      </button>
      <RegisterForm />
    </div>
  );
};
