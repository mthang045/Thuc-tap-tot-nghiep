"""
Extended templates for Flask application
Cac component HTML bo sung
"""

# Account Settings Page Template
ACCOUNT_SETTINGS_TEMPLATE = """
<div class="container mx-auto px-4 py-8 max-w-6xl">
    <div class="mb-8">
        <h1 class="text-4xl font-bold gradient-text mb-2">Cai dat tai khoan</h1>
        <p class="text-slate-400">Quan ly thong tin ca nhan va tuy chinh tai khoan</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <!-- Sidebar -->
        <div class="lg:col-span-1">
            <div class="bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 rounded-xl p-4 space-y-2">
                <button onclick="showTab('profile')" class="tab-btn w-full flex items-center gap-3 px-4 py-3 rounded-lg">
                    <i class="fas fa-user w-5 h-5"></i>
                    <span>Thong tin ca nhan</span>
                </button>
                <button onclick="showTab('security')" class="tab-btn w-full flex items-center gap-3 px-4 py-3 rounded-lg">
                    <i class="fas fa-shield-alt w-5 h-5"></i>
                    <span>Bao mat</span>
                </button>
                <button onclick="showTab('notifications')" class="tab-btn w-full flex items-center gap-3 px-4 py-3 rounded-lg">
                    <i class="fas fa-bell w-5 h-5"></i>
                    <span>Thong bao</span>
                </button>
                <button onclick="showTab('billing')" class="tab-btn w-full flex items-center gap-3 px-4 py-3 rounded-lg">
                    <i class="fas fa-credit-card w-5 h-5"></i>
                    <span>Thanh toan</span>
                </button>
            </div>
        </div>

        <!-- Content -->
        <div class="lg:col-span-3">
            <div id="profile-tab" class="tab-content bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 rounded-xl p-8">
                <h2 class="text-2xl font-bold mb-6 text-cyan-300">Thong tin ca nhan</h2>
                <form id="profile-form">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <label class="block text-sm font-medium mb-2">Ho va ten</label>
                            <input type="text" name="fullName" class="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 focus:outline-none focus:border-cyan-500">
                        </div>
                        <div>
                            <label class="block text-sm font-medium mb-2">Email</label>
                            <input type="email" name="email" class="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 focus:outline-none focus:border-cyan-500">
                        </div>
                        <div>
                            <label class="block text-sm font-medium mb-2">So dien thoai</label>
                            <input type="tel" name="phone" class="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 focus:outline-none focus:border-cyan-500">
                        </div>
                        <div>
                            <label class="block text-sm font-medium mb-2">Cong ty</label>
                            <input type="text" name="company" class="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 focus:outline-none focus:border-cyan-500">
                        </div>
                    </div>
                    <button type="submit" class="mt-6 bg-gradient-to-r from-cyan-500 to-pink-500 px-6 py-3 rounded-full font-semibold hover:shadow-lg transition">
                        <i class="fas fa-save mr-2"></i>Luu thay doi
                    </button>
                </form>
            </div>

            <div id="security-tab" class="tab-content hidden bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 rounded-xl p-8">
                <h2 class="text-2xl font-bold mb-6 text-cyan-300">Bao mat</h2>
                <form id="password-form">
                    <div class="space-y-4">
                        <div>
                            <label class="block text-sm font-medium mb-2">Mat khau hien tai</label>
                            <input type="password" name="currentPassword" class="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 focus:outline-none focus:border-cyan-500">
                        </div>
                        <div>
                            <label class="block text-sm font-medium mb-2">Mat khau moi</label>
                            <input type="password" name="newPassword" class="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 focus:outline-none focus:border-cyan-500">
                        </div>
                        <div>
                            <label class="block text-sm font-medium mb-2">Xac nhan mat khau moi</label>
                            <input type="password" name="confirmPassword" class="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 focus:outline-none focus:border-cyan-500">
                        </div>
                    </div>
                    <button type="submit" class="mt-6 bg-gradient-to-r from-cyan-500 to-pink-500 px-6 py-3 rounded-full font-semibold hover:shadow-lg transition">
                        <i class="fas fa-lock mr-2"></i>Doi mat khau
                    </button>
                </form>
            </div>
        </div>
    </div>
</div>
"""

