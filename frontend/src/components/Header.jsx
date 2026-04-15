import { useState } from 'react';
import { LogIn, UserPlus, User, LogOut, FileText, Settings, Home, Crown, Shield } from 'lucide-react';
import logoImage from '/logo.png';
import { AuthModal } from './AuthModal';

export function Header({ isAuthenticated, isAdmin, userEmail, userAvatar, currentPage, onLogin, onLogout, onNavigate }) {
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authView, setAuthView] = useState('login');
  const [showUserMenu, setShowUserMenu] = useState(false);

  const handleOpenAuth = (view) => {
    setAuthView(view);
    setShowAuthModal(true);
  };

  const handleLoginSuccess = async (email, password) => {
    const result = await onLogin(email, password);
    if (result.success) {
      setShowAuthModal(false);
    }
    return result;
  };

  return (
    <>
      <header className="relative z-20 border-b border-slate-700/50 backdrop-blur-xl bg-slate-900/50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <button 
              onClick={() => onNavigate('home')}
              className="flex items-center gap-3 hover:opacity-80 transition-opacity"
            >
              <div className="relative flex-shrink-0">
                <div className="absolute inset-0 bg-gradient-to-r from-cyan-400 to-pink-500 rounded-full blur-lg opacity-40"></div>
                <div className="relative w-12 h-12 rounded-full overflow-hidden flex items-center justify-center">
                  <img 
                    src={logoImage} 
                    alt="GenZ Logo" 
                    className="w-full h-full object-cover shadow-lg shadow-cyan-500/30"
                  />
                </div>
              </div>
              <div className="hidden sm:block">
                <h1 className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-pink-500 text-xl">
                  GenZ Legal AI
                </h1>
                <p className="text-slate-500 text-xs">Giải pháp pháp lý thông minh</p>
              </div>
            </button>

            {/* Navigation */}
            <nav className="hidden md:flex items-center gap-2">
              {isAuthenticated && (
                <>
                  <button
                    onClick={() => onNavigate('home')}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                      currentPage === 'home'
                        ? 'bg-cyan-600/20 text-cyan-300 border border-cyan-500/30'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                    }`}
                  >
                    <Home className="w-4 h-4" />
                    Trang chủ
                  </button>
                  <button
                    onClick={() => onNavigate('history')}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                      currentPage === 'history'
                        ? 'bg-cyan-600/20 text-cyan-300 border border-cyan-500/30'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                    }`}
                  >
                    <FileText className="w-4 h-4" />
                    Lịch sử
                  </button>
                </>
              )}
              <button
                onClick={() => onNavigate('pricing')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                  currentPage === 'pricing'
                    ? 'bg-cyan-600/20 text-cyan-300 border border-cyan-500/30'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                }`}
              >
                <Crown className="w-4 h-4" />
                Gói dịch vụ
              </button>
              {isAdmin && (
                <button
                  onClick={() => onNavigate('admin')}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                    currentPage === 'admin'
                      ? 'bg-red-600/20 text-red-300 border border-red-500/30'
                      : 'text-red-400 hover:text-red-300 hover:bg-red-900/20'
                  }`}
                >
                  <Shield className="w-4 h-4" />
                  Admin
                </button>
              )}
            </nav>

            {/* Auth Buttons */}
            {!isAuthenticated ? (
              <div className="flex items-center gap-3">
                <button
                  onClick={() => handleOpenAuth('login')}
                  className="flex items-center gap-2 px-4 py-2 text-cyan-300 hover:text-cyan-200 transition-colors"
                >
                  <LogIn className="w-4 h-4" />
                  <span className="hidden sm:inline">Đăng nhập</span>
                </button>
                <button
                  onClick={() => handleOpenAuth('register')}
                  className="flex items-center gap-2 px-5 py-2 bg-gradient-to-r from-cyan-600 to-pink-600 hover:from-cyan-500 hover:to-pink-500 text-white rounded-lg transition-all shadow-lg shadow-cyan-500/30"
                >
                  <UserPlus className="w-4 h-4" />
                  <span className="hidden sm:inline">Đăng ký</span>
                </button>
              </div>
            ) : (
              <div className="relative">
                <button
                  onClick={() => setShowUserMenu(!showUserMenu)}
                  className="flex items-center gap-3 px-4 py-2 bg-slate-800/50 hover:bg-slate-800 border border-slate-700 rounded-lg transition-all"
                >
                  <div className="w-8 h-8 rounded-full overflow-hidden flex items-center justify-center flex-shrink-0 bg-slate-800">
                    {userAvatar ? (
                      <img src={userAvatar} alt="avatar" className="w-full h-full object-cover" />
                    ) : (
                      <div className="bg-gradient-to-br from-cyan-500 to-pink-500 w-full h-full flex items-center justify-center">
                        <User className="w-4 h-4 text-white" />
                      </div>
                    )}
                  </div>
                  <div className="text-left hidden sm:block">
                    <div className="text-slate-300 text-sm">{userEmail}</div>
                  </div>
                </button>

                {/* User Menu Dropdown */}
                {showUserMenu && (
                  <>
                    <div 
                      className="fixed inset-0 z-30" 
                      onClick={() => setShowUserMenu(false)}
                    />
                    <div className="absolute right-0 top-full mt-2 w-64 bg-slate-900/95 backdrop-blur-xl border border-slate-700 rounded-xl shadow-2xl shadow-black/50 overflow-hidden z-40">
                      <div className="p-4 border-b border-slate-700">
                        <div className="flex items-center gap-3 mb-2">
                          <div className="w-10 h-10 rounded-full overflow-hidden flex items-center justify-center flex-shrink-0 bg-slate-800">
                            {userAvatar ? (
                              <img src={userAvatar} alt="avatar" className="w-full h-full object-cover" />
                            ) : (
                              <div className="bg-gradient-to-br from-cyan-500 to-pink-500 w-full h-full flex items-center justify-center">
                                <User className="w-5 h-5 text-white" />
                              </div>
                            )}
                          </div>
                          <div>
                            <div className="text-slate-300">Tài khoản</div>
                            <div className="text-cyan-400 text-sm">{userEmail}</div>
                          </div>
                        </div>
                        {isAdmin && (
                          <div className="mt-2 px-2 py-1 bg-red-500/20 border border-red-500/30 rounded text-red-300 text-xs text-center">
                            Admin Account
                          </div>
                        )}
                      </div>
                      <div className="p-2">
                        {isAdmin && (
                          <button 
                            onClick={() => {
                              setShowUserMenu(false);
                              onNavigate('admin');
                            }}
                            className="w-full flex items-center gap-3 px-4 py-2.5 text-red-400 hover:bg-red-900/20 rounded-lg transition-colors"
                          >
                            <Shield className="w-4 h-4" />
                            Admin Dashboard
                          </button>
                        )}
                        <button 
                          onClick={() => {
                            setShowUserMenu(false);
                            onNavigate('pricing');
                          }}
                          className="w-full flex items-center gap-3 px-4 py-2.5 text-pink-400 hover:bg-pink-900/20 rounded-lg transition-colors"
                        >
                          <Crown className="w-4 h-4" />
                          Nâng cấp Pro
                        </button>
                        <button 
                          onClick={() => {
                            setShowUserMenu(false);
                            onNavigate('history');
                          }}
                          className="w-full flex items-center gap-3 px-4 py-2.5 text-slate-300 hover:bg-slate-800 rounded-lg transition-colors"
                        >
                          <FileText className="w-4 h-4" />
                          Lịch sử phân tích
                        </button>
                        <button 
                          onClick={() => {
                            setShowUserMenu(false);
                            onNavigate('settings');
                          }}
                          className="w-full flex items-center gap-3 px-4 py-2.5 text-slate-300 hover:bg-slate-800 rounded-lg transition-colors"
                        >
                          <Settings className="w-4 h-4" />
                          Cài đặt tài khoản
                        </button>
                        <div className="my-2 border-t border-slate-700"></div>
                        <button 
                          onClick={() => {
                            setShowUserMenu(false);
                            onLogout();
                          }}
                          className="w-full flex items-center gap-3 px-4 py-2.5 text-red-400 hover:bg-red-900/20 rounded-lg transition-colors"
                        >
                          <LogOut className="w-4 h-4" />
                          Đăng xuất
                        </button>
                      </div>
                    </div>
                  </>
                )}
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Auth Modal */}
      {showAuthModal && (
        <AuthModal
          initialView={authView}
          onClose={() => setShowAuthModal(false)}
          onLogin={handleLoginSuccess}
        />
      )}
    </>
  );
}