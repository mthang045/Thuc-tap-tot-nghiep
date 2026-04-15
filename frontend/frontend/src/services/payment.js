// Payment service for VNPay only

class PaymentService {
  constructor() {
    this.apiBase = import.meta.env.VITE_API_URL || '/api';
  }

  // VNPay payment
  async createVNPayPayment(plan, amount, billingCycle = 'monthly') {
    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch(`${this.apiBase}/payments/vnpay/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': token ? `Bearer ${token}` : ''
        },
        credentials: 'include',
        body: JSON.stringify({
          plan,
          amount,
          billing_cycle: billingCycle,
          return_url: `${window.location.origin}/payment/return`
        })
      });

      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        return { success: false, error: data.error || 'Không tạo được giao dịch VNPay' };
      }

      return {
        success: true,
        paymentUrl: data.payment_url,
        txnRef: data.txn_ref,
        method: 'vnpay'
      };
    } catch (error) {
      console.error('VNPay error:', error);
      return { success: false, error: error.message };
    }
  }

  // Process payment via VNPay only
  async processPayment(plan, billingCycle = 'monthly') {
    // Plan pricing
    const pricing = {
      pro: {
        monthly: 299000,
        yearly: 2990000,
      },
      enterprise: {
        monthly: 999000,
        yearly: 9990000,
      }
    };

    const amount = pricing[plan]?.[billingCycle] || 0;

    if (amount === 0) {
      return { success: true, message: 'Gói miễn phí không cần thanh toán' };
    }

    return this.createVNPayPayment(plan, amount, billingCycle);
  }

  // Verify payment callback (for VNPay, MoMo)
  async verifyPayment(_params) {
    // In production, send params to backend for verification
    // Backend validates signature and updates user subscription
    // TODO: Implement real verification with backend API
    
    // Simulate verification
    return {
      success: true,
      verified: true,
      message: 'Thanh toán thành công'
    };
  }
}

export default new PaymentService();
