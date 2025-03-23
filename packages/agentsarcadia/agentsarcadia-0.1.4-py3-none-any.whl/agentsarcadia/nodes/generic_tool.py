

def create_generic_tool_node(tool_registry):
    """ツールレジストリを使用して汎用ツールノードを作成する関数"""
    
    def _generic_tool_node(state):
        """汎用ツールノード：tool_nameに基づいて適切なツールを実行"""
        tool_name = state.get("tool_name", "").lower()
        tool_params = state.get("tool_params", "")
        
        print("="*50)
        print(f"generic_tool_node: ツール名 = '{tool_name}', パラメータ = '{tool_params}'")
        
        tool_function = tool_registry.get_tool(tool_name)
        if tool_function:
            print(f"ツール '{tool_name}' を実行します")
            result = tool_function(tool_params)
            print(f"ツール実行結果: {result}")
            state["result"] = result
        else:
            error_msg = f"エラー: 不明なツール名「{tool_name}」です。"
            print(error_msg)
            state["result"] = error_msg
        
        print("="*50)
        return state
    
    return _generic_tool_node