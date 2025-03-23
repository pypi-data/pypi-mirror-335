from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda

from lib.states.base import AgentState
from lib.nodes.start import start_node
from lib.nodes.llm_decision import llm_decision_node
from lib.nodes.parse_response import parse_response_node
from lib.nodes.error import error_node
from lib.nodes.generic_tool import create_generic_tool_node
from lib.tool_registry import ToolRegistry
from lib.tool_router import create_tool_router


def create_simple_workflow(llm, prompt, tool_registry=None):
    """ツールレジストリを使用してワークフローを構築する"""
    # デフォルトのツールレジストリを作成
    if tool_registry is None:
        tool_registry = ToolRegistry()
    
    # StateGraphの初期化
    workflow = StateGraph(AgentState)
    
    # 動的に作成されたノード関数
    generic_tool_node = create_generic_tool_node(tool_registry)
    tool_router = create_tool_router(tool_registry)
    
    # ノードの追加
    workflow.add_node("start_node", RunnableLambda(start_node))
    workflow.add_node("llm_decision_node", RunnableLambda(llm_decision_node(llm, prompt)))
    workflow.add_node("parse_response_node", RunnableLambda(parse_response_node))
    workflow.add_node("generic_tool_node", RunnableLambda(generic_tool_node))
    workflow.add_node("error_node", RunnableLambda(error_node))
    
    # エントリーポイントの設定
    workflow.set_entry_point("start_node")
    
    # エッジの定義
    workflow.add_edge("start_node", "llm_decision_node")
    workflow.add_edge("llm_decision_node", "parse_response_node")
    
    # 条件付きエッジの定義
    workflow.add_conditional_edges(
        "parse_response_node",
        tool_router,
        {
            "generic_tool_node": "generic_tool_node",
            "error_node": "error_node"
        }
    )
    
    # 各ツールノードからの終了
    workflow.add_edge("generic_tool_node", END)
    workflow.add_edge("error_node", END)
    
    return workflow.compile() 