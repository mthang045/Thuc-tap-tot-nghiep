import { useState, useEffect } from 'react';
import { FileText, Download, Search, Crown } from 'lucide-react';

const categoryIcons = {
  'Thương mại': '🏪',
  'Nhân sự': '👥',
  'Pháp lý': '⚖️',
  'Bất động sản': '🏠',
  'Tài chính': '💰',
  'Nội bộ': '📋',
};

const defaultTemplates = [
  { template_id: 't1', title: 'Hợp đồng mua bán hàng hóa', category: 'Thương mại', description: 'Mẫu hợp đồng mua bán hàng hóa.', tags: ['thương mại', 'mua bán'] },
  { template_id: 't2', title: 'Hợp đồng lao động', category: 'Nhân sự', description: 'Mẫu HĐLĐ theo Bộ luật Lao động 2019.', tags: ['lao động', 'nhân sự'] },
  { template_id: 't3', title: 'Thỏa thuận bảo mật (NDA)', category: 'Pháp lý', description: 'Thỏa thuận bảo mật thông tin.', tags: ['bảo mật', 'NDA'] },
  { template_id: 't4', title: 'Hợp đồng thuê nhà ở', category: 'Bất động sản', description: 'Mẫu hợp đồng thuê nhà.', tags: ['thuê nhà', 'bất động sản'] },
  { template_id: 't5', title: 'Hợp đồng cung cấp dịch vụ', category: 'Thương mại', description: 'Mẫu hợp đồng dịch vụ.', tags: ['dịch vụ', 'thương mại'] },
  { template_id: 't6', title: 'Hợp đồng giao khoán', category: 'Thương mại', description: 'Mẫu hợp đồng giao khoán.', tags: ['giao khoán', 'thương mại'] },
  { template_id: 't7', title: 'Quy chế nội bộ công ty', category: 'Nội bộ', description: 'Mẫu quy chế nội bộ.', tags: ['nội bộ', 'công ty'] },
  { template_id: 't8', title: 'Giấy ủy quyền', category: 'Pháp lý', description: 'Mẫu giấy ủy quyền.', tags: ['ủy quyền', 'pháp lý'] },
  { template_id: 't9', title: 'Biên bản họp', category: 'Nội bộ', description: 'Mẫu biên bản họp.', tags: ['biên bản', 'nội bộ'] },
  { template_id: 't10', title: 'Hợp đồng vay tiền', category: 'Tài chính', description: 'Mẫu hợp đồng vay tiền.', tags: ['vay tiền', 'tài chính'] },
  { template_id: 't11', title: 'Quyết định bổ nhiệm', category: 'Nhân sự', description: 'Mẫu quyết định bổ nhiệm.', tags: ['bổ nhiệm', 'nhân sự'] },
  { template_id: 't12', title: 'Đơn xin nghỉ việc', category: 'Nhân sự', description: 'Mẫu đơn xin nghỉ việc.', tags: ['nghỉ việc', 'nhân sự'] },
  { template_id: 't13', title: 'Hợp đồng thuê nhà', category: 'Bất động sản', description: 'Mẫu hợp đồng thuê nhà chi tiết.', tags: ['thuê nhà', 'bất động sản'] },
];

