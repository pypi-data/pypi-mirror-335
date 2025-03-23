
def divide_tool(input_str: str) -> str:
    """
    ツール２：割り算
    入力例："10,2" → "結果: 10 / 2 = 5.0"
    """
    try:
        a, b = map(float, input_str.split(","))
        if b == 0:
            return "エラー: ゼロによる割り算はできません"
        return f"結果: {a} / {b} = {a/b}"
    except Exception as e:
        return f"エラー: {e}"