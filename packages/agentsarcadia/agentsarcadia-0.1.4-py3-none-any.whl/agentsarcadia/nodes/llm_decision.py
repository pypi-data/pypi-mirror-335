def llm_decision_node(llm, prompt_template):
    """LLMを使用して次のアクションを決定するノード関数を生成"""
    
    def _decision_node(state):
        """LLMで次のアクションを決定"""
        try:
            # デバッグ情報
            print(f"リクエスト: {state.get('user_request', 'リクエストなし')}")
            
            # ユーザーのリクエストをプロンプトに挿入
            formatted_prompt = prompt_template.format_messages(
                user_request=state.get("user_request", "")
            )
            
            # LLMに問い合わせ
            response = llm.invoke(formatted_prompt)
            
            # 応答を状態に保存
            response_content = response.content
            print(f"LLM応答: {response_content}")
            state["llm_response"] = response_content
            
        except Exception as e:
            print(f"LLM判断ノードでエラー発生: {str(e)}")
            state["llm_response"] = "エラー: LLM呼び出し中に問題が発生しました"
        
        return state
    
    return _decision_node