from typing import TypedDict


class AgentState(TypedDict):
    """計算ワークフローの状態を表現するクラス"""
    user_request: str  # ユーザーリクエスト
    llm_response: str  # LLMの応答
    tool_name: str  # 使用するツール名
    tool_params: str  # ツールへの入力パラメータ
    result: str  # 処理結果

