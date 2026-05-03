import { useEffect, useMemo, useState } from 'react';
import { FileText, Calendar, Eye, Download, Filter, RefreshCw, AlertTriangle, Info, CheckCircle, Sparkles, TrendingUp, Shield, ArrowLeft } from 'lucide-react';
import apiService from '../../services/api';

import logoImage from '/logo.png';

export function AnalyticsManagement() {
  const [filterStatus, setFilterStatus] = useState('all');
  const [analyses, setAnalyses] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedAnalysis, setSelectedAnalysis] = useState(null);
  const [isDetailLoading, setIsDetailLoading] = useState(false);

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

  const handleView = async (analysisId) => {
    try {
      setIsDetailLoading(true);
      setSelectedAnalysis(null);
      const response = await apiService.getAdminAnalysisDetail(analysisId);
      
      if (response.success && response.analysis) {
        setSelectedAnalysis(response.analysis);
      } else {
        alert('Không thể tải chi tiết: ' + (response.message || 'Lỗi không xác định'));
      }
    } catch (err) {
      alert('Lỗi: ' + err.message);
    } finally {
      setIsDetailLoading(false);
    }
  };

  const handleDownloadPDF = async (analysis) => {
    try {
      if (!analysis?.id) {
        alert('Không tìm thấy ID phân tích');
        return;
      }
      await apiService.downloadAdminAnalysisPDF(analysis.id, analysis.fileName);
    } catch (err) {
      alert('Lỗi tải PDF: ' + err.message);
    }
  };

  const getSeverityConfig = (severity) => {
    switch (severity) {
      case 'high':
        return {
          color: 'red',
          label: 'Nghiêm trọng',
          icon: AlertTriangle,
          bgClass: 'bg-gradient-to-br from-red-900/40 to-orange-900/40',
          borderClass: 'border-red-500/50',
          textClass: 'text-red-300',
          badgeClass: 'bg-gradient-to-r from-red-500 to-orange-500 text-white shadow-lg shadow-red-500/50',
          iconBg: 'bg-red-500/20 border border-red-500/30'
        };
      case 'medium':
        return {
          color: 'yellow',
          label: 'Trung bình',
          icon: AlertTriangle,
          bgClass: 'bg-gradient-to-br from-yellow-900/40 to-amber-900/40',
          borderClass: 'border-yellow-500/50',
          textClass: 'text-yellow-300',
          badgeClass: 'bg-gradient-to-r from-yellow-500 to-amber-500 text-white shadow-lg shadow-yellow-500/50',
          iconBg: 'bg-yellow-500/20 border border-yellow-500/30'
        };
      case 'low':
        return {
          color: 'blue',
          label: 'Thấp',
          icon: Info,
          bgClass: 'bg-gradient-to-br from-blue-900/40 to-indigo-900/40',
          borderClass: 'border-blue-500/50',
          textClass: 'text-blue-300',
          badgeClass: 'bg-gradient-to-r from-blue-500 to-indigo-500 text-white shadow-lg shadow-blue-500/50',
          iconBg: 'bg-blue-500/20 border border-blue-500/30'
        };
      default:
        return {
          color: 'blue',
          label: 'Thông tin',
          icon: Info,
          bgClass: 'bg-gradient-to-br from-blue-900/40 to-indigo-900/40',
          borderClass: 'border-blue-500/50',
          textClass: 'text-blue-300',
          badgeClass: 'bg-gradient-to-r from-blue-500 to-indigo-500 text-white shadow-lg shadow-blue-500/50',
          iconBg: 'bg-blue-500/20 border border-blue-500/30'
        };
    }
  };

  const cleanMarkdownText = (value) => {
    if (typeof value !== 'string') {
      return value || '';
    }
    return value
      .replace(/\*\*/g, '')
      .replace(/^#{1,6}\s+/gm, '')
      .replace(/^\s*-\s+/gm, '• ')
      .replace(/^\s*\d+\.\s+/gm, '• ')
      .trim();
  };

  const calculateSafetyScore = (analysis) => {
    if (analysis?.safetyScore !== undefined) {
      return analysis.safetyScore;
    }
    let score = 100;
    const issues = analysis?.issuesList || analysis?.issues || [];
    if (Array.isArray(issues)) {
      issues.forEach(issue => {
        const severity = issue.severity || issue.type || 'low';
        if (severity === 'high') score -= 10;
        else if (severity === 'medium') score -= 5;
        else if (severity === 'low') score -= 2;
      });
    }
    return Math.max(0, Math.min(100, score));
  };

  const handleDownloadDetailPDF = async () => {
    if (!selectedAnalysis) return;
    setIsDetailLoading(true);
    try {
      const pdfData = {
        contract_name: selectedAnalysis.fileName || 'Hop_Dong_Admin',
        upload_date: selectedAnalysis.date || new Date().toLocaleString('vi-VN'),
        high_risk: selectedAnalysis.highRisk || 0,
        medium_risk: selectedAnalysis.mediumRisk || 0,
        low_risk: selectedAnalysis.lowRisk || 0,
        total_issues: Array.isArray(selectedAnalysis.issuesList) ? selectedAnalysis.issuesList.length : 0,
        issues: selectedAnalysis.issuesList || [],
        ai_analysis: selectedAnalysis.aiAnalysis || selectedAnalysis.ai_analysis || '',
        safety_score: calculateSafetyScore(selectedAnalysis),
      };
      await apiService.generatePDF(pdfData);
    } catch (error) {
      console.error('Error generating PDF:', error);
      alert('Lỗi khi tạo báo cáo PDF: ' + error.message);
    } finally {
      setIsDetailLoading(false);
    }
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
                  <button
                    className="flex items-center gap-2 px-4 py-2 bg-cyan-600/20 text-cyan-300 hover:bg-cyan-600/30 rounded-lg transition-colors border border-cyan-500/30 disabled:opacity-50"
                    disabled={!analysis?.id}
                    onClick={() => handleView(analysis.id)}
                  >
                    <Eye className="w-4 h-4" />
                    <span className="hidden sm:inline">Xem</span>
                  </button>
                  <button
                    title="Tải báo cáo PDF"
                    disabled={!analysis?.id || analysis.status !== 'completed'}
                    className="p-2 text-slate-400 hover:text-cyan-400 hover:bg-slate-800 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                    onClick={() => handleDownloadPDF(analysis)}
                  >
                    <Download className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {(selectedAnalysis || isDetailLoading) && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 overflow-y-auto" onClick={() => !isDetailLoading && setSelectedAnalysis(null)}>
          <div className="w-full max-w-6xl my-8 relative" onClick={(e) => e.stopPropagation()}>
            <div className="bg-slate-900/95 border border-slate-700 rounded-2xl overflow-hidden shadow-2xl">
              {/* Header */}
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/20 to-pink-500/20 rounded-2xl"></div>
                <div className="relative bg-slate-900/70 backdrop-blur-xl border-b border-slate-700/50 p-6">
                  <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                    <div className="flex items-start gap-4">
                      <div className="bg-gradient-to-br from-cyan-500 to-pink-500 p-3 rounded-xl shadow-lg shadow-cyan-500/30">
                        <FileText className="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <h3 className="text-cyan-100 text-xl mb-1">{selectedAnalysis?.fileName || 'Chi tiết phân tích'}</h3>
                        <div className="flex flex-wrap items-center gap-3 text-sm text-slate-400">
                          <span className="flex items-center gap-1">
                            <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse shadow-lg shadow-cyan-500/50"></div>
                            Phân tích hoàn tất
                          </span>
                          <span>•</span>
                          <span>{formatDate(selectedAnalysis?.date)}</span>
                          <span>•</span>
                          <span>User: <span className="text-cyan-300">{selectedAnalysis?.user}</span></span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <button
                        onClick={handleDownloadDetailPDF}
                        disabled={isDetailLoading}
                        className="group flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-cyan-600 to-pink-600 text-white rounded-xl hover:from-cyan-500 hover:to-pink-500 transition-all shadow-xl shadow-pink-500/30 hover:shadow-cyan-500/50 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <Download className={`w-5 h-5 ${isDetailLoading ? 'animate-bounce' : 'group-hover:animate-bounce'}`} />
                        {isDetailLoading ? 'Đang tải...' : 'Tải PDF'}
                      </button>
                      <button
                        className="p-2.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-all"
                        onClick={() => setSelectedAnalysis(null)}
                      >
                        <span className="text-2xl">&times;</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              {/* Content */}
              <div className="p-6 space-y-6 max-h-[70vh] overflow-y-auto">
                {isDetailLoading ? (
                  <div className="text-slate-400 text-center py-12">Đang tải chi tiết...</div>
                ) : selectedAnalysis ? (
                  <>
                    {/* Statistics Dashboard */}
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                      <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700/50">
                        <div className="flex items-center gap-2 mb-1">
                          <Shield className="w-4 h-4 text-slate-400" />
                          <div className="text-slate-400 text-xs">Tổng vấn đề</div>
                        </div>
                        <div className="text-2xl font-bold text-slate-200">{selectedAnalysis.issuesList?.length || 0}</div>
                      </div>
                      <div className="bg-gradient-to-br from-red-900/40 to-orange-900/40 rounded-xl p-4 border-2 border-red-500/50">
                        <div className="flex items-center gap-2 mb-1">
                          <AlertTriangle className="w-4 h-4 text-red-400" />
                          <div className="text-red-300 text-xs">Nghiêm trọng</div>
                        </div>
                        <div className="text-2xl font-bold text-red-200">{selectedAnalysis.highRisk || 0}</div>
                      </div>
                      <div className="bg-gradient-to-br from-yellow-900/40 to-amber-900/40 rounded-xl p-4 border-2 border-yellow-500/50">
                        <div className="flex items-center gap-2 mb-1">
                          <AlertTriangle className="w-4 h-4 text-yellow-400" />
                          <div className="text-yellow-300 text-xs">Trung bình</div>
                        </div>
                        <div className="text-2xl font-bold text-yellow-200">{selectedAnalysis.mediumRisk || 0}</div>
                      </div>
                      <div className="bg-gradient-to-br from-blue-900/40 to-indigo-900/40 rounded-xl p-4 border-2 border-blue-500/50">
                        <div className="flex items-center gap-2 mb-1">
                          <Info className="w-4 h-4 text-blue-400" />
                          <div className="text-blue-300 text-xs">Thấp</div>
                        </div>
                        <div className="text-2xl font-bold text-blue-200">{selectedAnalysis.lowRisk || 0}</div>
                      </div>
                    </div>

                    {/* Contract Info */}
                    <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700/50">
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                        <div>
                          <span className="text-slate-400">Loại hợp đồng:</span>
                          <div className="text-slate-200 font-medium">{selectedAnalysis.contractType || 'Không rõ'}</div>
                        </div>
                        <div>
                          <span className="text-slate-400">Mức rủi ro:</span>
                          <div className="text-slate-200 font-medium">{selectedAnalysis.riskLevel || 'Không rõ'}</div>
                        </div>
                        <div>
                          <span className="text-slate-400">Ngày phân tích:</span>
                          <div className="text-slate-200 font-medium">{formatDate(selectedAnalysis.date)}</div>
                        </div>
                      </div>
                    </div>

                    {/* Issues List */}
                    {Array.isArray(selectedAnalysis.issuesList) && selectedAnalysis.issuesList.length > 0 && (
                      <div className="space-y-4">
                        <div className="flex items-center gap-3">
                          <div className="bg-gradient-to-r from-red-600 to-orange-600 p-2 rounded-lg shadow-lg shadow-red-500/50">
                            <AlertTriangle className="w-5 h-5 text-white" />
                          </div>
                          <h4 className="text-cyan-100 font-semibold">Chi tiết các vấn đề phát hiện</h4>
                        </div>
                        {selectedAnalysis.issuesList.map((issue, index) => {
                          if (!issue) return null;
                          const issueType = issue.severity || issue.type || 'medium';
                          const config = getSeverityConfig(issueType);
                          const Icon = config.icon;
                          const issueTitle = issue.title || issue || '';
                          const issueDesc = issue.description || '';
                          const issueRef = issue.reference || issue.article || '';
                          const issueSuggestion = issue.suggestion || issue.recommendation || '';

                          return (
                            <div
                              key={index}
                              className={`relative ${config.bgClass} border ${config.borderClass} rounded-xl p-4 shadow-lg`}
                            >
                              <div className="flex items-start gap-3">
                                <div className={`flex-shrink-0 ${config.iconBg} p-2 rounded-lg`}>
                                  <Icon className={`w-4 h-4 ${config.textClass}`} />
                                </div>
                                <div className="flex-1 min-w-0">
                                  <div className="flex items-center gap-2 mb-1 flex-wrap">
                                    <h5 className={`font-semibold ${config.textClass}`}>{issueTitle}</h5>
                                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${config.badgeClass}`}>
                                      {config.label}
                                    </span>
                                  </div>
                                  {issueDesc && (
                                    <p className="text-slate-300 text-sm mb-2 leading-relaxed">{issueDesc}</p>
                                  )}
                                  {issueRef && (
                                    <div className="flex items-center gap-1.5 mb-2">
                                      <span className="text-slate-500 text-xs">Điều luật:</span>
                                      <span className="text-cyan-400 text-xs font-medium">{issueRef}</span>
                                    </div>
                                  )}
                                  {issueSuggestion && (
                                    <div className="mt-2 p-2 bg-slate-800/50 rounded-lg border border-slate-700/50">
                                      <div className="text-xs text-green-400 font-medium mb-1">Khuyến nghị:</div>
                                      <p className="text-slate-300 text-sm">{issueSuggestion}</p>
                                    </div>
                                  )}
                                </div>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    )}

                    {/* Safety Score */}
                    <div className="bg-gradient-to-br from-cyan-900/30 to-pink-900/30 border-2 border-cyan-500/30 rounded-xl p-6">
                      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                        <div className="flex items-center gap-4">
                          <div className="bg-gradient-to-br from-cyan-500 to-pink-500 p-3 rounded-xl shadow-lg shadow-cyan-500/50">
                            <TrendingUp className="w-6 h-6 text-white" />
                          </div>
                          <div>
                            <div className="text-slate-400 text-sm mb-1">Điểm an toàn tổng thể</div>
                            <div className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-pink-400">
                              {calculateSafetyScore(selectedAnalysis)}/100
                            </div>
                          </div>
                        </div>
                        {selectedAnalysis.safetyReasoning && (
                          <div className="flex-1 bg-slate-800/50 rounded-xl p-3 border border-slate-700">
                            <div className="text-xs text-slate-400 mb-1 font-semibold">Nhận xét của AI:</div>
                            <div className="text-sm text-slate-300 leading-relaxed italic">
                              {cleanMarkdownText(selectedAnalysis.safetyReasoning)}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* AI Analysis */}
                    {(selectedAnalysis.aiAnalysis || selectedAnalysis.ai_analysis) && (
                      <div className="bg-gradient-to-br from-purple-900/40 to-pink-900/40 border-2 border-purple-500/30 rounded-xl p-6">
                        <div className="flex items-start gap-4 mb-4">
                          <div className="bg-gradient-to-br from-purple-500 to-pink-500 p-2.5 rounded-xl shadow-lg shadow-purple-500/50">
                            <Sparkles className="w-5 h-5 text-white" />
                          </div>
                          <div>
                            <h4 className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-200 to-pink-200 mb-1">
                              Phân tích chi tiết từ AI
                            </h4>
                            <p className="text-purple-200/80 text-sm">Đánh giá chuyên sâu bởi trí tuệ nhân tạo</p>
                          </div>
                        </div>
                        <div className="text-purple-100/90 leading-relaxed whitespace-pre-wrap bg-slate-800/30 rounded-lg p-4">
                          {cleanMarkdownText(selectedAnalysis.aiAnalysis || selectedAnalysis.ai_analysis)}
                        </div>
                      </div>
                    )}

                    {/* Summary */}
                    {selectedAnalysis.summaryText && (
                      <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700/50">
                        <div className="flex items-start gap-3">
                          <div className="bg-cyan-500/20 p-2 rounded-lg">
                            <FileText className="w-5 h-5 text-cyan-400" />
                          </div>
                          <div>
                            <h4 className="text-cyan-200 font-semibold mb-2">Tóm tắt</h4>
                            <div className="text-slate-300 leading-relaxed whitespace-pre-wrap">
                              {cleanMarkdownText(selectedAnalysis.summaryText)}
                            </div>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Important Notice */}
                    <div className="bg-gradient-to-br from-cyan-900/30 to-emerald-900/30 border-2 border-cyan-500/30 rounded-xl p-6">
                      <div className="flex items-start gap-4">
                        <div className="bg-gradient-to-br from-cyan-500 to-emerald-500 p-2.5 rounded-xl shadow-lg shadow-cyan-500/50">
                          <CheckCircle className="w-5 h-5 text-white" />
                        </div>
                        <div>
                          <h4 className="text-cyan-100 mb-2 flex items-center gap-2">
                            Lưu ý quan trọng
                            <span className="text-xs bg-cyan-500/20 text-cyan-300 px-2 py-0.5 rounded-full border border-cyan-500/30">Khuyến cáo</span>
                          </h4>
                          <p className="text-slate-300 leading-relaxed text-sm">
                            Đây là kết quả phân tích tự động bằng AI với công nghệ RAG (Retrieval-Augmented Generation). Để đảm bảo tính chính xác cao nhất và tuân thủ pháp luật, vui lòng tham khảo ý kiến của luật sư hoặc chuyên gia pháp lý trước khi ký kết hợp đồng. Hệ thống chỉ mang tính chất tham khảo, cảnh báo sớm và hỗ trợ ra quyết định.
                          </p>
                        </div>
                      </div>
                    </div>
                  </>
                ) : null}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
