import { AlertTriangle, CheckCircle, Info, FileText, ArrowLeft, Download, TrendingUp, Shield, Sparkles } from 'lucide-react';
import { useState } from 'react';
import apiService from '../services/api';

import logoImage from '/logo.png';

export function AnalysisResults({ data, onReset }) {
  const [isGeneratingPDF, setIsGeneratingPDF] = useState(false);

  const handleDownloadPDF = async () => {
    setIsGeneratingPDF(true);
    try {
      // Prepare data for PDF
      const pdfData = {
        contract_name: data.contractName,
        upload_date: data.uploadDate,
        high_risk: data.highRisk,
        medium_risk: data.mediumRisk,
        low_risk: data.lowRisk,
        total_issues: data.totalIssues,
        issues: data.issues,
        ai_analysis: data.aiAnalysis || '',
        recommendations: data.summary
      };

      await apiService.generatePDF(pdfData);
    } catch (error) {
      console.error('Error generating PDF:', error);
      alert('Lỗi khi tạo báo cáo PDF: ' + error.message);
    } finally {
      setIsGeneratingPDF(false);
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

  // Calculate safety score - more logical approach
  // Start with 100 points (perfect contract) and deduct based on severity
  const calculateSafetyScore = () => {
    // Use AI-provided score if available
    if (data.safetyScore !== undefined) {
      return data.safetyScore;
    }
    
    // Fallback: Calculate based on issues
    let score = 100;
    score -= data.highRisk * 10;    // High risk: -10 points each
    score -= data.mediumRisk * 5;   // Medium risk: -5 points each
    score -= data.lowRisk * 2;      // Low risk: -2 points each
    
    // Ensure score stays between 0-100
    return Math.max(0, Math.min(100, score));
  };
  
  const riskScore = calculateSafetyScore();

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Logo in header */}
      <div className="flex items-center justify-between mb-8">
        <button
          onClick={onReset}
          className="group flex items-center gap-2 text-slate-400 hover:text-cyan-300 transition-all duration-300 hover:-translate-x-1"
        >
          <div className="bg-slate-800/80 backdrop-blur-sm p-2 rounded-lg shadow-md group-hover:shadow-cyan-500/30 transition-all border border-slate-700 group-hover:border-cyan-500/50">
            <ArrowLeft className="w-5 h-5" />
          </div>
          <span>Phân tích hợp đồng mới</span>
        </button>
        
        <div className="relative flex-shrink-0">
          <div className="absolute inset-0 bg-gradient-to-r from-cyan-400 to-pink-500 rounded-full blur-xl opacity-40"></div>
          <div className="relative w-10 h-10 md:w-14 md:h-14 rounded-full overflow-hidden flex items-center justify-center">
            <img 
              src={logoImage} 
              alt="GenZ Logo" 
              className="w-full h-full object-cover shadow-lg shadow-cyan-500/30"
            />
          </div>
        </div>
      </div>

      {/* Header Card */}
      <div className="relative mb-8">
        <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/20 to-pink-500/20 rounded-3xl blur-2xl"></div>
        <div className="relative bg-slate-900/70 backdrop-blur-xl rounded-3xl shadow-2xl border border-slate-700/50 p-8">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
            <div className="flex items-start gap-5">
              <div className="bg-gradient-to-br from-cyan-500 to-pink-500 p-4 rounded-2xl shadow-xl shadow-cyan-500/30">
                <FileText className="w-8 h-8 text-white" />
              </div>
              <div>
                <h2 className="text-cyan-100 mb-2">{data.contractName}</h2>
                <div className="flex flex-wrap items-center gap-4 text-slate-400">
                  <span className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse shadow-lg shadow-cyan-500/50"></div>
                    Phân tích hoàn tất
                  </span>
                  <span>•</span>
                  <span>{data.uploadDate}</span>
                </div>
              </div>
            </div>
            
            <button 
              onClick={handleDownloadPDF}
              disabled={isGeneratingPDF}
              className="group flex items-center gap-3 px-6 py-3 bg-gradient-to-r from-cyan-600 to-pink-600 text-white rounded-xl hover:from-cyan-500 hover:to-pink-500 transition-all duration-300 shadow-xl shadow-pink-500/30 hover:shadow-cyan-500/50 self-start lg:self-auto disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Download className={`w-5 h-5 ${isGeneratingPDF ? 'animate-bounce' : 'group-hover:animate-bounce'}`} />
              {isGeneratingPDF ? 'Đang tạo PDF...' : 'Tải báo cáo PDF'}
            </button>
          </div>
        </div>
      </div>

      {/* Enhanced Statistics Dashboard - All cards equal height */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6 mb-8">
        {/* Total Issues */}
        <div className="relative group">
          <div className="absolute inset-0 bg-gradient-to-br from-slate-500 to-slate-600 rounded-2xl opacity-0 group-hover:opacity-20 transition-opacity blur-xl"></div>
          <div className="relative bg-slate-900/70 backdrop-blur-sm rounded-2xl shadow-lg border border-slate-600/50 p-6 hover:shadow-2xl transition-all duration-300 h-full">
            <div className="flex items-center gap-2 mb-2">
              <Shield className="w-5 h-5 text-slate-400" />
              <div className="text-slate-400 text-sm">Tổng vấn đề</div>
            </div>
            <div className="text-3xl font-bold text-slate-200">{data.totalIssues}</div>
          </div>
        </div>

        {/* High Risk */}
        <div className="relative group">
          <div className="absolute inset-0 bg-gradient-to-br from-red-500 to-orange-500 rounded-2xl opacity-0 group-hover:opacity-30 transition-opacity blur-xl"></div>
          <div className="relative bg-gradient-to-br from-red-900/40 to-orange-900/40 rounded-2xl shadow-lg border-2 border-red-500/50 p-6 hover:shadow-2xl hover:shadow-red-500/30 transition-all duration-300 backdrop-blur-sm h-full">
            <div className="flex items-center gap-2 mb-2">
              <AlertTriangle className="w-5 h-5 text-red-400" />
              <div className="text-red-300 text-sm">Nghiêm trọng</div>
            </div>
            <div className="text-3xl font-bold text-red-200">{data.highRisk}</div>
          </div>
        </div>

        {/* Medium Risk */}
        <div className="relative group">
          <div className="absolute inset-0 bg-gradient-to-br from-yellow-500 to-amber-500 rounded-2xl opacity-0 group-hover:opacity-30 transition-opacity blur-xl"></div>
          <div className="relative bg-gradient-to-br from-yellow-900/40 to-amber-900/40 rounded-2xl shadow-lg border-2 border-yellow-500/50 p-6 hover:shadow-2xl hover:shadow-yellow-500/30 transition-all duration-300 backdrop-blur-sm h-full">
            <div className="flex items-center gap-2 mb-2">
              <AlertTriangle className="w-5 h-5 text-yellow-400" />
              <div className="text-yellow-300 text-sm">Trung bình</div>
            </div>
            <div className="text-3xl font-bold text-yellow-200">{data.mediumRisk}</div>
          </div>
        </div>

        {/* Low Risk */}
        <div className="relative group">
          <div className="absolute inset-0 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-2xl opacity-0 group-hover:opacity-30 transition-opacity blur-xl"></div>
          <div className="relative bg-gradient-to-br from-blue-900/40 to-indigo-900/40 rounded-2xl shadow-lg border-2 border-blue-500/50 p-6 hover:shadow-2xl hover:shadow-blue-500/30 transition-all duration-300 backdrop-blur-sm h-full">
            <div className="flex items-center gap-2 mb-2">
              <Info className="w-5 h-5 text-blue-400" />
              <div className="text-blue-300 text-sm">Thấp</div>
            </div>
            <div className="text-3xl font-bold text-blue-200">{data.lowRisk}</div>
          </div>
        </div>
      </div>

      {/* Issues List */}
      <div className="space-y-6">
        <div className="flex items-center gap-3">
          <div className="bg-gradient-to-r from-red-600 to-orange-600 p-2 rounded-lg shadow-lg shadow-red-500/50">
            <AlertTriangle className="w-6 h-6 text-white" />
          </div>
          <h2 className="text-cyan-100">Chi tiết các vấn đề phát hiện</h2>
        </div>
        
        {data.issues.map((issue, index) => {
          const config = getSeverityConfig(issue.severity);
          const Icon = config.icon;
          
          return (
            <div
              key={index}
              className="group relative animate-fade-in"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              {/* Issue content here */}
            </div>
          );
        })}
      </div>

      {/* Enhanced Footer Info */}
      <div className="mt-10 relative">
        {/* AI DETAILED ANALYSIS SECTION */}
        {data.aiAnalysis && (
          <div className="mb-6 relative animate-fade-in">
            <div className="absolute inset-0 bg-gradient-to-r from-purple-500/20 to-pink-500/20 rounded-2xl blur-xl"></div>
            <div className="relative bg-gradient-to-br from-purple-900/40 to-pink-900/40 border-2 border-purple-500/30 rounded-2xl p-8 shadow-xl backdrop-blur-xl">
              <div className="flex items-start gap-4 mb-6">
                <div className="bg-gradient-to-br from-purple-500 to-pink-500 p-3 rounded-xl flex-shrink-0 shadow-lg shadow-purple-500/50">
                  <Sparkles className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-200 to-pink-200 mb-2">
                    Phân tích chi tiết từ AI
                  </h3>
                  <p className="text-purple-200/80">Đánh giá chuyên sâu bởi trí tuệ nhân tạo</p>
                </div>
              </div>
              <div className="prose prose-invert max-w-none">
                <div className="text-purple-100/90 leading-relaxed whitespace-pre-wrap">
                  {data.aiAnalysis}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* SAFETY SCORE CARD - Moved here below AI analysis */}
        <div className="mb-6 relative animate-fade-in">
          <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/20 to-pink-500/20 rounded-2xl blur-xl"></div>
          <div className="relative bg-gradient-to-br from-slate-900/80 to-slate-800/80 backdrop-blur-xl rounded-2xl shadow-2xl border-2 border-cyan-500/30 p-8">
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
              <div className="flex items-center gap-4">
                <div className="bg-gradient-to-br from-cyan-500 to-pink-500 p-4 rounded-2xl shadow-xl shadow-cyan-500/50">
                  <TrendingUp className="w-8 h-8 text-white" />
                </div>
                <div>
                  <div className="text-slate-400 text-sm mb-1">Điểm an toàn tổng thể</div>
                  <div className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-pink-400">
                    {riskScore.toFixed(0)}/100
                  </div>
                </div>
              </div>
              {data.safetyReasoning && (
                <div className="flex-1 bg-slate-800/50 rounded-xl p-4 border border-slate-700">
                  <div className="text-xs text-slate-400 mb-2 font-semibold">💡 Nhận xét của AI:</div>
                  <div className="text-sm text-slate-300 leading-relaxed italic">
                    {data.safetyReasoning}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
        
        <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/20 to-emerald-500/20 rounded-2xl blur-xl"></div>
        <div className="relative bg-gradient-to-br from-cyan-900/30 to-emerald-900/30 border-2 border-cyan-500/30 rounded-2xl p-8 shadow-xl backdrop-blur-xl">
          <div className="flex items-start gap-4">
            <div className="bg-gradient-to-br from-cyan-500 to-emerald-500 p-3 rounded-xl flex-shrink-0 shadow-lg shadow-cyan-500/50">
              <CheckCircle className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-cyan-100 mb-3 flex items-center gap-2">
                Lưu ý quan trọng
                <span className="text-xs bg-cyan-500/20 text-cyan-300 px-2 py-1 rounded-full border border-cyan-500/30">Khuyến cáo</span>
              </h3>
              <p className="text-slate-300 leading-relaxed">
                Đây là kết quả phân tích tự động bằng AI với công nghệ RAG (Retrieval-Augmented Generation). Để đảm bảo tính chính xác cao nhất và tuân thủ pháp luật, vui lòng tham khảo ý kiến của luật sư hoặc chuyên gia pháp lý trước khi ký kết hợp đồng. Hệ thống chỉ mang tính chất tham khảo, cảnh báo sớm và hỗ trợ ra quyết định.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}