import os
from functools import lru_cache
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from src.workflow.state import AgentState
# PAGEINDEX: Import PageIndex instead of vector_db
from pageindex_rag import get_page_index_retriever
from src.classifier import SVMContractClassifier
from src.resource_config import (
    GROQ_API_KEY, GROQ_MODEL, LLM_TEMPERATURE, 
    LLM_MAX_TOKENS, SVM_MODEL_DIR, DEFAULT_TOP_K
)

# Khởi tạo LLM với GROQ - lazy instantiation
_llm = None
_svm_classifier = None
_retriever = None

def get_llm():
    """Lazy load LLM"""
    global _llm
    if _llm is None:
        _llm = ChatGroq(
            model=GROQ_MODEL, 
            api_key=GROQ_API_KEY, 
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS
        )
    return _llm

def get_svm_classifier():
    """Lazy load SVM Classifier"""
    global _svm_classifier
    if _svm_classifier is None:
        try:
            _svm_classifier = SVMContractClassifier(model_dir=SVM_MODEL_DIR)
            print("✓ SVM Classifier initialized")
        except Exception as e:
            print(f"⚠️ Warning: Could not load SVM Classifier: {e}")
    return _svm_classifier

def get_cached_retriever():
    """
    Lazy load Retriever (singleton)
    PAGEINDEX: Now uses PageIndex tree-based retrieval instead of vector search
    """
    global _retriever
    if _retriever is None:
        print("🌲 Initializing PageIndex retriever...")
        _retriever = get_page_index_retriever()
        print("✓ PageIndex retriever initialized")
    return _retriever

# Cache cho LLM responses
@lru_cache(maxsize=50)
def _cached_llm_call(prompt_hash: str, text_hash: str):
    """Cache LLM responses để tránh gọi lại với cùng input"""
    return None  # Placeholder - actual cache key

# --- NODE 1: SVM CLASSIFICATION (NEW) ---
def svm_classification_node(state: AgentState):
    """
    Nhiệm vụ: Sử dụng SVM để phân loại và đánh giá sơ bộ hợp đồng
    """
    print("--- BƯỚC 1: PHÂN LOẠI VỚI SVM ---")
    contract_text = state['contract_text']
    
    svm_results = {}
    svm_classifier = get_svm_classifier()
    
    if svm_classifier:
        try:
            # Phân tích toàn diện với SVM
            analysis = svm_classifier.analyze_contract(contract_text)
            svm_results = analysis
            
            print(f"  ✓ Loại hợp đồng: {analysis.get('contract_type', {}).get('predicted_type', 'N/A')}")
            print(f"  ✓ Mức độ rủi ro: {analysis.get('risk_assessment', {}).get('predicted_risk', 'N/A')}")
            print(f"  ✓ Vi phạm: {'Có' if analysis.get('violation_check', {}).get('has_violation') else 'Không'}")
        except Exception as e:
            print(f"  ⚠️ SVM classification error: {e}")
            svm_results = {'error': str(e)}
    else:
        print("  ⚠️ SVM Classifier not available, skipping classification")
    
    return {"svm_results": svm_results}

# --- NODE 2: EXTRACTOR ---
def extract_clauses_node(state: AgentState):
    """
    Nhiệm vụ: Đọc hợp đồng thô và tách thành các ý chính cần review.
    """
    print("--- BƯỚC 2: TRÍCH XUẤT ĐIỀU KHOẢN ---")
    contract_text = state['contract_text']
    llm = get_llm()
    
    # Prompt yêu cầu AI tách điều khoản - tối ưu, ngắn gọn
    prompt = ChatPromptTemplate.from_template(
        """Trích xuất các điều khoản quan trọng: Lương, Thưởng, Thời gian làm việc, Chấm dứt hợp đồng, Bảo mật.
        Tách bằng '|||'. Chỉ nội dung, không tiêu đề.
        
        Hợp đồng: {text}
        """
    )
    chain = prompt | llm
    result = chain.invoke({"text": contract_text[:3000]})  # Giới hạn input length
    
    # Tách chuỗi kết quả thành list
    clauses = [c.strip() for c in result.content.split('|||') if c.strip()]
    
    # Nếu có SVM classifier, kiểm tra vi phạm cho từng điều khoản (batch nếu có thể)
    svm_classifier = get_svm_classifier()
    if svm_classifier:
        clauses_with_violations = []
        for clause in clauses[:10]:  # Giới hạn tối đa 10 clauses
            try:
                violation_check = svm_classifier.detect_violation(clause)
                clauses_with_violations.append({
                    'text': clause,
                    'has_violation': violation_check['has_violation'],
                    'violation_probability': violation_check['violation_probability']
                })
            except:
                clauses_with_violations.append({
                    'text': clause,
                    'has_violation': False,
                    'violation_probability': 0.0
                })
        return {"extracted_clauses": clauses, "clauses_with_svm": clauses_with_violations}
    
    return {"extracted_clauses": clauses}

