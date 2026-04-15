import { useEffect, useRef, useState } from 'react';
import { Mail, Lock, LogIn, Eye, EyeOff } from 'lucide-react';

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || '';

export function LoginForm({ onLogin, onGoogleLogin, onForgotPassword }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const googleButtonRef = useRef(null);
  const googleLoginHandlerRef = useRef(onGoogleLogin);
  const isGoogleConfigured = Boolean(GOOGLE_CLIENT_ID);

  useEffect(() => {
    googleLoginHandlerRef.current = onGoogleLogin;
  }, [onGoogleLogin]);

  useEffect(() => {
    if (!isGoogleConfigured) return;
    let isCancelled = false;

    const handleGoogleResponse = async (response) => {
      const loginHandler = googleLoginHandlerRef.current;
      if (!response?.credential || !loginHandler) return;
      setIsLoading(true);
      try {
        const result = await loginHandler(response.credential);
        if (!result?.success) {
          alert(result?.message || 'Đăng nhập Google thất bại');
        }
      } catch (error) {
        alert('Lỗi đăng nhập Google: ' + error.message);
      } finally {
        setIsLoading(false);
      }
    };

    const initGoogleSignIn = () => {
      if (isCancelled || !window.google?.accounts?.id || !googleButtonRef.current) return;

      if (!window.__genzGoogleInitialized) {
        window.google.accounts.id.initialize({
          client_id: GOOGLE_CLIENT_ID,
          callback: handleGoogleResponse,
        });
        window.__genzGoogleInitialized = true;
      }

      googleButtonRef.current.innerHTML = '';
      window.google.accounts.id.renderButton(googleButtonRef.current, {
        theme: 'outline',
        size: 'large',
        text: 'signin_with',
        width: 320,
      });
    };

    if (window.google?.accounts?.id) {
      initGoogleSignIn();
      return () => {
        isCancelled = true;
      };
    }

    const existingScript = document.querySelector('script[src="https://accounts.google.com/gsi/client"]');
    if (existingScript) {
      existingScript.addEventListener('load', initGoogleSignIn);
      return () => {
        isCancelled = true;
        existingScript.removeEventListener('load', initGoogleSignIn);
      };
    }

    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.defer = true;
    script.onload = initGoogleSignIn;
    document.head.appendChild(script);

    return () => {
      isCancelled = true;
      script.onload = null;
    };
  }, [isGoogleConfigured]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!email || !password) {
      alert('Vui lòng nhập đầy đủ email và mật khẩu!');
      return;
    }

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

      <div>
        <label htmlFor="email" className="block text-slate-300 mb-2">Email</label>
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

      <div>
        <label htmlFor="password" className="block text-slate-300 mb-2">Mật khẩu</label>
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

      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-slate-700"></div>
        </div>
        <div className="relative flex justify-center text-sm">
          <span className="px-4 bg-slate-900/70 text-slate-500">Hoặc đăng nhập với</span>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4">
        <div className="bg-slate-800/40 border border-slate-700 rounded-xl px-4 py-3 flex items-center justify-center">
          {isGoogleConfigured ? (
            <div ref={googleButtonRef}></div>
          ) : (
            <span className="text-slate-500 text-sm">Google login chưa cấu hình</span>
          )}
        </div>
      </div>
    </form>
  );
}