# Pricing Plans Template
PRICING_TEMPLATE = """
<div class="container mx-auto px-4 py-8 max-w-7xl">
    <div class="text-center mb-12">
        <h1 class="text-4xl font-bold gradient-text mb-4">Goi cuoc linh hoat</h1>
        <p class="text-slate-400 text-lg">Chon goi phu hop voi nhu cau cua ban</p>
    </div>

    <div class="grid md:grid-cols-3 gap-8">
        <!-- Free Plan -->
        <div class="bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-8">
            <div class="text-center mb-6">
                <i class="fas fa-star text-4xl text-slate-400 mb-4"></i>
                <h3 class="text-2xl font-bold mb-2">Mien phi</h3>
                <p class="text-slate-400">Dung thu cac tinh nang co ban</p>
            </div>
            <div class="text-center mb-6">
                <div class="text-4xl font-bold">0 VND</div>
                <div class="text-slate-400">/thang</div>
            </div>
            <ul class="space-y-3 mb-8">
                <li class="flex items-center gap-2">
                    <i class="fas fa-check text-green-400"></i>
                    <span>5 phan tich/thang</span>
                </li>
                <li class="flex items-center gap-2">
                    <i class="fas fa-check text-green-400"></i>
                    <span>Phan tich co ban</span>
                </li>
                <li class="flex items-center gap-2">
                    <i class="fas fa-check text-green-400"></i>
                    <span>Luu tru 30 ngay</span>
                </li>
            </ul>
            <button class="w-full bg-slate-700 px-6 py-3 rounded-full font-semibold">Goi hien tai</button>
        </div>

        <!-- Pro Plan -->
        <div class="bg-gradient-to-br from-cyan-900/40 to-blue-900/40 backdrop-blur-xl border-2 border-cyan-500/50 rounded-2xl p-8 relative">
            <div class="absolute -top-4 left-1/2 transform -translate-x-1/2">
                <span class="bg-gradient-to-r from-cyan-500 to-blue-500 px-4 py-1 rounded-full text-sm font-semibold">Pho bien</span>
            </div>
            <div class="text-center mb-6">
                <i class="fas fa-bolt text-4xl text-cyan-400 mb-4"></i>
                <h3 class="text-2xl font-bold mb-2">Professional</h3>
                <p class="text-slate-400">Cho ca nhan va doanh nghiep nho</p>
            </div>
            <div class="text-center mb-6">
                <div class="text-4xl font-bold">299.000 VND</div>
                <div class="text-slate-400">/thang</div>
            </div>
            <ul class="space-y-3 mb-8">
                <li class="flex items-center gap-2">
                    <i class="fas fa-check text-cyan-400"></i>
                    <span>50 phan tich/thang</span>
                </li>
                <li class="flex items-center gap-2">
                    <i class="fas fa-check text-cyan-400"></i>
                    <span>Phan tich nang cao voi AI</span>
                </li>
                <li class="flex items-center gap-2">
                    <i class="fas fa-check text-cyan-400"></i>
                    <span>Luu tru khong gioi han</span>
                </li>
                <li class="flex items-center gap-2">
                    <i class="fas fa-check text-cyan-400"></i>
                    <span>Email support 24/7</span>
                </li>
            </ul>
            <button onclick="upgradePlan('pro')" class="w-full bg-gradient-to-r from-cyan-500 to-blue-500 px-6 py-3 rounded-full font-semibold hover:shadow-lg transition">
                Nang cap len Pro
            </button>
        </div>

        <!-- Enterprise Plan -->
        <div class="bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-8">
            <div class="text-center mb-6">
                <i class="fas fa-building text-4xl text-purple-400 mb-4"></i>
                <h3 class="text-2xl font-bold mb-2">Enterprise</h3>
                <p class="text-slate-400">Cho doanh nghiep lon</p>
            </div>
            <div class="text-center mb-6">
                <div class="text-4xl font-bold">999.000 VND</div>
                <div class="text-slate-400">/thang</div>
            </div>
            <ul class="space-y-3 mb-8">
                <li class="flex items-center gap-2">
                    <i class="fas fa-check text-purple-400"></i>
                    <span>Khong gioi han phan tich</span>
                </li>
                <li class="flex items-center gap-2">
                    <i class="fas fa-check text-purple-400"></i>
                    <span>AI phan tich chuyen sau</span>
                </li>
                <li class="flex items-center gap-2">
                    <i class="fas fa-check text-purple-400"></i>
                    <span>API access day du</span>
                </li>
                <li class="flex items-center gap-2">
                    <i class="fas fa-check text-purple-400"></i>
                    <span>Dedicated support</span>
                </li>
            </ul>
            <button onclick="upgradePlan('enterprise')" class="w-full bg-gradient-to-r from-purple-500 to-pink-500 px-6 py-3 rounded-full font-semibold hover:shadow-lg transition">
                Lien he tu van
            </button>
        </div>
    </div>
</div>
"""

