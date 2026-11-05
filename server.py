"""Servidor MCP de clima atual usando a API gratuita Open-Meteo (sem chave de API)."""

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("clima-mcp")

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
TIMEOUT = 10

# Traduz o código do tempo em uma descrição em português.
CODIGOS_TEMPO = {
    0: "céu limpo",
    1: "predominantemente limpo",
    2: "parcialmente nublado",
    3: "nublado",
    45: "neblina",
    48: "neblina com geada",
    51: "garoa fraca",
    53: "garoa moderada",
    55: "garoa forte",
    56: "garoa congelante fraca",
    57: "garoa congelante forte",
    61: "chuva fraca",
    63: "chuva moderada",
    65: "chuva forte",
    66: "chuva congelante fraca",
    67: "chuva congelante forte",
    71: "neve fraca",
    73: "neve moderada",
    75: "neve forte",
    77: "grãos de neve",
    80: "pancadas de chuva fracas",
    81: "pancadas de chuva moderadas",
    82: "pancadas de chuva fortes",
    85: "pancadas de neve fracas",
    86: "pancadas de neve fortes",
    95: "tempestade",
    96: "tempestade com granizo fraco",
    99: "tempestade com granizo forte",
}


# Erro com mensagem amigável para mostrar ao usuário.
class ErroClima(Exception):
    """Erro com mensagem amigável para o usuário."""


# Pega os dados brutos da API do clima.
def buscar_clima(cidade: str) -> dict:
    """Busca o clima atual de uma cidade. Lança ErroClima se algo der errado."""
    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            geo = client.get(
                GEOCODING_URL,
                params={"name": cidade, "count": 1, "language": "pt"},
            )
            geo.raise_for_status()
            resultados = geo.json().get("results")
            if not resultados:
                raise ErroClima(f"Cidade '{cidade}' não encontrada.")
            local = resultados[0]

            resp = client.get(
                FORECAST_URL,
                params={
                    "latitude": local["latitude"],
                    "longitude": local["longitude"],
                    "current": "temperature_2m,apparent_temperature,weather_code,wind_speed_10m",
                },
            )
            resp.raise_for_status()
            atual = resp.json()["current"]
    except httpx.TimeoutException:
        raise ErroClima("Tempo esgotado ao consultar o serviço de clima. Tente novamente.")
    except httpx.HTTPError as e:
        raise ErroClima(f"Erro de rede ao consultar o serviço de clima: {e}")
    except (KeyError, ValueError):
        raise ErroClima("Resposta inesperada do serviço de clima.")

    return {
        "nome": local["name"],
        "pais": local.get("country", ""),
        "temperatura": atual["temperature_2m"],
        "sensacao": atual["apparent_temperature"],
        "vento": atual["wind_speed_10m"],
        "condicao": CODIGOS_TEMPO.get(atual["weather_code"], "condição desconhecida"),
    }


# Ferramenta: transforma os dados em texto para o usuário.
@mcp.tool()
def obter_clima(cidade: str) -> str:
    """Obtém o clima atual (agora) de uma cidade.

    Use quando o usuário perguntar sobre temperatura, sensação térmica, vento
    ou condição do tempo atual em uma cidade específica.

    Args:
        cidade: Nome da cidade, por exemplo "Joinville" ou "São Paulo".
    """
    try:
        c = buscar_clima(cidade)
    except ErroClima as e:
        return str(e)

    local = f"{c['nome']}, {c['pais']}" if c["pais"] else c["nome"]
    return (
        f"Clima atual em {local}:\n"
        f"- Temperatura: {c['temperatura']}°C\n"
        f"- Sensação térmica: {c['sensacao']}°C\n"
        f"- Vento: {c['vento']} km/h\n"
        f"- Condição: {c['condicao']}"
    )


# Ferramenta: compara a temperatura de duas cidades.
@mcp.tool()
def comparar_cidades(cidade1: str, cidade2: str) -> str:
    """Compara o clima atual de duas cidades e diz qual está mais quente agora.

    Use quando o usuário quiser comparar temperaturas entre duas cidades
    ou saber qual delas está mais quente ou mais fria neste momento.

    Args:
        cidade1: Nome da primeira cidade, por exemplo "Joinville".
        cidade2: Nome da segunda cidade, por exemplo "Curitiba".
    """
    try:
        c1 = buscar_clima(cidade1)
        c2 = buscar_clima(cidade2)
    except ErroClima as e:
        return str(e)

    diferenca = round(abs(c1["temperatura"] - c2["temperatura"]), 1)
    resumo = (
        f"{c1['nome']}: {c1['temperatura']}°C ({c1['condicao']}) | "
        f"{c2['nome']}: {c2['temperatura']}°C ({c2['condicao']})"
    )
    if diferenca == 0:
        return f"{c1['nome']} e {c2['nome']} estão com a mesma temperatura agora.\n{resumo}"

    mais_quente, mais_fria = (c1, c2) if c1["temperatura"] > c2["temperatura"] else (c2, c1)
    return (
        f"{mais_quente['nome']} está mais quente que {mais_fria['nome']} "
        f"em {diferenca}°C.\n{resumo}"
    )


if __name__ == "__main__":
    mcp.run()
