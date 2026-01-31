// Global state
let currentUser = null;
let isAdmin = false;
let selectedFile = null;
let currentResults = null;

// Initialize user from sessionStorage
function initUser() {
    const email = sessionStorage.getItem('userEmail');
    const admin = sessionStorage.getItem('isAdmin') === 'true';
    if (email) {
        currentUser = email;
        isAdmin = admin;
        updateUIAfterLogin();
    }
}

// Page navigation
function showPage(pageName) {
    // For SPA-style navigation
    if (document.querySelectorAll('.page').length > 0) {
        document.querySelectorAll('.page').forEach(page => page.classList.add('hidden'));
        const targetPage = document.getElementById(`${pageName}-page`);
        if (targetPage) {
            targetPage.classList.remove('hidden');
        }
        
        // Update active nav button
        document.querySelectorAll('[id^="nav-"]').forEach(btn => {
            btn.classList.remove('bg-cyan-600/20', 'text-cyan-300', 'border', 'border-cyan-500/30');
            btn.classList.add('text-slate-400', 'hover:text-slate-200', 'hover:bg-slate-800');
        });
        
        const activeBtn = document.getElementById(`nav-${pageName}`);
        if (activeBtn) {
            activeBtn.classList.remove('text-slate-400', 'hover:text-slate-200', 'hover:bg-slate-800');
            activeBtn.classList.add('bg-cyan-600/20', 'text-cyan-300', 'border', 'border-cyan-500/30');
        }
        
        if (pageName === 'history' && currentUser) {
            loadHistory();
        }
    }
}

// Login/Logout
function showLoginModal(view = 'login') {
    const modal = document.getElementById('login-modal');
    if (modal) {
        modal.classList.remove('hidden');
        modal.classList.add('flex');
        
        // Switch to login or register view
        const loginForm = document.getElementById('login-form');
        const registerForm = document.getElementById('register-form');
        if (view === 'login') {
            loginForm?.classList.remove('hidden');
            registerForm?.classList.add('hidden');
        } else {
            loginForm?.classList.add('hidden');
            registerForm?.classList.remove('hidden');
        }
    }
}

function hideLoginModal() {
    const modal = document.getElementById('login-modal');
    if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
    }
}

// Toggle user dropdown menu
function toggleUserMenu() {
    const dropdown = document.getElementById('user-dropdown');
    if (dropdown) {
        dropdown.classList.toggle('hidden');
    }
}

// Close dropdown when clicking outside
document.addEventListener('click', (e) => {
    const userMenu = document.getElementById('user-menu');
    const dropdown = document.getElementById('user-dropdown');
    if (userMenu && dropdown && !userMenu.contains(e.target)) {
        dropdown.classList.add('hidden');
    }
});

async function handleLogin(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = {
        email: formData.get('email'),
        password: formData.get('password')
    };
    
    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            currentUser = result.email;
            isAdmin = result.is_admin;
            sessionStorage.setItem('userEmail', result.email);
            sessionStorage.setItem('isAdmin', result.is_admin);
            updateUIAfterLogin();
            hideLoginModal();
        } else {
            alert(result.message);
        }
    } catch (error) {
        alert('Lỗi kết nối đến server');
    }
}

async function logout() {
    try {
        await fetch('/api/logout', {method: 'POST'});
        currentUser = null;
        isAdmin = false;
        sessionStorage.removeItem('userEmail');
        sessionStorage.removeItem('isAdmin');
        updateUIAfterLogout();
        showPage('home');
    } catch (error) {
        alert('Lỗi khi đăng xuất');
    }
}

function updateUIAfterLogin() {
    // Hide auth buttons, show user menu
    const authButtons = document.getElementById('auth-buttons');
    const userMenu = document.getElementById('user-menu');
    
    if (authButtons) authButtons.classList.add('hidden');
    if (userMenu) {
        userMenu.classList.remove('hidden');
        const userEmailElements = document.querySelectorAll('#user-email, #dropdown-email');
        userEmailElements.forEach(el => el.textContent = currentUser);
    }
    
    // Show authenticated nav items
    const navHistory = document.getElementById('nav-history');
    const navAdmin = document.getElementById('nav-admin');
    
    if (navHistory) navHistory.classList.remove('hidden');
    if (isAdmin && navAdmin) navAdmin.classList.remove('hidden');
}

function updateUIAfterLogout() {
    const authButtons = document.getElementById('auth-buttons');
    const userMenu = document.getElementById('user-menu');
    const navHistory = document.getElementById('nav-history');
    const navAdmin = document.getElementById('nav-admin');
    
    if (authButtons) authButtons.classList.remove('hidden');
    if (userMenu) userMenu.classList.add('hidden');
    if (navHistory) navHistory.classList.add('hidden');
    if (navAdmin) navAdmin.classList.add('hidden');
}

// File upload
function handleDragOver(event) {
    event.preventDefault();
    event.currentTarget.classList.add('border-cyan-500');
}

function handleDragLeave(event) {
    event.currentTarget.classList.remove('border-cyan-500');
}

function handleDrop(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('border-cyan-500');
    
    const files = event.dataTransfer.files;
    if (files.length > 0) {
        processFile(files[0]);
    }
}

function handleFileSelect(event) {
    const files = event.target.files;
    if (files && files.length > 0) {
        processFile(files[0]);
    }
}

