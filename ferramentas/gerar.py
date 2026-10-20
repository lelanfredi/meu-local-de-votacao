"""Gera o index.html a partir da lista de seções alteradas do TSE.

Uso:
  python3 ferramentas/gerar.py ferramentas/dados/tse_AAAA-MM-DD_HHMM.csv "20/10/2026 às 6h27"

O CSV tem as colunas UF;MUNICIPIO;ZONA;SECAO;ELEITORES;LOCAL_1T;LOCAL_2T,
copiadas do painel do TSE (sig.tse.jus.br > Eleitorado > Capilaridade > Seções alteradas).
O mapa (contorno dos estados) é mantido; a posição de cada cidade vem da tabela
de municípios do IBGE em ferramentas/dados.
"""
import csv
import json
import re
import sys
import unicodedata
from pathlib import Path

AQUI = Path(__file__).parent
SITE = AQUI.parent / "index.html"

# Projeção do mapa (equirretangular), ajustada sobre as cidades do mapa original
AX, BX, AY, BY = 25.252286270091666, 1873.7271518472753, -26.143216208069973, 141.1747433741313


def chave(nome):
    s = unicodedata.normalize("NFD", nome).encode("ascii", "ignore").decode().upper()
    return " ".join(re.sub(r"[^A-Z0-9 ]", " ", s).split())


def coordenadas():
    ufs = {r["codigo_uf"]: r["uf"] for r in csv.DictReader(open(AQUI / "dados/estados_ibge.csv", encoding="utf-8-sig"))}
    out = {}
    for r in csv.DictReader(open(AQUI / "dados/municipios_ibge.csv", encoding="utf-8")):
        lon, lat = float(r["longitude"]), float(r["latitude"])
        out[(ufs[r["codigo_uf"]], chave(r["nome"]))] = [round(AX * lon + BX, 1), round(AY * lat + BY, 1)]
    return out


def main(arquivo, quando):
    linhas = list(csv.DictReader(open(arquivo, encoding="utf-8"), delimiter=";"))
    html = SITE.read_text(encoding="utf-8")
    ini = html.index("const RAW = ") + len("const RAW = ")
    antigo, fim = json.JSONDecoder().raw_decode(html[ini:])

    textos, idx = [], {}
    def i(s):
        s = " ".join(s.split())
        if s not in idx:
            idx[s] = len(textos)
            textos.append(s)
        return idx[s]

    geo = coordenadas()
    xy, faltam = {}, set()
    regs = []
    for l in linhas:
        uf, mun = l["UF"].strip(), l["MUNICIPIO"].strip()
        r = [i(uf), i(mun), int(l["ZONA"]), int(l["SECAO"]), i(l["LOCAL_1T"]), i(l["LOCAL_2T"]), int(l["ELEITORES"])]
        regs.append(r)
        p = geo.get((uf, chave(mun)))
        if p:
            xy[f"{r[0]}|{r[1]}"] = p
        else:
            faltam.add(f"{mun} ({uf})")

    novo = {"s": textos, "r": regs, "geo": {"states": antigo["geo"]["states"], "h": antigo["geo"]["h"], "xy": xy}}
    html = html[:ini] + json.dumps(novo, ensure_ascii=False, separators=(",", ":")) + html[ini + fim:]

    html, n1 = re.subn(r"(<b>Dados oficiais do TSE</b>, )[^<]*?\.(?= <span id=\"t-total\">)",
                       rf"\g<1>atualizados em {quando}.", html)
    html, n2 = re.subn(r"consultada em [^<]*? no (<a href=\"https://sig\.tse\.jus\.br/\")",
                       rf"consultada em {quando} no \1", html)
    if n1 != 1 or n2 != 1:
        sys.exit(f"Não achei os textos de data para trocar ({n1}, {n2}).")

    SITE.write_text(html, encoding="utf-8")
    cidades = len({(r[0], r[1]) for r in regs})
    print(f"{len(regs)} seções, {cidades} cidades, {sum(r[6] for r in regs)} eleitores.")
    if faltam:
        print("Sem posição no mapa:", ", ".join(sorted(faltam)))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
