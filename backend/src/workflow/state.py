from typing import TypedDict, List, Dict, Any

class AgentState(TypedDict):
    """
    Cấu trúc dữ liệu chia sẻ giữa các bước (Nodes) trong Graph.
    Giống như một cái giỏ hàng, đi qua mỗi node sẽ được bỏ thêm dữ liệu vào.
    """
    # Đầu vào: Toàn bộ văn bản hợp đồng
    contract_text: str
    
    # Bước 0: Kết quả phân loại SVM (NEW!)
    svm_results: Dict[str, Any]
    
    # Bước 1: Danh sách các điều khoản đã tách ra
    extracted_clauses: List[str]
    
    # Bước 2: Kết quả tra cứu luật cho từng điều khoản
    # Cấu trúc: [{'clause': '...', 'laws': '...'}, ...]
    research_results: List[Dict[str, Any]]
    
    # Bước 3: Báo cáo cuối cùng (Markdown)
    final_report: str