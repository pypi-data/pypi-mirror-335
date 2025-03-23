# Agents Arcadia

Agents Arcadia は、LLM（Large Language Model）を活用した柔軟なワークフロー自動化フレームワークです。  
本プロジェクトは、LangGraph と langchain-openai を活用し、ユーザーのリクエストに基づいた動的な処理やツール呼び出しを実現します。  
例えば、足し算、割り算（ゼロ除算エラーチェック付き）、数値比較といった基本的なツールを組み合わせることで、記事自動投稿やその他自動化シナリオへの応用が可能です。

## 特徴

- **モジュール化された構成:**  
  `nodes`, `prompts`, `states`, `tools`, `workflows` などのディレクトリに機能が分割され、拡張性と保守性を向上。

- **LLM による動的判断:**  
  langchain-openai を利用して、ユーザーリクエストに応じたツールの呼び出しや分岐処理を自動化します。

- **ツールの統合:**  
  足し算、割り算、数値比較などのツールを標準装備。各ツールは柔軟に拡張可能です。

- **柔軟なワークフロー設計:**  
  LangGraph を用いた分岐やエラーハンドリングを含む複雑なワークフローの構築が容易です。

## インストール

PyPI で公開されている場合、以下のコマンドでインストールできます：

```bash
pip install agentsarcadia
```


## 使い方

以下は、簡単なワークフローを実行する例です。  
この例では、ユーザーリクエストに基づき、LLM の判断を経て適切なツール（例：足し算）が呼び出されます。

```python
import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from agentsarcadia.tools.add import add_tool
from agentsarcadia.tools.divide import divide_tool
from agentsarcadia.tools.compare_num import compare_tool
from agentsarcadia.tool_registry import ToolRegistry
from agentsarcadia.workflows.simple_flow import create_simple_workflow
from agentsarcadia.prompts.calculate import get_prompt

# .envファイルから環境変数を読み込む
load_dotenv()

# ChatOpenAIの初期化（temperature=0 で決定的な応答）
# 環境変数からAPIキーを取得
llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini", api_key=os.environ.get("OPENAI_API_KEY"))

# プロンプトを取得
prompt = get_prompt()

def setup_tools():
    """利用可能なツールを設定する"""
    tool_registry = ToolRegistry()
    tool_registry.register_tools({
        "足し算": add_tool,
        "割り算": divide_tool,
        "数値比較": compare_tool,
    })
    return tool_registry

if __name__ == "__main__":
    # ユーザーからのリクエスト例
    # user_request = "3.11と3.9はどちらが大きいですか？"
    # user_request = "3と5を足してください"
    user_request = "10と3で割り算してください"
    
    # ツールの設定
    tool_registry = setup_tools()
    
    # ワークフローの構築
    graph = create_simple_workflow(llm, prompt, tool_registry)
    graph.get_graph().draw_mermaid_png(output_file_path="workflow.png")
    
    # 初期状態の作成
    initial_state = {"user_request": user_request}
    
    # ワークフローの実行
    result = graph.invoke(initial_state)
    
    print("最終結果:", result["result"])

```

詳細なサンプルコードは、[sample](sample/) ディレクトリ内のコードもご参照ください。

## コントリビューション

本プロジェクトへの貢献を歓迎します。  
1. リポジトリをフォークしてください。  
2. 新しいブランチを作成して変更を加えてください。  
3. プルリクエストを作成し、変更内容の説明を記載してください。  

詳細は [CONTRIBUTING.md](CONTRIBUTING.md) をご確認ください。

## ライセンス

このプロジェクトは [MIT License](LICENSE) の下で公開されています。  