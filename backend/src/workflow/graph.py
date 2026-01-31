from langgraph.graph import StateGraph, END
from src.workflow.state import AgentState
from src.workflow.nodes import svm_classification_node, extract_clauses_node, research_node, analyst_node

def build_graph():
    """
    Hàm khởi tạo và biên dịch LangGraph với SVM Classification
    """
    # 1. Khởi tạo Graph với State đã định nghĩa
    workflow = StateGraph(AgentState)
    
    # 2. Thêm các Nodes (Các bước xử lý) - Thêm SVM classification
    workflow.add_node("svm_classifier", svm_classification_node)
    workflow.add_node("extractor", extract_clauses_node)
    workflow.add_node("researcher", research_node)
    workflow.add_node("analyst", analyst_node)
    
    # 3. Tạo các cạnh (Edges) - Quy định luồng đi
    # Bắt đầu -> SVM Classification (NEW)
    workflow.set_entry_point("svm_classifier")
    
    # SVM Classification -> Extractor
    workflow.add_edge("svm_classifier", "extractor")
    
    # Extractor -> Researcher
    workflow.add_edge("extractor", "researcher")
    
    # Researcher -> Analyst
    workflow.add_edge("researcher", "analyst")
    
    # Analyst -> Kết thúc
    workflow.add_edge("analyst", END)
    
    # 4. Compile (Biên dịch) thành App để chạy
    app = workflow.compile()
    
    return app