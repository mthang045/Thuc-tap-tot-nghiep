import { useRef, useState } from 'react';
import { Upload, FileText, CheckCircle, Scale, Sparkles, Shield, Zap } from 'lucide-react';
import logoImage from '/logo.png';

export function UploadSection({ onFileUpload, isAnalyzing }) {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleFileSelect = (e) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleFile = (file) => {
    const validTypes = ['.pdf', '.doc', '.docx', '.txt'];
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
    
    if (validTypes.includes(fileExtension)) {
      setSelectedFile(file);
    } else {
      alert('Vui lòng chọn file PDF, DOC, DOCX hoặc TXT');
    }
  };

  const handleAnalyze = () => {
    if (selectedFile) {
      onFileUpload(selectedFile);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 md:py-12 max-w-6xl">
      {/* Header with Logo */}
      <div className="text-center mb-16">
        <div className="flex flex-col items-center justify-center mb-8 animate-float">
          <div className="relative mb-6">
            <div className="absolute inset-0 bg-gradient-to-r from-cyan-400 to-pink-500 rounded-full blur-2xl opacity-60"></div>
            <div className="relative bg-white p-6 rounded-full shadow-2xl shadow-cyan-500/50">
              <img 
                src={logoImage} 
                alt="GenZ Logo" 
                className="h-24 md:h-32 w-24 md:w-32 object-cover rounded-full"
              />
            </div>
          </div>
        </div>
        <p className="text-cyan-100/90 mb-3 text-xl">
          Giải pháp pháp lý cho kỷ nguyên số
        </p>
        <p className="text-slate-400 max-w-2xl mx-auto leading-relaxed">
          Công nghệ AI &amp; RAG hiện đại giúp rà soát hợp đồng tự động, phát hiện vi phạm pháp luật và đưa ra khuyến nghị chuyên nghiệp trong vài giây
        </p>
      </div>

      {/* Enhanced Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
        <div className="group relative">
          <div className="absolute inset-0 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-2xl opacity-0 group-hover:opacity-20 transition-opacity blur-xl"></div>
          <div className="relative bg-slate-900/60 backdrop-blur-xl p-8 rounded-2xl shadow-xl border border-cyan-500/30 hover:border-cyan-400/60 transition-all duration-300 hover:-translate-y-1">
            <div className="bg-gradient-to-br from-cyan-500 to-blue-500 w-14 h-14 rounded-xl flex items-center justify-center mb-5 shadow-lg shadow-cyan-500/50">
              <Sparkles className="w-7 h-7 text-white" />
            </div>
            <h3 className="text-cyan-100 mb-3">Trích xuất thông minh</h3>
            <p className="text-slate-400 leading-relaxed">
              AI đọc và phân tích tất cả điều khoản trong hợp đồng với độ chính xác cao
            </p>
          </div>
        </div>

        <div className="group relative">
          <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl opacity-0 group-hover:opacity-20 transition-opacity blur-xl"></div>
          <div className="relative bg-slate-900/60 backdrop-blur-xl p-8 rounded-2xl shadow-xl border border-purple-500/30 hover:border-purple-400/60 transition-all duration-300 hover:-translate-y-1">
            <div className="bg-gradient-to-br from-purple-500 to-pink-500 w-14 h-14 rounded-xl flex items-center justify-center mb-5 shadow-lg shadow-purple-500/50">
              <Shield className="w-7 h-7 text-white" />
            </div>
            <h3 className="text-purple-100 mb-3">So sánh pháp lý</h3>
            <p className="text-slate-400 leading-relaxed">
              Đối chiếu với cơ sở dữ liệu Luật Lao động, Luật Thương mại và các văn bản liên quan
            </p>
          </div>
        </div>

        <div className="group relative">
          <div className="absolute inset-0 bg-gradient-to-r from-pink-500 to-rose-500 rounded-2xl opacity-0 group-hover:opacity-20 transition-opacity blur-xl"></div>
          <div className="relative bg-slate-900/60 backdrop-blur-xl p-8 rounded-2xl shadow-xl border border-pink-500/30 hover:border-pink-400/60 transition-all duration-300 hover:-translate-y-1">
            <div className="bg-gradient-to-br from-pink-500 to-rose-500 w-14 h-14 rounded-xl flex items-center justify-center mb-5 shadow-lg shadow-pink-500/50">
              <Zap className="w-7 h-7 text-white" />
            </div>
            <h3 className="text-pink-100 mb-3">Cảnh báo tức thì</h3>
            <p className="text-slate-400 leading-relaxed">
              Phát hiện nhanh các điều khoản vi phạm và bất lợi cho người ký kết
            </p>
          </div>
        </div>
      </div>

      {/* Enhanced Upload Area */}
      <div className="relative">
        <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/20 to-pink-500/20 rounded-3xl blur-2xl"></div>
        <div className="relative bg-slate-900/70 backdrop-blur-xl rounded-3xl shadow-2xl border border-slate-700/50 p-8 md:p-10">
          <div
            className={`relative border-2 border-dashed rounded-2xl p-12 md:p-16 text-center transition-all duration-300 ${
              isDragging
                ? 'border-pink-400 bg-gradient-to-br from-cyan-900/40 to-pink-900/40 scale-[1.02] shadow-inner shadow-pink-500/20'
                : 'border-slate-600 bg-slate-800/30'
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <input
              ref={fileInputRef}
              type="file"
              className="hidden"
              accept=".pdf,.doc,.docx,.txt"
              onChange={handleFileSelect}
            />
            
            <div className="flex flex-col items-center">
              <div className={`relative p-6 rounded-2xl mb-6 transition-all duration-300 ${
                isDragging 
                  ? 'bg-gradient-to-br from-cyan-500/30 to-pink-500/30 scale-110 shadow-lg shadow-pink-500/30' 
                  : 'bg-gradient-to-br from-slate-700/50 to-slate-800/50'
              }`}>
                <Upload className={`w-12 h-12 md:w-14 md:h-14 transition-all duration-300 ${
                  isDragging ? 'text-pink-300 scale-110' : 'text-slate-400'
                }`} />
                {isDragging && (
                  <div className="absolute inset-0 bg-pink-500/30 rounded-2xl animate-ping"></div>
                )}
              </div>
              
              {selectedFile ? (
                <div className="mb-6 animate-fade-in">
                  <div className="flex items-center gap-4 bg-gradient-to-r from-cyan-900/60 to-blue-900/60 border-2 border-cyan-400/50 rounded-xl px-6 py-4 shadow-lg shadow-cyan-500/20">
                    <div className="bg-gradient-to-br from-cyan-500 to-blue-500 p-2 rounded-lg shadow-lg shadow-cyan-500/50">
                      <FileText className="w-6 h-6 text-white" />
                    </div>
                    <div className="text-left">
                      <div className="text-cyan-100 mb-1">{selectedFile.name}</div>
                      <div className="text-cyan-400 text-sm flex items-center gap-2">
                        <CheckCircle className="w-4 h-4" />
                        Sẵn sàng phân tích
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <>
                  <p className="text-slate-300 mb-3 text-lg">
                    Kéo thả file hợp đồng vào đây
                  </p>
                  <p className="text-slate-500 mb-6">
                    hoặc
                  </p>
                </>
              )}
              
              <button
                onClick={() => fileInputRef.current?.click()}
                className="px-8 py-3.5 bg-gradient-to-r from-slate-700 to-slate-800 text-slate-200 rounded-xl hover:from-slate-600 hover:to-slate-700 transition-all duration-300 shadow-lg hover:shadow-xl hover:-translate-y-0.5 border border-slate-600"
              >
                {selectedFile ? 'Chọn file khác' : 'Chọn file từ máy tính'}
              </button>
              
              <p className="text-slate-500 mt-6">
                Hỗ trợ: PDF, DOC, DOCX, TXT • Tối đa 10MB
              </p>
            </div>
          </div>

          {selectedFile && (
            <div className="mt-8 flex justify-center animate-fade-in">
              <button
                onClick={handleAnalyze}
                disabled={isAnalyzing}
                className="group relative px-10 py-4 bg-gradient-to-r from-cyan-500 via-blue-500 to-pink-500 text-white rounded-xl hover:from-cyan-400 hover:via-blue-400 hover:to-pink-400 transition-all duration-300 shadow-2xl shadow-pink-500/50 hover:shadow-cyan-500/50 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-3 text-lg overflow-hidden"
              >
                <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300"></div>
                <div className="relative flex items-center gap-3">
                  {isAnalyzing ? (
                    <>
                      <div className="w-6 h-6 border-3 border-white border-t-transparent rounded-full animate-spin" />
                      Đang phân tích hợp đồng...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-6 h-6" />
                      Bắt đầu phân tích với AI
                    </>
                  )}
                </div>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Enhanced Info Section */}
      <div className="mt-12 bg-gradient-to-r from-slate-900/80 to-slate-800/80 backdrop-blur-xl border-2 border-cyan-500/30 rounded-2xl p-8 shadow-xl shadow-cyan-500/10">
        <h3 className="text-cyan-100 mb-5 flex items-center gap-3 text-xl">
          <div className="bg-gradient-to-br from-cyan-500 to-blue-500 p-2 rounded-lg shadow-lg shadow-cyan-500/50">
            <Scale className="w-6 h-6 text-white" />
          </div>
          Quy trình phân tích RAG
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex items-start gap-3 group">
            <div className="bg-gradient-to-br from-cyan-500 to-blue-500 text-white w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 shadow-lg shadow-cyan-500/50 group-hover:scale-110 transition-transform">1</div>
            <p className="text-slate-300 leading-relaxed">Đọc và trích xuất các điều khoản trong hợp đồng bằng AI</p>
          </div>
          <div className="flex items-start gap-3 group">
            <div className="bg-gradient-to-br from-purple-500 to-pink-500 text-white w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 shadow-lg shadow-purple-500/50 group-hover:scale-110 transition-transform">2</div>
            <p className="text-slate-300 leading-relaxed">So sánh với cơ sở dữ liệu pháp luật (RAG Vector Database)</p>
          </div>
          <div className="flex items-start gap-3 group">
            <div className="bg-gradient-to-br from-pink-500 to-rose-500 text-white w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 shadow-lg shadow-pink-500/50 group-hover:scale-110 transition-transform">3</div>
            <p className="text-slate-300 leading-relaxed">Phát hiện và cảnh báo các điều khoản vi phạm hoặc rủi ro</p>
          </div>
          <div className="flex items-start gap-3 group">
            <div className="bg-gradient-to-br from-orange-500 to-red-500 text-white w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 shadow-lg shadow-orange-500/50 group-hover:scale-110 transition-transform">4</div>
            <p className="text-slate-300 leading-relaxed">Đưa ra khuyến nghị dựa trên quy định pháp luật hiện hành</p>
          </div>
        </div>
      </div>
    </div>
  );
}