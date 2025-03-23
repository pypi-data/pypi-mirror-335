


def add_tool(input_str: str) -> str:
    """
    ツール１：足し算
    入力例："3,5" → "結果: 3 + 5 = 8.0"
    """
    try:
        a, b = map(float, input_str.split(","))
        return f"結果: {a} + {b} = {a+b}"
    except Exception as e:
        return f"エラー: {e}"
