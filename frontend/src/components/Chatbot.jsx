import { useState, useRef, useEffect } from 'react';
import { Send, X, Bot, User, Loader2, Maximize2, Minimize2, Sparkles } from 'lucide-react';

const STORAGE_KEY = 'legal-ai-chat-history';

export function Chatbot({ isOpen, onClose, contractText = '', analysisData = null }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  useEffect(() => {
    loadChatHistory();
  }, []);

  useEffect(() => {
    if (messages.length > 0) {
      saveChatHistory(messages);
    }
  }, [messages]);

  const loadChatHistory = async () => {
    try {
      const response = await fetch('/api/chat/history', {
        method: 'GET',
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        if (data.messages && Array.isArray(data.messages) && data.messages.length > 0) {
          setMessages(data.messages);
          return;
        }
      }
    } catch (err) {
      console.log('[ChatHistory] Backend API not available, falling back to localStorage:', err.message);
    }

    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) {
          setMessages(parsed);
        }
      }
    } catch (err) {
      console.error('[ChatHistory] Failed to load from localStorage:', err);
    }
  };

  const saveChatHistory = (msgs) => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(msgs));
    } catch (err) {
      console.error('[ChatHistory] Failed to save to localStorage:', err);
    }
  };

  const clearChatHistory = () => {
    setMessages([]);
    localStorage.removeItem(STORAGE_KEY);
  };

  // Helper: add a friendly assistant error message
  const addFriendlyError = (title, detail) => {
    const msg = {
      role: 'assistant',
      content: `❌ ${title}\n\n${detail}\n\nVui lòng thử lại sau hoặc liên hệ hỗ trợ nếu sự cố tiếp tục.`
    };
    setMessages(prev => [...prev, msg]);
  };

  const sendMessage = async () => {
    const text = input.trim();
    if (!text || isLoading) return;

    const userMessage = { role: 'user', content: text };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Build context
      const context = {};
      if (contractText) {
        context.contract_text = contractText;
      } else if (analysisData) {
        const summaryParts = [];
        if (analysisData.summary) summaryParts.push(`Tóm tắt: ${analysisData.summary}`);
        if (analysisData.aiAnalysis) summaryParts.push(`Phân tích AI: ${analysisData.aiAnalysis}`);
        if (analysisData.issues && analysisData.issues.length > 0) {
          const issueTexts = analysisData.issues.map(i => {
            const sev = i.severity || i.type || 'medium';
            return `[${sev.toUpperCase()}] ${i.title || i}`;
          });
          summaryParts.push(`Các vấn đề phát hiện:\n${issueTexts.join('\n')}`);
        }
        context.contract_text = summaryParts.join('\n\n');
      }

      const response = await fetch('/api/chat/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          message: text,
          history: messages,
          context
        })
      });

      // --- HTTP Error Handling ---
      if (!response.ok) {
        const status = response.status;
        console.error(`[Chat] HTTP Error: ${status} ${response.statusText}`);

        let friendlyTitle = '';
        let friendlyDetail = '';

        if (status === 404) {
          friendlyTitle = 'Không tìm thấy dịch vụ';
          friendlyDetail = 'Endpoint trò chuyện hiện chưa được cấu hình trên máy chủ (lỗi 404).';
        } else if (status === 401 || status === 403) {
          friendlyTitle = 'Phiên đăng nhập hết hạn';
          friendlyDetail = 'Vui lòng đăng nhập lại để tiếp tục sử dụng.';
        } else if (status >= 500) {
          friendlyTitle = 'Máy chủ gặp sự cố';
          friendlyDetail = 'Dịch vụ AI đang bận hoặc gặp lỗi nội bộ. Vui lòng thử lại sau.';
        } else {
          friendlyTitle = 'Đã xảy ra lỗi';
          friendlyDetail = `Máy chủ trả về mã lỗi ${status}. Vui lòng thử lại sau.`;
        }

        addFriendlyError(friendlyTitle, friendlyDetail);
        setIsLoading(false);
        return;
      }

      // --- Try to parse JSON ---
      let data;
      try {
        data = await response.json();
      } catch (parseError) {
        console.error('[Chat] Failed to parse JSON response. Raw response is not JSON.');
        addFriendlyError(
          'Phản hồi không hợp lệ',
          'Máy chủ trả về dữ liệu không đúng định dạng. Vui lòng thử lại.'
        );
        setIsLoading(false);
        return;
      }

      // --- Validate response structure ---
      if (data && data.success && data.reply) {
        const assistantMessage = { role: 'assistant', content: data.reply };
        setMessages(prev => [...prev, assistantMessage]);
      } else {
        // Backend returned JSON but not in expected format
        const errMsg = data?.error || data?.message || '';
        if (errMsg) {
          addFriendlyError('AI gặp sự cố', errMsg);
        } else {
          addFriendlyError(
            'Không nhận được phản hồi hợp lệ',
            'Hệ thống AI không trả về kết quả đúng. Vui lòng thử lại.'
          );
        }
      }
    } catch (error) {
      console.error('========== CHAT ERROR DETAILS ==========');
      console.error('Error name:', error.name);
      console.error('Error message:', error.message);
      console.error('Error cause:', error.cause);

      let friendlyTitle = 'Không thể kết nối máy chủ';
      let friendlyDetail = '';

      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        friendlyDetail = 'Không thể kết nối đến máy chủ. Vui lòng kiểm tra đường truyền mạng hoặc đảm bảo máy chủ đang hoạt động.';
      } else if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
        friendlyDetail = 'Lỗi mạng: không thể kết nối đến máy chủ. Kiểm tra kết nối internet và thử lại.';
      } else if (error.name === 'AbortError') {
        friendlyDetail = 'Yêu cầu bị hủy do quá thời gian chờ. Vui lòng thử lại.';
      } else {
        friendlyDetail = `Đã xảy ra lỗi không xác định: ${error.message}`;
      }

      console.error('==========================================');
      addFriendlyError(friendlyTitle, friendlyDetail);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const cleanMarkdown = (text) => {
    if (typeof text !== 'string') return text || '';
    return text
      .replace(/\*\*/g, '')
      .replace(/\*/g, '')
      .replace(/^#{1,6}\s+/gm, '')
      .replace(/```[\s\S]*?```/g, (match) => match.replace(/```\w*\n?/g, ''))
      .replace(/`([^`]+)`/g, '$1')
      .trim();
  };

  if (!isOpen) return null;

  const sizeClass = isExpanded ? 'w-[600px] h-[700px]' : 'w-[380px] h-[520px]';

  return (
    <div
      className={`fixed bottom-20 right-6 z-50 flex flex-col bg-slate-900 border border-cyan-500/40 rounded-2xl shadow-2xl shadow-cyan-500/20 overflow-hidden transition-all duration-300 ${sizeClass}`}
      style={{ maxHeight: 'calc(100vh - 120px)' }}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-3.5 bg-gradient-to-r from-cyan-600 to-blue-600 flex-shrink-0">
        <div className="flex items-center gap-3">
          <div className="bg-white/20 p-1.5 rounded-lg">
            <Bot className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="text-white font-semibold text-sm">AI Legal Assistant</div>
            <div className="text-cyan-200 text-xs flex items-center gap-1">
              <span className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse"></span>
              Đang hoạt động
            </div>
          </div>
        </div>
        <div className="flex items-center gap-1">
          {messages.length > 0 && (
            <button
              onClick={clearChatHistory}
              className="p-1.5 text-white/60 hover:text-white hover:bg-white/20 rounded-lg transition-colors text-xs"
              title="Xóa lịch sử chat"
            >
              🗑️
            </button>
          )}
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1.5 text-white/80 hover:text-white hover:bg-white/20 rounded-lg transition-colors"
            title={isExpanded ? 'Thu nhỏ' : 'Phóng to'}
          >
            {isExpanded ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
          </button>
          <button
            onClick={onClose}
            className="p-1.5 text-white/80 hover:text-white hover:bg-white/20 rounded-lg transition-colors"
            title="Đóng"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center px-4">
            <div className="bg-gradient-to-br from-cyan-500/20 to-blue-500/20 border border-cyan-500/30 rounded-2xl p-6 mb-4">
              <Sparkles className="w-10 h-10 text-cyan-400 mx-auto mb-3" />
              <h3 className="text-cyan-100 font-semibold mb-2">Chào bạn!</h3>
              <p className="text-slate-400 text-sm leading-relaxed">
                Tôi có thể giúp bạn giải thích các điều khoản trong hợp đồng, trả lời câu hỏi pháp lý, và đưa ra lời khuyên cơ bản.
              </p>
            </div>
            <p className="text-slate-500 text-xs">
              {analysisData
                ? 'Tôi đã có thông tin phân tích hợp đồng của bạn. Hãy hỏi tôi nhé!'
                : 'Hãy đặt câu hỏi về hợp đồng hoặc pháp luật.'}
            </p>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex items-start gap-2.5 animate-fade-in ${
              msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'
            }`}
          >
            <div
              className={`flex-shrink-0 w-8 h-8 rounded-xl flex items-center justify-center ${
                msg.role === 'user'
                  ? 'bg-gradient-to-br from-cyan-500 to-blue-500'
                  : 'bg-gradient-to-br from-purple-500 to-pink-500'
              }`}
            >
              {msg.role === 'user' ? (
                <User className="w-4 h-4 text-white" />
              ) : (
                <Bot className="w-4 h-4 text-white" />
              )}
            </div>
            <div
              className={`max-w-[75%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
                msg.role === 'user'
                  ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white rounded-tr-sm'
                  : 'bg-slate-800 text-slate-200 rounded-tl-sm border border-slate-700/50'
              }`}
            >
              <div className="whitespace-pre-wrap">{cleanMarkdown(msg.content)}</div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex items-start gap-2.5 animate-fade-in">
            <div className="flex-shrink-0 w-8 h-8 rounded-xl flex items-center justify-center bg-gradient-to-br from-purple-500 to-pink-500">
              <Bot className="w-4 h-4 text-white" />
            </div>
            <div className="bg-slate-800 text-slate-300 rounded-2xl rounded-tl-sm border border-slate-700/50 px-4 py-3">
              <div className="flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin text-purple-400" />
                <span className="text-sm">AI đang gõ...</span>
              </div>
              <div className="flex gap-1 mt-2">
                <span className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                <span className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                <span className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="flex-shrink-0 p-3 border-t border-slate-700/50 bg-slate-900/80">
        <div className="flex items-end gap-2">
          <textarea
            ref={inputRef}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Hỏi về hợp đồng..."
            rows={1}
            className="flex-1 bg-slate-800 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-slate-200 placeholder-slate-500 resize-none focus:outline-none focus:border-cyan-500/60 focus:ring-1 focus:ring-cyan-500/30 transition-all"
            style={{ maxHeight: '120px' }}
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim() || isLoading}
            className={`flex-shrink-0 p-2.5 rounded-xl transition-all ${
              input.trim() && !isLoading
                ? 'bg-gradient-to-r from-cyan-500 to-blue-500 text-white shadow-lg shadow-cyan-500/30 hover:from-cyan-400 hover:to-blue-400'
                : 'bg-slate-800 text-slate-500 cursor-not-allowed'
            }`}
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        <p className="text-slate-600 text-[10px] mt-1.5 text-center">
          Câu trả lời chỉ mang tính tham khảo. Hãy tham khảo ý kiến luật sư cho các vấn đề nghiêm trọng.
        </p>
      </div>
    </div>
  );
}
