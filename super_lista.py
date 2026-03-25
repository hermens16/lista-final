import os
from collections import defaultdict, Counter
import subprocess
import unicodedata
import re
import requests

print("🚀 SUPER LISTA FINAL + FULL")

playlists = [
    ("H", "https://raw.githubusercontent.com/hermens16/h/refs/heads/main/h.m3u8"),
    ("PLUTO", r"C:\Users\User\Dev\pluto-tv\pluto_br_final.m3u8"),
    ("PLEX", r"C:\Users\User\Dev\plex-tv\playlist_final.m3u"),
    ("SAMSUNG", r"C:\Users\User\Dev\samsung-tv\samsung_final.m3u")
]

ALVO_FIXO = {"TV CULTURA", "CANAL UOL"}

saida_h = []
saida_fast = []
saida_fast_full = []

canais_fast_vistos = set()

# NORMALIZAÇÃO
def normalizar_nome(nome):
    nome = nome.upper().strip()
    nome = unicodedata.normalize('NFKD', nome)
    nome = nome.encode('ASCII', 'ignore').decode()
    nome = re.sub(r'\s+', ' ', nome)
    return nome

def extrair_grupo(extinf):
    if 'group-title="' in extinf:
        return extinf.split('group-title="')[1].split('"')[0]
    return "VARIEDADES"

def normalizar_grupo(g):
    g = g.upper()
    if "ABERTA" in g: return "TV ABERTA"
    if "EVENT" in g: return "EVENTOS"
    if "SPORT" in g: return "ESPORTES"
    if "MOVIE" in g: return "FILMES"
    if "SERIE" in g: return "SÉRIES"
    if "DOC" in g: return "DOCUMENTÁRIOS"
    if "ANIME" in g: return "ANIME & TOKUSATSU"
    if "DESENHO" in g: return "DESENHOS 24H"
    if "INFANT" in g: return "INFANTIL"
    if "MUSIC" in g: return "MÚSICA"
    if "NEWS" in g or "NOTIC" in g: return "NOTÍCIAS"
    return "VARIEDADES"

def ler_playlist(caminho):
    if caminho.startswith("http"):
        return requests.get(caminho).text.splitlines()
    with open(caminho, encoding="utf-8", errors="ignore") as f:
        return f.read().splitlines()

# 🔥 LEITURA
for tipo, caminho in playlists:

    linhas = ler_playlist(caminho)
    i = 0

    while i < len(linhas):

        if linhas[i].strip().startswith("#EXTINF"):

            extinf = linhas[i].strip() + "\n"

            j = i + 1
            while j < len(linhas) and not linhas[j].strip():
                j += 1

            if j >= len(linhas):
                break

            url = linhas[j].strip() + "\n"

            nome = extinf.split(",")[-1].strip()
            nome_norm = normalizar_nome(nome)

            if tipo == "H":
                saida_h.append((extinf, url, tipo))
            else:
                # FULL (sem dedup)
                saida_fast_full.append((extinf, url, tipo))

                # DEDUP
                if nome_norm not in canais_fast_vistos:
                    canais_fast_vistos.add(nome_norm)
                    saida_fast.append((extinf, url, tipo))

            i = j + 1
            continue

        i += 1

# 🔥 REPOSICIONAMENTO CULTURA
def reposicionar_tv_aberta(lista):

    base = []
    pluto_alvo = []

    for extinf, url, origem in lista:
        nome = normalizar_nome(extinf.split(",")[-1])

        if origem == "PLUTO" and nome in ALVO_FIXO:
            pluto_alvo.append((extinf, url, origem))
        else:
            base.append((extinf, url, origem))

    resultado = []
    inserido = False

    for item in base:
        resultado.append(item)

        nome = normalizar_nome(item[0].split(",")[-1])

        if not inserido and nome == "CULTURA":
            resultado.extend(pluto_alvo)
            inserido = True

    if not inserido and pluto_alvo:
        resultado = pluto_alvo + resultado

    return resultado

# AGRUPAMENTO
def montar_lista(saida_total):

    grupos = defaultdict(list)

    for extinf, url, origem in saida_total:

        grupo = normalizar_grupo(extrair_grupo(extinf))
        extinf = re.sub(r'group-title="[^"]*"', f'group-title="{grupo}"', extinf)

        grupos[grupo].append((extinf, url, origem))

    if "TV ABERTA" in grupos:
        grupos["TV ABERTA"] = reposicionar_tv_aberta(grupos["TV ABERTA"])

    return grupos

ORDEM = [
    "TV ABERTA","EVENTOS","ESPORTES","FILMES","SÉRIES",
    "DOCUMENTÁRIOS","ANIME & TOKUSATSU","DESENHOS 24H",
    "INFANTIL","MÚSICA","NOTÍCIAS","VARIEDADES"
]

def salvar(nome, grupos):
    with open(nome, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for g in ORDEM:
            if g in grupos:
                for e,u,_ in grupos[g]:
                    f.write(e)
                    f.write(u)

# 🔥 GERAR AS DUAS LISTAS

lista_dedup = saida_h + saida_fast
lista_full = saida_h + saida_fast_full

grupos_dedup = montar_lista(lista_dedup)
grupos_full = montar_lista(lista_full)

salvar("super_lista.m3u", grupos_dedup)
salvar("super_lista_full.m3u", grupos_full)

# GIT
subprocess.run("git add -A", shell=True)
subprocess.run('git commit -m "gera lista dedup + full corrigido"', shell=True)
subprocess.run("git push", shell=True)

print("✅ GEROU: super_lista.m3u + super_lista_full.m3u")
