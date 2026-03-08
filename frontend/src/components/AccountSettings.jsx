import { useState, useEffect } from 'react';
import { User, Mail, Phone, Lock, Save, Camera, Bell, Shield, CreditCard, LogOut } from 'lucide-react';
import api from '../services/api';

export function AccountSettings({ userEmail, onLogout }) {
  const [activeTab, setActiveTab] = useState('profile');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [avatarFile, setAvatarFile] = useState(null);
  const [avatarPreview, setAvatarPreview] = useState('');
  
  // Profile state
  const [profileData, setProfileData] = useState({
    fullName: '',
    email: userEmail || '',
    phone: '',
    company: '',
    position: '',
    avatar: ''
  });

  // Security state
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });

  // Notifications state
  const [notifications, setNotifications] = useState({
    emailAnalysis: true,
    emailMarketing: false,
    pushNotifications: true,
    weeklyReport: true
  });

  // Load profile data on mount
  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      setLoading(true);
      const response = await api.getProfile();
      if (response.success && response.profile) {
        setProfileData({
          fullName: response.profile.full_name || '',
          email: response.profile.email || '',
          phone: response.profile.phone || '',
          company: response.profile.company || '',
          position: response.profile.position || '',
          avatar: response.profile.avatar || ''
        });
        if (response.profile.avatar) {
          setAvatarPreview(`http://localhost:5000${response.profile.avatar}`);
        }
      }
    } catch (error) {
      console.error('Error loading profile:', error);
      alert('Không thể tải thông tin cá nhân: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAvatarChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file type
      const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'];
      if (!allowedTypes.includes(file.type)) {
        alert('Chỉ chấp nhận file ảnh: PNG, JPG, JPEG, GIF, WEBP');
        return;
      }
      
      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        alert('Kích thước file không được vượt quá 5MB');
        return;
      }
      
      setAvatarFile(file);
      setAvatarPreview(URL.createObjectURL(file));
    }
  };

  const handleSaveProfile = async (e) => {
    e.preventDefault();
    
    try {
      setSaving(true);
      
      // Upload avatar first if changed
      if (avatarFile) {
        const avatarResponse = await api.uploadAvatar(avatarFile);
        if (avatarResponse.success) {
          console.log('Avatar uploaded:', avatarResponse.avatar_url);
        }
      }
      
      // Update profile data
      const response = await api.updateProfile({
        full_name: profileData.fullName,
        phone: profileData.phone,
        company: profileData.company,
        position: profileData.position
      });
      
      if (response.success) {
        alert('✅ Đã lưu thông tin tài khoản!');
        setAvatarFile(null);
        await loadProfile(); // Reload to get updated data
      } else {
        alert('⚠️ ' + (response.error || 'Không thể cập nhật thông tin'));
      }
    } catch (error) {
      console.error('Error saving profile:', error);
      alert('❌ Lỗi khi lưu thông tin: ' + error.message);
    } finally {
      setSaving(false);
    }
  };

  const handleChangePassword = (e) => {
    e.preventDefault();
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      alert('Mật khẩu mới không khớp!');
      return;
    }
    alert('Đã thay đổi mật khẩu thành công!');
    setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' });
  };

  const tabs = [
    { id: 'profile', label: 'Thông tin cá nhân', icon: User },
    { id: 'security', label: 'Bảo mật', icon: Shield },
    { id: 'notifications', label: 'Thông báo', icon: Bell },
    { id: 'billing', label: 'Thanh toán', icon: CreditCard }
  ];

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-pink-500 mb-2">
          Cài đặt tài khoản
        </h1>
        <p className="text-slate-400">
          Quản lý thông tin cá nhân và tùy chỉnh tài khoản
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar */}
        <div className="lg:col-span-1">
          <div className="bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 rounded-xl p-4 space-y-2">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                    activeTab === tab.id
                      ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-lg shadow-cyan-500/30'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                  }`}
                >
                  <Icon className="w-5 h-5 flex-shrink-0" />
                  <span className="text-sm sm:text-base">{tab.label}</span>
                </button>
              );
            })}
            <div className="pt-4 border-t border-slate-700">
              <button
                onClick={onLogout}
                className="w-full flex items-center gap-3 px-4 py-3 text-red-400 hover:text-red-300 hover:bg-red-900/20 rounded-lg transition-all"
              >
                <LogOut className="w-5 h-5 flex-shrink-0" />
                <span className="text-sm sm:text-base">Đăng xuất</span>
              </button>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="lg:col-span-3">
          <div className="bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 rounded-xl p-8">
            {/* Profile Tab */}
            {activeTab === 'profile' && (
              <form onSubmit={handleSaveProfile} className="space-y-6">
                <div>
                  <h2 className="text-cyan-100 mb-4">Thông tin cá nhân</h2>
                  
                  {/* Avatar */}
                  <div className="flex items-center gap-6 mb-8">
                    <div className="relative">
                      <div className="bg-gradient-to-br from-cyan-500 to-pink-500 w-24 h-24 rounded-full flex items-center justify-center overflow-hidden">
                        {avatarPreview ? (
                          <img src={avatarPreview} alt="Avatar" className="w-full h-full object-cover" />
                        ) : (
                          <User className="w-12 h-12 text-white" />
                        )}
                      </div>
                      <label
                        htmlFor="avatar-upload"
                        className="absolute bottom-0 right-0 p-2 bg-slate-800 border border-slate-700 rounded-full hover:bg-slate-700 transition-colors cursor-pointer"
                      >
                        <Camera className="w-4 h-4 text-slate-300" />
                      </label>
                      <input
                        id="avatar-upload"
                        type="file"
                        accept="image/png,image/jpeg,image/jpg,image/gif,image/webp"
                        onChange={handleAvatarChange}
                        className="hidden"
                      />
                    </div>
                    <div>
                      <h3 className="text-slate-200 mb-1">{profileData.fullName || 'Chưa có tên'}</h3>
                      <p className="text-slate-400 text-sm mb-2">{profileData.email}</p>
                      <label
                        htmlFor="avatar-upload"
                        className="text-cyan-400 hover:text-cyan-300 text-sm transition-colors cursor-pointer"
                      >
                        Thay đổi ảnh đại diện
                      </label>
                    </div>
                  </div>

                  {/* Form Fields */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-slate-300 mb-2">Họ và tên</label>
                      <div className="relative">
                        <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500">
                          <User className="w-5 h-5" />
                        </div>
                        <input
                          type="text"
                          value={profileData.fullName}
                          onChange={(e) => setProfileData({ ...profileData, fullName: e.target.value })}
                          className="w-full bg-slate-800/50 border border-slate-700 rounded-xl pl-12 pr-4 py-3 text-slate-200 focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/20 transition-all"
                          placeholder="Nhập họ và tên"
                          disabled={loading}
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-slate-300 mb-2">Email</label>
                      <div className="relative">
                        <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500">
                          <Mail className="w-5 h-5" />
                        </div>
                        <input
                          type="email"
                          value={profileData.email}
                          className="w-full bg-slate-800/50 border border-slate-700 rounded-xl pl-12 pr-4 py-3 text-slate-400 cursor-not-allowed"
                          disabled
                          readOnly
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-slate-300 mb-2">Số điện thoại</label>
                      <div className="relative">
                        <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500">
                          <Phone className="w-5 h-5" />
                        </div>
                        <input
                          type="tel"
                          value={profileData.phone}
                          onChange={(e) => setProfileData({ ...profileData, phone: e.target.value })}
                          className="w-full bg-slate-800/50 border border-slate-700 rounded-xl pl-12 pr-4 py-3 text-slate-200 focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/20 transition-all"
                          placeholder="Nhập số điện thoại"
                          disabled={loading}
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-slate-300 mb-2">Công ty</label>
                      <input
                        type="text"
                        value={profileData.company}
                        onChange={(e) => setProfileData({ ...profileData, company: e.target.value })}
                        className="w-full bg-slate-800/50 border border-slate-700 rounded-xl px-4 py-3 text-slate-200 focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/20 transition-all"
                        placeholder="Nhập tên công ty"
                        disabled={loading}
                      />
                    </div>

                    <div>
                      <label className="block text-slate-300 mb-2">Chức vụ</label>
                      <input
                        type="text"
                        value={profileData.position}
                        onChange={(e) => setProfileData({ ...profileData, position: e.target.value })}
                        className="w-full bg-slate-800/50 border border-slate-700 rounded-xl px-4 py-3 text-slate-200 focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/20 transition-all"
                        placeholder="Nhập chức vụ"
                        disabled={loading}
                      />
                    </div>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={saving || loading}
                  className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white rounded-xl transition-all shadow-lg shadow-cyan-500/30 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Save className="w-5 h-5" />
                  {saving ? 'Đang lưu...' : 'Lưu thay đổi'}
                </button>
              </form>
            )}

            {/* Security Tab */}
            {activeTab === 'security' && (
              <form onSubmit={handleChangePassword} className="space-y-6">
                <div>
                  <h2 className="text-cyan-100 mb-4">Đổi mật khẩu</h2>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="block text-slate-300 mb-2">Mật khẩu hiện tại</label>
                      <div className="relative">
                        <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500">
                          <Lock className="w-5 h-5" />
                        </div>
                        <input
                          type="password"
                          value={passwordData.currentPassword}
                          onChange={(e) => setPasswordData({ ...passwordData, currentPassword: e.target.value })}
                          placeholder="••••••••"
                          className="w-full bg-slate-800/50 border border-slate-700 rounded-xl pl-12 pr-4 py-3 text-slate-200 placeholder-slate-500 focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/20 transition-all"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-slate-300 mb-2">Mật khẩu mới</label>
                      <div className="relative">
                        <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500">
                          <Lock className="w-5 h-5" />
                        </div>
                        <input
                          type="password"
                          value={passwordData.newPassword}
                          onChange={(e) => setPasswordData({ ...passwordData, newPassword: e.target.value })}
                          placeholder="••••••••"
                          className="w-full bg-slate-800/50 border border-slate-700 rounded-xl pl-12 pr-4 py-3 text-slate-200 placeholder-slate-500 focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/20 transition-all"
                        />
                      </div>
                      <p className="text-slate-500 text-sm mt-2">Tối thiểu 8 ký tự, bao gồm chữ và số</p>
                    </div>

                    <div>
                      <label className="block text-slate-300 mb-2">Xác nhận mật khẩu mới</label>
                      <div className="relative">
                        <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500">
                          <Lock className="w-5 h-5" />
                        </div>
                        <input
                          type="password"
                          value={passwordData.confirmPassword}
                          onChange={(e) => setPasswordData({ ...passwordData, confirmPassword: e.target.value })}
                          placeholder="••••••••"
                          className="w-full bg-slate-800/50 border border-slate-700 rounded-xl pl-12 pr-4 py-3 text-slate-200 placeholder-slate-500 focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/20 transition-all"
                        />
                      </div>
                    </div>
                  </div>
                </div>

                <button
                  type="submit"
                  className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white rounded-xl transition-all shadow-lg shadow-cyan-500/30"
                >
                  <Save className="w-5 h-5" />
                  Đổi mật khẩu
                </button>

                {/* Two-Factor Authentication */}
                <div className="pt-6 border-t border-slate-700">
                  <h3 className="text-slate-200 mb-4">Xác thực hai yếu tố (2FA)</h3>
                  <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-xl border border-slate-700">
                    <div>
                      <div className="text-slate-300 mb-1">Bảo mật nâng cao</div>
                      <div className="text-slate-500 text-sm">Kích hoạt xác thực 2 bước khi đăng nhập</div>
                    </div>
                    <button
                      type="button"
                      className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg transition-colors text-sm"
                    >
                      Kích hoạt
                    </button>
                  </div>
                </div>
              </form>
            )}

            {/* Notifications Tab */}
            {activeTab === 'notifications' && (
              <div className="space-y-6">
                <h2 className="text-cyan-100 mb-4">Cài đặt thông báo</h2>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-xl border border-slate-700">
                    <div>
                      <div className="text-slate-300 mb-1">Email khi phân tích hoàn tất</div>
                      <div className="text-slate-500 text-sm">Nhận email thông báo khi hợp đồng được phân tích xong</div>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={notifications.emailAnalysis}
                        onChange={(e) => setNotifications({ ...notifications, emailAnalysis: e.target.checked })}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-slate-700 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-cyan-500/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-cyan-600"></div>
                    </label>
                  </div>

                  <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-xl border border-slate-700">
                    <div>
                      <div className="text-slate-300 mb-1">Email marketing</div>
                      <div className="text-slate-500 text-sm">Nhận thông tin về tính năng mới và ưu đãi</div>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={notifications.emailMarketing}
                        onChange={(e) => setNotifications({ ...notifications, emailMarketing: e.target.checked })}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-slate-700 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-cyan-500/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-cyan-600"></div>
                    </label>
                  </div>

                  <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-xl border border-slate-700">
                    <div>
                      <div className="text-slate-300 mb-1">Thông báo đẩy</div>
                      <div className="text-slate-500 text-sm">Nhận thông báo trực tiếp trên trình duyệt</div>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={notifications.pushNotifications}
                        onChange={(e) => setNotifications({ ...notifications, pushNotifications: e.target.checked })}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-slate-700 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-cyan-500/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-cyan-600"></div>
                    </label>
                  </div>

                  <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-xl border border-slate-700">
                    <div>
                      <div className="text-slate-300 mb-1">Báo cáo hàng tuần</div>
                      <div className="text-slate-500 text-sm">Nhận tổng hợp các phân tích trong tuần</div>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={notifications.weeklyReport}
                        onChange={(e) => setNotifications({ ...notifications, weeklyReport: e.target.checked })}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-slate-700 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-cyan-500/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-cyan-600"></div>
                    </label>
                  </div>
                </div>
              </div>
            )}

            {/* Billing Tab */}
            {activeTab === 'billing' && (
              <div className="space-y-6">
                <h2 className="text-cyan-100 mb-4">Gói dịch vụ</h2>
                
                {/* Current Plan */}
                <div className="bg-gradient-to-br from-cyan-900/40 to-blue-900/40 border-2 border-cyan-500/50 rounded-xl p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h3 className="text-cyan-100 mb-1">Gói miễn phí</h3>
                      <p className="text-slate-400 text-sm">5 phân tích/tháng</p>
                    </div>
                    <div className="text-cyan-400 text-2xl">$0</div>
                  </div>
                  <div className="space-y-2 mb-6">
                    <div className="flex items-center gap-2 text-slate-300 text-sm">
                      <div className="w-1.5 h-1.5 bg-cyan-400 rounded-full"></div>
                      5 hợp đồng/tháng
                    </div>
                    <div className="flex items-center gap-2 text-slate-300 text-sm">
                      <div className="w-1.5 h-1.5 bg-cyan-400 rounded-full"></div>
                      Phân tích cơ bản
                    </div>
                    <div className="flex items-center gap-2 text-slate-300 text-sm">
                      <div className="w-1.5 h-1.5 bg-cyan-400 rounded-full"></div>
                      Lưu trữ 30 ngày
                    </div>
                  </div>
                  <a 
                    href="#" 
                    onClick={(e) => {
                      e.preventDefault();
                      window.dispatchEvent(new CustomEvent('navigate-pricing'));
                    }}
                    className="block w-full px-6 py-3 bg-gradient-to-r from-pink-600 to-purple-600 hover:from-pink-500 hover:to-purple-500 text-white rounded-xl transition-all shadow-lg shadow-pink-500/30 text-center"
                  >
                    Xem tất cả gói dịch vụ
                  </a>
                </div>

                {/* Usage Stats */}
                <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                  <h3 className="text-slate-200 mb-4">Sử dụng tháng này</h3>
                  <div className="space-y-4">
                    <div>
                      <div className="flex items-center justify-between text-sm mb-2">
                        <span className="text-slate-400">Phân tích đã dùng</span>
                        <span className="text-cyan-400">3/5</span>
                      </div>
                      <div className="w-full bg-slate-700 rounded-full h-2">
                        <div className="bg-gradient-to-r from-cyan-500 to-blue-500 h-2 rounded-full" style={{ width: '60%' }}></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}