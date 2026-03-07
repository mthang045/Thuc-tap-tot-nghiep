import { useState, useEffect } from 'react';
import { UploadSection } from './components/UploadSection';
import { AnalysisResults } from './components/AnalysisResults';
import { AnalysisHistory } from './components/AnalysisHistory';
import { AccountSettings } from './components/AccountSettings';
import { PricingPlans } from './components/PricingPlans';
import { AdminDashboard } from './components/admin/AdminDashboard';
import { Header } from './components/Header';
import apiService from './services/api';

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [userEmail, setUserEmail] = useState('');
  const [currentPage, setCurrentPage] = useState('home');
  const [analysisData, setAnalysisData] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isLoadingAuth, setIsLoadingAuth] = useState(true);

  // Restore session on mount (session-based auth with cookies)
  useEffect(() => {
    const restoreSession = async () => {
      try {
        // Check if we have a session cookie (backend will verify)
        const response = await apiService.verifyToken();
        if (response && response.success && response.user) {
          setUserEmail(response.user.email);
          setIsAuthenticated(true);
          setIsAdmin(response.user.is_admin || false);
        }
      } catch (error) {
        console.log('No active session or session expired');
        // No need to clear anything - session cookies handled by backend
      } finally {
        setIsLoadingAuth(false);
      }
    };
    
    restoreSession();
  }, []);

  const handleLogin = async (email, password) => {
    try {
      const response = await apiService.login(email, password);
      console.log('Login response:', response);
      
      // Check if login was successful (session-based auth, no token needed)
      if (response && response.success) {
        // Session is stored in cookies by backend
        setUserEmail(response.email || email);
        setIsAuthenticated(true);
        setIsAdmin(response.is_admin || false);
        return { success: true };
      } else {
        // Handle case where login failed
        return { success: false, message: response?.message || response?.error || 'Đăng nhập thất bại' };
      }
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, message: error.message || 'Lỗi kết nối' };
    }
  };

  const handleLogout = async () => {
    try {
      await apiService.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Session cookies cleared by backend
      setIsAuthenticated(false);
      setIsAdmin(false);
      setUserEmail('');
      setAnalysisData(null);
      setCurrentPage('home');
    }
  };

  const handleNavigate = (page) => {
    setCurrentPage(page);
    setAnalysisData(null);
  };

  const handleUpgrade = (plan) => {
    // Simulate payment process
    alert(`Bạn đã chọn gói ${plan === 'pro' ? 'Professional' : 'Enterprise'}`);
  };

  const handleViewAnalysis = (historyItem) => {
    // Transform history data to analysis format
    const data = historyItem.fullData || {};
    const issuesArray = data.issues || [];
    
    const analysisData = {
      fileName: data.filename || historyItem.fileName,
      uploadDate: data.upload_time || historyItem.date,
      riskLevel: data.risk_level || 'medium',
      summary: data.summary || '',
      aiAnalysis: data.ai_analysis || '',
      totalIssues: issuesArray.length,
      highRisk: historyItem.highRisk || 0,
      mediumRisk: historyItem.mediumRisk || 0,
      lowRisk: historyItem.lowRisk || 0,
      issues: issuesArray.map((issue, idx) => ({
        type: typeof issue === 'string' ? 
          (issue.includes('🚨') ? 'high' : (issue.includes('⚡') ? 'medium' : 'low')) : 
          (issue.severity || 'medium'),
        title: typeof issue === 'string' ? issue.replace(/[🚨⚡ℹ️]/g, '').trim() : (issue.title || issue),
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
    
    setAnalysisData(analysisData);
    setCurrentPage('home');
  };

  const handleFileUpload = async (file) => {
    setIsAnalyzing(true);
    
    try {
      // Call backend API to upload and analyze contract
      const response = await apiService.uploadContract(file);
      console.log('Upload response:', response);
      
      // Check if response is successful
      if (!response.success) {
        alert(response.error || 'Phân tích thất bại');
        setIsAnalyzing(false);
        return;
      }
      
      // Get analysis data from response
      const data = response.data;
      
      // Count issues by severity
      const issuesArray = data.issues || [];
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
      
      // Transform backend response to frontend format
      const analysisData = {
        fileName: data.filename,
        uploadDate: data.upload_time,
        riskLevel: data.risk_level || 'medium',
        summary: data.summary,
        aiAnalysis: data.ai_analysis || '', // THÊM AI ANALYSIS
        totalIssues: issuesArray.length,
        highRisk: highRiskCount,
        mediumRisk: mediumRiskCount,
        lowRisk: lowRiskCount,
        issues: issuesArray.map((issue, idx) => ({
          type: typeof issue === 'string' ? 
            (issue.includes('🚨') ? 'high' : (issue.includes('⚡') ? 'medium' : 'low')) : 
            (issue.severity || 'medium'),
          title: typeof issue === 'string' ? issue.replace(/[🚨⚡ℹ️]/g, '').trim() : (issue.title || issue),
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
      
      console.log('Transformed analysis data:', analysisData);
      setAnalysisData(analysisData);
      
    } catch (error) {
      console.error('Upload error:', error);
      alert('Lỗi khi phân tích hợp đồng: ' + error.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-950 to-purple-950">
      {isLoadingAuth ? (
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-white text-xl">Đang tải...</div>
        </div>
      ) : isAdmin && currentPage === 'admin' ? (
        <AdminDashboard 
          onNavigate={handleNavigate}
          onLogout={handleLogout}
          userEmail={userEmail}
        />
      ) : (
        <>
          <Header
            isAuthenticated={isAuthenticated}
            isAdmin={isAdmin}
            userEmail={userEmail}
            currentPage={currentPage}
            onLogin={handleLogin}
            onLogout={handleLogout}
            onNavigate={handleNavigate}
          />

          <main className="container mx-auto px-4 py-8">
        {currentPage === 'home' && !analysisData && (
          <UploadSection
            isAuthenticated={isAuthenticated}
            onFileUpload={handleFileUpload}
            isAnalyzing={isAnalyzing}
          />
        )}

        {currentPage === 'home' && analysisData && (
          <AnalysisResults
            data={analysisData}
            onNewAnalysis={() => setAnalysisData(null)}
          />
        )}

        {currentPage === 'history' && (
          <AnalysisHistory 
            userEmail={userEmail}
            onViewAnalysis={handleViewAnalysis}
          />
        )}

        {currentPage === 'settings' && (
          <AccountSettings 
            userEmail={userEmail}
            onUpgrade={handleUpgrade}
          />
        )}

        {currentPage === 'pricing' && (
          <PricingPlans 
            isAuthenticated={isAuthenticated}
            onUpgrade={handleUpgrade}
          />
        )}
      </main>
      </>
      )}
    </div>
  );
}

