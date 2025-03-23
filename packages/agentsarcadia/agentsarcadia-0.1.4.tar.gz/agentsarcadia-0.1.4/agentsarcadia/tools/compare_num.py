
def compare_tool(input_str: str) -> str:
    """
    ツール３：数値比較
    入力例："7,3" → "結果: 最初の数値が大きい"
    """
    try:
        a, b = map(float, input_str.split(","))
        if a > b:
            return "結果: 最初の数値が大きい"
        elif a < b:
            return "結果: 二番目の数値が大きい"
        else:
            return "結果: 両方の数値は等しい"
    except Exception as e:
        return f"エラー: {e}"