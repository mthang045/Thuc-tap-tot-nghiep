// API service for backend communication
const API_URL = '/api';

class ApiService {
  constructor() {
    this.baseURL = API_URL;
  }

  // Get CSRF token from cookie
  getCsrfToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  // Helper method for fetch requests
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const allowUnauthorized = options.allowUnauthorized === true;
    const config = {
      ...options,
      headers: {
        ...options.headers,
      },
      credentials: 'include', // Include cookies for session auth
    };

    delete config.allowUnauthorized;

    // Add CSRF token for unsafe methods
    const csrfToken = this.getCsrfToken();
    if (csrfToken && !['GET', 'HEAD', 'OPTIONS', 'TRACE'].includes(options.method?.toUpperCase())) {
      config.headers['X-CSRFToken'] = csrfToken;
    }

    // Only set JSON content type when sending a JSON body.
    if (options.body !== undefined && options.body !== null && !(options.body instanceof FormData)) {
      config.headers['Content-Type'] = 'application/json';
    }

    try {
      const response = await fetch(url, config);
      if (endpoint === '/verify') {
        console.info('[auth] verifyToken response status:', response.status);
      }
      
      // Try to parse JSON response
      let data;
      try {
        data = await response.json();
      } catch (e) {
        data = { error: 'Invalid response from server' };
      }

      if (!response.ok) {
        if (allowUnauthorized && response.status === 401) {
          if (endpoint === '/verify') {
            console.info('[auth] No active session found (401 from /verify)');
          }
          return data;
        }
        const errorMessage = data.error || data.message || data.detail || 'Request failed';
        throw new Error(errorMessage);
      }

      return data;
    } catch (error) {
      console.error(`API Error: ${endpoint}`, error);
      throw error;
    }
  }

  // Fetch CSRF token from server
  async fetchCsrfToken() {
    try {
      await fetch(`${this.baseURL}/csrf/`, {
        credentials: 'include',
      });
    } catch (error) {
      console.error('Failed to fetch CSRF token:', error);
    }
  }

  // Authentication
  async login(email, password) {
    console.info('[auth] api.login called for', email);
    // Ensure we have CSRF token before login
    await this.fetchCsrfToken();
    const body = JSON.stringify({ email, password });
    console.info('[auth] api.login request prepared');
    const response = await this.request('/login', {
      method: 'POST',
      body: body,
    });

    return response;
  }

  async googleLogin(credential) {
    await this.fetchCsrfToken();
    return this.request('/google-login', {
      method: 'POST',
      body: JSON.stringify({ credential }),
    });
  }

  async register(fullName, email, phone, password) {
    // Ensure we have CSRF token before register
    await this.fetchCsrfToken();
    return this.request('/register', {
      method: 'POST',
      body: JSON.stringify({
        full_name: fullName,
        email,
        phone,
        password,
      }),
    });
  }

  async logout() {
    return this.request('/logout', {
      method: 'POST',
    });
  }

  async verifyToken() {
    return this.request('/verify', {
      method: 'GET',
      allowUnauthorized: true,
    });
  }

  // Contract upload and analysis
  async uploadContract(file) {
    const formData = new FormData();
    formData.append('file', file);

    return this.request('/upload', {
      method: 'POST',
      body: formData,
    });
  }

  // Get analysis history
  async getHistory() {
    return this.request('/history', {
      method: 'GET',
    });
  }

  // Get specific analysis by ID
  async getAnalysisDetail(historyId) {
    return this.request(`/history/${historyId}`, {
      method: 'GET',
    });
  }

  // Get specific contract analysis
  async getContractAnalysis(contractId) {
    return this.request(`/contracts/${contractId}/analysis`, {
      method: 'GET',
    });
  }

  // Generate PDF report
  async generatePDF(analysisData) {
    try {
      const response = await fetch(`${this.baseURL}/generate-pdf/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/pdf',
        },
        credentials: 'include',
        body: JSON.stringify(analysisData),
      });

      if (!response.ok) {
        throw new Error('Failed to generate PDF');
      }

      // Get the blob
      const blob = await response.blob();
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${analysisData.contract_name || 'report'}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      return { success: true };
    } catch (error) {
      console.error('PDF generation error:', error);
      throw error;
    }
  }

  // Admin endpoints
  async getAdminStats() {
    return this.request('/admin/stats', {
      method: 'GET',
    });
  }

  async getAdminUsers() {
    return this.request('/admin/users', {
      method: 'GET',
    });
  }

  async updateAdminUser(userId, payload) {
    return this.request(`/admin/users/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    });
  }

  async deleteAdminUser(userId) {
    return this.request(`/admin/users/${userId}`, {
      method: 'DELETE',
    });
  }

  async getAdminAnalyses() {
    return this.request('/admin/analyses', {
      method: 'GET',
    });
  }

  async getAdminAnalysisDetail(analysisId) {
    const result = await this.request(`/admin/analyses/${analysisId}`, {
      method: 'GET',
    });
    console.log('[api] getAdminAnalysisDetail result:', result);
    return result;
  }

  async downloadAdminAnalysis(analysisId, fileName = 'analysis') {
    const response = await fetch(`${this.baseURL}/admin/analyses/${analysisId}/download`, {
      method: 'GET',
      credentials: 'include',
    });

    if (!response.ok) {
      let data = {};
      try {
        data = await response.json();
      } catch (e) {
        // ignore parse error
      }
      throw new Error(data.message || data.error || 'Không thể tải báo cáo');
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${String(fileName || 'analysis').replace(/\.[^/.]+$/, '')}_analysis.txt`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);

    return { success: true };
  }

  // Download admin analysis as PDF
  async downloadAdminAnalysisPDF(analysisId, fileName = 'analysis') {
    try {
      const response = await fetch(`${this.baseURL}/admin/analyses/${analysisId}/download-pdf`, {
        method: 'GET',
        credentials: 'include',
      });

      if (!response.ok) {
        let data = {};
        try {
          data = await response.json();
        } catch (e) {
          // ignore parse error
        }
        throw new Error(data.message || data.error || 'Không thể tải báo cáo PDF');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${String(fileName || 'Bao_Cao').replace(/\.[^/.]+$/, '')}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      return { success: true };
    } catch (error) {
      console.error('PDF download error:', error);
      throw error;
    }
  }

  // Get all contracts (admin)
  async getAllContracts() {
    return this.request('/contracts/', {
      method: 'GET',
    });
  }

  // Profile endpoints
  async getProfile() {
    return this.request('/profile/', {
      method: 'GET',
    });
  }

  async updateProfile(profileData) {
    return this.request('/profile/', {
      method: 'PUT',
      body: JSON.stringify(profileData),
    });
  }

  async uploadAvatar(file) {
    const formData = new FormData();
    formData.append('avatar', file);
    
    return this.request('/upload-avatar/', {
      method: 'POST',
      body: formData,
    });
  }

  async changePassword(oldPassword, newPassword) {
    return this.request('/change-password/', {
      method: 'PUT',
      body: JSON.stringify({ old_password: oldPassword, new_password: newPassword }),
    });
  }

  async deleteAvatar() {
    return this.request('/delete-avatar/', {
      method: 'DELETE'
    });
  }

  // Chat with AI about contract/legal questions
  async chat(message, history = [], context = {}) {
    return this.request('/chat/', {
      method: 'POST',
      body: JSON.stringify({ message, history, context }),
    });
  }
}

export default new ApiService();
