import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from agentsarcadia.tools.add import add_tool
from agentsarcadia.tools.divide import divide_tool
from agentsarcadia.tools.compare_num import compare_tool
from agentsarcadia.tool_registry import ToolRegistry
from agentsarcadia.workflows.simple_flow import create_simple_workflow
from agentsarcadia.prompts.calculate import get_prompt

# .envファイルから環境変数を読み込む
load_dotenv()

# ChatOpenAIの初期化（temperature=0 で決定的な応答）
# 環境変数からAPIキーを取得
llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini", api_key=os.environ.get("OPENAI_API_KEY"))

# プロンプトを取得
prompt = get_prompt()

def setup_tools():
    """利用可能なツールを設定する"""
    tool_registry = ToolRegistry()
    tool_registry.register_tools({
        "足し算": add_tool,
        "割り算": divide_tool,
        "数値比較": compare_tool,
    })
    return tool_registry

if __name__ == "__main__":
    # ユーザーからのリクエスト例
    # user_request = "3.11と3.9はどちらが大きいですか？"
    # user_request = "3と5を足してください"
    user_request = "10と3で割り算してください"
    
    # ツールの設定
    tool_registry = setup_tools()
    
    # ワークフローの構築
    graph = create_simple_workflow(llm, prompt, tool_registry)
    graph.get_graph().draw_mermaid_png(output_file_path="workflow.png")
    
    # 初期状態の作成
    initial_state = {"user_request": user_request}
    
    # ワークフローの実行
    result = graph.invoke(initial_state)
    
    print("最終結果:", result["result"])