// Payment service for VNPay, MoMo, Stripe integration
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

class PaymentService {
  async request(endpoint, options = {}) {
    const method = (options.method || 'GET').toUpperCase();
    const defaultHeaders = method === 'GET' ? {} : { 'Content-Type': 'application/json' };

    const response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers: {
        ...defaultHeaders,
        ...(options.headers || {}),
      },
      credentials: 'include',
    });

    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(data.error || data.message || 'Payment request failed');
    }
    return data;
  }

  // VNPay payment
  async createVNPayPayment(plan, amount, billingCycle = 'monthly') {
    try {
      const result = await this.request('/payments/vnpay/create', {
        method: 'POST',
        body: JSON.stringify({
          plan,
          amount,
          billing_cycle: billingCycle,
          return_url: `${window.location.origin}/payment/return`,
        }),
      });

      return {
        success: true,
        paymentUrl: result.payment_url,
        method: 'vnpay',
        txnRef: result.txn_ref,
      };
    } catch (error) {
      console.error('VNPay error:', error);
      return { success: false, error: error.message };
    }
  }

  // MoMo payment
  async createMoMoPayment(_plan, _amount) {
    try {
      // In production, call backend API to create MoMo payment
      // Backend will use MoMo API with proper signature
      // TODO: Use plan and amount parameters when implementing real API
      
      // Simulate MoMo deeplink/QR
      const orderId = `GENZLEGAL_${Date.now()}`;
      
      return {
        success: true,
        orderId: orderId,
        qrCode: `https://test-payment.momo.vn/v2/gateway/api/create?orderId=${orderId}`,
        deeplink: `momo://app?action=payment&orderId=${orderId}`,
        method: 'momo'
      };
    } catch (error) {
      console.error('MoMo error:', error);
      return { success: false, error: error.message };
    }
  }

  // Stripe payment
  async createStripePayment(_plan, _amount) {
    try {
      // In production, call backend to create Stripe checkout session
      // Backend uses Stripe SDK with secret key
      // TODO: Use plan and amount parameters when implementing real API
      
      const sessionId = `sess_${Date.now()}`;
      
      return {
        success: true,
        sessionId: sessionId,
        checkoutUrl: `https://checkout.stripe.com/pay/${sessionId}`,
        method: 'stripe'
      };
    } catch (error) {
      console.error('Stripe error:', error);
      return { success: false, error: error.message };
    }
  }

  // Bank transfer info
  getBankTransferInfo(plan, amount) {
    return {
      success: true,
      method: 'bank_transfer',
      bankInfo: {
        bankName: 'Ngân hàng TMCP Á Châu (ACB)',
        accountNumber: '123456789',
        accountName: 'CONG TY TNHH GENZLEGAL AI',
        amount: amount,
        content: `GENZLEGAL ${plan.toUpperCase()} ${Date.now()}`,
        note: 'Vui lòng chuyển khoản đúng nội dung để hệ thống tự động xác nhận thanh toán'
      }
    };
  }

  // Process payment based on selected method
  async processPayment(plan, method, billingCycle = 'monthly') {
    // Plan pricing
    const pricing = {
      'basic': 0,
      'pro': 299000,
      'enterprise': 999000
    };

    const amount = pricing[plan] || 0;

    if (amount === 0) {
      return { success: true, message: 'Gói miễn phí không cần thanh toán' };
    }

    switch (method) {
      case 'vnpay':
        return this.createVNPayPayment(plan, amount, billingCycle);
      case 'momo':
        return this.createMoMoPayment(plan, amount);
      case 'stripe':
        return this.createStripePayment(plan, amount);
      case 'bank_transfer':
        return this.getBankTransferInfo(plan, amount);
      default:
        return { success: false, error: 'Phương thức thanh toán không hợp lệ' };
    }
  }

  // Verify payment callback (for VNPay, MoMo)
  async verifyPayment(params) {
    try {
      const txnRef = params?.txn_ref || params?.txnRef;
      if (!txnRef) {
        return { success: false, verified: false, error: 'Thiếu mã giao dịch' };
      }

      const result = await this.request(`/payments/status/${encodeURIComponent(txnRef)}`, {
        method: 'GET',
        headers: {},
      });

      return {
        success: true,
        verified: result?.payment?.status === 'success',
        payment: result.payment,
      };
    } catch (error) {
      return { success: false, verified: false, error: error.message };
    }
  }
}

export default new PaymentService();