# --- NODE 3: RESEARCHER (WITH PAGEINDEX) ---
def research_node(state: AgentState):
    """
    PAGEINDEX: Uses tree-based search with LLM reasoning instead of vector similarity.
    More transparent and accurate retrieval for complex legal documents.
    """
    print("--- BƯỚC 3: TRA CỨU LUẬT (PAGEINDEX) ---")
    clauses = state['extracted_clauses']
    retriever = get_cached_retriever()
    results = []
    
    # Lấy thông tin SVM nếu có
    clauses_with_svm = state.get('clauses_with_svm', [])
    
    # Giới hạn số clauses để xử lý
    max_clauses = min(len(clauses), 10)
    
    for idx in range(max_clauses):
        clause = clauses[idx]
        
        # PAGEINDEX: Tree-based retrieval with reasoning
        print(f"  🌲 PageIndex searching for clause {idx+1}...")
        docs = retriever.invoke(clause, k=DEFAULT_TOP_K)
        
        # Format legal context from PageIndex results
        legal_context_parts = []
        for doc in docs:
            # PageIndex returns dict with metadata including path
            content = doc.get('content', '')
            metadata = doc.get('metadata', {})
            path = metadata.get('path', 'Unknown')
            title = metadata.get('title', 'Untitled')
            
            legal_context_parts.append(f"[{path}] {title}\n{content[:200]}...")
        
        legal_context = "\n\n".join(legal_context_parts)
        if not legal_context:
            legal_context = "Không tìm thấy quy định pháp luật cụ thể."
        
        result_item = {
            'clause': clause[:300],  # Giới hạn độ dài clause
            'laws': legal_context,
            'retrieval_method': 'pageindex'  # Mark as PageIndex retrieval
        }
        
        # Thêm thông tin SVM violation nếu có
        if idx < len(clauses_with_svm):
            svm_info = clauses_with_svm[idx]
            if svm_info.get('has_violation'):
                result_item['svm_violation'] = {
                    'has_violation': svm_info['has_violation'],
                    'violation_probability': svm_info['violation_probability']
                }
        
        results.append(result_item)
        print(f"  ✓ Đã tra cứu điều khoản {idx+1}/{max_clauses}")
    
    return {"research_results": results}

# --- NODE 4: ANALYST ---
def analyst_node(state: AgentState):
    print("--- BƯỚC 4: PHÂN TÍCH RỦI RO ---")
    research_data = state['research_results']
    svm_results = state.get('svm_results', {})
    llm = get_llm()
    
    # Thêm thông tin SVM classification vào context - ngắn gọn
    context_parts = []
    
    # Thêm tổng quan từ SVM
    if svm_results:
        svm_summary = "=== PHÂN TÍCH SVM ===\n"
        if 'contract_type' in svm_results:
            ct = svm_results['contract_type']
            svm_summary += f"Loại: {ct.get('predicted_type', 'N/A')} ({ct.get('confidence', 0):.0%})\n"
        if 'risk_assessment' in svm_results:
            ra = svm_results['risk_assessment']
            svm_summary += f"Rủi ro: {ra.get('predicted_risk', 'N/A')} ({ra.get('confidence', 0):.0%})\n"
        if 'violation_check' in svm_results:
            vc = svm_results['violation_check']
            has_vio = "Có" if vc.get('has_violation') else "Không"
            svm_summary += f"Vi phạm: {has_vio} ({vc.get('violation_probability', 0):.0%})\n"
        context_parts.append(svm_summary)
    
    # Thêm chi tiết điều khoản - rút gọn
    for idx, item in enumerate(research_data[:5], 1):  # Chỉ lấy 5 điều khoản đầu
        clause_text = item['clause'][:200]  # Giới hạn 200 ký tự
        laws_text = item['laws'][:300]  # Giới hạn 300 ký tự
        
        item_text = f"\nMỤC {idx}:\n- Nội dung: {clause_text}\n"
        
        # Thêm cảnh báo SVM nếu có
        if 'svm_violation' in item:
            svm_vio = item['svm_violation']
            if svm_vio.get('has_violation'):
                item_text += f"  [⚠️ Vi phạm: {svm_vio.get('violation_probability', 0):.0%}]\n"
        
        item_text += f"- Luật: {laws_text}\n"
        context_parts.append(item_text)
    
    context_str = "\n".join(context_parts)
    
    prompt_text = """Bạn là Luật sư AI. Phân tích hợp đồng dựa trên dữ liệu sau (bao gồm SVM và tra cứu luật).

Dữ liệu: {data}

Yêu cầu (ngắn gọn):
1. Tóm tắt loại hợp đồng và rủi ro
2. Phân tích các điều khoản chính
3. Danh sách vi phạm cụ thể
4. Khuyến nghị sửa đổi"""
    
    prompt = ChatPromptTemplate.from_template(prompt_text)
    chain = prompt | llm
    result = chain.invoke({"data": context_str})
    
    return {"final_report": result.content}