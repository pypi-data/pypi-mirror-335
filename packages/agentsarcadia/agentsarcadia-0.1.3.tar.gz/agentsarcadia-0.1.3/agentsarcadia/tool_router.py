

def create_tool_router(tool_registry):
    """ツールレジストリを使用してルーターを作成する関数"""
    
    def _tool_router(state):
        """ツールルーター：適切なツールノードへの分岐を決定"""
        tool_name = state.get("tool_name", "").lower()
        
        print("="*50)
        print(f"ツールルーター: tool_name = '{tool_name}'")
        print(f"利用可能なツール: {list(tool_registry.tools.keys())}")
        
        if tool_registry.has_tool(tool_name):
            print(f"ツール '{tool_name}' が見つかりました")
            print("generic_tool_nodeに分岐します")
            print("="*50)
            return "generic_tool_node"
        else:
            print(f"ツール '{tool_name}' は登録されていません")
            print("error_nodeに分岐します")
            print("="*50)
            return "error_node"
    
    return _tool_router