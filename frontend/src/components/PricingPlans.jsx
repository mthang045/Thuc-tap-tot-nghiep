import { useState } from 'react';
import { Check, X, Zap, Crown, Building2, Sparkles, FileText } from 'lucide-react';
import { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, BorderStyle, AlignmentType, HeadingLevel } from 'docx';
import paymentService from '../services/payment';

export function PricingPlans({ onUpgrade, currentPlan = 'free' }) {
  const [billingCycle, setBillingCycle] = useState('monthly');
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [showTemplateModal, setShowTemplateModal] = useState(false);
  const [templateModalFor, setTemplateModalFor] = useState('');
  const [allTemplates, setAllTemplates] = useState(null);
  const [isLoadingTemplates, setIsLoadingTemplates] = useState(false);
  const normalizedCurrentPlan = String(currentPlan || 'free').toLowerCase() === 'free' ? 'free' : 'pro';

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
          <Check className="w-4 h-4 text-green-400" />
        )}
        <span className={isExcluded ? 'text-slate-600' : 'text-slate-300'}>{text}</span>
      </div>
    );
  };

  const fetchAllTemplates = async () => {
    setIsLoadingTemplates(true);
    try {
      const resp = await fetch('/v1/templates', { credentials: 'include' });
      if (resp.ok) {
        const data = await resp.json();
        setAllTemplates(data.templates || []);
      }
    } catch (e) {
      console.error('Failed to load templates', e);
    } finally {
      setIsLoadingTemplates(false);
    }
  };

  const openTemplateModal = (planId) => {
    setTemplateModalFor(planId);
    fetchAllTemplates();
    setShowTemplateModal(true);
  };

  const downloadTemplate = async (templateId) => {
    try {
      const resp = await fetch(`/api/templates/${templateId}/download`, {
        method: 'GET',
        credentials: 'include'
      });

      if (!resp.ok) {
        // Đọc text trước, thử parse thành JSON
        const text = await resp.text();
        try {
          const err = JSON.parse(text);
          alert('Không thể tải file: ' + (err.error || resp.statusText));
        } catch {
          alert('Không thể tải file: ' + resp.statusText);
        }
        return;
      }

      const blob = await resp.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      const cd = resp.headers.get('Content-Disposition');
      let filename = 'template.txt';
      if (cd) {
        const match = /filename\*=UTF-8''([^;]+)|filename="?([^";]+)"?/.exec(cd);
        if (match) filename = decodeURIComponent(match[1] || match[2] || filename);
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

  const exportPricingPlansWord = async () => {
    const formatPrice = (price) => {
      return new Intl.NumberFormat('vi-VN').format(price);
    };

    const borderStyle = { style: BorderStyle.SINGLE, size: 1, color: "666666" };
    
    const headerRow = new TableRow({
      children: [
        new TableCell({
          children: [new Paragraph({ children: [new TextRun({ text: "Tính năng", bold: true })] })],
          width: { size: 50, type: WidthType.PERCENTAGE },
          shading: { fill: "0ea5e9", type: "clear" },
          borders: { top: borderStyle, bottom: borderStyle, left: borderStyle, right: borderStyle },
        }),
        new TableCell({
          children: [new Paragraph({ children: [new TextRun({ text: "Thường", bold: true })], alignment: AlignmentType.CENTER })],
          width: { size: 25, type: WidthType.PERCENTAGE },
          shading: { fill: "334155", type: "clear" },
          borders: { top: borderStyle, bottom: borderStyle, left: borderStyle, right: borderStyle },
        }),
        new TableCell({
          children: [new Paragraph({ children: [new TextRun({ text: "Pro", bold: true })], alignment: AlignmentType.CENTER })],
          width: { size: 25, type: WidthType.PERCENTAGE },
          shading: { fill: "0891b2", type: "clear" },
          borders: { top: borderStyle, bottom: borderStyle, left: borderStyle, right: borderStyle },
        }),
      ],
    });

    const featureRows = [
      { name: "Phân tích/tháng", free: "5", pro: "50" },
      { name: "Lưu trữ", free: "30 ngày", pro: "Vĩnh viễn" },
      { name: "Kích thước file", free: "10MB", pro: "50MB" },
      { name: "Loại file", free: "PDF, DOCX", pro: "PDF, DOCX, TXT" },
      { name: "Phân tích điều khoản", free: "Cơ bản", pro: "Nâng cao" },
      { name: "Đề xuất khuyến nghị", free: "Có", pro: "Có (Chi tiết)" },
      { name: "So sánh hợp đồng", free: "Không", pro: "Có" },
      { name: "Phân tích ngôn ngữ", free: "Tiếng Việt", pro: "Tiếng Việt" },
      { name: "Chat hỏi đáp", free: "Không", pro: "Có" },
      { name: "Báo cáo PDF", free: "Có", pro: "Có" },
      { name: "Báo cáo Word", free: "Không", pro: "Có" },
      { name: "Tùy chỉnh template", free: "Không", pro: "Có" },
    ];

    const dataRows = featureRows.map((f, idx) => 
      new TableRow({
        children: [
          new TableCell({
            children: [new Paragraph({ children: [new TextRun({ text: f.name })] })],
            borders: { top: borderStyle, bottom: borderStyle, left: borderStyle, right: borderStyle },
          }),
          new TableCell({
            children: [new Paragraph({ 
              children: [new TextRun({ 
                text: f.free === "Không" ? "✗" : f.free, 
                color: f.free === "Không" ? "ef4444" : "334155" 
              })], 
              alignment: AlignmentType.CENTER 
            })],
            borders: { top: borderStyle, bottom: borderStyle, left: borderStyle, right: borderStyle },
          }),
          new TableCell({
            children: [new Paragraph({ 
              children: [new TextRun({ text: f.pro, color: "0ea5e9" })], 
              alignment: AlignmentType.CENTER 
            })],
            borders: { top: borderStyle, bottom: borderStyle, left: borderStyle, right: borderStyle },
          }),
        ],
      })
    );

    const table = new Table({
      rows: [headerRow, ...dataRows],
      width: { size: 100, type: WidthType.PERCENTAGE },
    });

    const doc = new Document({
      sections: [{
        properties: {},
        children: [
          new Paragraph({
            children: [
              new TextRun({ 
                text: "BẢNG GIÁ DỊCH VỤ", 
                bold: true, 
                size: 48,
                color: "0ea5e9"
              }),
            ],
            alignment: AlignmentType.CENTER,
            spacing: { after: 200 },
          }),
          new Paragraph({
            children: [
              new TextRun({ 
                text: "Nâng cấp để sử dụng đầy đủ sức mạnh AI phân tích hợp đồng chuyên nghiệp", 
                size: 24,
                color: "64748b"
              }),
            ],
            alignment: AlignmentType.CENTER,
            spacing: { after: 400 },
          }),
          new Paragraph({
            children: [new TextRun({ text: "SO SÁNH CHI TIẾT CÁC GÓI", bold: true, size: 28 })],
            spacing: { after: 200 },
          }),
          table,
          new Paragraph({ spacing: { before: 400, after: 200 } }),
          new Paragraph({
            children: [new TextRun({ text: "GÓI THƯỜNG", bold: true, size: 32, color: "334155" })],
          }),
          new Paragraph({
            children: [
              new TextRun({ text: "Miễn phí", bold: true, size: 36, color: "334155" }),
            ],
          }),
          new Paragraph({
            children: [new TextRun({ text: "Dùng thử các tính năng cơ bản", size: 22, color: "64748b" })],
          }),
          new Paragraph({
            children: [
              new TextRun({ text: "5 phân tích/tháng", size: 22 }),
              new TextRun({ text: "  •  ", size: 22 }),
              new TextRun({ text: "Lưu trữ 30 ngày", size: 22 }),
              new TextRun({ text: "  •  ", size: 22 }),
              new TextRun({ text: "File 10MB", size: 22 }),
            ],
            spacing: { before: 100, after: 100 },
          }),
          new Paragraph({ spacing: { before: 300, after: 200 } }),
          new Paragraph({
            children: [new TextRun({ text: "GÓI PRO", bold: true, size: 32, color: "0891b2" })],
          }),
          new Paragraph({
            children: [
              new TextRun({ text: `${formatPrice(299000)}đ/tháng`, bold: true, size: 36, color: "0891b2" }),
            ],
          }),
          new Paragraph({
            children: [new TextRun({ text: "Cho cá nhân và doanh nghiệp nhỏ", size: 22, color: "64748b" })],
          }),
          new Paragraph({
            children: [
              new TextRun({ text: "50 phân tích/tháng", size: 22 }),
              new TextRun({ text: "  •  ", size: 22 }),
              new TextRun({ text: "Lưu trữ vĩnh viễn", size: 22 }),
              new TextRun({ text: "  •  ", size: 22 }),
              new TextRun({ text: "File 50MB", size: 22 }),
            ],
            spacing: { before: 100, after: 100 },
          }),
          new Paragraph({
            children: [
              new TextRun({ text: `Tiết kiệm ${formatPrice(299000 * 12 - 2990000)}đ/năm khi chọn thanh toán hàng năm`, size: 20, italics: true, color: "22c55e" }),
            ],
          }),
          new Paragraph({ spacing: { before: 400 } }),
          new Paragraph({
            children: [new TextRun({ text: `Ngày xuất: ${new Date().toLocaleDateString('vi-VN')}`, size: 18, color: "94a3b8" })],
            alignment: AlignmentType.CENTER,
          }),
        ],
      }],
    });

    const blob = await Packer.toBlob(doc);
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'bang-gia-dich-vu.docx';
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  };

  const categoryIcons = {
    'Thương mại': '🏪',
    'Nhân sự': '👥',
    'Pháp lý': '⚖️',
    'Bất động sản': '🏠',
    'Tài chính': '💰',
    'Nội bộ': '📋',
  };

  const templates = allTemplates || [
    { template_id: 't1', title: 'Hợp đồng mua bán hàng hóa', category: 'Thương mại', description: 'Mẫu hợp đồng mua bán hàng hóa.' },
    { template_id: 't2', title: 'Hợp đồng lao động', category: 'Nhân sự', description: 'Mẫu HĐLĐ theo Bộ luật Lao động 2019.' },
    { template_id: 't3', title: 'Thỏa thuận bảo mật (NDA)', category: 'Pháp lý', description: 'Thỏa thuận bảo mật thông tin.' },
    { template_id: 't4', title: 'Hợp đồng thuê nhà ở', category: 'Bất động sản', description: 'Mẫu hợp đồng thuê nhà.' },
    { template_id: 't5', title: 'Hợp đồng cung cấp dịch vụ', category: 'Thương mại', description: 'Mẫu hợp đồng dịch vụ.' },
    { template_id: 't6', title: 'Hợp đồng giao khoán', category: 'Thương mại', description: 'Mẫu hợp đồng giao khoán.' },
    { template_id: 't7', title: 'Quy chế nội bộ công ty', category: 'Nội bộ', description: 'Mẫu quy chế nội bộ.' },
    { template_id: 't8', title: 'Giấy ủy quyền', category: 'Pháp lý', description: 'Mẫu giấy ủy quyền.' },
    { template_id: 't9', title: 'Biên bản họp', category: 'Nội bộ', description: 'Mẫu biên bản họp.' },
    { template_id: 't10', title: 'Hợp đồng vay tiền', category: 'Tài chính', description: 'Mẫu hợp đồng vay tiền.' },
    { template_id: 't11', title: 'Quyết định bổ nhiệm', category: 'Nhân sự', description: 'Mẫu quyết định bổ nhiệm.' },
    { template_id: 't12', title: 'Đơn xin nghỉ việc', category: 'Nhân sự', description: 'Mẫu đơn xin nghỉ việc.' },
    { template_id: 't13', title: 'Hợp đồng thuê nhà', category: 'Bất động sản', description: 'Mẫu hợp đồng thuê nhà chi tiết.' },
  ];

  const handleUpgradeClick = (planId) => {
    if (planId === normalizedCurrentPlan) {
      return;
    }
    setSelectedPlan(planId);
    setShowPaymentModal(true);
  };

  const handlePayment = async (method) => {
    try {
      const result = await paymentService.processPayment(selectedPlan, method, billingCycle);
      
      if (result.success) {
        if (result.paymentUrl) {
          // Redirect to payment gateway
          setShowPaymentModal(false);
          window.location.href = result.paymentUrl;
          return;
        } else if (result.checkoutUrl) {
          // Redirect to Stripe checkout
          setShowPaymentModal(false);
          window.location.href = result.checkoutUrl;
          return;
        } else if (result.deeplink) {
          // MoMo deeplink
          window.open(result.deeplink, '_blank');
          alert('Vui lòng hoàn tất thanh toán trên ứng dụng MoMo');
        } else if (result.bankInfo) {
          // Show bank transfer info
          alert(`Thông tin chuyển khoản:\n\nNgân hàng: ${result.bankInfo.bankName}\nSố tài khoản: ${result.bankInfo.accountNumber}\nChủ tài khoản: ${result.bankInfo.accountName}\nSố tiền: ${result.bankInfo.amount.toLocaleString()} VNĐ\nNội dung: ${result.bankInfo.content}\n\n${result.bankInfo.note}`);
        }
        
        setShowPaymentModal(false);
        if (method === 'bank_transfer') {
          onUpgrade(selectedPlan);
        }
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
      </div>

      {/* Pricing Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-16">
        {plans.map((plan, index) => {
          const Icon = plan.icon;
          const price = billingCycle === 'monthly' ? plan.price.monthly : plan.price.yearly;
          const yearlyDiscount = billingCycle === 'yearly' && plan.price.yearly > 0;
          const isCurrentPlan = plan.id === normalizedCurrentPlan;

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
                  <button
                    disabled={isCurrentPlan}
                    onClick={() => handleUpgradeClick(plan.id)}
                    className={`w-full py-3 rounded-xl transition-all ${
                      isCurrentPlan
                        ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                        : 'bg-gradient-to-r from-cyan-600 to-blue-600 hover:opacity-90 text-white shadow-lg shadow-cyan-500/30'
                    }`}
                  >
                    {isCurrentPlan ? 'Gói hiện tại' : plan.buttonText}
                  </button>
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
                onClick={() => handlePayment('vnpay')}
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
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm" onClick={() => setShowTemplateModal(false)}>
          <div className="bg-slate-900 border border-cyan-500/30 rounded-2xl p-6 max-w-3xl w-full max-h-[85vh] overflow-hidden flex flex-col" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-5 flex-shrink-0">
              <div>
                <h3 className="text-cyan-100 text-xl font-bold">
                  {templateModalFor === 'pro' ? '📄 Thư viện mẫu tài liệu Pro' : '🔒 Nâng cấp để sử dụng'}
                </h3>
                <p className="text-slate-400 text-sm mt-1">
                  {templateModalFor === 'pro' ? `${allTemplates?.length || 0} mẫu hợp đồng & tài liệu pháp lý` : 'Gói Pro để truy cập tất cả 13 mẫu tài liệu'}
                </p>
              </div>
              <button onClick={() => setShowTemplateModal(false)} className="text-slate-400 hover:text-white text-2xl leading-none">&times;</button>
            </div>

            {templateModalFor === 'free' ? (
              <div className="flex-1 flex flex-col items-center justify-center py-8">
                <div className="text-6xl mb-4">🔒</div>
                <h4 className="text-white text-xl font-bold mb-2">Nội dung chỉ dành cho Pro</h4>
                <p className="text-slate-400 text-center mb-6 max-w-md">
                  Mở khóa 13 mẫu hợp đồng và tài liệu pháp lý chuyên nghiệp để sử dụng ngay hôm nay.
                </p>
                <div className="grid grid-cols-3 gap-3 mb-6 max-w-md">
                  {['Hợp đồng mua bán', 'Hợp đồng thuê nhà', 'Hợp đồng dịch vụ', 'Hợp đồng lao động', 'Thỏa thuận NDA', 'Hợp đồng vay tiền', 'Biên bản họp', 'Quy chế nội bộ'].map((name, i) => (
                    <div key={i} className="bg-slate-800/50 rounded-lg px-3 py-2 text-slate-500 text-xs text-center border border-slate-700/50">
                      {name}
                    </div>
                  ))}
                </div>
                <button onClick={() => { setShowTemplateModal(false); handleUpgradeClick('pro'); }} className="px-8 py-3 bg-gradient-to-r from-cyan-500 to-blue-500 text-white rounded-xl font-semibold shadow-lg shadow-cyan-500/30 hover:from-cyan-400 hover:to-blue-400 transition-all">
                  Nâng cấp Pro ngay
                </button>
              </div>
            ) : isLoadingTemplates ? (
              <div className="flex-1 flex items-center justify-center">
                <div className="animate-spin w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full"></div>
                <span className="ml-3 text-slate-400">Đang tải danh sách...</span>
              </div>
            ) : (
              <div className="overflow-y-auto flex-1 space-y-6 pr-2">
                {/* Group templates by category */}
                {['Thương mại', 'Nhân sự', 'Pháp lý', 'Bất động sản', 'Tài chính', 'Nội bộ'].map(cat => {
                  const catTemplates = (allTemplates || []).filter(t => t.category === cat);
                  if (!catTemplates.length) return null;
                  return (
                    <div key={cat}>
                      <div className="flex items-center gap-2 mb-3">
                        <span className="text-xl">{categoryIcons[cat] || '📄'}</span>
                        <h4 className="text-cyan-200 font-semibold">{cat}</h4>
                        <div className="flex-1 h-px bg-slate-700/50"></div>
                      </div>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        {catTemplates.map(t => (
                          <div key={t.template_id} className="group bg-slate-800/50 border border-slate-700/50 rounded-xl p-4 hover:border-cyan-500/40 hover:bg-slate-800/80 transition-all">
                            <div className="flex items-start justify-between gap-3">
                              <div className="flex-1 min-w-0">
                                <h5 className="text-slate-100 font-semibold mb-1 group-hover:text-cyan-200 transition-colors">{t.title || t.name}</h5>
                                <p className="text-slate-400 text-xs leading-relaxed line-clamp-2">{t.description}</p>
                                <div className="flex flex-wrap gap-1 mt-2">
                                  {t.tags?.slice(0, 3).map(tag => (
                                    <span key={tag} className="px-2 py-0.5 bg-slate-700/50 text-slate-500 text-[10px] rounded-full">{tag}</span>
                                  ))}
                                </div>
                              </div>
                              <button
                                onClick={() => downloadTemplate(t.template_id)}
                                className="flex-shrink-0 w-9 h-9 bg-cyan-600/20 hover:bg-cyan-500 text-cyan-400 hover:text-white rounded-lg flex items-center justify-center transition-all border border-cyan-500/30 hover:border-cyan-400"
                                title="Tải về"
                              >
                                <FileText className="w-4 h-4" />
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {templateModalFor === 'pro' && (
              <div className="mt-4 pt-4 border-t border-slate-700/50 flex-shrink-0">
                <p className="text-slate-500 text-xs text-center">
                  💡 Tất cả mẫu tài liệu chỉ mang tính tham khảo. Vui lòng tham khảo ý kiến luật sư trước khi sử dụng.
                </p>
              </div>
            )}
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
            <p className="text-slate-400 text-sm">Gói miễn phí luôn có sẵn. Gói Pro có thể dùng thử 7 ngày không mất phí.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
