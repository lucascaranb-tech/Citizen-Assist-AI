import re
import unicodedata
from pathlib import Path

DATA_VERIFICACAO = "01/10/2026"
PASTA = Path(__file__).parent / "fichas"

# A FC-07 não tem linha de palavras-chave: temas complementares
TEMAS_FC07 = [r"sabado", r"atendimento", r"libras", r"interprete", r"terceir",
              r"procuracao", r"taxa", r"pagamento", r"privacidade", r"agend", r"horario"]


def normaliza(texto: str) -> str:
    texto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def carregar_fichas() -> dict:
    fichas = {}
    for arq in sorted(PASTA.glob("FC-*.md")):
        texto = arq.read_text(encoding="utf-8")
        m = re.search(r"\*\*Palavras-chave:\*\*(.+)", texto)
        kws = [normaliza(k).strip() for k in m.group(1).split(",")] if m else []
        fichas[arq.name[:5]] = {"texto": texto, "kws": [k for k in kws if k]}
    return fichas


def buscar(pergunta: str, fichas: dict, k: int = 2) -> list[str]:
    q = normaliza(pergunta)
    pontos = []
    for codigo, f in fichas.items():
        if codigo == "FC-07":
            if any(re.search(t, q) for t in TEMAS_FC07):
                pontos.append((1, codigo))
            continue
        p = sum(1 for kw in f["kws"] if re.search(rf"\b{re.escape(kw)}\b", q))
        if p:
            pontos.append((p, codigo))
    pontos.sort(reverse=True)
    return [c for _, c in pontos[:k]]