# Admin Dashboard Template
ADMIN_TEMPLATE = """
<div class="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-950 to-purple-950">
    <header class="border-b border-slate-700/50 backdrop-blur-xl bg-slate-900/50">
        <div class="container mx-auto px-4 py-4">
            <div class="flex items-center justify-between">
                <div class="flex items-center gap-4">
                    <i class="fas fa-shield-alt text-3xl text-red-400"></i>
                    <div>
                        <h1 class="text-xl font-bold gradient-text">Admin Dashboard</h1>
                        <p class="text-slate-500 text-xs">Quan tri he thong GenZ Legal AI</p>
                    </div>
                </div>
                <div class="flex items-center gap-3">
                    <div class="px-4 py-2 bg-red-500/20 border border-red-500/30 rounded-lg">
                        <i class="fas fa-shield-alt text-red-400 mr-2"></i>
                        <span class="text-red-300 text-sm">Admin Mode</span>
                    </div>
                    <button onclick="exitAdmin()" class="px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg transition">
                        Thoat Admin
                    </button>
                </div>
            </div>
        </div>
    </header>

    <div class="container mx-auto px-4 py-8">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div class="bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 rounded-xl p-6">
                <div class="flex items-center justify-between mb-4">
                    <i class="fas fa-users text-3xl text-cyan-400"></i>
                    <span class="text-2xl font-bold" id="total-users">0</span>
                </div>
                <p class="text-slate-400">Tong nguoi dung</p>
            </div>
            <div class="bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 rounded-xl p-6">
                <div class="flex items-center justify-between mb-4">
                    <i class="fas fa-file-alt text-3xl text-pink-400"></i>
                    <span class="text-2xl font-bold" id="total-analyses">0</span>
                </div>
                <p class="text-slate-400">Tong phan tich</p>
            </div>
            <div class="bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 rounded-xl p-6">
                <div class="flex items-center justify-between mb-4">
                    <i class="fas fa-user-check text-3xl text-green-400"></i>
                    <span class="text-2xl font-bold" id="active-users">0</span>
                </div>
                <p class="text-slate-400">Nguoi dung hoat dong</p>
            </div>
            <div class="bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 rounded-xl p-6">
                <div class="flex items-center justify-between mb-4">
                    <i class="fas fa-chart-line text-3xl text-purple-400"></i>
                    <span class="text-2xl font-bold">99.2%</span>
                </div>
                <p class="text-slate-400">Uptime</p>
            </div>
        </div>
    </div>
</div>
"""
