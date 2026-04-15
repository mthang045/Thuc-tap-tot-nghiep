import { Save, Globe, Mail, Shield, Database, Zap } from 'lucide-react';

export function SystemSettings() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-pink-500 mb-2">
          Cài đặt hệ thống
        </h1>
        <p className="text-slate-400">Quản lý cấu hình và tùy chỉnh hệ thống</p>
      </div>

      {/* General Settings */}
      <div className="bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 rounded-xl p-6">
        <h2 className="text-cyan-100 mb-4 flex items-center gap-2">
          <Globe className="w-5 h-5" />
          Cài đặt chung
        </h2>
        <div className="space-y-4">
          <div>
            <label className="block text-slate-300 mb-2">Tên hệ thống</label>
            <input
              type="text"
              defaultValue="GenZ Legal AI"
              className="w-full bg-slate-800/50 border border-slate-700 rounded-xl px-4 py-3 text-slate-200 focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/20 transition-all"
            />
          </div>
          <div>
            <label className="block text-slate-300 mb-2">Email liên hệ</label>
            <input
              type="email"
              defaultValue="contact@genzlegal.ai"
              className="w-full bg-slate-800/50 border border-slate-700 rounded-xl px-4 py-3 text-slate-200 focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/20 transition-all"
            />
          </div>
          <div>
            <label className="block text-slate-300 mb-2">Timezone</label>
            <select className="w-full bg-slate-800/50 border border-slate-700 rounded-xl px-4 py-3 text-slate-200 focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/20 transition-all">
              <option>Asia/Ho_Chi_Minh (GMT+7)</option>
              <option>Asia/Bangkok (GMT+7)</option>
              <option>Asia/Singapore (GMT+8)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Email Settings */}
      <div className="bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 rounded-xl p-6">
        <h2 className="text-cyan-100 mb-4 flex items-center gap-2">
          <Mail className="w-5 h-5" />
          Cài đặt Email
        </h2>
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-slate-300 mb-2">SMTP Host</label>
              <input
                type="text"
                defaultValue="smtp.gmail.com"
                className="w-full bg-slate-800/50 border border-slate-700 rounded-xl px-4 py-3 text-slate-200 focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/20 transition-all"
              />
            </div>
            <div>
              <label className="block text-slate-300 mb-2">SMTP Port</label>
              <input
                type="text"
                defaultValue="587"
                className="w-full bg-slate-800/50 border border-slate-700 rounded-xl px-4 py-3 text-slate-200 focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/20 transition-all"
              />
            </div>
          </div>
          <div>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                defaultChecked
                className="w-5 h-5 bg-slate-800 border-slate-700 rounded text-cyan-500 focus:ring-cyan-500/20"
              />
              <span className="text-slate-300">Gửi email thông báo tự động</span>
            </label>
          </div>
        </div>
      </div>

      {/* AI Settings */}
      <div className="bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 rounded-xl p-6">
        <h2 className="text-cyan-100 mb-4 flex items-center gap-2">
          <Zap className="w-5 h-5" />
          Cài đặt AI
        </h2>
        <div className="space-y-4">
          <div>
            <label className="block text-slate-300 mb-2">AI Model</label>
            <select className="w-full bg-slate-800/50 border border-slate-700 rounded-xl px-4 py-3 text-slate-200 focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/20 transition-all">
              <option>GPT-4 Turbo</option>
              <option>GPT-4</option>
              <option>GPT-3.5 Turbo</option>
            </select>
          </div>
          <div>
            <label className="block text-slate-300 mb-2">Max Tokens</label>
            <input
              type="number"
              defaultValue="4096"
              className="w-full bg-slate-800/50 border border-slate-700 rounded-xl px-4 py-3 text-slate-200 focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/20 transition-all"
            />
          </div>
          <div>
            <label className="block text-slate-300 mb-2">Temperature</label>
            <div className="flex items-center gap-4">
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                defaultValue="0.7"
                className="flex-1"
              />
              <span className="text-slate-400 text-sm w-12">0.7</span>
            </div>
          </div>
        </div>
      </div>

      {/* Security Settings */}
      <div className="bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 rounded-xl p-6">
        <h2 className="text-cyan-100 mb-4 flex items-center gap-2">
          <Shield className="w-5 h-5" />
          Bảo mật
        </h2>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-xl">
            <div>
              <div className="text-slate-300 mb-1">Bắt buộc 2FA cho Admin</div>
              <div className="text-slate-500 text-sm">Yêu cầu xác thực 2 bước khi đăng nhập admin</div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" defaultChecked className="sr-only peer" />
              <div className="w-11 h-6 bg-slate-700 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-cyan-500/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-cyan-600"></div>
            </label>
          </div>
          <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-xl">
            <div>
              <div className="text-slate-300 mb-1">Giới hạn tốc độ API</div>
              <div className="text-slate-500 text-sm">Bảo vệ khỏi spam và abuse</div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" defaultChecked className="sr-only peer" />
              <div className="w-11 h-6 bg-slate-700 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-cyan-500/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-cyan-600"></div>
            </label>
          </div>
        </div>
      </div>

      {/* Database Settings */}
      <div className="bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 rounded-xl p-6">
        <h2 className="text-cyan-100 mb-4 flex items-center gap-2">
          <Database className="w-5 h-5" />
          Cơ sở dữ liệu
        </h2>
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-slate-800/50 rounded-xl">
              <div className="text-slate-400 text-sm mb-1">Database Size</div>
              <div className="text-2xl text-cyan-400">2.4 GB</div>
            </div>
            <div className="p-4 bg-slate-800/50 rounded-xl">
              <div className="text-slate-400 text-sm mb-1">Total Records</div>
              <div className="text-2xl text-purple-400">12,456</div>
            </div>
          </div>
          <div className="flex gap-3">
            <button className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg transition-colors text-sm">
              Backup Database
            </button>
            <button className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg transition-colors text-sm">
              Optimize Tables
            </button>
          </div>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex justify-end">
        <button className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white rounded-xl transition-all shadow-lg shadow-cyan-500/30">
          <Save className="w-5 h-5" />
          Lưu tất cả cài đặt
        </button>
      </div>
    </div>
  );
}
