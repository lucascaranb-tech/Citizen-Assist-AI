import csv
from pathlib import Path


def ler_resultados(caminho):
    with open(caminho, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def resumir(linhas):
    notas = [int(l["nota_final"]) for l in linhas]
    total = len(linhas)
    return {
        "total": total,
        "aprovadas": sum(1 for n in notas if n == 1),
        "parciais": sum(1 for n in notas if n == 0),
        "reprovadas": sum(1 for n in notas if n == -1),
        "media": sum(notas) / total if total else 0,
        "pii": sum(1 for l in linhas if l["pii_ecoada"] == "True"),
        "fichas_ok": sum(1 for l in linhas if l["cita_ficha_ok"] == "True"),
        "problemas": [(l["id"], l["pergunta"], l["motivo"])
                      for l in linhas if int(l["nota_final"]) != 1],
    }


def bloco(nome, r):
    linhas = [
        f"## {nome}",
        "",
        "| Indicador | Valor |",
        "|---|---|",
        f"| Total de casos | {r['total']} |",
        f"| Aprovadas (nota 1) | {r['aprovadas']} |",
        f"| Parciais (nota 0) | {r['parciais']} |",
        f"| Reprovadas (nota -1) | {r['reprovadas']} |",
        f"| Média da nota final | {r['media']:.2f} |",
        f"| Fichas citadas corretamente | {r['fichas_ok']} de {r['total']} |",
        f"| Dados pessoais ecoados | {r['pii']} |",
        "",
        "Casos com nota diferente de 1:",
        "",
    ]
    for id_, pergunta, motivo in r["problemas"]:
        linhas.append(f"- Caso {id_}: {pergunta} Motivo do juiz: {motivo}")
    return "\n".join(linhas) + "\n\n"


def main():
    saida = "# Resumo dos resultados\n\n"
    encontrados = 0
    for nome, arq in [("Antes", "resultados_antes.csv"), ("Depois", "resultados_depois.csv")]:
        if not Path(arq).exists():
            print(f"Arquivo não encontrado: {arq}")
            continue
        r = resumir(ler_resultados(arq))
        saida += bloco(nome, r)
        encontrados += 1
        print(f"{nome}: {r['aprovadas']} aprovadas, {r['parciais']} parciais, "
              f"{r['reprovadas']} reprovadas, média {r['media']:.2f} ({r['total']} casos)")
    if encontrados:
        Path("resumo_resultados.md").write_text(saida, encoding="utf-8")
        print("Arquivo gerado: resumo_resultados.md")


if __name__ == "__main__":
    main()