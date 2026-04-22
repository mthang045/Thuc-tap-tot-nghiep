import { useEffect, useMemo, useState } from 'react';
import { TrendingUp, Users, FileText, DollarSign, RefreshCw } from 'lucide-react';
import apiService from '../../services/api';

const MONTH_LABELS = ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9', 'T10', 'T11', 'T12'];

const emptyMonthlyCounts = () => Array(12).fill(0);

const normalizeSeries = (value) => (Array.isArray(value) && value.length === 12 ? value : emptyMonthlyCounts());

const parseMonthIndex = (value) => {
  if (!value) return null;

  const directDate = new Date(value);
  if (!Number.isNaN(directDate.getTime())) {
    return directDate.getMonth();
  }

  const match = String(value).match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})/);
  if (!match) return null;

  const day = Number(match[1]);
  const month = Number(match[2]);
  const year = Number(match[3]);
  const date = new Date(year, month - 1, day);
  return Number.isNaN(date.getTime()) ? null : date.getMonth();
};

const isAllZeroSeries = (series) => Array.isArray(series) && series.every((item) => Number(item || 0) === 0);

export function SystemStats() {
  const [usersByMonth, setUsersByMonth] = useState(emptyMonthlyCounts());
  const [analysesByMonth, setAnalysesByMonth] = useState(emptyMonthlyCounts());
  const [revenueByMonth, setRevenueByMonth] = useState(Array(12).fill(0));
  const [topUsers, setTopUsers] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setIsLoading(true);
      setError('');
      const [usersResponse, analysesResponse, statsResponse] = await Promise.all([
        apiService.getAdminUsers(),
        apiService.getAdminAnalyses(),
        apiService.getAdminStats(),
      ]);

      const users = Array.isArray(usersResponse.users) ? usersResponse.users : [];
      const analyses = Array.isArray(analysesResponse.analyses) ? analysesResponse.analyses : [];

      const derivedUsersByMonth = emptyMonthlyCounts();
      users.forEach((user) => {
        const monthIndex = parseMonthIndex(user.joinDate || user.created_at || user.createdAt);
        if (monthIndex !== null) {
          derivedUsersByMonth[monthIndex] += 1;
        }
      });

      const derivedAnalysesByMonth = emptyMonthlyCounts();
      const derivedAnalysesByUser = {};
      analyses.forEach((analysis) => {
        const monthIndex = parseMonthIndex(analysis.date || analysis.created_at || analysis.timestamp);
        if (monthIndex !== null) {
          derivedAnalysesByMonth[monthIndex] += 1;
        }

        const userEmail = analysis.user || 'unknown';
        derivedAnalysesByUser[userEmail] = (derivedAnalysesByUser[userEmail] || 0) + 1;
      });

      const backendUsersByMonth = normalizeSeries(statsResponse.stats?.users_by_month);
      const backendAnalysesByMonth = normalizeSeries(statsResponse.stats?.analyses_by_month);
      const backendRevenueByMonth = normalizeSeries(statsResponse.stats?.revenue_by_month);

      const resolvedUsersByMonth = isAllZeroSeries(backendUsersByMonth) && users.length > 0
        ? derivedUsersByMonth
        : backendUsersByMonth;

      const resolvedAnalysesByMonth = isAllZeroSeries(backendAnalysesByMonth) && analyses.length > 0
        ? derivedAnalysesByMonth
        : backendAnalysesByMonth;

      const backendTopUsers = Array.isArray(statsResponse.stats?.top_users) ? statsResponse.stats.top_users : [];
      const fallbackTopUsers = Object.entries(derivedAnalysesByUser)
        .map(([email, analysesCount]) => ({
          email,
          analyses: analysesCount,
          revenue: 0,
        }))
        .sort((a, b) => b.analyses - a.analyses)
        .slice(0, 5);

      setUsersByMonth(resolvedUsersByMonth);
      setAnalysesByMonth(resolvedAnalysesByMonth);
      setRevenueByMonth(backendRevenueByMonth);
      setTopUsers(backendTopUsers.length > 0 ? backendTopUsers : fallbackTopUsers);
    } catch (err) {
      console.error('Failed to load system stats:', err);
      setError(err.message || 'Không thể tải thống kê hệ thống');
      setUsersByMonth(emptyMonthlyCounts());
      setAnalysesByMonth(emptyMonthlyCounts());
      setRevenueByMonth(Array(12).fill(0));
      setTopUsers([]);
    } finally {
      setIsLoading(false);
    }
  };

  const chartData = useMemo(() => {
    return {
      users: usersByMonth,
      analyses: analysesByMonth,
      revenue: revenueByMonth,
    };
  }, [usersByMonth, analysesByMonth, revenueByMonth]);

  const maxUsers = Math.max(...chartData.users, 1);
  const maxAnalyses = Math.max(...chartData.analyses, 1);
  const maxRevenue = Math.max(...chartData.revenue, 1);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-pink-500 mb-2">Thống kê hệ thống</h1>
          <p className="text-slate-400">Biểu đồ và báo cáo chi tiết từ dữ liệu thật</p>
        </div>
        <button
          onClick={loadStats}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-slate-700 bg-slate-900/70 text-slate-200 hover:border-cyan-500/50 hover:text-cyan-300 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          Tải lại
        </button>
      </div>

      {error && (
        <div className="bg-red-900/20 border border-red-700/30 text-red-300 rounded-xl p-4">{error}</div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-cyan-100 flex items-center gap-2">
              <Users className="w-5 h-5" />
              Người dùng mới
            </h2>
            <span className="text-green-400 text-sm">Dữ liệu thật</span>
          </div>
          <div className="flex items-end gap-2 h-48">
            {chartData.users.map((value, index) => (
              <div key={index} className="flex-1 flex flex-col items-center gap-2">
                <div className="w-full bg-slate-800 rounded-t-lg relative overflow-hidden" style={{ height: `${(value / maxUsers) * 100}%`, minHeight: '4px' }}>
                  <div className="absolute inset-0 bg-gradient-to-t from-cyan-500 to-blue-500 animate-fade-in" style={{ animationDelay: `${index * 50}ms` }}></div>
                </div>
                <span className="text-slate-500 text-xs">{MONTH_LABELS[index]}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-cyan-100 flex items-center gap-2">
              <FileText className="w-5 h-5" />
              Số lượng phân tích
            </h2>
            <span className="text-green-400 text-sm">Dữ liệu thật</span>
          </div>
          <div className="flex items-end gap-2 h-48">
            {chartData.analyses.map((value, index) => (
              <div key={index} className="flex-1 flex flex-col items-center gap-2">
                <div className="w-full bg-slate-800 rounded-t-lg relative overflow-hidden" style={{ height: `${(value / maxAnalyses) * 100}%`, minHeight: '4px' }}>
                  <div className="absolute inset-0 bg-gradient-to-t from-purple-500 to-pink-500 animate-fade-in" style={{ animationDelay: `${index * 50}ms` }}></div>
                </div>
                <span className="text-slate-500 text-xs">{MONTH_LABELS[index]}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-cyan-100 flex items-center gap-2">
              <DollarSign className="w-5 h-5" />
              Doanh thu ước tính từ dữ liệu thật
            </h2>
            <span className="text-green-400 text-sm">Từ phân tích thực tế</span>
          </div>
          <div className="flex items-end gap-2 h-48">
            {chartData.revenue.map((value, index) => (
              <div key={index} className="flex-1 flex flex-col items-center gap-2">
                <div className="w-full bg-slate-800 rounded-t-lg relative overflow-hidden" style={{ height: `${(value / maxRevenue) * 100}%`, minHeight: '4px' }}>
                  <div className="absolute inset-0 bg-gradient-to-t from-green-500 to-emerald-500 animate-fade-in" style={{ animationDelay: `${index * 50}ms` }}></div>
                </div>
                <span className="text-slate-500 text-xs">{MONTH_LABELS[index]}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-cyan-100 flex items-center gap-2">
              <TrendingUp className="w-5 h-5" />
              Top người dùng
            </h2>
          </div>
          <div className="space-y-3">
            {topUsers.length === 0 ? (
              <div className="text-slate-400 text-sm">Chưa có dữ liệu.</div>
            ) : (
              topUsers.map((user, index) => (
                <div key={`${user.email}-${index}`} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="bg-gradient-to-br from-cyan-500 to-pink-500 w-8 h-8 rounded-full flex items-center justify-center text-white text-sm">
                      {index + 1}
                    </div>
                    <div>
                      <div className="text-slate-300 text-sm">{user.email}</div>
                      <div className="text-slate-500 text-xs">{user.analyses} phân tích</div>
                    </div>
                  </div>
                  <div className="text-green-400 text-sm">{Number(user.revenue || 0).toLocaleString('vi-VN')} VNĐ</div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {isLoading && (
        <div className="text-slate-400 text-sm">Đang tải dữ liệu thống kê...</div>
      )}
    </div>
  );
}
