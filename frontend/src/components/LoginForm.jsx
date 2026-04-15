import { useState } from 'react';
import { Mail, Lock, LogIn, Eye, EyeOff } from 'lucide-react';

export function LoginForm({ onLogin, onForgotPassword }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validation
    if (!email || !password) {
      alert('Vui lòng nhập đầy đủ email và mật khẩu!');
      return;
    }
    
    console.log('Login attempt:', { email, passwordLength: password?.length });
    setIsLoading(true);

    try {
      const result = await onLogin(email, password);
      if (!result.success) {
        alert(result.message || 'Đăng nhập thất bại');
      }
    } catch (error) {
      alert('Lỗi đăng nhập: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <h2 className="text-cyan-100 mb-2">Chào mừng trở lại!</h2>
        <p className="text-slate-400">Đăng nhập để tiếp tục sử dụng dịch vụ</p>
      </div>

      {/* Email Field */}
      <div>
        <label htmlFor="email" className="block text-slate-300 mb-2">
          Email
        </label>
        <div className="relative">
          <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500">
            <Mail className="w-5 h-5" />
          </div>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            placeholder="example@email.com"
            className="w-full bg-slate-800/50 border border-slate-700 rounded-xl pl-12 pr-4 py-3.5 text-slate-200 placeholder-slate-500 focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/20 transition-all"
          />
        </div>
      </div>

      {/* Password Field */}
      <div>
        <label htmlFor="password" className="block text-slate-300 mb-2">
          Mật khẩu
        </label>
        <div className="relative">
          <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500">
            <Lock className="w-5 h-5" />
          </div>
          <input
            id="password"
            type={showPassword ? 'text' : 'password'}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            placeholder="••••••••"
            className="w-full bg-slate-800/50 border border-slate-700 rounded-xl pl-12 pr-12 py-3.5 text-slate-200 placeholder-slate-500 focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/20 transition-all"
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors"
          >
            {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Forgot Password */}
      <div className="flex items-center justify-between">
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            className="w-4 h-4 bg-slate-800 border-slate-700 rounded text-cyan-500 focus:ring-cyan-500/20"
          />
          <span className="text-slate-400 text-sm">Ghi nhớ đăng nhập</span>
        </label>
        <button
          type="button"
          onClick={onForgotPassword}
          className="text-cyan-400 hover:text-cyan-300 text-sm transition-colors"
        >
          Quên mật khẩu?
        </button>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isLoading}
        className="group w-full relative px-8 py-4 bg-gradient-to-r from-cyan-500 via-blue-500 to-cyan-600 text-white rounded-xl hover:from-cyan-400 hover:via-blue-400 hover:to-cyan-500 transition-all duration-300 shadow-xl shadow-cyan-500/30 hover:shadow-cyan-500/50 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3 overflow-hidden"
      >
        <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300"></div>
        <div className="relative flex items-center gap-3">
          {isLoading ? (
            <>
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Đang xử lý...
            </>
          ) : (
            <>
              <LogIn className="w-5 h-5" />
              Đăng nhập
            </>
          )}
        </div>
      </button>

      {/* Divider */}
      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-slate-700"></div>
        </div>
        <div className="relative flex justify-center text-sm">
          <span className="px-4 bg-slate-900/70 text-slate-500">Hoặc đăng nhập với</span>
        </div>
      </div>

      {/* Social Login */}
      <div className="grid grid-cols-2 gap-4">
        <button
          type="button"
          className="flex items-center justify-center gap-3 px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-xl hover:border-slate-600 hover:bg-slate-800 transition-all"
        >
          <svg className="w-5 h-5" viewBox="0 0 24 24">
            <path fill="#EA4335" d="M5.27 9.76A7.46 7.46 0 0 1 12 5.16c1.75 0 3.3.6 4.52 1.58l3.4-3.4A11.85 11.85 0 0 0 12 0C7.31 0 3.25 2.7 1.27 6.55l3.99 3.21Z"/>
            <path fill="#34A853" d="M16.04 18.01A7.4 7.4 0 0 1 12 19.16a7.46 7.46 0 0 1-6.73-4.4l-4 3.2A11.85 11.85 0 0 0 12 24c2.93 0 5.58-1.08 7.6-2.84l-3.56-2.95Z"/>
            <path fill="#4A90E2" d="M19.6 21.16A11.8 11.8 0 0 0 24 12c0-.83-.09-1.64-.24-2.4H12v4.8h6.72a5.76 5.76 0 0 1-2.48 3.8l3.56 2.96Z"/>
            <path fill="#FBBC05" d="M5.27 14.76A7.38 7.38 0 0 1 4.8 12c0-.96.17-1.88.47-2.76L1.27 6.04A11.82 11.82 0 0 0 0 12c0 2.05.52 3.97 1.27 5.65l4-3.2Z"/>
          </svg>
          <span className="text-slate-300">Google</span>
        </button>
        <button
          type="button"
          className="flex items-center justify-center gap-3 px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-xl hover:border-slate-600 hover:bg-slate-800 transition-all"
        >
          <svg className="w-5 h-5" fill="#1877F2" viewBox="0 0 24 24">
            <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
          </svg>
          <span className="text-slate-300">Facebook</span>
        </button>
      </div>
    </form>
  );
}
