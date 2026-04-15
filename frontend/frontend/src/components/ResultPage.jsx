import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { AnalysisResults } from './AnalysisResults';
import apiService from '../services/api';

export function ResultPage({ analysisData: propAnalysisData }) {
  const { id } = useParams();
  const navigate = useNavigate();
  const [analysisData, setAnalysisData] = useState(propAnalysisData);
  const [isLoading, setIsLoading] = useState(!propAnalysisData && !!id);
  const [error, setError] = useState(null);

  useEffect(() => {
    // If we have analysis data from state, use it
    if (propAnalysisData) {
      setAnalysisData(propAnalysisData);
      setIsLoading(false);
      return;
    }

    // If we have an ID in URL, fetch from API
    if (id) {
      const fetchAnalysisData = async () => {
        try {
          setIsLoading(true);
          const response = await apiService.getAnalysisDetail(id);
          
          if (!response.success || !response.data) {
            throw new Error('Không tìm thấy dữ liệu phân tích');
          }

          const data = response.data;
          const issuesArray = data.issues || [];
          
          // Count issues by severity
          const highRiskCount = issuesArray.filter(i => 
            (typeof i === 'string' && i.includes('🚨')) || 
            (typeof i === 'object' && i.severity === 'high')
          ).length;
          const mediumRiskCount = issuesArray.filter(i => 
            (typeof i === 'string' && i.includes('⚡')) || 
            (typeof i === 'object' && i.severity === 'medium')
          ).length;
          const lowRiskCount = issuesArray.filter(i => 
            (typeof i === 'string' && i.includes('ℹ️')) || 
            (typeof i === 'object' && i.severity === 'low')
          ).length;

          // Transform to component format
          const transformedData = {
            fileName: data.filename,
            uploadDate: data.upload_time,
            riskLevel: data.risk_level || 'medium',
            summary: data.summary || '',
            aiAnalysis: data.ai_analysis || '',
            safetyScore: data.safety_score,
            safetyReasoning: data.safety_reasoning,
            totalIssues: issuesArray.length,
            highRisk: highRiskCount,
            mediumRisk: mediumRiskCount,
            lowRisk: lowRiskCount,
            issues: issuesArray.map((issue) => ({
              type: typeof issue === 'string' ? 
                (issue.includes('🚨') ? 'high' : (issue.includes('⚡') ? 'medium' : 'low')) : 
                (issue.severity || 'medium'),
              title: typeof issue === 'string' ? issue.replace(/🚨/g, '').replace(/⚡/g, '').replace(/ℹ️/g, '').trim() : (issue.title || issue),
              description: typeof issue === 'string' ? '' : (issue.description || ''),
              reference: typeof issue === 'string' ? '' : (issue.location || issue.article || ''),
              suggestion: typeof issue === 'string' ? '' : (issue.recommendation || '')
            })),
            keyPoints: [
              `Loại hợp đồng: ${data.contract_type || 'Không xác định'}`,
              `Mức độ rủi ro: ${data.risk_level || 'Không xác định'}`,
              `Khả năng vi phạm: ${data.has_violation ? 'Có' : 'Không'}`
            ],
            recommendations: issuesArray,
            legalReferences: data.legal_references ? data.legal_references.map(ref => ({
              title: ref.title,
              articles: [ref.content],
              relevance: ref.source
            })) : []
          };

          setAnalysisData(transformedData);
          setError(null);
        } catch (err) {
          console.error('Error fetching analysis:', err);
          setError(err.message || 'Không thể tải dữ liệu phân tích');
        } finally {
          setIsLoading(false);
        }
      };

      fetchAnalysisData();
    }
  }, [id, propAnalysisData]);

  const handleReset = () => {
    navigate('/');
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-white text-xl">Đang tải kết quả phân tích...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <div className="text-red-400 text-xl mb-4">Lỗi: {error}</div>
        <button 
          onClick={handleReset}
          className="px-6 py-3 bg-cyan-600 text-white rounded-lg hover:bg-cyan-500"
        >
          Quay lại trang chủ
        </button>
      </div>
    );
  }

  if (!analysisData) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <div className="text-slate-400 text-xl mb-4">Không tìm thấy dữ liệu phân tích</div>
        <button 
          onClick={handleReset}
          className="px-6 py-3 bg-cyan-600 text-white rounded-lg hover:bg-cyan-500"
        >
          Quay lại trang chủ
        </button>
      </div>
    );
  }

  return <AnalysisResults data={analysisData} onReset={handleReset} />;
}
