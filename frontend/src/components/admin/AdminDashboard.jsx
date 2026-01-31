import { useState } from 'react';
import { LayoutDashboard, Users, FileText, BarChart3, Settings, Shield } from 'lucide-react';
import { AdminOverview } from './AdminOverview';
import { UserManagement } from './UserManagement';
import { AnalyticsManagement } from './AnalyticsManagement';
import { SystemStats } from './SystemStats';
import { SystemSettings } from './SystemSettings';
import logoImage from '/logo.png';

export function AdminDashboard({ onExitAdmin }) {
  const [activeTab, setActiveTab] = useState('overview');

  const tabs = [
    { id: 'overview', label: 'Tổng quan', icon: LayoutDashboard },
    { id: 'users', label: 'Người dùng', icon: Users },
    { id: 'analytics', label: 'Phân tích', icon: FileText },
    { id: 'stats', label: 'Thống kê', icon: BarChart3 },
    { id: 'settings', label: 'Cài đặt', icon: Settings }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-950 to-purple-950">
      {/* Header */}
      <header className="border-b border-slate-700/50 backdrop-blur-xl bg-slate-900/50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-cyan-400 to-pink-500 rounded-full blur-lg opacity-40"></div>
                <div className="relative bg-white p-2 rounded-full shadow-lg shadow-cyan-500/30">
                  <img 
                    src={logoImage} 
                    alt="GenZ Logo" 
                    className="h-10 w-10 object-cover rounded-full"
                  />
                </div>
              </div>
              <div>
                <h1 className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-pink-500 text-xl">
                  Admin Dashboard
                </h1>
                <p className="text-slate-500 text-xs">Quản trị hệ thống GenZ Legal AI</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="px-4 py-2 bg-red-500/20 border border-red-500/30 rounded-lg flex items-center gap-2">
                <Shield className="w-4 h-4 text-red-400" />
                <span className="text-red-300 text-sm">Admin Mode</span>
              </div>
              <button
                onClick={onExitAdmin}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition-colors text-sm"
              >
                Thoát Admin
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 rounded-xl p-4 space-y-2 sticky top-8">
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
                    <Icon className="w-5 h-5" />
                    <span>{tab.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Content */}
          <div className="lg:col-span-4">
            {activeTab === 'overview' && <AdminOverview />}
            {activeTab === 'users' && <UserManagement />}
            {activeTab === 'analytics' && <AnalyticsManagement />}
            {activeTab === 'stats' && <SystemStats />}
            {activeTab === 'settings' && <SystemSettings />}
          </div>
        </div>
      </div>
    </div>
  );
}
