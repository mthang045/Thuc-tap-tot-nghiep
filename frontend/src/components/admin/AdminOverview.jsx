import { useState, useEffect } from 'react';
import { Users, FileText, TrendingUp, DollarSign, Activity, AlertCircle } from 'lucide-react';
import apiService from '../../services/api';

export function AdminOverview() {
  const [stats, setStats] = useState([
    { label: 'Tổng người dùng', value: '0', change: '+0%', icon: Users, color: 'cyan' },
    { label: 'Phân tích hôm nay', value: '0', change: '+0%', icon: FileText, color: 'blue' },
    { label: 'Doanh thu tháng', value: '0 VNĐ', change: '+0%', icon: DollarSign, color: 'green' },
    { label: 'Tỷ lệ chuyển đổi', value: '0%', change: '+0%', icon: TrendingUp, color: 'purple' }
  ]);
  const [isLoading, setIsLoading] = useState(true);
  const [recentActivities, setRecentActivities] = useState([]);
  const [systemStatus, setSystemStatus] = useState([]);

  useEffect(() => {
    loadAdminStats();
  }, []);

  const loadAdminStats = async () => {
    try {
      setIsLoading(true);
      const response = await apiService.getAdminStats();
      const statsData = response.stats || response;

      const totalUsers = Number(statsData.total_users || statsData.totalUsers || 0);
      const totalAnalyses = Number(statsData.total_analyses || statsData.totalAnalyses || 0);
      const totalContracts = Number(statsData.total_contracts || statsData.totalContracts || totalAnalyses);
      const monthlyRevenue = Number(statsData.monthly_revenue || statsData.monthlyRevenue || 0);
      const successRate = Number(statsData.success_rate || statsData.successRate || 0);
      
      setStats([
        { label: 'Tổng người dùng', value: totalUsers.toString(), change: '', icon: Users, color: 'cyan' },
        { label: 'Tổng hợp đồng', value: totalContracts.toString(), change: '', icon: FileText, color: 'blue' },
        { label: 'Tổng phân tích', value: totalAnalyses.toString(), change: '', icon: DollarSign, color: 'green' },
        { label: 'Tỷ lệ thành công', value: `${successRate}%`, change: '', icon: TrendingUp, color: 'purple' }
      ]);

      const activities = (response.recent_activities || []).map(item => ({
        user: item.user || 'unknown',
        action: item.action || 'Phân tích hợp đồng',
        time: item.time || 'vừa xong',
        type: item.type || 'analysis'
      }));
      setRecentActivities(activities);

      const activeUsers = Number(statsData.active_users || statsData.activeUsers || 0);
      const adminUsers = Number(statsData.admin_users || statsData.adminUsers || 0);
      setSystemStatus([
        { name: 'API Server', status: 'online', uptime: '100%', color: 'green' },
        { name: 'Database', status: 'online', uptime: '100%', color: 'green' },
        { name: 'Người dùng hoạt động', status: 'online', uptime: totalUsers ? `${Math.round((activeUsers / totalUsers) * 100)}%` : '0%', color: 'green' },
        { name: 'Admin accounts', status: 'online', uptime: totalUsers ? `${Math.round((adminUsers / totalUsers) * 100)}%` : '0%', color: 'yellow' },
      ]);
    } catch (error) {
      console.error('Failed to load admin stats:', error);
      setRecentActivities([]);
      setSystemStatus([]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
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
