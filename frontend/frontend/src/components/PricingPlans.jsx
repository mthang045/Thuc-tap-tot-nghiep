import { useState } from 'react';
import { Check, X, Zap, Crown, Building2, Sparkles } from 'lucide-react';
import paymentService from '../services/payment';

export function PricingPlans({ userEmail, onUpgrade }) {
  const apiBase = import.meta.env.VITE_API_BASE || 'http://localhost:5000';
  const [billingCycle, setBillingCycle] = useState('monthly');
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [voucherCode, setVoucherCode] = useState('');
  const [voucherLoading, setVoucherLoading] = useState(false);
  const [voucherError, setVoucherError] = useState('');
  const [voucherSuccess, setVoucherSuccess] = useState('');
  const [showTemplateModal, setShowTemplateModal] = useState(false);
  const [templateModalFor, setTemplateModalFor] = useState('');
  const templates = [
    { id: 't1', title: 'Mẫu hợp đồng mua bán', desc: 'Bao gồm điều khoản thanh toán, giao nhận, bảo hành.' },
    { id: 't2', title: 'Mẫu hợp đồng lao động', desc: 'Quy định công việc, lương thưởng, chấm dứt hợp đồng.' },
    { id: 't3', title: 'Mẫu NDA (Bảo mật)', desc: 'Bảo vệ thông tin nhạy cảm giữa hai bên.' }
  ];

  const renderComparisonCell = (value) => {
    const text = String(value || '').trim();
    const excludedKeywords = ['Không', '✗', '✖', 'No', 'N/A'];
    const isExcluded = excludedKeywords.includes(text);

    return (
      <div className="flex items-center justify-center gap-3">
        {isExcluded ? (
          <div className="bg-slate-700/30 p-1 rounded-full flex items-center justify-center">
            <X className="w-4 h-4 text-slate-500" />
          </div>
        ) : (
          <div className="bg-green-500/20 p-1 rounded-full flex items-center justify-center">
            <Check className="w-4 h-4 text-green-400" />
          </div>
        )}
        <span className={isExcluded ? 'text-slate-600' : 'text-slate-300'}>{text}</span>
      </div>
    );
  };

  const openTemplateModal = (planId) => {
    setTemplateModalFor(planId);
    setShowTemplateModal(true);
  };

  const applyVoucher = async () => {
    setVoucherError('');
    setVoucherSuccess('');
    if (!voucherCode) {
      setVoucherError('Vui lòng nhập mã voucher');
      return;
    }
    setVoucherLoading(true);
    try {
      const apiUrl = `${apiBase}/api/vouchers/apply`;
      const token = localStorage.getItem('authToken');
      const resp = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': token ? `Bearer ${token}` : ''
        },
        credentials: 'include',
        body: JSON.stringify({ code: voucherCode })
      });

      const data = await resp.json().catch(() => ({}));
      if (!resp.ok) {
        setVoucherError(data.error || 'Mã không hợp lệ');
        setVoucherLoading(false);
        return;
      }

      // Success
      setVoucherSuccess(data.message || 'Áp dụng mã thành công');
      // If server provided a new token (e.g., free_pro), save it and upgrade UI
      if (data.token) {
        localStorage.setItem('authToken', data.token);
        // Immediately update UI
        try { onUpgrade && onUpgrade('pro'); } catch (e) {}
        // show confetti celebration
        try { createConfetti(); } catch (e) {}
      }

      // If discount value provided, you can use it to apply on checkout
      setVoucherLoading(false);
      // show minimal confetti / celebration
      setTimeout(() => setVoucherSuccess(''), 5000);
    } catch (e) {
      setVoucherError(e.message || 'Lỗi server');
      setVoucherLoading(false);
    }
  };

  // Lightweight confetti effect (DOM-based, no extra deps)
  const createConfetti = (count = 30) => {
    if (typeof document === 'undefined') return;
    // inject styles once
    if (!document.getElementById('confetti-styles')) {
      const style = document.createElement('style');
      style.id = 'confetti-styles';
      style.innerHTML = `
      @keyframes confetti-fall { 0% { transform: translateY(-10vh) rotate(0deg); opacity:1 } 100% { transform: translateY(110vh) rotate(720deg); opacity:0 } }
      .confetti-piece { position:fixed; top:0; left:0; width:10px; height:14px; pointer-events:none; transform-origin:center; }
      `;
      document.head.appendChild(style);
    }

    const container = document.createElement('div');
    container.className = 'confetti-container';
    container.style.position = 'fixed';
    container.style.top = '0';
    container.style.left = '0';
    container.style.width = '100%';
    container.style.height = '100%';
    container.style.pointerEvents = 'none';
    container.style.overflow = 'visible';
    container.style.zIndex = 9999;
    document.body.appendChild(container);

    const colors = ['#06b6d4', '#7c3aed', '#ec4899', '#f59e0b', '#10b981'];
    for (let i = 0; i < count; i++) {
      const el = document.createElement('div');
      el.className = 'confetti-piece';
      const w = 8 + Math.random() * 12;
      el.style.width = `${w}px`;
      el.style.height = `${w * 1.4}px`;
      el.style.background = colors[Math.floor(Math.random() * colors.length)];
      el.style.left = Math.random() * 100 + '%';
      el.style.transform = `translateY(-10vh) rotate(${Math.random() * 360}deg)`;
      const delay = Math.random() * 0.6;
      const duration = 2 + Math.random() * 2.5;
      el.style.animation = `confetti-fall ${duration}s ${delay}s linear forwards`;
      container.appendChild(el);
    }

    // remove after animations
    setTimeout(() => {
      try { container.remove(); } catch (e) {}
    }, 7000);
  };

  const downloadTemplate = async (templateId) => {
    try {
      const resp = await fetch(`${apiBase}/api/templates/${templateId}/download`, {
        method: 'GET',
        credentials: 'include'
      });

      if (!resp.ok) {
        const err = await resp.json().catch(() => ({}));
        alert('Không thể tải file: ' + (err.error || resp.statusText));
        return;
      }

      const blob = await resp.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      // try to extract filename from Content-Disposition
      const cd = resp.headers.get('Content-Disposition');
      let filename = 'template.txt';
      if (cd) {
        const match = /filename\*=UTF-8''([^;]+)|filename="?([^";]+)"?/.exec(cd);
        if (match) filename = decodeURIComponent(match[1] || match[2] || filename);
      } else {
        // fallback to templateId
        filename = templateId + '.txt';
      }

      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Download error', err);
      alert('Lỗi khi tải file: ' + err.message);
    }
  };

  const handleUpgradeClick = (planId) => {
    setSelectedPlan(planId);
    setShowPaymentModal(true);
  };

  const handlePayment = async () => {
    try {
      const result = await paymentService.processPayment(selectedPlan, billingCycle);
      
      if (result.success) {
        if (result.paymentUrl) {
          // Redirect to payment gateway
          window.location.href = result.paymentUrl;
          return;
        }
        
        setShowPaymentModal(false);
        onUpgrade(selectedPlan);
      } else {
        alert('Lỗi thanh toán: ' + result.error);
      }
    } catch (error) {
      alert('Lỗi xử lý thanh toán: ' + error.message);
    }
  };

  const plans = [
    {
      id: 'free',
      name: 'Thường',
      icon: Sparkles,
      price: { monthly: 0, yearly: 0 },
      description: 'Dùng thử các tính năng cơ bản',
      color: 'slate',
      gradient: 'from-slate-600 to-slate-700',
      features: [
        { text: '5 phân tích/tháng', included: true },
        { text: 'Lưu trữ: 30 ngày', included: true },
        { text: 'Kích thước file tối đa: 10MB', included: true },
        { text: 'Loại file: PDF, DOCX', included: true },
        { text: 'Phân tích điều khoản: Cơ bản', included: true },
        { text: 'Đề xuất khuyến nghị: Có', included: true },
        { text: 'So sánh hợp đồng: Không', included: false },
        { text: 'Phân tích ngôn ngữ: Tiếng Việt', included: true },
        { text: 'Chat hỏi đáp: Không', included: false },
        { text: 'Báo cáo PDF: Có', included: true },
        { text: 'Báo cáo Word: Không', included: false },
        { text: 'Tùy chỉnh template: Không', included: false }
      ],
      buttonText: 'Gói hiện tại',
      isPopular: false
    },
    {
      id: 'pro',
      name: 'Pro',
      icon: Zap,
      price: { monthly: 299000, yearly: 2990000 },
      description: 'Cho cá nhân và doanh nghiệp nhỏ',
      color: 'cyan',
      gradient: 'from-cyan-600 to-blue-600',
      features: [
        { text: '50 phân tích/tháng', included: true },
        { text: 'Lưu trữ: Vĩnh viễn', included: true },
        { text: 'Kích thước file tối đa: 50MB', included: true },
        { text: 'Loại file: PDF, DOCX, TXT', included: true },
        { text: 'Phân tích điều khoản: Nâng cao', included: true },
        { text: 'Đề xuất khuyến nghị: Có (Chi tiết)', included: true },
        { text: 'So sánh hợp đồng: Có', included: true },
        { text: 'Phân tích ngôn ngữ: Tiếng Việt', included: true },
        { text: 'Chat hỏi đáp: Có', included: true },
        { text: 'Báo cáo PDF: Có', included: true },
        { text: 'Báo cáo Word: Có', included: true },
        { text: 'Tùy chỉnh template: Có', included: true }
      ],
      buttonText: 'Nâng cấp lên Pro',
      isPopular: true
    },
    
  ];

  const comparisonFeatures = [
    {
      category: 'Phân tích cơ bản',
      features: [
        { name: 'Số lượng phân tích/tháng', free: '5', pro: '50' },
        { name: 'Thời gian lưu trữ', free: '30 ngày', pro: 'Vĩnh viễn' },
        { name: 'Kích thước file tối đa', free: '10MB', pro: '50MB' },
        { name: 'Loại file hỗ trợ', free: 'PDF, DOCX', pro: 'PDF, DOCX, TXT' }
      ]
    },
    {
      category: 'Tính năng AI',
      features: [
        { name: 'Phân tích điều khoản', free: 'Cơ bản', pro: 'Nâng cao' },
        { name: 'Đề xuất khuyến nghị', free: 'Có', pro: 'Có + Chi tiết' },
        { name: 'So sánh hợp đồng', free: 'Không', pro: 'Có' },
        { name: 'Phân tích ngôn ngữ', free: 'Tiếng Việt', pro: 'Tiếng Việt' },
        { name: 'Chat hỏi đáp về hợp đồng', free: 'Không', pro: 'Có' }
      ]
    },
    {
      category: 'Xuất báo cáo',
      features: [
        { name: 'Báo cáo PDF', free: 'Có', pro: 'Có' },
        { name: 'Báo cáo Word', free: 'Không', pro: 'Có' },
        { name: 'Tùy chỉnh template', free: 'Không', pro: 'Có' }
      ]
    }
  ];

  const formatPrice = (price) => {
    return new Intl.NumberFormat('vi-VN').format(price);
  };

  const getDiscount = () => {
    return billingCycle === 'yearly' ? 17 : 0; // ~2 tháng miễn phí
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Header */}
      <div className="text-center mb-12">
        <h1 className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-blue-400 to-pink-500 mb-4">
          Chọn gói dịch vụ phù hợp
        </h1>
        <p className="text-slate-400 text-lg max-w-2xl mx-auto mb-8">
          Nâng cấp để sử dụng đầy đủ sức mạnh AI phân tích hợp đồng chuyên nghiệp
        </p>

        {/* Billing Toggle */}
        <div className="inline-flex items-center gap-4 bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 rounded-xl p-2">
          <button
            onClick={() => setBillingCycle('monthly')}
            className={`px-6 py-2.5 rounded-lg transition-all ${
              billingCycle === 'monthly'
                ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-lg shadow-cyan-500/30'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Hàng tháng
          </button>
          <button
            onClick={() => setBillingCycle('yearly')}
            className={`px-6 py-2.5 rounded-lg transition-all flex items-center gap-2 ${
              billingCycle === 'yearly'
                ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-lg shadow-cyan-500/30'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Hàng năm
            <span className="px-2 py-0.5 bg-pink-500 text-white text-xs rounded-full">
              Tiết kiệm {getDiscount()}%
            </span>
          </button>
        </div>
        {/* Voucher input */}
        <div className="mt-6 flex items-center justify-center gap-3">
          <input
            value={voucherCode}
            onChange={(e) => setVoucherCode(e.target.value)}
            placeholder="Nhập mã Voucher"
            className="p-3 rounded-lg bg-slate-800 text-slate-200 w-80"
          />
          <button onClick={applyVoucher} disabled={voucherLoading} className="px-4 py-3 bg-amber-500 text-white rounded-lg">
            {voucherLoading ? 'Đang áp dụng...' : 'Áp dụng'}
          </button>
        </div>
        {voucherError && <div className="text-red-400 text-center mt-2">{voucherError}</div>}
        {voucherSuccess && <div className="text-green-400 text-center mt-2">{voucherSuccess} 🎉</div>}
      </div>

      {/* Pricing Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-16">
        {plans.map((plan, index) => {
          const Icon = plan.icon;
          const price = billingCycle === 'monthly' ? plan.price.monthly : plan.price.yearly;
          const yearlyDiscount = billingCycle === 'yearly' && plan.price.yearly > 0;

          return (
            <div
              key={plan.id}
              className={`relative group animate-fade-in ${
                plan.isPopular ? 'md:scale-105 md:-mt-4 md:mb-4' : ''
              }`}
              style={{ animationDelay: `${index * 100}ms` }}
            >
              {/* Popular Badge */}
              {plan.isPopular && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 z-10">
                  <div className="flex items-center gap-2 px-4 py-1.5 bg-gradient-to-r from-pink-500 to-purple-500 text-white rounded-full text-sm shadow-lg shadow-pink-500/50">
                    <Crown className="w-4 h-4" />
                    Phổ biến nhất
                  </div>
                </div>
              )}

              <div className={`absolute inset-0 bg-gradient-to-r ${plan.gradient} rounded-2xl opacity-0 group-hover:opacity-20 transition-opacity blur-xl`}></div>
              
              <div className={`relative bg-slate-900/70 backdrop-blur-xl rounded-2xl border-2 overflow-hidden transition-all duration-300 ${
                plan.isPopular 
                  ? 'border-cyan-500/50 shadow-2xl shadow-cyan-500/20' 
                  : 'border-slate-700/50 hover:border-slate-600'
              }`}>
                <div className="p-8">
                  {/* Icon & Name */}
                  <div className="flex items-center gap-3 mb-4">
                    <div className={`bg-gradient-to-br ${plan.gradient} p-3 rounded-xl shadow-lg`}>
                      <Icon className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h3 className="text-xl text-slate-100">{plan.name}</h3>
                      <p className="text-slate-500 text-sm">{plan.description}</p>
                    </div>
                  </div>

                  {/* Price */}
                  <div className="mb-6">
                    <div className="flex items-baseline gap-2">
                      <span className="text-4xl text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-pink-400">
                        {price === 0 ? 'Miễn phí' : `${formatPrice(price)}₫`}
                      </span>
                      {price > 0 && (
                        <span className="text-slate-500">
                          /{billingCycle === 'monthly' ? 'tháng' : 'năm'}
                        </span>
                      )}
                    </div>
                    {yearlyDiscount && (
                      <p className="text-green-400 text-sm mt-1">
                        Tiết kiệm {formatPrice(plan.price.monthly * 12 - plan.price.yearly)}₫/năm
                      </p>
                    )}
                  </div>

                  {/* Features */}
                  <ul className="space-y-3 mb-8">
                    {plan.features.map((feature, i) => (
                      <li key={i} className="flex items-start gap-3">
                        {feature.included ? (
                          <div className="bg-green-500/20 p-1 rounded-full flex-shrink-0">
                            <Check className="w-4 h-4 text-green-400" />
                          </div>
                        ) : (
                          <div className="bg-slate-700/30 p-1 rounded-full flex-shrink-0">
                            <X className="w-4 h-4 text-slate-600" />
                          </div>
                        )}
                        <span className={feature.included ? 'text-slate-300' : 'text-slate-600'}>
                          {feature.text}
                        </span>
                      </li>
                    ))}
                  </ul>

                  {/* CTA Button */}
                  {plan.id === 'free' ? (
                    <button
                      disabled
                      className="w-full py-3 bg-slate-800 text-slate-500 rounded-xl cursor-not-allowed"
                    >
                      {plan.buttonText}
                    </button>
                  ) : (
                    <button
                      onClick={() => handleUpgradeClick(plan.id)}
                      className={`w-full py-3 bg-gradient-to-r ${plan.gradient} hover:opacity-90 text-white rounded-xl transition-all shadow-lg ${
                        plan.id === 'pro' ? 'shadow-cyan-500/30' : 'shadow-purple-500/30'
                      }`}
                    >
                      {plan.buttonText}
                    </button>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Payment Modal */}
      {showPaymentModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl p-8 max-w-md w-full">
            <h3 className="text-cyan-100 text-xl mb-6">Chọn phương thức thanh toán</h3>
            
            <div className="space-y-3">
              <button
                onClick={handlePayment}
                className="w-full p-4 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 rounded-xl text-white transition-all flex items-center justify-between"
              >
                <span className="font-semibold">VNPay</span>
                <span className="text-sm">Visa, Mastercard, ATM</span>
              </button>
            </div>

            <button
              onClick={() => setShowPaymentModal(false)}
              className="w-full mt-4 py-3 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl transition-all"
            >
              Hủy
            </button>
          </div>
        </div>
      )}

      {/* Comparison Table */}
      <div className="bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-8 mb-8">
        <h2 className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-pink-500 mb-8 text-center">
          So sánh chi tiết các gói
        </h2>

        <div className="space-y-8">
          {comparisonFeatures.map((category, catIndex) => (
            <div key={catIndex}>
              <h3 className="text-cyan-100 mb-4 flex items-center gap-2">
                <div className="w-1 h-6 bg-gradient-to-b from-cyan-500 to-pink-500 rounded-full"></div>
                {category.category}
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-slate-700">
                      <th className="text-left text-slate-400 py-3 px-4 w-1/2">Tính năng</th>
                      <th className="text-center text-slate-400 py-3 px-4">Thường</th>
                      <th className="text-center text-cyan-400 py-3 px-4">Pro</th>
                    </tr>
                  </thead>
                  <tbody>
                    {category.features.map((feature, i) => (
                      <tr key={i} className="border-b border-slate-800 hover:bg-slate-800/30 transition-colors">
                        <td className="text-slate-300 py-3 px-4">{feature.name}</td>
                        {/* Free column */}
                        <td className="text-center text-slate-400 py-3 px-4">
                          {feature.name === 'Tùy chỉnh template' ? (
                            <button
                              onClick={() => openTemplateModal('free')}
                              className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-800 hover:bg-slate-700 text-slate-300"
                            >
                              <X className="w-4 h-4 text-slate-500" />
                              Nâng cấp
                            </button>
                          ) : renderComparisonCell(feature.free)}
                        </td>

                        {/* Pro column */}
                        <td className="text-center text-cyan-300 py-3 px-4">
                          {feature.name === 'Tùy chỉnh template' ? (
                            <button
                              onClick={() => openTemplateModal('pro')}
                              className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-green-500/10 hover:bg-green-500/20 text-slate-300"
                            >
                              <Check className="w-4 h-4 text-green-400" />
                              Xem mẫu
                            </button>
                          ) : renderComparisonCell(feature.pro)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Template Modal */}
      {showTemplateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl p-6 max-w-xl w-full">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-cyan-100 text-lg">Mẫu template ({templateModalFor === 'pro' ? 'Pro' : 'Thường'})</h3>
              <button onClick={() => setShowTemplateModal(false)} className="text-slate-400">Đóng</button>
            </div>

            <div className="space-y-4">
              {templates.map(t => (
                <div key={t.id} className="p-4 bg-slate-800/50 rounded-lg border border-slate-700">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-slate-200 font-semibold">{t.title}</div>
                      <div className="text-slate-400 text-sm">{t.desc}</div>
                    </div>
                    <div>
                      {templateModalFor === 'pro' ? (
                        <button onClick={() => downloadTemplate(t.id)} className="px-3 py-2 bg-cyan-600 text-white rounded-lg">Tải về</button>
                      ) : (
                        <button onClick={() => { setShowTemplateModal(false); handleUpgradeClick('pro'); }} className="px-3 py-2 bg-amber-600 text-white rounded-lg">Nâng cấp</button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* FAQ Section */}
      <div className="bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-8">
        <h2 className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-pink-500 mb-6 text-center">
          Câu hỏi thường gặp
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-cyan-100 mb-2">Có thể thay đổi gói dịch vụ không?</h3>
            <p className="text-slate-400 text-sm">Có, bạn có thể nâng cấp hoặc hạ cấp bất cứ lúc nào. Phí sẽ được tính theo tỷ lệ thời gian sử dụng.</p>
          </div>
          <div>
            <h3 className="text-cyan-100 mb-2">Chính sách hoàn tiền như thế nào?</h3>
            <p className="text-slate-400 text-sm">Chúng tôi có chính sách hoàn tiền trong 14 ngày đầu tiên nếu bạn không hài lòng với dịch vụ.</p>
          </div>
          <div>
            <h3 className="text-cyan-100 mb-2">Thanh toán như thế nào?</h3>
            <p className="text-slate-400 text-sm">Chấp nhận thẻ tín dụng, thẻ ghi nợ, chuyển khoản ngân hàng và ví điện tử.</p>
          </div>
          <div>
            <h3 className="text-cyan-100 mb-2">Có hỗ trợ dùng thử không?</h3>
            <p className="text-slate-400 text-sm">Gói miễn phí luôn có sẵn. Gói Pro và Enterprise có thể dùng thử 7 ngày không mất phí.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
