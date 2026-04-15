import { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { LoginForm } from './LoginForm';
import { RegisterForm } from './RegisterForm';
import { ForgotPasswordForm } from './ForgotPasswordForm';

export function AuthModal({ initialView, onClose, onLogin }) {
  const [activeView, setActiveView] = useState(initialView);

  // Prevent body scroll when modal is open
  useEffect(() => {
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, []);

  // Close on escape key
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, [onClose]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/70 backdrop-blur-sm animate-fade-in"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative w-full max-w-md animate-fade-in">
        <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/20 to-pink-500/20 rounded-3xl blur-2xl"></div>
        <div className="relative bg-slate-900/95 backdrop-blur-xl rounded-3xl shadow-2xl border border-slate-700/50 p-8 max-h-[90vh] overflow-y-auto">
          {/* Close Button */}
          <button
            onClick={onClose}
            className="absolute top-4 right-4 p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition-all"
          >
            <X className="w-5 h-5" />
          </button>

          {/* Tabs */}
          {activeView !== 'forgot' && (
            <div className="flex gap-2 mb-8 bg-slate-800/50 p-1.5 rounded-xl">
              <button
                onClick={() => setActiveView('login')}
                className={`flex-1 py-3 px-4 rounded-lg transition-all duration-300 ${
                  activeView === 'login'
                    ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-lg shadow-cyan-500/30'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Đăng nhập
              </button>
              <button
                onClick={() => setActiveView('register')}
                className={`flex-1 py-3 px-4 rounded-lg transition-all duration-300 ${
                  activeView === 'register'
                    ? 'bg-gradient-to-r from-pink-600 to-purple-600 text-white shadow-lg shadow-pink-500/30'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Đăng ký
              </button>
            </div>
          )}

          {/* Forms */}
          {activeView === 'login' && (
            <LoginForm 
              onLogin={onLogin} 
              onForgotPassword={() => setActiveView('forgot')}
            />
          )}
          {activeView === 'register' && (
            <RegisterForm onRegister={() => setActiveView('login')} />
          )}
          {activeView === 'forgot' && (
            <ForgotPasswordForm onBack={() => setActiveView('login')} />
          )}
        </div>
      </div>
    </div>
  );
}
