import { useState, useEffect } from 'react';
import { FileText, Calendar, AlertTriangle, Download, Eye, Trash2, Search, Filter } from 'lucide-react';
import apiService from '../services/api';

export function AnalysisHistory({ onViewAnalysis }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [historyData, setHistoryData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      setIsLoading(true);
      const response = await apiService.getHistory();
      
      if (response.success) {
        // Transform backend data to frontend format
        const transformedData = response.history.map((contract, index) => {
          const data = contract.data || {};
          
          // Parse date safely
          let date = 'N/A';
          try {
            if (contract.timestamp) {
              date = new Date(contract.timestamp).toISOString().split('T')[0];
            } else if (data.upload_time) {
              date = data.upload_time.split(' ')[0]; // Format: "DD/MM/YYYY HH:MM:SS"
            }
          } catch (e) {
            console.warn('Invalid date:', contract.timestamp);
            date = 'N/A';
          }
          
          return {
            id: contract.id || index + 1,
            fileName: data.filename || 'Không rõ',
            date: date,
            totalIssues: (data.issues || []).length || 0,
            highRisk: (data.issues || []).filter(i => 
              (typeof i === 'string' && i.includes('🚨')) || 
              (typeof i === 'object' && i.severity === 'high')
            ).length,
            mediumRisk: (data.issues || []).filter(i => 
              (typeof i === 'string' && i.includes('⚡')) || 
              (typeof i === 'object' && i.severity === 'medium')
            ).length,
            lowRisk: (data.issues || []).filter(i => 
              (typeof i === 'string' && i.includes('ℹ️')) || 
              (typeof i === 'object' && i.severity === 'low')
            ).length,
            status: 'completed',
            fullData: data // Store full data for viewing
          };
        });
        
        setHistoryData(transformedData);
      }
    } catch (error) {
      console.error('Failed to load history:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredHistory = historyData.filter(item => {
    const matchesSearch = item.fileName.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterStatus === 'all' || item.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

  const getStatusBadge = (status) => {
    switch (status) {
      case 'completed':
        return <span className="px-3 py-1 bg-green-500/20 text-green-300 text-xs rounded-full border border-green-500/30">Hoàn thành</span>;
      case 'processing':
        return <span className="px-3 py-1 bg-blue-500/20 text-blue-300 text-xs rounded-full border border-blue-500/30 flex items-center gap-1">
          <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" />
          Đang xử lý
        </span>;
      case 'failed':
        return <span className="px-3 py-1 bg-red-500/20 text-red-300 text-xs rounded-full border border-red-500/30">Lỗi</span>;
    }
  };

  const getRiskScore = (item) => {
    if (item.totalIssues === 0) return 100;
    return 100 - ((item.highRisk * 20 + item.mediumRisk * 10 + item.lowRisk * 5) / item.totalIssues) * 10;
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-pink-500 mb-2">
          Lịch sử phân tích
        </h1>
        <p className="text-slate-400">
          Quản lý và xem lại các hợp đồng đã phân tích
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 rounded-xl p-6">
          <div className="text-slate-400 text-sm mb-1">Tổng số phân tích</div>
          <div className="text-cyan-100 text-2xl">{historyData.length}</div>
        </div>
        <div className="bg-slate-900/70 backdrop-blur-xl border border-green-500/30 rounded-xl p-6">
          <div className="text-green-400 text-sm mb-1">Hoàn thành</div>
          <div className="text-green-300 text-2xl">{historyData.filter(h => h.status === 'completed').length}</div>
        </div>
        <div className="bg-slate-900/70 backdrop-blur-xl border border-blue-500/30 rounded-xl p-6">
          <div className="text-blue-400 text-sm mb-1">Đang xử lý</div>
          <div className="text-blue-300 text-2xl">{historyData.filter(h => h.status === 'processing').length}</div>
        </div>
        <div className="bg-slate-900/70 backdrop-blur-xl border border-red-500/30 rounded-xl p-6">
          <div className="text-red-400 text-sm mb-1">Có vấn đề</div>
          <div className="text-red-300 text-2xl">{historyData.filter(h => h.highRisk > 0).length}</div>
        </div>
      </div>

      {/* Search and Filter */}
      <div className="bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 rounded-xl p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Search */}
          <div className="relative">
            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500">
              <Search className="w-5 h-5" />
            </div>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Tìm kiếm theo tên file..."
              className="w-full bg-slate-800/50 border border-slate-700 rounded-xl pl-12 pr-4 py-3 text-slate-200 placeholder-slate-500 focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/20 transition-all"
            />
          </div>

          {/* Filter */}
          <div className="relative">
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
      </div>

      {/* History List */}
      <div className="space-y-4">
        {filteredHistory.length === 0 ? (
          <div className="bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 rounded-xl p-12 text-center">
            <FileText className="w-16 h-16 text-slate-600 mx-auto mb-4" />
            <h3 className="text-slate-400 mb-2">Không tìm thấy kết quả</h3>
            <p className="text-slate-500 text-sm">Thử thay đổi bộ lọc hoặc từ khóa tìm kiếm</p>
          </div>
        ) : (
          filteredHistory.map((item, index) => (
            <div
              key={item.id}
              className="group relative animate-fade-in bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 rounded-xl overflow-hidden hover:border-cyan-500/50 transition-all duration-300"
              style={{ animationDelay: `${index * 50}ms` }}
            >
              <div className="p-6">
                <div className="flex flex-col lg:flex-row lg:items-center gap-4">
                  {/* Icon and Info */}
                  <div className="flex items-start gap-4 flex-1">
                    <div className="bg-gradient-to-br from-cyan-500 to-blue-500 p-3 rounded-xl shadow-lg shadow-cyan-500/30 flex-shrink-0">
                      <FileText className="w-6 h-6 text-white" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-slate-200 truncate">{item.fileName}</h3>
                        {getStatusBadge(item.status)}
                      </div>
                      <div className="flex items-center gap-4 text-sm text-slate-400">
                        <span className="flex items-center gap-1">
                          <Calendar className="w-4 h-4" />
                          {new Date(item.date).toLocaleDateString('vi-VN')}
                        </span>
                        {item.status === 'completed' && (
                          <>
                            <span>•</span>
                            <span className="flex items-center gap-1">
                              <AlertTriangle className="w-4 h-4" />
                              {item.totalIssues} vấn đề
                            </span>
                            <span>•</span>
                            <span className="text-cyan-400">
                              Điểm).toFixed(0)}/100
                            </span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Risk Summary */}
                  {item.status === 'completed' && (
                    <div className="flex items-center gap-2">
                      {item.highRisk > 0 && (
                        <div className="px-3 py-1.5 bg-red-500/20 border border-red-500/30 rounded-lg">
                          <span className="text-red-300 text-sm">{item.highRisk} cao</span>
                        </div>
                      )}
                      {item.mediumRisk > 0 && (
                        <div className="px-3 py-1.5 bg-yellow-500/20 border border-yellow-500/30 rounded-lg">
                          <span className="text-yellow-300 text-sm">{item.mediumRisk} TB</span>
                        </div>
                      )}
                      {item.lowRisk > 0 && (
                        <div className="px-3 py-1.5 bg-blue-500/20 border border-blue-500/30 rounded-lg">
                          <span className="text-blue-300 text-sm">{item.lowRisk} thấp</span>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Actions */}
                  <div className="flex items-center gap-2">
                    {item.status === 'completed' && (
                      <>
                        <button
                          onClick={() => onViewAnalysis(item)}
                          className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white rounded-lg transition-all shadow-lg shadow-cyan-500/30"
                        >
                          <Eye className="w-4 h-4" />
                          <span className="hidden sm:inline">Xem</span>
                        </button>
                        <button className="p-2 text-slate-400 hover:text-cyan-400 hover:bg-slate-800 rounded-lg transition-all">
                          <Download className="w-5 h-5" />
                        </button>
                      </>
                    )}
                    <button className="p-2 text-slate-400 hover:text-red-400 hover:bg-red-900/20 rounded-lg transition-all">
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
