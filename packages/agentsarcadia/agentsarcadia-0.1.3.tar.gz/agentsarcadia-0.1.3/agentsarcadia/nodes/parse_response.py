def parse_response_node(state):
    """LLMの応答を解析してツール名とパラメータを抽出"""
    
    # デバッグ情報
    print("="*50)
    print("parse_response_node 開始")
    print(f"状態キー: {list(state.keys())}")
    
    # llm_responseがない場合のフォールバック処理
    if "llm_response" not in state:
        print("警告: llm_responseキーが見つかりません")
        state["llm_response"] = "エラー: レスポンスが取得できませんでした"
    
    decision = state["llm_response"]
    print(f"解析する応答: '{decision}'")
    
    # 以下は元のコードを維持
    # ツール名と引数を抽出するロジック
    try:
        # 余分な空白や改行を削除してから処理
        cleaned_decision = decision.strip()
        print(f"クリーニング後の応答: '{cleaned_decision}'")
        
        # コロンで分割（最初のコロンのみ）
        parts = cleaned_decision.split(':', 1)
        print(f"分割結果: {parts}")
        
        if len(parts) != 2:
            print("エラー: コロンで区切られた形式ではありません")
            raise ValueError("不正な形式です（コロン区切りではありません）")
        
        tool_name = parts[0].strip()
        tool_params = parts[1].strip()
        
        print(f"抽出したツール名: '{tool_name}'")
        print(f"抽出したパラメータ: '{tool_params}'")
        
        state["tool_name"] = tool_name
        state["tool_params"] = tool_params
        print("状態を更新しました")
        
    except Exception as e:
        print(f"応答解析エラー: {str(e)}")
        state["error"] = f"応答の解析に失敗しました: {str(e)}"
        state["tool_name"] = "unknown"
        state["tool_params"] = ""
    
    print("parse_response_node 終了")
    print("="*50)
    return state