export function TemplatesPage({ onNavigate }) {
  const [templates, setTemplates] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('Tất cả');
  const [downloadingId, setDownloadingId] = useState(null);

  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    setIsLoading(true);
    try {
      const resp = await fetch('/v1/templates', { credentials: 'include' });
      if (resp.ok) {
        const data = await resp.json();
        setTemplates(data.templates || []);
      } else {
        setTemplates(defaultTemplates);
      }
    } catch (e) {
      console.error('Failed to load templates', e);
      setTemplates(defaultTemplates);
    } finally {
      setIsLoading(false);
    }
  };

  const downloadTemplate = async (templateId) => {
    setDownloadingId(templateId);
    try {
      const resp = await fetch(`/api/templates/${templateId}/download`, {
        method: 'GET',
        credentials: 'include'
      });

      if (!resp.ok) {
        const text = await resp.text();
        try {
          const err = JSON.parse(text);
          alert('Không thể tải file: ' + (err.error || resp.statusText));
        } catch {
          alert('Không thể tải file: ' + resp.statusText);
        }
        setDownloadingId(null);
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
    } finally {
      setDownloadingId(null);
    }
  };

  const categories = ['Tất cả', 'Thương mại', 'Nhân sự', 'Pháp lý', 'Bất động sản', 'Tài chính', 'Nội bộ'];

  const filteredTemplates = templates.length > 0 ? templates.filter(t => {
    const matchesSearch = searchQuery === '' ||
      (t.title || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
      (t.description || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
      (t.tags || []).some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesCategory = selectedCategory === 'Tất cả' || t.category === selectedCategory;
    return matchesSearch && matchesCategory;
  }) : defaultTemplates.filter(t => {
    const matchesSearch = searchQuery === '' ||
      (t.title || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
      (t.description || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
      (t.tags || []).some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesCategory = selectedCategory === 'Tất cả' || t.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const groupedTemplates = categories.slice(1).reduce((acc, cat) => {
    const catTemplates = filteredTemplates.filter(t => t.category === cat);
    if (catTemplates.length > 0) {
      acc[cat] = catTemplates;
    }
    return acc;
  }, {});

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Header */}
      <div className="text-center mb-10">
        <div className="flex items-center justify-center gap-3 mb-3">
          <div className="bg-gradient-to-br from-amber-400 to-orange-500 p-2 rounded-lg shadow-lg shadow-amber-500/40">
            <Crown className="w-6 h-6 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-pink-400">
            Thư viện mẫu tài liệu Pro
          </h1>
        </div>
        <p className="text-slate-400 max-w-2xl mx-auto">
          Kho mẫu hợp đồng và tài liệu pháp lý thông minh. Tải về và tùy chỉnh theo nhu cầu của bạn.
        </p>
      </div>

      {/* Search & Filter */}
      <div className="flex flex-col sm:flex-row gap-4 mb-8">
        <div className="relative flex-1">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
          <input
            type="text"
            placeholder="Tìm kiếm mẫu tài liệu..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            className="w-full pl-12 pr-4 py-3 bg-slate-800/50 border border-slate-700 rounded-xl text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 focus:ring-2 focus:ring-cyan-500/20 transition-all"
          />
        </div>
        <div className="flex gap-2 flex-wrap">
          {categories.map(cat => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                selectedCategory === cat
                  ? 'bg-cyan-600 text-white shadow-lg shadow-cyan-500/30'
                  : 'bg-slate-800/50 text-slate-400 hover:bg-slate-700 hover:text-slate-200 border border-slate-700'
              }`}
            >
              {cat === 'Tất cả' ? cat : `${categoryIcons[cat] || '📄'} ${cat}`}
            </button>
          ))}
        </div>
      </div>

      {/* Loading State */}
      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin w-10 h-10 border-3 border-cyan-500 border-t-transparent rounded-full"></div>
          <span className="ml-4 text-slate-400">Đang tải danh sách mẫu tài liệu...</span>
        </div>
      ) : (
        <>
          {/* Template Count */}
          <div className="mb-6 text-slate-400 text-sm">
            Tìm thấy <span className="text-cyan-400 font-semibold">{filteredTemplates.length}</span> mẫu tài liệu
          </div>

          {/* Grouped Templates */}
          {Object.entries(groupedTemplates).map(([category, catTemplates]) => (
            <div key={category} className="mb-10">
              <div className="flex items-center gap-3 mb-4">
                <span className="text-2xl">{categoryIcons[category] || '📄'}</span>
                <h2 className="text-xl font-semibold text-cyan-100">{category}</h2>
                <div className="flex-1 h-px bg-slate-700/50"></div>
                <span className="text-slate-500 text-sm">{catTemplates.length} mẫu</span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {catTemplates.map(t => (
                  <div
                    key={t.template_id}
                    className="group bg-slate-900/70 border border-slate-700/50 rounded-xl p-5 hover:border-cyan-500/40 hover:bg-slate-800/60 transition-all"
                  >
                    <div className="flex items-start justify-between gap-3 mb-3">
                      <div className="flex-1 min-w-0">
                        <h3 className="text-slate-100 font-semibold mb-1 group-hover:text-cyan-200 transition-colors line-clamp-2">
                          {t.title || t.name}
                        </h3>
                        <p className="text-slate-400 text-sm leading-relaxed line-clamp-2">
                          {t.description}
                        </p>
                      </div>
                      <button
                        onClick={() => downloadTemplate(t.template_id)}
                        disabled={downloadingId === t.template_id}
                        className="flex-shrink-0 w-10 h-10 bg-cyan-600/20 hover:bg-cyan-500 text-cyan-400 hover:text-white rounded-lg flex items-center justify-center transition-all border border-cyan-500/30 hover:border-cyan-400 disabled:opacity-50"
                        title="Tải về"
                      >
                        {downloadingId === t.template_id ? (
                          <div className="w-4 h-4 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin"></div>
                        ) : (
                          <Download className="w-4 h-4" />
                        )}
                      </button>
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {(t.tags || []).slice(0, 4).map(tag => (
                        <span
                          key={tag}
                          className="px-2 py-0.5 bg-slate-800 text-slate-500 text-xs rounded-full border border-slate-700"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}

          {/* Empty State */}
          {filteredTemplates.length === 0 && (
            <div className="text-center py-20">
              <FileText className="w-16 h-16 text-slate-600 mx-auto mb-4" />
              <h3 className="text-slate-300 text-lg mb-2">Không tìm thấy mẫu tài liệu</h3>
              <p className="text-slate-500">Thử thay đổi từ khóa tìm kiếm hoặc danh mục</p>
            </div>
          )}
        </>
      )}

      {/* Footer Note */}
      <div className="mt-10 pt-6 border-t border-slate-700/50">
        <p className="text-slate-500 text-sm text-center">
          💡 Tất cả mẫu tài liệu chỉ mang tính tham khảo. Vui lòng tham khảo ý kiến luật sư trước khi sử dụng.
        </p>
      </div>
    </div>
  );
}
