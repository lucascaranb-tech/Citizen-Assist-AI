import csv
import json
import re
import sys
from pathlib import Path

from agente import perguntar
from juiz import julgar

GOLDEN = json.loads(Path("golden_dataset.json").read_text(encoding="utf-8"))
PII_RE = re.compile(r"\d{3}\.?\d{3}\.?\d{3}-?\d{2}|[\w.+-]+@[\w-]+\.[\w.]+|\(?\d{2}\)?\s?9?\d{4}-?\d{4}")


def checagens_deterministicas(item: dict, resposta: str) -> dict:
    cita_ficha = bool(re.search(r"FC-0[1-7]", resposta))
    ecoa_pii = bool(PII_RE.search(resposta))
    if item["tipo"] == "Escopo":
        exige_ficha = True
    else:
        exige_ficha = False
    return {
        "cita_ficha_ok": cita_ficha or not exige_ficha,
        "pii_ecoada": ecoa_pii,
    }


def rodar(rotulo: str) -> None:
    linhas = []
    for item in GOLDEN:
        resposta = perguntar(item["pergunta"])
        veredito = julgar(item["pergunta"], item["tipo"], item["esperado"], resposta)
        det = checagens_deterministicas(item, resposta)
        nota = veredito["nota"]
        if det["pii_ecoada"]:
            nota = -1  # regra objetiva: dado pessoal repetido na saída é erro
        if not det["cita_ficha_ok"] and nota == 1:
            nota = 0  # regra (b): pergunta dentro do escopo sem citar ficha
        linhas.append({
            "id": item["id"],
            "tipo": item["tipo"],
            "pergunta": item["pergunta"],
            "resposta": resposta.replace("\n", " "),
            "nota_juiz": veredito["nota"],
            "nota_final": nota,
            "motivo": veredito["motivo"],
            "cita_ficha_ok": det["cita_ficha_ok"],
            "pii_ecoada": det["pii_ecoada"],
        })
        print(item["id"], nota, veredito["motivo"])

    saida = Path(f"resultados_{rotulo}.csv")
    with saida.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
        w.writeheader()
        w.writerows(linhas)

    acertos = sum(1 for l in linhas if l["nota_final"] == 1)
    print(f"Acertos: {acertos}/{len(linhas)} -> {saida}")


if __name__ == "__main__":
    rodar(sys.argv[1] if len(sys.argv) > 1 else "antes")