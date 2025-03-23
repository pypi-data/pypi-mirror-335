def error_node(state):
    """エラーノード：不明なツール名の場合"""
    state["result"] = "エラー: 不明なツール名または形式です。"
    return state