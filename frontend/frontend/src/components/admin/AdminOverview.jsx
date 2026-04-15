import { useState, useEffect } from 'react';
import { Users, FileText, TrendingUp, DollarSign, Activity, AlertCircle, RefreshCw, Info } from 'lucide-react';
import apiService from '../../services/api';

export function AdminOverview() {
  const [stats, setStats] = useState([
    { label: 'Tổng người dùng', value: '0', change: '+0%', icon: Users, color: 'cyan' },
    { label: 'Phân tích hôm nay', value: '0', change: '+0%', icon: FileText, color: 'blue' },
    { label: 'Doanh thu tháng', value: '0 VNĐ', change: '+0%', icon: DollarSign, color: 'green' },
    { label: 'Tỷ lệ chuyển đổi', value: '0%', change: '+0%', icon: TrendingUp, color: 'purple' }
  ]);
  const [isLoading, setIsLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(null);

  useEffect(() => {
    loadAdminStats();
  }, []);

  const loadAdminStats = async () => {
    try {
      setIsLoading(true);
      const response = await apiService.getAdminStats();

      // Normalize response shape and provide safe defaults
      const totalUsers = Number(response?.total_users ?? response?.data?.total_users ?? 0) || 0;
      const totalContracts = Number(response?.total_contracts ?? response?.data?.total_contracts ?? 0) || 0;
      const totalAnalyses = Number(response?.total_analyses ?? response?.data?.total_analyses ?? 0) || 0;

      const successRate = totalContracts > 0 ? Math.round((totalAnalyses / totalContracts) * 100) : 0;

      setStats([
        { label: 'Tổng người dùng', value: String(totalUsers), change: '+12%', icon: Users, color: 'cyan' },
        { label: 'Tổng hợp đồng', value: String(totalContracts), change: '+23%', icon: FileText, color: 'blue' },
        { label: 'Tổng phân tích', value: String(totalAnalyses), change: '+8%', icon: DollarSign, color: 'green' },
        { label: 'Tỷ lệ thành công', value: `${successRate}%`, change: '+5%', icon: TrendingUp, color: 'purple' }
      ]);
      setLastUpdated(new Date().toLocaleString());
    } catch (error) {
      console.error('Failed to load admin stats:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const recentActivities = [
    { user: 'user@email.com', action: 'Nâng cấp lên Pro', time: '2 phút trước', type: 'upgrade' },
    { user: 'admin@email.com', action: 'Phân tích hợp đồng', time: '5 phút trước', type: 'analysis' },
    { user: 'test@email.com', action: 'Đăng ký mới', time: '12 phút trước', type: 'signup' },
    { user: 'demo@email.com', action: 'Tải báo cáo', time: '23 phút trước', type: 'download' },
    { user: 'user2@email.com', action: 'Hủy gói Pro', time: '1 giờ trước', type: 'downgrade' }
  ];

  const systemStatus = [
    { name: 'API Server', status: 'online', uptime: '99.9%', color: 'green' },
    { name: 'AI Processing', status: 'online', uptime: '99.5%', color: 'green' },
    { name: 'Database', status: 'online', uptime: '100%', color: 'green' },
    { name: 'Storage', status: 'warning', uptime: '85%', color: 'yellow' }
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="text-sm text-slate-400 flex items-center gap-2">
          <Info className="w-4 h-4 text-slate-400" />
          <span title="Dữ liệu lấy trực tiếp từ /api/admin/stats (MongoDB)">Dữ liệu: /api/admin/stats</span>
          {lastUpdated && <span className="text-xs text-slate-500">· Cập nhật: {lastUpdated}</span>}
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={loadAdminStats}
            className="flex items-center gap-2 bg-slate-800/60 hover:bg-slate-800 text-slate-200 text-xs py-1 px-3 rounded-md"
            disabled={isLoading}
            title="Làm mới số liệu"
          >
            <RefreshCw className="w-4 h-4" />
            <span>{isLoading ? 'Đang tải...' : 'Làm mới'}</span>
          </button>
        </div>
      </div>
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div
              key={index}
              className="bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 rounded-xl p-6 hover:border-cyan-500/50 transition-all animate-fade-in"
              style={{ animationDelay: `${index * 50}ms` }}
            >
              <div className="flex items-center justify-between mb-4">
                <div className={`bg-gradient-to-br from-${stat.color}-500 to-${stat.color}-600 p-3 rounded-xl shadow-lg`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
                <span className="text-green-400 text-sm">{stat.change}</span>
              </div>
              <div className="text-slate-400 text-sm mb-1">{stat.label}</div>
              <div className="text-2xl text-slate-100">{stat.value}</div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Activities */}
        <div className="lg:col-span-2 bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-cyan-100 flex items-center gap-2">
              <Activity className="w-5 h-5" />
              Hoạt động gần đây
            </h2>
          </div>
          <div className="space-y-3">
            {recentActivities.map((activity, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg hover:bg-slate-800 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div className={`w-2 h-2 rounded-full ${
                    activity.type === 'upgrade' ? 'bg-green-400' :
                    activity.type === 'downgrade' ? 'bg-red-400' :
                    activity.type === 'signup' ? 'bg-blue-400' :
                    'bg-slate-400'
                  }`}></div>
                  <div>
                    <div className="text-slate-200 text-sm">{activity.user}</div>
                    <div className="text-slate-500 text-xs">{activity.action}</div>
                  </div>
                </div>
                <div className="text-slate-500 text-xs">{activity.time}</div>
              </div>
            ))}
          </div>
        </div>

        {/* System Status */}
        <div className="bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-cyan-100 flex items-center gap-2">
              <AlertCircle className="w-5 h-5" />
              Trạng thái hệ thống
            </h2>
          </div>
          <div className="space-y-4">
            {systemStatus.map((system, index) => (
              <div key={index}>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${
                      system.color === 'green' ? 'bg-green-400 animate-pulse' :
                      system.color === 'yellow' ? 'bg-yellow-400 animate-pulse' :
                      'bg-red-400 animate-pulse'
                    }`}></div>
                    <span className="text-slate-300 text-sm">{system.name}</span>
                  </div>
                  <span className={`text-xs ${
                    system.color === 'green' ? 'text-green-400' :
                    system.color === 'yellow' ? 'text-yellow-400' :
                    'text-red-400'
                  }`}>
                    {system.status}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-slate-700 rounded-full h-1.5">
                    <div 
                      className={`h-1.5 rounded-full ${
                        system.color === 'green' ? 'bg-green-500' :
                        system.color === 'yellow' ? 'bg-yellow-500' :
                        'bg-red-500'
                      }`}
                      style={{ width: system.uptime }}
                    ></div>
                  </div>
                  <span className="text-slate-500 text-xs">{system.uptime}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
