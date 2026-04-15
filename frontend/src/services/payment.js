// Payment service for VNPay, MoMo, Stripe integration

class PaymentService {
  // VNPay payment
  async createVNPayPayment(plan, amount) {
    try {
      // In production, call backend API to create payment URL
      // For now, simulate VNPay redirect
      const vnpayUrl = 'https://sandbox.vnpayment.vn/paymentv2/vpcpay.html';
      const params = new URLSearchParams({
        vnp_Version: '2.1.0',
        vnp_Command: 'pay',
        vnp_TmnCode: 'YOUR_TMN_CODE',
        vnp_Amount: amount * 100, // VNPay uses smallest currency unit
        vnp_CurrencyCode: 'VND',
        vnp_TxnRef: Date.now().toString(),
        vnp_OrderInfo: `Nang cap goi ${plan}`,
        vnp_OrderType: 'billpayment',
        vnp_Locale: 'vn',
        vnp_ReturnUrl: `${window.location.origin}/payment/return`,
        vnp_IpAddr: '127.0.0.1',
        vnp_CreateDate: new Date().toISOString().replace(/[-:]/g, '').split('.')[0]
      });

      return {
        success: true,
        paymentUrl: `${vnpayUrl}?${params.toString()}`,
        method: 'vnpay'
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
  async processPayment(plan, method) {
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
        return this.createVNPayPayment(plan, amount);
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
