export function AboutPage() {
  return (
    <section className="mx-auto max-w-4xl rounded-2xl border border-cyan-500/20 bg-slate-900/60 p-8 shadow-xl shadow-cyan-500/10">
      <h1 className="mb-4 text-cyan-100">Về chúng tôi</h1>
      <p className="mb-4 text-slate-300 leading-relaxed">
        GenZ Legal AI phát triển nền tảng phân tích hợp đồng pháp lý bằng AI dành cho doanh nghiệp và cá nhân tại Việt Nam.
        Hệ thống kết hợp SVM, PageIndex Tree và LLM để hỗ trợ người dùng rà soát điều khoản, nhận diện rủi ro và
        đưa ra khuyến nghị cải thiện phù hợp với bối cảnh pháp lý hiện hành.
      </p>
      <p className="mb-4 text-slate-300 leading-relaxed">
        Mục tiêu của chúng tôi là giúp quá trình kiểm tra hợp đồng trở nên nhanh hơn, minh bạch hơn và dễ tiếp cận hơn.
        Chúng tôi luôn ưu tiên tính chính xác, khả năng giải thích và trải nghiệm người dùng trong từng tính năng.
      </p>
      <p className="text-slate-400">
        Nếu bạn cần hỗ trợ, vui lòng liên hệ: cskh@genzlegal.ai
      </p>
    </section>
  );
}
