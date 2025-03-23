from langchain_core.prompts import ChatPromptTemplate

def get_prompt():
    """計算ワークフロー用のプロンプトテンプレートを取得する"""
    prompt_template = """
あなたは計算を支援するAIアシスタントです。
ユーザーのリクエスト: {user_request}

以下のツールが利用可能です:
- 足し算: 2つの数値を足し算します
- 割り算: 2つの数値で割り算を行います
- 数値比較: 2つの数値を比較します

必ず以下の形式で回答してください。コロン（:）が必須です。
ツール名: パラメータ

例：
足し算: 3, 5
割り算: 10, 2
数値比較: 7, 3

補足説明や余計な文章は含めないでください。
"""
    return ChatPromptTemplate.from_template(prompt_template) 