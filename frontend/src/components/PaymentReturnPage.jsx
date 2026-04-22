import { useEffect, useMemo, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import paymentService from '../services/payment';

export function PaymentReturnPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [verified, setVerified] = useState(false);
  const [message, setMessage] = useState('Dang xac minh giao dich...');
  const [payment, setPayment] = useState(null);

  const txnRef = useMemo(() => searchParams.get('txn_ref') || '', [searchParams]);
  const status = useMemo(() => searchParams.get('status') || '', [searchParams]);
  const code = useMemo(() => searchParams.get('code') || '', [searchParams]);

  useEffect(() => {
    let active = true;

    const run = async () => {
      if (!txnRef) {
        setLoading(false);
        setVerified(false);
        setMessage('Khong tim thay ma giao dich.');
        return;
      }

      const result = await paymentService.verifyPayment({ txn_ref: txnRef });
      if (!active) return;

      if (result.success && result.verified) {
        setVerified(true);
        setPayment(result.payment || null);
        setMessage('Thanh toan thanh cong. Goi dich vu da duoc cap nhat.');
      } else {
        setVerified(false);
        setPayment(result.payment || null);
        setMessage(result.error || 'Thanh toan chua thanh cong. Vui long thu lai.');
      }

      setLoading(false);
    };

    run();

    return () => {
      active = false;
    };
  }, [txnRef]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center px-4">
      <div className="w-full max-w-xl rounded-2xl border border-slate-700/60 bg-slate-900/80 p-8 shadow-2xl shadow-black/30">
        <h1 className="text-2xl font-bold mb-4">Ket qua thanh toan VNPay</h1>

        {loading ? (
          <p className="text-slate-300">Dang xu ly giao dich...</p>
        ) : (
          <>
            <div className={`rounded-lg p-4 mb-4 ${verified ? 'bg-emerald-900/30 border border-emerald-700/50' : 'bg-rose-900/30 border border-rose-700/50'}`}>
              <p className="font-medium">{message}</p>
            </div>

            <div className="space-y-2 text-sm text-slate-300 mb-6">
              <p>Ma giao dich: <span className="text-slate-100">{txnRef || '-'}</span></p>
              <p>Trang thai tu redirect: <span className="text-slate-100">{status || '-'}</span></p>
              <p>Ma phan hoi VNPay: <span className="text-slate-100">{code || '-'}</span></p>
              {payment && (
                <>
                  <p>Trang thai trong he thong: <span className="text-slate-100">{payment.status || '-'}</span></p>
                  <p>Goi dich vu: <span className="text-slate-100">{payment.plan || '-'}</span></p>
                  <p>So tien: <span className="text-slate-100">{Number(payment.amount || 0).toLocaleString('vi-VN')} VND</span></p>
                </>
              )}
            </div>
          </>
        )}

        <div className="flex gap-3">
          <button
            onClick={() => navigate('/pricing')}
            className="px-4 py-2 rounded-lg bg-slate-700 hover:bg-slate-600 transition-colors"
          >
            Quay lai bang gia
          </button>
          <button
            onClick={() => navigate('/')}
            className="px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 transition-colors"
          >
            Ve trang chu
          </button>
        </div>
      </div>
    </div>
  );
}
