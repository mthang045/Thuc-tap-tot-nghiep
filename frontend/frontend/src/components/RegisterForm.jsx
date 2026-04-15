import { useState } from 'react';
import { Mail, Lock, User, UserPlus, Eye, EyeOff, Phone } from 'lucide-react';
import apiService from '../services/api';

export function RegisterForm({ onRegister }) {
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    phone: '',
    password: '',
    confirmPassword: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [agreedToTerms, setAgreedToTerms] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (formData.password !== formData.confirmPassword) {
      alert('Mật khẩu không khớp!');
      return;
    }

    if (!agreedToTerms) {
      alert('Vui lòng đồng ý với điều khoản sử dụng!');
      return;
    }

    setIsLoading(true);

    try {
      const response = await apiService.register(
        formData.fullName,
        formData.email,
        formData.phone,
        formData.password
      );
      
      if (response.success) {
        alert('Đăng ký thành công! Vui lòng đăng nhập.');
        onRegister(); // Chuyển về form đăng nhập
      } else {
        alert('Đăng ký thất bại: ' + (response.error || 'Lỗi không xác định'));
      }
    } catch (error) {
      alert('Lỗi đăng ký: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <h2 className="text-pink-100 mb-2">Tạo tài khoản mới</h2>
        <p className="text-slate-400">Đăng ký để trải nghiệm dịch vụ</p>
      </div>

      {/* Full Name Field */}
      <div>
        <label htmlFor="fullName" className="block text-slate-300 mb-2">
          Họ và tên
        </label>
        <div className="relative">
          <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500">
            <User className="w-5 h-5" />
          </div>
          <input
            id="fullName"
            type="text"
            value={formData.fullName}
            onChange={(e) => handleChange('fullName', e.target.value)}
            required
            placeholder="Nguyễn Văn A"
            className="w-full bg-slate-800/50 border border-slate-700 rounded-xl pl-12 pr-4 py-3.5 text-slate-200 placeholder-slate-500 focus:border-pink-500 focus:outline-none focus:ring-2 focus:ring-pink-500/20 transition-all"
          />
        </div>
      </div>

      {/* Email Field */}
      <div>
        <label htmlFor="register-email" className="block text-slate-300 mb-2">
          Email
        </label>
        <div className="relative">
          <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500">
            <Mail className="w-5 h-5" />
          </div>
          <input
            id="register-email"
            type="email"
            value={formData.email}
            onChange={(e) => handleChange('email', e.target.value)}
            required
            placeholder="example@email.com"
            className="w-full bg-slate-800/50 border border-slate-700 rounded-xl pl-12 pr-4 py-3.5 text-slate-200 placeholder-slate-500 focus:border-pink-500 focus:outline-none focus:ring-2 focus:ring-pink-500/20 transition-all"
          />
        </div>
      </div>

      {/* Phone Field */}
      <div>
        <label htmlFor="phone" className="block text-slate-300 mb-2">
          Số điện thoại
        </label>
        <div className="relative">
          <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500">
            <Phone className="w-5 h-5" />
          </div>
          <input
            id="phone"
            type="tel"
            value={formData.phone}
            onChange={(e) => handleChange('phone', e.target.value)}
            required
            placeholder="0123456789"
            className="w-full bg-slate-800/50 border border-slate-700 rounded-xl pl-12 pr-4 py-3.5 text-slate-200 placeholder-slate-500 focus:border-pink-500 focus:outline-none focus:ring-2 focus:ring-pink-500/20 transition-all"
          />
        </div>
      </div>

      {/* Password Field */}
      <div>
        <label htmlFor="register-password" className="block text-slate-300 mb-2">
          Mật khẩu
        </label>
        <div className="relative">
          <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500">
            <Lock className="w-5 h-5" />
          </div>
          <input
            id="register-password"
            type={showPassword ? 'text' : 'password'}
            value={formData.password}
            onChange={(e) => handleChange('password', e.target.value)}
            required
            placeholder="••••••••"
            className="w-full bg-slate-800/50 border border-slate-700 rounded-xl pl-12 pr-12 py-3.5 text-slate-200 placeholder-slate-500 focus:border-pink-500 focus:outline-none focus:ring-2 focus:ring-pink-500/20 transition-all"
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors"
          >
            {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
          </button>
        </div>
        <p className="text-slate-500 text-sm mt-2">Tối thiểu 8 ký tự, bao gồm chữ và số</p>
      </div>

      {/* Confirm Password Field */}
      <div>
        <label htmlFor="confirmPassword" className="block text-slate-300 mb-2">
          Xác nhận mật khẩu
        </label>
        <div className="relative">
          <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500">
            <Lock className="w-5 h-5" />
          </div>
          <input
            id="confirmPassword"
            type={showConfirmPassword ? 'text' : 'password'}
            value={formData.confirmPassword}
            onChange={(e) => handleChange('confirmPassword', e.target.value)}
            required
            placeholder="••••••••"
            className="w-full bg-slate-800/50 border border-slate-700 rounded-xl pl-12 pr-12 py-3.5 text-slate-200 placeholder-slate-500 focus:border-pink-500 focus:outline-none focus:ring-2 focus:ring-pink-500/20 transition-all"
          />
          <button
            type="button"
            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
            className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors"
          >
            {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Terms Checkbox */}
      <label className="flex items-start gap-3 cursor-pointer">
        <input
          type="checkbox"
          checked={agreedToTerms}
          onChange={(e) => setAgreedToTerms(e.target.checked)}
          className="w-5 h-5 mt-0.5 bg-slate-800 border-slate-700 rounded text-pink-500 focus:ring-pink-500/20 flex-shrink-0"
        />
        <span className="text-slate-400 text-sm leading-relaxed">
          Tôi đồng ý với{' '}
          <a href="#" className="text-pink-400 hover:text-pink-300">Điều khoản sử dụng</a>
          {' '}và{' '}
          <a href="#" className="text-pink-400 hover:text-pink-300">Chính sách bảo mật</a>
        </span>
      </label>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isLoading}
        className="group w-full relative px-8 py-4 bg-gradient-to-r from-pink-500 via-purple-500 to-pink-600 text-white rounded-xl hover:from-pink-400 hover:via-purple-400 hover:to-pink-500 transition-all duration-300 shadow-xl shadow-pink-500/30 hover:shadow-pink-500/50 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3 overflow-hidden"
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
              <UserPlus className="w-5 h-5" />
              Đăng ký tài khoản
            </>
          )}
        </div>
      </button>
    </form>
  );
}
