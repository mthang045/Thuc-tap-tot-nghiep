import { useState } from 'react';
import { Search, Filter, Edit, Trash2, Ban, CheckCircle, Crown, X } from 'lucide-react';

export function UserManagement() {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterPlan, setFilterPlan] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');
  const [selectedUsers, setSelectedUsers] = useState([]);
  const [editingUser, setEditingUser] = useState(null);

  // Mock data
  const [users, setUsers] = useState([
    {
      id: '1',
      name: 'Nguyễn Văn A',
      email: 'user@example.com',
      plan: 'pro',
      status: 'active',
      joinDate: '2024-01-15',
      lastActive: '2024-12-07',
      analysisCount: 45
    },
    {
      id: '2',
      name: 'Trần Thị B',
      email: 'demo@company.com',
      plan: 'enterprise',
      status: 'active',
      joinDate: '2024-02-20',
      lastActive: '2024-12-08',
      analysisCount: 120
    },
    {
      id: '3',
      name: 'Lê Văn C',
      email: 'test@email.com',
      plan: 'free',
      status: 'pending',
      joinDate: '2024-12-01',
      lastActive: '2024-12-05',
      analysisCount: 3
    },
    {
      id: '4',
      name: 'Phạm Thị D',
      email: 'user2@email.com',
      plan: 'pro',
      status: 'suspended',
      joinDate: '2024-03-10',
      lastActive: '2024-11-30',
      analysisCount: 67
    }
  ]);

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesPlan = filterPlan === 'all' || user.plan === filterPlan;
    const matchesStatus = filterStatus === 'all' || user.status === filterStatus;
    return matchesSearch && matchesPlan && matchesStatus;
  });

  const getPlanBadge = (plan) => {
    switch (plan) {
      case 'free':
        return (
          <span className="inline-flex items-center gap-1.5 px-4 py-1.5 bg-slate-700/50 text-slate-300 text-sm rounded-full border border-slate-600/50">
            Free
          </span>
        );
      case 'pro':
        return (
          <span className="inline-flex items-center gap-1.5 px-4 py-1.5 bg-cyan-600/30 text-cyan-300 text-sm rounded-full border border-cyan-500/50">
            <Crown className="w-3.5 h-3.5" />
            Pro
          </span>
        );
      case 'enterprise':
        return (
          <span className="inline-flex items-center gap-1.5 px-4 py-1.5 bg-purple-600/30 text-purple-300 text-sm rounded-full border border-purple-500/50">
            <Crown className="w-3.5 h-3.5" />
            Enterprise
          </span>
        );
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'active':
        return (
          <span className="inline-flex items-center px-4 py-1.5 bg-green-600/20 text-green-400 text-sm rounded-full border border-green-500/40">
            Hoạt động
          </span>
        );
      case 'suspended':
        return (
          <span className="inline-flex items-center px-4 py-1.5 bg-red-600/20 text-red-400 text-sm rounded-full border border-red-500/40">
            Tạm khóa
          </span>
        );
      case 'pending':
        return (
          <span className="inline-flex items-center px-4 py-1.5 bg-yellow-600/20 text-yellow-400 text-sm rounded-full border border-yellow-500/40">
            Chờ xác thực
          </span>
        );
    }
  };

  const handleSuspendUser = (userId) => {
    setUsers(users.map(user => 
      user.id === userId 
        ? { ...user, status: user.status === 'suspended' ? 'active' : 'suspended' }
        : user
    ));
  };

  const handleDeleteUser = (userId) => {
    if (confirm('Bạn có chắc muốn xóa người dùng này?')) {
      setUsers(users.filter(user => user.id !== userId));
    }
  };

  const handleActivateUser = (userId) => {
    setUsers(users.map(user => 
      user.id === userId 
        ? { ...user, status: 'active' }
        : user
    ));
  };

  const handleChangePlan = (userId, newPlan) => {
    setUsers(users.map(user => 
      user.id === userId 
        ? { ...user, plan: newPlan }
        : user
    ));
    setEditingUser(null);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-pink-500 mb-2">
            Quản lý người dùng
          </h1>
          <p className="text-slate-400">Tổng số {users.length} người dùng</p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 rounded-xl p-5">
          <div className="text-slate-400 text-xs mb-1">Free</div>
          <div className="text-2xl text-slate-300">{users.filter(u => u.plan === 'free').length}</div>
        </div>
        <div className="bg-cyan-900/20 backdrop-blur-xl border border-cyan-700/30 rounded-xl p-5">
          <div className="text-cyan-400 text-xs mb-1">Pro</div>
          <div className="text-2xl text-cyan-300">{users.filter(u => u.plan === 'pro').length}</div>
        </div>
        <div className="bg-purple-900/20 backdrop-blur-xl border border-purple-700/30 rounded-xl p-5">
          <div className="text-purple-400 text-xs mb-1">Enterprise</div>
          <div className="text-2xl text-purple-300">{users.filter(u => u.plan === 'enterprise').length}</div>
        </div>
      </div>

      {/* Search and Filter */}
      <div className="bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 rounded-xl p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="relative">
            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500">
              <Search className="w-5 h-5" />
            </div>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Tìm kiếm..."
              className="w-full bg-slate-800/50 border border-slate-700 rounded-xl pl-12 pr-4 py-3 text-slate-200 placeholder-slate-500 focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/20 transition-all"
            />
          </div>
          <div className="relative">
            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500">
              <Filter className="w-5 h-5" />
            </div>
            <select
              value={filterPlan}
              onChange={(e) => setFilterPlan(e.target.value)}
              className="w-full bg-slate-800/50 border border-slate-700 rounded-xl pl-12 pr-4 py-3 text-slate-200 focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/20 transition-all appearance-none cursor-pointer"
            >
              <option value="all">Tất cả gói</option>
              <option value="free">Free</option>
              <option value="pro">Pro</option>
              <option value="enterprise">Enterprise</option>
            </select>
          </div>
          <div className="relative">
            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500">
              <Filter className="w-5 h-5" />
            </div>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="w-full bg-slate-800/50 border border-slate-700 rounded-xl pl-12 pr-4 py-3 text-slate-200 focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/20 transition-all appearance-none cursor-pointer"
            >
              <option value="all">Tất cả trạng thái</option>
              <option value="active">Hoạt động</option>
              <option value="suspended">Tạm khóa</option>
              <option value="pending">Chờ xác thực</option>
            </select>
          </div>
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-700/50 bg-slate-800/80">
                <th className="text-left text-slate-300 py-4 px-6 text-sm">Người dùng</th>
                <th className="text-center text-slate-300 py-4 px-6 text-sm">Gói</th>
                <th className="text-center text-slate-300 py-4 px-6 text-sm">Trạng thái</th>
                <th className="text-center text-slate-300 py-4 px-6 text-sm">Ngày tham gia</th>
                <th className="text-center text-slate-300 py-4 px-6 text-sm">Phân tích</th>
                <th className="text-center text-slate-300 py-4 px-6 text-sm">Thao tác</th>
              </tr>
            </thead>
            <tbody>
              {filteredUsers.map((user, index) => (
                <tr
                  key={user.id}
                  className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-all duration-200 animate-fade-in"
                  style={{ animationDelay: `${index * 50}ms` }}
                >
                  <td className="py-5 px-6">
                    <div>
                      <div className="text-slate-200 mb-1">{user.name}</div>
                      <div className="text-slate-500 text-sm">{user.email}</div>
                    </div>
                  </td>
                  <td className="py-5 px-6 text-center">
                    {editingUser === user.id ? (
                      <div className="flex items-center justify-center gap-2">
                        <select
                          value={user.plan}
                          onChange={(e) => handleChangePlan(user.id, e.target.value)}
                          className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-slate-200 text-sm"
                        >
                          <option value="free">Free</option>
                          <option value="pro">Pro</option>
                          <option value="enterprise">Enterprise</option>
                        </select>
                        <button
                          onClick={() => setEditingUser(null)}
                          className="p-1 text-slate-400 hover:text-slate-200"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    ) : (
                      <div className="flex items-center justify-center">
                        {getPlanBadge(user.plan)}
                      </div>
                    )}
                  </td>
                  <td className="py-5 px-6 text-center">
                    <div className="flex items-center justify-center">
                      {getStatusBadge(user.status)}
                    </div>
                  </td>
                  <td className="py-5 px-6 text-center">
                    <span className="text-slate-300">{new Date(user.joinDate).toLocaleDateString('vi-VN')}</span>
                  </td>
                  <td className="py-5 px-6 text-center">
                    <span className="text-cyan-400">{user.totalAnalyses}</span>
                  </td>
                  <td className="py-5 px-6">
                    <div className="flex items-center justify-center gap-2">
                      <button
                        onClick={() => setEditingUser(user.id)}
                        className="p-2 text-cyan-400 hover:bg-cyan-900/30 rounded-lg transition-all"
                        title="Chỉnh sửa gói"
                      >
                        <Edit className="w-4 h-4" />
                      </button>
                      
                      {user.status === 'pending' ? (
                        <button
                          onClick={() => handleActivateUser(user.id)}
                          className="p-2 text-green-400 hover:bg-green-900/30 rounded-lg transition-all"
                          title="Kích hoạt"
                        >
                          <CheckCircle className="w-4 h-4" />
                        </button>
                      ) : user.status === 'active' ? (
                        <button
                          onClick={() => handleSuspendUser(user.id)}
                          className="p-2 text-yellow-400 hover:bg-yellow-900/30 rounded-lg transition-all"
                          title="Tạm khóa"
                        >
                          <Ban className="w-4 h-4" />
                        </button>
                      ) : (
                        <button
                          onClick={() => handleActivateUser(user.id)}
                          className="p-2 text-green-400 hover:bg-green-900/30 rounded-lg transition-all"
                          title="Kích hoạt lại"
                        >
                          <CheckCircle className="w-4 h-4" />
                        </button>
                      )}
                      
                      <button
                        onClick={() => handleDeleteUser(user.id)}
                        className="p-2 text-red-400 hover:bg-red-900/30 rounded-lg transition-all"
                        title="Xóa"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredUsers.length === 0 && (
          <div className="text-center py-12">
            <p className="text-slate-500">Không tìm thấy người dùng nào</p>
          </div>
        )}
      </div>

      {/* Bulk Actions */}
      {selectedUsers.length > 0 && (
        <div className="fixed bottom-8 left-1/2 -translate-x-1/2 bg-slate-900/95 backdrop-blur-xl border border-slate-700 rounded-xl shadow-2xl p-4 animate-fade-in">
          <div className="flex items-center gap-4">
            <span className="text-slate-300">
              Đã chọn {selectedUsers.length} người dùng
            </span>
            <div className="flex gap-2">
              <button className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg transition-colors text-sm">
                Đổi gói hàng loạt
              </button>
              <button className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded-lg transition-colors text-sm">
                Xóa hàng loạt
              </button>
              <button
                onClick={() => setSelectedUsers([])}
                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg transition-colors text-sm"
              >
                Hủy
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
