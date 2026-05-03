import { useState, useEffect } from 'react';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { UploadSection } from './components/UploadSection';
import { ResultPage } from './components/ResultPage';
import { AnalysisHistory } from './components/AnalysisHistory';
import { AccountSettings } from './components/AccountSettings';
import { PricingPlans } from './components/PricingPlans';
import { AdminDashboard } from './components/admin/AdminDashboard';
import { Header } from './components/Header';
import { Footer } from './components/Footer';
import { AboutPage } from './components/AboutPage';
import { PrivacyPolicyPage } from './components/PrivacyPolicyPage';
import { TermsPage } from './components/TermsPage';
import { PaymentReturnPage } from './components/PaymentReturnPage';
import { Chatbot } from './components/Chatbot';
import { TemplatesPage } from './components/TemplatesPage';
import apiService from './services/api';

const SESSION_HINT_KEY = 'legal-ai-session-hint';

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [userEmail, setUserEmail] = useState('');
  const [userAvatar, setUserAvatar] = useState('');
  const [userPlan, setUserPlan] = useState('free');
  const [analysisData, setAnalysisData] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState({ percent: 0, stage: '', detail: '' });
  const [isLoadingAuth, setIsLoadingAuth] = useState(true);
  const [showChatbot, setShowChatbot] = useState(false);
  
  const navigate = useNavigate();
  const location = useLocation();

  const loadCurrentProfile = async () => {
    try {
      const profileResponse = await apiService.getProfile();
      if (profileResponse && profileResponse.success && profileResponse.profile) {
        const profile = profileResponse.profile;
        if (profile.avatar) {
          setUserAvatar(`http://localhost:5000${profile.avatar}`);
        }

        const normalizedPlan = String(profile.plan || profile.subscription_tier || 'free').toLowerCase() === 'free' ? 'free' : 'pro';
        setUserPlan(normalizedPlan);
        return profile;
      }
    } catch (error) {
      console.warn('Could not load profile:', error);
    }

    return null;
  };

  // Restore session on mount (session-based auth with cookies)
  useEffect(() => {
    const restoreSession = async () => {
      // Chỉ restore session nếu user đã tick "Ghi nhớ đăng nhập"
      const rememberLogin = window.localStorage.getItem('legal-ai-remember') === 'true';
      const hasSessionHint = window.localStorage.getItem(SESSION_HINT_KEY) === '1';

      if (!hasSessionHint || !rememberLogin) {
        console.info('[auth] No session hint or remember not enabled, skipping restore');
        setIsLoadingAuth(false);
        return;
      }

      console.info('[auth] Session hint found, verifying backend session...');

      try {
        // Check if we have a session cookie (backend will verify)
        const response = await apiService.verifyToken();
        if (response && response.success && response.user) {
          console.info('[auth] Session restored for', response.user.email);
          setUserEmail(response.user.email);
          setIsAuthenticated(true);
          setIsAdmin(response.user.is_admin || false);
          await loadCurrentProfile();
        }
      } catch (error) {
        console.info('[auth] No active session or session expired');
        // No need to clear anything - session cookies handled by backend
      } finally {
        setIsLoadingAuth(false);
      }
    };
    
    restoreSession();
  }, []);

  // Listen for profile updates from AccountSettings (or other parts)
  useEffect(() => {
    const handler = (ev) => {
      const profile = ev.detail;
      if (profile && profile.avatar) {
        setUserAvatar(`http://localhost:5000${profile.avatar}`);
      } else {
        setUserAvatar('');
      }
      if (profile && profile.email) setUserEmail(profile.email);
      if (profile) {
        const normalizedPlan = String(profile.plan || profile.subscription_tier || 'free').toLowerCase() === 'free' ? 'free' : 'pro';
        setUserPlan(normalizedPlan);
      }
    };
    window.addEventListener('profile-updated', handler);
    return () => window.removeEventListener('profile-updated', handler);
  }, []);

  const handleLogin = async (email, password) => {
    try {
      console.info('[auth] Login requested for', email);
      const response = await apiService.login(email, password);

      // Check if login was successful (session cookie already set by backend)
      if (response && response.success) {
        window.localStorage.setItem(SESSION_HINT_KEY, '1');
        console.info('[auth] Login success for', response.user?.email || email);
        setUserEmail(response.user?.email || response.email || email);
        setIsAuthenticated(true);
        setIsAdmin(response.user?.is_admin || response.is_admin || false);
        await loadCurrentProfile();
        return { success: true };
      } else {
        // Handle case where login failed
        console.info('[auth] Login failed for', email, response);
        return { success: false, message: response?.message || response?.error || 'Đăng nhập thất bại' };
      }
    } catch (error) {
      console.error('[auth] Login error:', error);
      return { success: false, message: error.message || 'Lỗi kết nối' };
    }
  };

  const handleGoogleLogin = async (credential) => {
    try {
      console.info('[auth] Google login requested');
      const response = await apiService.googleLogin(credential);
      if (response && response.success) {
        window.localStorage.setItem(SESSION_HINT_KEY, '1');
        console.info('[auth] Google login success for', response.user?.email || 'unknown');
        setUserEmail(response.user?.email || '');
        setIsAuthenticated(true);
        setIsAdmin(response.user?.is_admin || false);
        await loadCurrentProfile();
        return { success: true };
      }

      return { success: false, message: response?.error || response?.message || 'Đăng nhập Google thất bại' };
    } catch (error) {
      console.error('[auth] Google login error:', error);
      return { success: false, message: error.message || 'Lỗi kết nối' };
    }
  };

  const handleLogout = async () => {
    try {
      console.info('[auth] Logout requested');
      await apiService.logout();
    } catch (error) {
      console.error('[auth] Logout error:', error);
    } finally {
      // Session cookies cleared by backend
      window.localStorage.removeItem(SESSION_HINT_KEY);
      setIsAuthenticated(false);
      setIsAdmin(false);
      setUserEmail('');
      setAnalysisData(null);
      navigate('/'); // Navigate to home
    }
  };

  const handleExitAdmin = () => {
    navigate('/');
  };

  const handleNavigate = (page) => {
    // Convert old page names to routes
    console.info('[nav] Navigate to', page);
    const routes = {
      'home': '/',
      'history': '/history',
      'settings': '/settings',
      'pricing': '/pricing',
      'templates': '/templates',
      'about': '/about',
      'privacy': '/privacy',
      'terms': '/terms',
      'admin': '/admin',
      'result': '/result'
    };
    navigate(routes[page] || '/');
  };

  const handleUpgrade = (plan) => {
    // Simulate payment process
    alert(`Bạn đã chọn gói ${plan === 'pro' ? 'Professional' : 'Free'}`);
  };

  const handleViewAnalysis = (historyItem) => {
    // Transform history data to analysis format
    const data = historyItem.fullData || {};
    const issuesArray = data.issues || [];
    
    const analysisData = {
      contractName: data.filename || historyItem.fileName,
      uploadDate: data.upload_time || historyItem.date,
      riskLevel: data.risk_level || 'medium',
      summary: data.summary || '',
      aiAnalysis: data.ai_analysis || '',
      
      // Safety Score - AI generated or calculated
      safetyScore: data.safety_score || historyItem.safetyScore,
      safetyReasoning: data.safety_reasoning || historyItem.safetyReasoning,
      
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
    // Use setTimeout to ensure state is updated before navigation
    setTimeout(() => navigate('/result'), 0);
  };

  const handleFileUpload = async (file) => {
    console.info('[upload] Upload started for', file?.name || 'unknown file');
    setIsAnalyzing(true);
    setAnalysisProgress({ percent: 8, stage: 'Đang tải file', detail: 'Đang gửi tài liệu lên máy chủ' });

    const progressSteps = [
      { percent: 24, stage: 'Đang trích xuất điều khoản', detail: 'AI đang đọc và tách các điều khoản quan trọng' },
      { percent: 48, stage: 'Đang phân tích rủi ro', detail: 'SVM và workflow pháp lý đang xử lý nội dung' },
      { percent: 70, stage: 'Đang tra cứu luật', detail: 'PageIndex đối chiếu các quy định liên quan' },
      { percent: 88, stage: 'Đang tổng hợp kết quả', detail: 'Hệ thống đang gom điểm số và khuyến nghị' },
    ];

    let progressIndex = 0;
    const progressTimer = window.setInterval(() => {
      const nextStep = progressSteps[progressIndex];
      if (!nextStep) {
        return;
      }

      setAnalysisProgress(nextStep);
      progressIndex += 1;
    }, 2000);
    
    try {
      // Call backend API to upload and analyze contract
      const response = await apiService.uploadContract(file);
      console.info('[upload] Upload response received', response?.success ? 'success' : 'failure');
      
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
        
        // Safety Score - AI generated or calculated
        safetyScore: data.safety_score,
        safetyReasoning: data.safety_reasoning,
        
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
      setAnalysisProgress({ percent: 100, stage: 'Hoàn tất', detail: 'Đang mở trang kết quả' });
      
      // Navigate to result page immediately after a successful analysis
      if (data.history_id) {
        navigate(`/result/${data.history_id}`);
      } else {
        navigate('/result');
      }
      
    } catch (error) {
      console.error('Upload error:', error);
      alert('Lỗi khi phân tích hợp đồng: ' + error.message);
    } finally {
      window.clearInterval(progressTimer);
      setIsAnalyzing(false);
      setAnalysisProgress({ percent: 0, stage: '', detail: '' });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-950 to-purple-950">
      {isLoadingAuth ? (
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-white text-xl">Đang tải...</div>
        </div>
      ) : location.pathname === '/admin' && isAdmin ? (
        <AdminDashboard 
          onNavigate={handleNavigate}
          onExitAdmin={handleExitAdmin}
          onLogout={handleLogout}
          userEmail={userEmail}
        />
      ) : (
        <>
          <Header
            isAuthenticated={isAuthenticated}
            isAdmin={isAdmin}
            userEmail={userEmail}
            userAvatar={userAvatar}
            userPlan={userPlan}
            currentPage={location.pathname === '/' ? 'home' : location.pathname.slice(1)}
            onLogin={handleLogin}
            onGoogleLogin={handleGoogleLogin}
            onLogout={handleLogout}
            onNavigate={handleNavigate}
          />

          <main className="container mx-auto px-4 py-8">
            <Routes>
              <Route path="/" element={
                <UploadSection
                  onFileUpload={handleFileUpload}
                  isAnalyzing={isAnalyzing}
                  analysisProgress={analysisProgress}
                />
              } />
              
              <Route path="/result" element={
                <ResultPage analysisData={analysisData} />
              } />
              
              <Route path="/result/:id" element={
                <ResultPage />
              } />
              
              <Route path="/history" element={
                <AnalysisHistory 
                  userEmail={userEmail}
                  onViewAnalysis={handleViewAnalysis}
                />
              } />
              
              <Route path="/settings" element={
                <AccountSettings 
                  userEmail={userEmail}
                  onUpgrade={handleUpgrade}
                />
              } />
              
              <Route path="/pricing" element={
                <PricingPlans
                  isAuthenticated={isAuthenticated}
                  onUpgrade={handleUpgrade}
                  currentPlan={userPlan}
                />
              } />

              <Route path="/templates" element={
                <TemplatesPage
                  onNavigate={handleNavigate}
                />
              } />

              <Route path="/about" element={<AboutPage />} />
              <Route path="/privacy" element={<PrivacyPolicyPage />} />
              <Route path="/terms" element={<TermsPage />} />
              <Route path="/payment/return" element={<PaymentReturnPage />} />
            </Routes>
          </main>

          <Footer />

          <Chatbot
            isOpen={showChatbot}
            onClose={() => setShowChatbot(false)}
            analysisData={analysisData}
          />

          <button
            onClick={() => setShowChatbot(true)}
            className="fixed bottom-6 right-6 z-40 w-14 h-14 bg-gradient-to-r from-cyan-500 to-pink-500 text-white rounded-full shadow-2xl shadow-cyan-500/40 flex items-center justify-center hover:from-cyan-400 hover:to-pink-400 transition-all duration-300 hover:scale-110 active:scale-95 group"
            title="Chat với AI"
          >
            <svg className="w-7 h-7 group-hover:animate-bounce" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M8.625 12a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H12m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 01-2.555-.337A5.972 5.972 0 015.41 20.97a5.969 5.969 0 01-.474-.065 4.48 4.48 0 00.978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25z" />
            </svg>
          </button>
        </>
      )}
    </div>
  );
}

