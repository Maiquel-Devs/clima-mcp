# clima-mcp

Servidor MCP em Python (FastMCP) que expõe ferramentas de clima atual para o GitHub Copilot, usando a API Open-Meteo (sem chave de API).

## Ferramentas

- `obter_clima(cidade)`: temperatura, sensação térmica, vento e condição do tempo agora.
- `comparar_cidades(cidade1, cidade2)`: diz qual cidade está mais quente e a diferença em graus.

## Instalação

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Testar com o GitHub Copilot

O arquivo [.vscode/mcp.json](.vscode/mcp.json) configura o servidor com transporte stdio, usando o Python do `.venv` com caminho absoluto. **Ajuste o caminho** se o projeto estiver em outra pasta.

1. Abra a pasta do projeto no VS Code.
2. Abra `.vscode/mcp.json` e clique em **Start** acima do servidor `clima-mcp`.
3. No chat do Copilot, ative o modo **Agent** e pergunte, por exemplo: "Qual o clima em Joinville?" ou "Qual está mais quente, Joinville ou Curitiba?".
