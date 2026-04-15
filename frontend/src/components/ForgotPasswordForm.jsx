import { useState } from 'react';
import { Mail, ArrowLeft, Send, CheckCircle } from 'lucide-react';

export function ForgotPasswordForm({ onBack }) {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setIsLoading(true);

    // Simulate API call
    setTimeout(() => {
      setIsSubmitted(true);
      setIsLoading(false);
    }, 1500);
  };

  if (isSubmitted) {
    return (
      <div className="text-center space-y-6 py-8">
        <div className="flex justify-center mb-6">
          <div className="bg-gradient-to-br from-green-500 to-emerald-500 p-6 rounded-full shadow-2xl shadow-green-500/50">
            <CheckCircle className="w-16 h-16 text-white" />
          </div>
        </div>
        
        <h2 className="text-cyan-100 mb-3">Email đã được gửi!</h2>
        <p className="text-slate-400 leading-relaxed max-w-md mx-auto">
          Chúng tôi đã gửi hướng dẫn đặt lại mật khẩu đến email <span className="text-cyan-400">{email}</span>. Vui lòng kiểm tra hộp thư của bạn.
        </p>

        <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4 text-left">
          <p className="text-slate-300 text-sm mb-2">Lưu ý:</p>
          <ul className="text-slate-400 text-sm space-y-1 list-disc list-inside">
            <li>Kiểm tra cả thư mục spam/junk</li>
            <li>Link có hiệu lực trong 24 giờ</li>
            <li>Không chia sẻ link với người khác</li>
          </ul>
        </div>

        <button
          onClick={onBack}
          className="group flex items-center justify-center gap-2 mx-auto px-6 py-3 text-cyan-400 hover:text-cyan-300 transition-colors"
        >
          <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
          Quay lại đăng nhập
        </button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <button
          type="button"
          onClick={onBack}
          className="group flex items-center gap-2 text-slate-400 hover:text-cyan-300 mb-6 transition-all"
        >
          <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
          Quay lại
        </button>
        
        <h2 className="text-cyan-100 mb-2">Quên mật khẩu?</h2>
        <p className="text-slate-400">
          Nhập email của bạn và chúng tôi sẽ gửi hướng dẫn đặt lại mật khẩu
        </p>
      </div>

      {/* Illustration */}
      <div className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-slate-700 rounded-2xl p-8 text-center">
        <div className="bg-gradient-to-br from-cyan-500/20 to-purple-500/20 w-24 h-24 rounded-full flex items-center justify-center mx-auto mb-4">
          <Mail className="w-12 h-12 text-cyan-400" />
        </div>
        <p className="text-slate-400 text-sm">
          Chúng tôi sẽ gửi link đặt lại mật khẩu đến email của bạn
        </p>
      </div>

      {/* Email Field */}
      <div>
        <label htmlFor="forgot-email" className="block text-slate-300 mb-2">
          Email
        </label>
        <div className="relative">
          <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500">
            <Mail className="w-5 h-5" />
          </div>
          <input
            id="forgot-email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            placeholder="example@email.com"
            className="w-full bg-slate-800/50 border border-slate-700 rounded-xl pl-12 pr-4 py-3.5 text-slate-200 placeholder-slate-500 focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/20 transition-all"
          />
        </div>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isLoading}
        className="group w-full relative px-8 py-4 bg-gradient-to-r from-cyan-500 via-purple-500 to-pink-500 text-white rounded-xl hover:from-cyan-400 hover:via-purple-400 hover:to-pink-400 transition-all duration-300 shadow-xl shadow-purple-500/30 hover:shadow-purple-500/50 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3 overflow-hidden"
      >
        <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300"></div>
        <div className="relative flex items-center gap-3">
          {isLoading ? (
            <>
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Đang gửi...
            </>
          ) : (
            <>
              <Send className="w-5 h-5" />
              Gửi hướng dẫn
            </>
          )}
        </div>
      </button>

      {/* Help Text */}
      <div className="text-center">
        <p className="text-slate-500 text-sm">
          Bạn nhớ mật khẩu rồi?{' '}
          <button
            type="button"
            onClick={onBack}
            className="text-cyan-400 hover:text-cyan-300 transition-colors"
          >
            Đăng nhập ngay
          </button>
        </p>
      </div>
    </form>
  );
}
