import { useEffect, useMemo, useState } from 'react';
import { FileText, Calendar, Eye, Download, Filter, RefreshCw } from 'lucide-react';
import apiService from '../../services/api';

export function AnalyticsManagement() {
  const [filterStatus, setFilterStatus] = useState('all');
  const [analyses, setAnalyses] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadAnalyses();
  }, []);

  const loadAnalyses = async () => {
    try {
      setIsLoading(true);
      setError('');
      const response = await apiService.getAdminAnalyses();
      setAnalyses(Array.isArray(response.analyses) ? response.analyses : []);
    } catch (err) {
      console.error('Failed to load admin analyses:', err);
      setError(err.message || 'Không thể tải danh sách phân tích');
      setAnalyses([]);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredAnalyses = useMemo(() => {
    return analyses.filter(a => filterStatus === 'all' || a.status === filterStatus);
  }, [analyses, filterStatus]);

  const getStatusBadge = (status) => {
    switch (status) {
      case 'completed':
        return <span className="px-3 py-1 bg-green-500/20 text-green-300 text-xs rounded-full border border-green-500/30">Hoàn thành</span>;
      case 'processing':
        return <span className="px-3 py-1 bg-blue-500/20 text-blue-300 text-xs rounded-full border border-blue-500/30 flex items-center gap-1"><div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" />Đang xử lý</span>;
      case 'failed':
        return <span className="px-3 py-1 bg-red-500/20 text-red-300 text-xs rounded-full border border-red-500/30">Lỗi</span>;
      default:
        return <span className="px-3 py-1 bg-slate-500/20 text-slate-300 text-xs rounded-full border border-slate-500/30">{status || 'unknown'}</span>;
    }
  };

  const formatDate = (value) => {
    if (!value) return 'Chưa có';
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return value;
    return date.toLocaleString('vi-VN');
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-pink-500 mb-2">Quản lý phân tích</h1>
          <p className="text-slate-400">Tất cả các phân tích trong hệ thống</p>
        </div>
        <button
          onClick={loadAnalyses}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-slate-700 bg-slate-900/70 text-slate-200 hover:border-cyan-500/50 hover:text-cyan-300 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          Tải lại
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 rounded-xl p-4">
          <div className="text-slate-400 text-sm mb-1">Tổng phân tích</div>
          <div className="text-2xl text-slate-100">{analyses.length}</div>
        </div>
        <div className="bg-slate-900/70 backdrop-blur-xl border border-green-500/30 rounded-xl p-4">
          <div className="text-green-400 text-sm mb-1">Hoàn thành</div>
          <div className="text-2xl text-green-300">{analyses.filter(a => a.status === 'completed').length}</div>
        </div>
        <div className="bg-slate-900/70 backdrop-blur-xl border border-blue-500/30 rounded-xl p-4">
          <div className="text-blue-400 text-sm mb-1">Đang xử lý</div>
          <div className="text-2xl text-blue-300">{analyses.filter(a => a.status === 'processing').length}</div>
        </div>
        <div className="bg-slate-900/70 backdrop-blur-xl border border-red-500/30 rounded-xl p-4">
          <div className="text-red-400 text-sm mb-1">Lỗi</div>
          <div className="text-2xl text-red-300">{analyses.filter(a => a.status === 'failed').length}</div>
        </div>
      </div>

      <div className="bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 rounded-xl p-6">
        <div className="relative max-w-md">
          <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500">
            <Filter className="w-5 h-5" />
          </div>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="w-full bg-slate-800/50 border border-slate-700 rounded-xl pl-12 pr-4 py-3 text-slate-200 focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/20 transition-all appearance-none cursor-pointer"
          >
            <option value="all">Tất cả trạng thái</option>
            <option value="completed">Hoàn thành</option>
            <option value="processing">Đang xử lý</option>
            <option value="failed">Lỗi</option>
          </select>
        </div>
      </div>

      {error && (
        <div className="bg-red-900/20 border border-red-700/30 text-red-300 rounded-xl p-4">{error}</div>
      )}

      <div className="space-y-4">
        {isLoading ? (
          <div className="bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 rounded-xl p-6 text-slate-400">Đang tải dữ liệu phân tích...</div>
        ) : filteredAnalyses.length === 0 ? (
          <div className="bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 rounded-xl p-6 text-slate-400">Không có phân tích nào phù hợp.</div>
        ) : (
          filteredAnalyses.map((analysis, index) => (
            <div
              key={analysis.id}
              className="bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 rounded-xl p-6 hover:border-cyan-500/50 transition-all animate-fade-in"
              style={{ animationDelay: `${index * 50}ms` }}
            >
              <div className="flex flex-col lg:flex-row lg:items-center gap-4">
                <div className="flex items-start gap-4 flex-1">
                  <div className="bg-gradient-to-br from-cyan-500 to-blue-500 p-3 rounded-xl shadow-lg shadow-cyan-500/30">
                    <FileText className="w-6 h-6 text-white" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-slate-200">{analysis.fileName}</h3>
                      {getStatusBadge(analysis.status)}
                    </div>
                    <div className="flex flex-wrap items-center gap-4 text-sm text-slate-400">
                      <span className="flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        {formatDate(analysis.date)}
                      </span>
                      <span>•</span>
                      <span>User: {analysis.user}</span>
                      <span>•</span>
                      <span className="text-cyan-400">{analysis.issues} vấn đề</span>
                      {analysis.highRisk > 0 && (
                        <>
                          <span>•</span>
                          <span className="text-red-400">{analysis.highRisk} nghiêm trọng</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button className="flex items-center gap-2 px-4 py-2 bg-cyan-600/20 text-cyan-300 hover:bg-cyan-600/30 rounded-lg transition-colors border border-cyan-500/30" disabled>
                    <Eye className="w-4 h-4" />
                    <span className="hidden sm:inline">Xem</span>
                  </button>
                  <button className="p-2 text-slate-400 hover:text-cyan-400 hover:bg-slate-800 rounded-lg transition-all" disabled>
                    <Download className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
