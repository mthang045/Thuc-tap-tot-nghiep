// API service for backend communication
const API_URL = import.meta.env.VITE_API_URL || '/api';
const API_BASE = import.meta.env.VITE_API_BASE || (API_URL.startsWith('http') ? new URL(API_URL).origin : 'http://localhost:5000');

export function toAbsoluteUrl(path = '') {
  if (!path) return '';
  if (/^https?:\/\//i.test(path)) return path;
  const normalized = path.startsWith('/') ? path : `/${path}`;
  return `${API_BASE}${normalized}`;
}

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
    const config = {
      ...options,
      headers: {
        ...options.headers,
      },
      credentials: 'include', // Include cookies for session auth
    };

    // Add JWT token from localStorage
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }

    // Add CSRF token for unsafe methods
    const csrfToken = this.getCsrfToken();
    if (csrfToken && !['GET', 'HEAD', 'OPTIONS', 'TRACE'].includes(options.method?.toUpperCase())) {
      config.headers['X-CSRFToken'] = csrfToken;
    }

    // Don't set Content-Type for FormData (browser sets it with boundary)
    if (!(options.body instanceof FormData)) {
      config.headers['Content-Type'] = 'application/json';
    }

    try {
      const response = await fetch(url, config);
      
      // Try to parse JSON response
      let data;
      try {
        data = await response.json();
      } catch {
        const statusText = response.statusText || 'Server error';
        data = { error: `HTTP ${response.status}: ${statusText}` };
      }

      if (!response.ok) {
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
    console.log('API Service - login called with:', { email, passwordLength: password?.length });
    // Ensure we have CSRF token before login
    await this.fetchCsrfToken();
    const body = JSON.stringify({ email, password });
    console.log('API Service - request body:', body);
    const response = await this.request('/login', {
      method: 'POST',
      body: body,
    });
    
    // Save token to localStorage if login successful
    if (response && response.success && response.token) {
      localStorage.setItem('authToken', response.token);
      console.log('Token saved to localStorage');
    }
    
    return response;
  }

  async googleLogin(credential) {
    await this.fetchCsrfToken();
    const response = await this.request('/google-login', {
      method: 'POST',
      body: JSON.stringify({ credential }),
    });

    if (response && response.success && response.token) {
      localStorage.setItem('authToken', response.token);
    }

    return response;
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
    // Clear token from localStorage
    localStorage.removeItem('authToken');
    return this.request('/logout', {
      method: 'POST',
    });
  }

  async verifyToken() {
    return this.request('/verify', {
      method: 'GET',
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

  // Admin: get users
  async adminListUsers() {
    return this.request('/admin/users', { method: 'GET' });
  }

  async adminUpdateUser(id, payload) {
    return this.request(`/admin/users/${id}`, { method: 'PUT', body: JSON.stringify(payload) });
  }

  async adminResetPassword(id) {
    return this.request(`/admin/users/${id}/reset-password`, { method: 'POST' });
  }

  // Admin: update voucher
  async adminUpdateVoucher(id, payload) {
    return this.request(`/admin/vouchers/${id}`, { method: 'PUT', body: JSON.stringify(payload) });
  }

  // Admin: get history with filters
  async adminGetHistory(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return this.request(`/admin/history?${qs}`, { method: 'GET' });
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
      const token = localStorage.getItem('authToken');
      const response = await fetch(`${this.baseURL}/generate-pdf`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': token ? `Bearer ${token}` : '',
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

  async requestPasswordReset(email) {
    return this.request('/forgot-password/request', {
      method: 'POST',
      body: JSON.stringify({ email }),
    });
  }

  async resetPasswordWithOtp(email, code, newPassword) {
    return this.request('/forgot-password/reset', {
      method: 'POST',
      body: JSON.stringify({ email, code, new_password: newPassword }),
    });
  }

  async deleteHistory(historyId) {
    return this.request(`/history/${historyId}`, {
      method: 'DELETE',
    });
  }

  async deleteAvatar() {
    return this.request('/delete-avatar/', {
      method: 'DELETE'
    });
  }

  // Vouchers
  async adminCreateVoucher(payload) {
    return this.request('/admin/vouchers', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async adminListVouchers() {
    return this.request('/admin/vouchers', {
      method: 'GET'
    });
  }

  async adminToggleVoucher(id) {
    return this.request(`/admin/vouchers/${id}/toggle`, {
      method: 'PUT'
    });
  }

  async applyVoucher(code) {
    return this.request('/vouchers/apply', {
      method: 'POST',
      body: JSON.stringify({ code }),
    });
  }

  async getPaymentHistory() {
    return this.request('/payments/history', {
      method: 'GET',
    });
  }

  async getPaymentStatus(txnRef) {
    return this.request(`/payments/status/${txnRef}`, {
      method: 'GET',
    });
  }
}

export default new ApiService();
