import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { CheckCircle2, XCircle } from 'lucide-react';
import api from '../services/api';

export function PaymentReturn() {
  const [searchParams] = useSearchParams();
  const [payment, setPayment] = useState(null);
  const [checking, setChecking] = useState(false);

  const status = searchParams.get('status');
  const plan = searchParams.get('plan') || payment?.plan || 'pro';
  const txnRef = searchParams.get('txn_ref') || '';
  const code = searchParams.get('code') || '';

  useEffect(() => {
    const fetchStatus = async () => {
      if (!txnRef) return;
      try {
        setChecking(true);
        const response = await api.getPaymentStatus(txnRef);
        if (response?.success && response.payment) {
          setPayment(response.payment);
        }
      } catch {
        // Keep UI fallback from URL params if status endpoint fails.
      } finally {
        setChecking(false);
      }
    };

    fetchStatus();
  }, [txnRef]);

  const finalStatus = payment?.status || status;
  const isSuccess = finalStatus === 'success';

  return (
    <div className="container mx-auto px-4 py-12 max-w-3xl">
      <div className="bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-8 text-center">
        <div className="flex justify-center mb-4">
          {isSuccess ? (
            <CheckCircle2 className="w-16 h-16 text-green-400" />
          ) : (
            <XCircle className="w-16 h-16 text-red-400" />
          )}
        </div>

        <h1 className="text-2xl text-slate-100 mb-3">
          {isSuccess ? 'Thanh toán thành công' : 'Thanh toán thất bại'}
        </h1>

        <p className="text-slate-400 mb-6">
          {isSuccess
            ? `Gói ${plan.toUpperCase()} của bạn đã được cập nhật.`
            : 'Giao dịch chưa hoàn tất. Bạn có thể thử lại hoặc chọn phương thức khác.'}
        </p>

        <div className="bg-slate-800/60 rounded-xl p-4 text-left text-sm text-slate-300 mb-6">
          <div>Mã giao dịch: {txnRef || 'N/A'}</div>
          <div>Mã phản hồi: {code || 'N/A'}</div>
          {checking && <div className="text-slate-400 mt-1">Đang xác minh trạng thái giao dịch...</div>}
        </div>

        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Link
            to="/pricing"
            className="px-5 py-2.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg transition-colors"
          >
            Quay lại bảng giá
          </Link>
          <Link
            to="/"
            className="px-5 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg transition-colors"
          >
            Về trang chủ
          </Link>
        </div>
      </div>
    </div>
  );
}
