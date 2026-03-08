// API service for backend communication
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

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
      } catch (e) {
        data = { error: 'Invalid response from server' };
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
}

export default new ApiService();
