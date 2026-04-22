import { useEffect, useMemo, useState } from 'react';
import { Search, Filter, Edit, Trash2, Ban, CheckCircle, Crown, X, RefreshCw } from 'lucide-react';
import apiService from '../../services/api';

export function UserManagement() {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterPlan, setFilterPlan] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');
  const [editingUser, setEditingUser] = useState(null);
  const [users, setUsers] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadUsers();
  }, []);

  const normalizeUser = (user) => ({
    id: user.id || user._id || user.email,
    name: user.name || user.full_name || user.username || user.email,
    email: user.email || '',
    plan: user.plan === 'free' ? 'free' : 'pro',
    status: user.status || (user.is_active === false ? 'suspended' : 'active'),
    joinDate: user.joinDate || user.created_at || user.createdAt || null,
    lastActive: user.lastActive || user.last_active || user.updated_at || null,
    analysisCount: Number(user.analysisCount || user.analysis_count || 0),
  });

  const loadUsers = async () => {
    try {
      setIsLoading(true);
      setError('');
      const response = await apiService.getAdminUsers();
      const fetchedUsers = Array.isArray(response.users) ? response.users.map(normalizeUser) : [];
      setUsers(fetchedUsers);
    } catch (err) {
      console.error('Failed to load admin users:', err);
      setError(err.message || 'Không thể tải danh sách người dùng');
      setUsers([]);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredUsers = useMemo(() => {
    return users.filter(user => {
      const email = (user.email || '').toLowerCase();
      const name = (user.name || '').toLowerCase();
      const matchesSearch = email.includes(searchTerm.toLowerCase()) || name.includes(searchTerm.toLowerCase());
      const matchesPlan = filterPlan === 'all' || user.plan === filterPlan;
      const matchesStatus = filterStatus === 'all' || user.status === filterStatus;
      return matchesSearch && matchesPlan && matchesStatus;
    });
  }, [users, searchTerm, filterPlan, filterStatus]);

  const getPlanBadge = (plan) => {
    switch (plan) {
      case 'free':
        return <span className="inline-flex items-center gap-1.5 px-4 py-1.5 bg-slate-700/50 text-slate-300 text-sm rounded-full border border-slate-600/50">Free</span>;
      case 'pro':
        return <span className="inline-flex items-center gap-1.5 px-4 py-1.5 bg-cyan-600/30 text-cyan-300 text-sm rounded-full border border-cyan-500/50"><Crown className="w-3.5 h-3.5" />Pro</span>;
      default:
        return <span className="inline-flex items-center gap-1.5 px-4 py-1.5 bg-slate-700/50 text-slate-300 text-sm rounded-full border border-slate-600/50">Free</span>;
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'active':
        return <span className="inline-flex items-center px-4 py-1.5 bg-green-600/20 text-green-400 text-sm rounded-full border border-green-500/40">Hoạt động</span>;
      case 'suspended':
        return <span className="inline-flex items-center px-4 py-1.5 bg-red-600/20 text-red-400 text-sm rounded-full border border-red-500/40">Tạm khóa</span>;
      case 'pending':
        return <span className="inline-flex items-center px-4 py-1.5 bg-yellow-600/20 text-yellow-400 text-sm rounded-full border border-yellow-500/40">Chờ xác thực</span>;
      default:
        return <span className="inline-flex items-center px-4 py-1.5 bg-slate-600/20 text-slate-300 text-sm rounded-full border border-slate-500/40">{status || 'unknown'}</span>;
    }
  };

  const updateUser = async (userId, payload) => {
    const response = await apiService.updateAdminUser(userId, payload);
    const updatedUser = response.user ? normalizeUser(response.user) : null;

    if (updatedUser) {
      setUsers(currentUsers => currentUsers.map(user => (user.id === userId ? { ...user, ...updatedUser } : user)));
    } else {
      await loadUsers();
    }

    return response;
  };

  const handleSuspendUser = async (userId) => {
    try {
      const currentUser = users.find(user => user.id === userId);
      if (!currentUser) return;

      await updateUser(userId, { is_active: currentUser.status === 'suspended' });
      setError('');
    } catch (err) {
      console.error('Failed to update user status:', err);
      setError(err.message || 'Không thể cập nhật trạng thái người dùng');
    }
  };

  const handleDeleteUser = async (userId) => {
    if (confirm('Bạn có chắc muốn xóa người dùng này?')) {
      try {
        await apiService.deleteAdminUser(userId);
        setUsers(currentUsers => currentUsers.filter(user => user.id !== userId));
        if (editingUser === userId) {
          setEditingUser(null);
        }
        setError('');
      } catch (err) {
        console.error('Failed to delete user:', err);
        setError(err.message || 'Không thể xóa người dùng');
      }
    }
  };

  const handleActivateUser = async (userId) => {
    try {
      await updateUser(userId, { is_active: true });
      setError('');
    } catch (err) {
      console.error('Failed to activate user:', err);
      setError(err.message || 'Không thể kích hoạt người dùng');
    }
  };

  const handleChangePlan = async (userId, newPlan) => {
    const safePlan = newPlan === 'free' ? 'free' : 'pro';

    try {
      await updateUser(userId, { plan: safePlan });
      setEditingUser(null);
      setError('');
    } catch (err) {
      console.error('Failed to update user plan:', err);
      setError(err.message || 'Không thể cập nhật hạng thành viên');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-pink-500 mb-2">Quản lý người dùng</h1>
          <p className="text-slate-400">Tổng số {users.length} người dùng</p>
        </div>
        <button
          onClick={loadUsers}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-slate-700 bg-slate-900/70 text-slate-200 hover:border-cyan-500/50 hover:text-cyan-300 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          Tải lại
        </button>
      </div>

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
          <div className="text-purple-400 text-xs mb-1">Tạm khóa</div>
          <div className="text-2xl text-purple-300">{users.filter(u => u.status === 'suspended').length}</div>
        </div>
      </div>

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

      {error && (
        <div className="bg-red-900/20 border border-red-700/30 text-red-300 rounded-xl p-4">{error}</div>
      )}

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
              {isLoading ? (
                <tr>
                  <td className="py-8 px-6 text-slate-400" colSpan="6">Đang tải dữ liệu người dùng...</td>
                </tr>
              ) : filteredUsers.length === 0 ? (
                <tr>
                  <td className="py-8 px-6 text-slate-400" colSpan="6">Không có người dùng phù hợp.</td>
                </tr>
              ) : (
                filteredUsers.map((user, index) => (
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
                          </select>
                          <button
                            onClick={() => setEditingUser(null)}
                            className="p-1 text-slate-400 hover:text-slate-200"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        </div>
                      ) : (
                        <div className="flex items-center justify-center">{getPlanBadge(user.plan)}</div>
                      )}
                    </td>
                    <td className="py-5 px-6 text-center">
                      <div className="flex items-center justify-center">{getStatusBadge(user.status)}</div>
                    </td>
                    <td className="py-5 px-6 text-center">
                      <span className="text-slate-300">
                        {user.joinDate ? new Date(user.joinDate).toLocaleDateString('vi-VN') : 'Chưa có'}
                      </span>
                    </td>
                    <td className="py-5 px-6 text-center">
                      <span className="text-cyan-400">{user.analysisCount}</span>
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
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