function processFile(file) {
    const validTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
    
    if (!validTypes.includes(file.type) && !file.name.match(/\.(pdf|doc|docx|txt)$/i)) {
        alert('Vui lòng chọn file PDF, DOC, DOCX hoặc TXT');
        return;
    }
    
    selectedFile = file;
    document.getElementById('file-name').textContent = file.name;
    document.getElementById('file-size').textContent = formatFileSize(file.size);
    document.getElementById('upload-area').classList.add('hidden');
    document.getElementById('file-info').classList.remove('hidden');
}

function clearFile() {
    selectedFile = null;
    document.getElementById('file-input').value = '';
    document.getElementById('upload-area').classList.remove('hidden');
    document.getElementById('file-info').classList.add('hidden');
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Contract analysis
async function analyzeContract() {
    if (!currentUser) {
        alert('Vui lòng đăng nhập để sử dụng tính năng này');
        showLoginModal();
        return;
    }
    
    if (!selectedFile) {
        alert('Vui lòng chọn file hợp đồng');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    document.getElementById('file-info').classList.add('hidden');
    document.getElementById('analyzing-status').classList.remove('hidden');
    
    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            currentResults = result.data;
            displayResults(result.data);
            showPage('results');
        } else {
            alert(result.message);
        }
    } catch (error) {
        alert('Lỗi khi phân tích hợp đồng: ' + error.message);
    } finally {
        document.getElementById('analyzing-status').classList.add('hidden');
        document.getElementById('file-info').classList.remove('hidden');
    }
}

function displayResults(data) {
    const resultsContent = document.getElementById('results-content');
    
    resultsContent.innerHTML = `
        <div class="bg-slate-900/70 backdrop-blur-xl rounded-3xl shadow-2xl border border-slate-700/50 p-8 mb-6">
            <div class="flex items-center gap-4 mb-6">
                <div class="bg-gradient-to-r from-cyan-500 to-pink-500 p-3 rounded-full">
                    <i class="fas fa-file-contract text-3xl text-white"></i>
                </div>
                <div>
                    <h2 class="text-3xl font-bold gradient-text">${data.contractName}</h2>
                    <p class="text-slate-400">Ngày phân tích: ${data.uploadDate}</p>
                </div>
            </div>
        </div>
        
        <div class="bg-slate-800/50 backdrop-blur-lg rounded-2xl p-8 border border-slate-700">
            <h3 class="text-2xl font-bold mb-4 text-cyan-300">
                <i class="fas fa-chart-line mr-2"></i>Kết quả phân tích
            </h3>
            <div class="prose prose-invert max-w-none">
                ${formatMarkdown(data.finalReport)}
            </div>
        </div>
        
        ${data.extractedClauses && data.extractedClauses.length > 0 ? `
        <div class="bg-slate-800/50 backdrop-blur-lg rounded-2xl p-8 border border-slate-700 mt-6">
            <h3 class="text-2xl font-bold mb-4 text-pink-300">
                <i class="fas fa-list mr-2"></i>Điều khoản đã trích xuất
            </h3>
            <div class="space-y-3">
                ${data.extractedClauses.map((clause, i) => `
                    <div class="bg-slate-700/30 p-4 rounded-lg">
                        <p class="text-sm text-slate-400 mb-1">Điều khoản ${i + 1}</p>
                        <p class="text-slate-200">${clause}</p>
                    </div>
                `).join('')}
            </div>
        </div>
        ` : ''}
    `;
}

function formatMarkdown(text) {
    // Simple markdown to HTML conversion
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/^### (.*$)/gim, '<h3 class="text-xl font-bold mt-4 mb-2 text-cyan-300">$1</h3>')
        .replace(/^## (.*$)/gim, '<h2 class="text-2xl font-bold mt-6 mb-3 text-pink-300">$1</h2>')
        .replace(/^# (.*$)/gim, '<h1 class="text-3xl font-bold mt-8 mb-4 gradient-text">$1</h1>')
        .replace(/^- (.*$)/gim, '<li class="ml-4 text-slate-300">$1</li>')
        .replace(/\n\n/g, '</p><p class="mb-4">')
        .replace(/^\d+\. (.*$)/gim, '<li class="ml-4 text-slate-300">$1</li>');
}

// History
async function loadHistory() {
    try {
        const response = await fetch('/api/history');
        const result = await response.json();
        
        if (result.success) {
            displayHistory(result.history);
        }
    } catch (error) {
        alert('Lỗi khi tải lịch sử');
    }
}

function displayHistory(history) {
    const historyContent = document.getElementById('history-content');
    
    if (history.length === 0) {
        historyContent.innerHTML = `
            <div class="text-center py-12 text-slate-400">
                <i class="fas fa-inbox text-6xl mb-4"></i>
                <p>Chưa có lịch sử phân tích</p>
            </div>
        `;
        return;
    }
    
    historyContent.innerHTML = `
        <div class="grid gap-4">
            ${history.map(item => `
                <div class="bg-slate-800/50 backdrop-blur-lg rounded-xl p-6 border border-slate-700 hover:border-cyan-500/50 transition cursor-pointer"
                     onclick='viewHistoryItem(${JSON.stringify(item.data)})'>
                    <div class="flex items-center justify-between">
                        <div class="flex items-center gap-4">
                            <div class="bg-cyan-500/20 p-3 rounded-lg">
                                <i class="fas fa-file-alt text-2xl text-cyan-400"></i>
                            </div>
                            <div>
                                <h3 class="font-bold text-lg">${item.data.contractName}</h3>
                                <p class="text-sm text-slate-400">${item.data.uploadDate}</p>
                            </div>
                        </div>
                        <i class="fas fa-chevron-right text-slate-400"></i>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function viewHistoryItem(data) {
    currentResults = data;
    showPage('results');
    displayResults();
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initUser();
});
