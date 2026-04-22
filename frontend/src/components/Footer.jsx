import { Link } from 'react-router-dom';
import logoImage from '/logo.png';

export function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="mt-16 border-t border-slate-700/50 bg-slate-950/80 backdrop-blur-xl">
      <div className="container mx-auto px-4 py-10">
        <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
          <div className="md:col-span-2">
            <div className="mb-4 flex items-center gap-4">
              <div className="h-16 w-16 overflow-hidden rounded-full border border-cyan-500/40 bg-slate-900">
                <img src={logoImage} alt="GenZ Legal AI" className="h-full w-full object-cover" />
              </div>
              <div>
                <h3 className="text-3xl text-slate-100">GenZ Legal AI</h3>
                <p className="text-sm text-slate-400">Giải pháp pháp lý thông minh cho doanh nghiệp và cá nhân</p>
              </div>
            </div>

            <p className="mb-2 text-slate-300">
                GIẢI PHÁP PHÁP LÝ GENZ AI
            </p>
            <p className="mb-1 text-slate-400">
              Địa chỉ: 18A Cộng Hòa, Phường Tân Sơn Nhất, TP.HCM
            </p>
            <p className="mb-1 text-slate-400">Hotline: 0877772244</p>
            <p className="text-slate-400">Email: cskh@genzlegal.ai</p>
          </div>

          <div>
            <h4 className="mb-4 text-sm uppercase tracking-wider text-slate-200">Thông tin</h4>
            <div className="space-y-3">
              <Link to="/about" className="block text-slate-400 transition-colors hover:text-cyan-300">
                Về chúng tôi
              </Link>
              <Link to="/privacy" className="block text-slate-400 transition-colors hover:text-cyan-300">
                Chính sách bảo mật
              </Link>
              <Link to="/terms" className="block text-slate-400 transition-colors hover:text-cyan-300">
                Điều khoản sử dụng
              </Link>
            </div>
          </div>
        </div>

        <div className="mt-8 border-t border-slate-700/50 pt-4 text-sm text-slate-500">
          Copyright {currentYear} GenZ Legal AI. All rights reserved.
        </div>
      </div>
    </footer>
  );
}
