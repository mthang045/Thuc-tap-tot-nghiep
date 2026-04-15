import { useEffect, useState, useCallback } from 'react';
import { Shield, Plus, Edit } from 'lucide-react';
import apiService from '../../services/api';

function Toast({ message, type = 'info', onClose }) {
  if (!message) return null;
  return (
    <div className={`fixed bottom-6 right-6 z-50 p-4 rounded-lg ${type === 'error' ? 'bg-red-600' : 'bg-green-600'} text-white`}> 
      <div className="flex items-center gap-3">
        <div className="flex-1">{message}</div>
        <button onClick={onClose} className="font-bold">✕</button>
      </div>
    </div>
  );
}

function VoucherEditModal({ voucher, onClose, onSave }) {
  const [expiresAt, setExpiresAt] = useState(voucher?.expires_at ? voucher.expires_at.split('T')[0] : '');
  const [maxUses, setMaxUses] = useState(voucher?.max_uses || voucher?.maxUses || 1);
  const [isActive, setIsActive] = useState(Boolean(voucher?.is_active));

  useEffect(() => {
    if (!voucher) return;
    // Defer state updates to avoid synchronous setState in effect
    const timer = setTimeout(() => {
      setExpiresAt(voucher?.expires_at ? voucher.expires_at.split('T')[0] : '');
      setMaxUses(voucher?.max_uses || voucher?.maxUses || 1);
      setIsActive(Boolean(voucher?.is_active));
    }, 0);
    return () => clearTimeout(timer);
  }, [voucher]);

  const handleSave = () => {
    onSave({ expires_at: expiresAt, max_uses: Number(maxUses) || 0, is_active: isActive });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
      <div className="bg-slate-900 p-6 rounded-lg w-full max-w-md">
        <h3 className="text-lg text-slate-100 mb-4">Chỉnh sửa Voucher</h3>
        <div className="space-y-3">
          <div>
            <label className="text-sm text-slate-400">Ngày hết hạn</label>
            <input type="date" value={expiresAt} onChange={e => setExpiresAt(e.target.value)} className="w-full p-2 bg-slate-800 rounded mt-1 text-slate-200" />
          </div>
          <div>
            <label className="text-sm text-slate-400">Số lượt tối đa</label>
            <input type="number" value={maxUses} onChange={e => setMaxUses(e.target.value)} min={1} className="w-full p-2 bg-slate-800 rounded mt-1 text-slate-200" />
          </div>
          <div className="flex items-center gap-3">
            <label className="text-sm text-slate-400">Hoạt động</label>
            <select value={isActive ? 'true' : 'false'} onChange={e => setIsActive(e.target.value === 'true')} className="p-2 bg-slate-800 rounded text-slate-200">
              <option value="true">True</option>
              <option value="false">False</option>
            </select>
          </div>
        </div>
        <div className="flex items-center justify-end gap-2 mt-4">
          <button onClick={onClose} className="px-3 py-2 bg-slate-800 rounded">Hủy</button>
          <button onClick={handleSave} className="px-3 py-2 bg-cyan-600 text-white rounded">Lưu</button>
        </div>
      </div>
    </div>
  );
}

export function VoucherManagement() {
  const [vouchers, setVouchers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [code, setCode] = useState('');
  const [maxUses, setMaxUses] = useState(1);
  const [error, setError] = useState('');

  const apiBase = import.meta.env.VITE_API_BASE || 'http://localhost:5000';

  const [editingVoucher, setEditingVoucher] = useState(null);
  const [toast, setToast] = useState({ message: '', type: 'info' });

  const fetchVouchers = useCallback(async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('authToken');
      const res = await fetch(`${apiBase}/api/admin/vouchers`, {
        headers: { 'Authorization': token ? `Bearer ${token}` : '' }
      });
      if (!res.ok) throw new Error('Không thể lấy danh sách');
      const data = await res.json();
      // backend returns { success: true, data: [...] }
      if (data && data.success && Array.isArray(data.data)) {
        setVouchers(data.data);
      } else if (Array.isArray(data)) {
        setVouchers(data);
      } else if (data && Array.isArray(data.vouchers)) {
        setVouchers(data.vouchers);
      } else {
        setVouchers([]);
      }
    } catch (e) {
      setError(e.message || 'Lỗi');
    } finally {
      setLoading(false);
    }
  }, [apiBase]);

  useEffect(() => { fetchVouchers(); }, [fetchVouchers]);


  const handleCreate = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const token = localStorage.getItem('authToken');
      const res = await fetch(`${apiBase}/api/admin/vouchers`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': token ? `Bearer ${token}` : '' },
        body: JSON.stringify({ code, max_uses: Number(maxUses) || 1, discount_type: 'free_pro', value: 0 })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Lỗi tạo voucher');
      setCode(''); setMaxUses(1);
      fetchVouchers();
    } catch (e) {
      setError(e.message || 'Lỗi');
    }
  };

  return (
    <div className="bg-slate-900/60 border border-slate-700 rounded-xl p-6">
      <div className="flex items-center gap-3 mb-4">
        <Shield className="w-5 h-5 text-red-400" />
        <h3 className="text-lg text-slate-100">Quản lý Voucher</h3>
      </div>

      <form onSubmit={handleCreate} className="flex items-center gap-2 mb-4">
        <input value={code} onChange={(e) => setCode(e.target.value)} placeholder="Mã voucher" className="p-2 rounded bg-slate-800 text-slate-200" />
        <input type="number" value={maxUses} onChange={(e) => setMaxUses(e.target.value)} min={1} className="p-2 w-24 rounded bg-slate-800 text-slate-200" />
        <button className="px-3 py-2 bg-amber-500 text-white rounded flex items-center gap-2"><Plus className="w-4 h-4"/>Tạo</button>
      </form>

      {error && <div className="text-red-400 mb-3">{error}</div>}
      {loading ? (
        <div className="text-slate-400">Đang tải...</div>
      ) : (
        <div className="space-y-2">
          {vouchers.length === 0 && <div className="text-slate-400">Chưa có voucher nào</div>}
          {vouchers.map((v) => (
            <div key={v._id || v.code} className="p-3 bg-slate-800 rounded flex items-center justify-between">
              <div>
                <div className="text-slate-200 font-medium">{v.code}</div>
                <div className="text-slate-400 text-sm">Sử dụng: {v.used_count || 0} / {v.max_uses || v.maxUses || '∞'}</div>
              </div>
              <div className="flex items-center gap-3">
                <div className="text-slate-300 text-sm">{v.is_active ? 'Hoạt động' : 'Không hoạt động'}</div>
                <button onClick={() => setEditingVoucher(v)} className="p-2 text-cyan-400 hover:bg-cyan-900/20 rounded">
                  <Edit className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {editingVoucher && (
        <VoucherEditModal
          voucher={editingVoucher}
          onClose={() => setEditingVoucher(null)}
          onSave={async (payload) => {
            try {
              const res = await apiService.adminUpdateVoucher(editingVoucher._id || editingVoucher.code, payload);
              if (res && res.success) {
                setToast({ message: 'Cập nhật voucher thành công', type: 'success' });
                setEditingVoucher(null);
                fetchVouchers();
              }
            } catch (e) {
              setToast({ message: e.message || 'Lỗi cập nhật', type: 'error' });
            }
          }}
        />
      )}

      <Toast message={toast.message} type={toast.type} onClose={() => setToast({ message: '' })} />
    </div>
  );
}
