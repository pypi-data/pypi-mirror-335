

class ToolRegistry:
    """ツールレジストリ：使用可能なツールを管理するクラス"""
    
    def __init__(self):
        self.tools = {}
    
    def register_tool(self, name, function):
        """ツールを登録する"""
        self.tools[name.lower()] = function
    
    def register_tools(self, tool_dict):
        """複数のツールを一度に登録する"""
        for name, function in tool_dict.items():
            self.register_tool(name, function)
    
    def get_tool(self, name):
        """ツール名から関数を取得する"""
        return self.tools.get(name.lower())
    
    def has_tool(self, name):
        """ツールが存在するか確認する"""
        return name.lower() in self.tools