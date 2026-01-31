import { TrendingUp, Users, FileText, DollarSign } from 'lucide-react';

export function SystemStats() {
  const chartData = {
    users: [12, 19, 15, 25, 32, 28, 35, 42, 38, 45, 52, 48],
    analyses: [45, 52, 48, 65, 72, 68, 85, 92, 88, 95, 102, 98],
    revenue: [5.2, 6.8, 7.2, 9.5, 11.2, 10.8, 13.5, 15.2, 14.8, 16.5, 18.2, 17.8]
  };

  const months = ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9', 'T10', 'T11', 'T12'];

  const topUsers = [
    { email: 'power@user.com', analyses: 234, revenue: '12.5M' },
    { email: 'demo@company.com', analyses: 189, revenue: '9.8M' },
    { email: 'test@business.com', analyses: 156, revenue: '8.2M' },
    { email: 'user@enterprise.com', analyses: 142, revenue: '7.5M' },
    { email: 'admin@startup.com', analyses: 128, revenue: '6.9M' }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-pink-500 mb-2">
          Thống kê hệ thống
        </h1>
        <p className="text-slate-400">Biểu đồ và báo cáo chi tiết</p>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Users Chart */}
        <div className="bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-cyan-100 flex items-center gap-2">
              <Users className="w-5 h-5" />
              Người dùng mới
            </h2>
            <span className="text-green-400 text-sm">+15%</span>
          </div>
          <div className="flex items-end gap-2 h-48">
            {chartData.users.map((value, index) => (
              <div key={index} className="flex-1 flex flex-col items-center gap-2">
                <div className="w-full bg-slate-800 rounded-t-lg relative overflow-hidden" style={{ height: `${(value / Math.max(...chartData.users)) * 100}%` }}>
                  <div className="absolute inset-0 bg-gradient-to-t from-cyan-500 to-blue-500 animate-fade-in" style={{ animationDelay: `${index * 50}ms` }}></div>
                </div>
                <span className="text-slate-500 text-xs">{months[index]}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Analyses Chart */}
        <div className="bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-cyan-100 flex items-center gap-2">
              <FileText className="w-5 h-5" />
              Số lượng phân tích
            </h2>
            <span className="text-green-400 text-sm">+23%</span>
          </div>
          <div className="flex items-end gap-2 h-48">
            {chartData.analyses.map((value, index) => (
              <div key={index} className="flex-1 flex flex-col items-center gap-2">
                <div className="w-full bg-slate-800 rounded-t-lg relative overflow-hidden" style={{ height: `${(value / Math.max(...chartData.analyses)) * 100}%` }}>
                  <div className="absolute inset-0 bg-gradient-to-t from-purple-500 to-pink-500 animate-fade-in" style={{ animationDelay: `${index * 50}ms` }}></div>
                </div>
                <span className="text-slate-500 text-xs">{months[index]}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Revenue Chart */}
        <div className="bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-cyan-100 flex items-center gap-2">
              <DollarSign className="w-5 h-5" />
              Doanh thu (triệu VNĐ)
            </h2>
            <span className="text-green-400 text-sm">+18%</span>
          </div>
          <div className="flex items-end gap-2 h-48">
            {chartData.revenue.map((value, index) => (
              <div key={index} className="flex-1 flex flex-col items-center gap-2">
                <div className="w-full bg-slate-800 rounded-t-lg relative overflow-hidden" style={{ height: `${(value / Math.max(...chartData.revenue)) * 100}%` }}>
                  <div className="absolute inset-0 bg-gradient-to-t from-green-500 to-emerald-500 animate-fade-in" style={{ animationDelay: `${index * 50}ms` }}></div>
                </div>
                <span className="text-slate-500 text-xs">{months[index]}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Top Users */}
        <div className="bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-cyan-100 flex items-center gap-2">
              <TrendingUp className="w-5 h-5" />
              Top người dùng
            </h2>
          </div>
          <div className="space-y-3">
            {topUsers.map((user, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="bg-gradient-to-br from-cyan-500 to-pink-500 w-8 h-8 rounded-full flex items-center justify-center text-white text-sm">
                    {index + 1}
                  </div>
                  <div>
                    <div className="text-slate-300 text-sm">{user.email}</div>
                    <div className="text-slate-500 text-xs">{user.analyses} phân tích</div>
                  </div>
                </div>
                <div className="text-green-400 text-sm">{user.revenue}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
