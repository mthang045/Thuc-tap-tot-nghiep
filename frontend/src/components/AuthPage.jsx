import { useState } from 'react';
import { LoginForm } from './LoginForm';
import { RegisterForm } from './RegisterForm';
import { ForgotPasswordForm } from './ForgotPasswordForm';
import logoImage from '/logo.png';
import { Shield, Sparkles, Zap } from 'lucide-react';

export function AuthPage({ onLogin }) {
  const [activeView, setActiveView] = useState('login');

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-8">
      <div className="w-full max-w-6xl grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12 items-center">
        {/* Left Side - Branding */}
        <div className="hidden lg:block">
          <div className="text-center lg:text-left">
            <div className="flex justify-center lg:justify-start mb-8 animate-float">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-cyan-400 to-pink-500 rounded-full blur-3xl opacity-60"></div>
                <div className="relative bg-white p-8 rounded-full shadow-2xl shadow-cyan-500/50">
                  <img 
                    src={logoImage} 
                    alt="GenZ Logo" 
                    className="h-32 w-32 object-cover rounded-full"
                  />
                </div>
              </div>
            </div>
            
            <h1 className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-blue-400 to-pink-500 mb-4">
              GenZ Legal AI
            </h1>
            <p className="text-cyan-100/90 text-xl mb-6">
              Giải pháp pháp lý cho kỷ nguyên số
            </p>
            <p className="text-slate-400 mb-12 leading-relaxed">
              Phân tích hợp đồng thông minh với công nghệ AI & RAG, bảo vệ quyền lợi pháp lý của bạn
            </p>

            {/* Features */}
            <div className="space-y-4">
              <div className="flex items-center gap-4 bg-slate-900/60 backdrop-blur-xl p-4 rounded-xl border border-cyan-500/30">
                <div className="bg-gradient-to-br from-cyan-500 to-blue-500 p-3 rounded-lg shadow-lg shadow-cyan-500/50">
                  <Sparkles className="w-6 h-6 text-white" />
                </div>
                <div className="text-left">
                  <h3 className="text-cyan-100 mb-1">Phân tích tức thì</h3>
                  <p className="text-slate-400 text-sm">AI đọc và phân tích hợp đồng trong vài giây</p>
                </div>
              </div>

              <div className="flex items-center gap-4 bg-slate-900/60 backdrop-blur-xl p-4 rounded-xl border border-purple-500/30">
                <div className="bg-gradient-to-br from-purple-500 to-pink-500 p-3 rounded-lg shadow-lg shadow-purple-500/50">
                  <Shield className="w-6 h-6 text-white" />
                </div>
                <div className="text-left">
                  <h3 className="text-purple-100 mb-1">Bảo mật tuyệt đối</h3>
                  <p className="text-slate-400 text-sm">Dữ liệu được mã hóa và bảo vệ an toàn</p>
                </div>
              </div>

              <div className="flex items-center gap-4 bg-slate-900/60 backdrop-blur-xl p-4 rounded-xl border border-pink-500/30">
                <div className="bg-gradient-to-br from-pink-500 to-rose-500 p-3 rounded-lg shadow-lg shadow-pink-500/50">
                  <Zap className="w-6 h-6 text-white" />
                </div>
                <div className="text-left">
                  <h3 className="text-pink-100 mb-1">Cảnh báo thông minh</h3>
                  <p className="text-slate-400 text-sm">Phát hiện vi phạm pháp luật tự động</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Side - Auth Forms */}
        <div className="relative">
          {/* Mobile Logo */}
          <div className="lg:hidden flex justify-center mb-8 animate-float">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-cyan-400 to-pink-500 rounded-full blur-2xl opacity-60"></div>
              <div className="relative bg-white p-6 rounded-full shadow-2xl shadow-cyan-500/50">
                <img 
                  src={logoImage} 
                  alt="GenZ Logo" 
                  className="h-20 w-20 object-cover rounded-full"
                />
              </div>
            </div>
          </div>

          <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/20 to-pink-500/20 rounded-3xl blur-2xl"></div>
          <div className="relative bg-slate-900/70 backdrop-blur-xl rounded-3xl shadow-2xl border border-slate-700/50 p-8 md:p-10">
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
              <RegisterForm onRegister={onLogin} />
            )}
            {activeView === 'forgot' && (
              <ForgotPasswordForm onBack={() => setActiveView('login')} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
