import os
from collections import defaultdict, Counter
import subprocess
import unicodedata
import re
import requests

print("🚀 SUPER LISTA FINAL (CORRIGIDO DEFINITIVO)")

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

vistos = set()
contador_nomes = Counter()
contador_grupos = Counter()

# NORMALIZAÇÃO
def normalizar_nome(nome):
    nome = nome.upper().strip()
    nome = unicodedata.normalize('NFKD', nome)
    nome = nome.encode('ASCII', 'ignore').decode()
    return re.sub(r'\s+', ' ', nome)

def extrair_grupo(extinf):
    m = re.search(r'group-title="([^"]+)"', extinf)
    return m.group(1) if m else None

def aplicar_grupo(extinf, grupo):
    if 'group-title="' in extinf:
        return re.sub(r'group-title="[^"]*"', f'group-title="{grupo}"', extinf)
    else:
        return extinf.replace("#EXTINF:-1", f'#EXTINF:-1 group-title="{grupo}"')

def normalizar_grupo(g):
    if not g:
        return "VARIEDADES"

    g_upper = g.upper()

    mapa = {
        "NOTIC": "NOTÍCIAS",
        "NEWS": "NOTÍCIAS",
        "ABERTA": "TV ABERTA",
        "EVENT": "EVENTOS",
        "SPORT": "ESPORTES",
        "FILME": "FILMES",
        "MOVIE": "FILMES",
        "SERIE": "SÉRIES",
        "DOC": "DOCUMENTÁRIOS",
        "ANIME": "ANIME & TOKUSATSU",
        "DESENHO": "DESENHOS 24H",
        "INFANT": "INFANTIL",
        "MUSIC": "MÚSICA",
        "RELIG": "RELIGIOSO"
    }

    for k, v in mapa.items():
        if k in g_upper:
            return v

    return g.strip()  # mantém original corretamente

def ler_playlist(caminho):
    try:
        if caminho.startswith("http"):
            return requests.get(caminho, timeout=15).text.splitlines()
        else:
            with open(caminho, encoding="utf-8", errors="ignore") as f:
                return f.read().splitlines()
    except:
        return []

# LEITURA
for tipo, caminho in playlists:

    linhas = ler_playlist(caminho)

    i = 0
    while i < len(linhas):

        if linhas[i].startswith("#EXTINF"):

            extinf = linhas[i].strip()

            j = i + 1
            while j < len(linhas) and not linhas[j].strip():
                j += 1

            if j >= len(linhas):
                break

            url = linhas[j].strip()

            nome = normalizar_nome(extinf.split(",")[-1])

            contador_nomes[nome] += 1

            if tipo == "H":
                saida_h.append((extinf, url, tipo))
            else:
                saida_fast_full.append((extinf, url, tipo))

                if nome not in vistos:
                    vistos.add(nome)
                    saida_fast.append((extinf, url, tipo))

            i = j + 1
            continue

        i += 1

# REPOSICIONAR
def reposicionar(lista):

    base = []
    extras = []

    for e, u, o in lista:
        nome = normalizar_nome(e.split(",")[-1])

        if o == "PLUTO" and nome in ALVO_FIXO:
            extras.append((e, u, o))
        else:
            base.append((e, u, o))

    resultado = []
    inserido = False

    for item in base:
        resultado.append(item)

        nome = normalizar_nome(item[0].split(",")[-1])

        if nome == "CULTURA" and not inserido:
            resultado.extend(extras)
            inserido = True

    return resultado

# AGRUPAR
def montar(lista):

    grupos = defaultdict(list)

    for e, u, o in lista:

        g_original = extrair_grupo(e)
        g_final = normalizar_grupo(g_original)

        contador_grupos[g_final] += 1

        e = aplicar_grupo(e, g_final)

        grupos[g_final].append((e, u, o))

    if "TV ABERTA" in grupos:
        grupos["TV ABERTA"] = reposicionar(grupos["TV ABERTA"])

    return grupos

ORDEM_FIXA = [
    "TV ABERTA","EVENTOS","ESPORTES","FILMES","SÉRIES",
    "DOCUMENTÁRIOS","ANIME & TOKUSATSU","DESENHOS 24H",
    "INFANTIL","MÚSICA","NOTÍCIAS","RELIGIOSO","VARIEDADES"
]

def salvar(nome, grupos):

    with open(nome, "w", encoding="utf-8") as f:

        f.write("#EXTM3U\n")

        # primeiro ordem fixa
        for g in ORDEM_FIXA:
            if g in grupos:
                for e, u, _ in grupos[g]:
                    f.write(e + "\n")
                    f.write(u + "\n")

        # depois TODOS os outros grupos
        for g in grupos:
            if g not in ORDEM_FIXA:
                for e, u, _ in grupos[g]:
                    f.write(e + "\n")
                    f.write(u + "\n")

# RELATÓRIO
def relatorio(nome, lista):

    duplicados = sum(v-1 for v in contador_nomes.values() if v > 1)

    with open(nome, "w", encoding="utf-8") as f:

        f.write("RELATORIO IPTV\n\n")
        f.write(f"Total canais: {len(lista)}\n")
        f.write(f"Duplicados removidos: {duplicados}\n\n")

        f.write("CANAIS POR GRUPO:\n")
        for g, qtd in contador_grupos.items():
            f.write(f"{g}: {qtd}\n")

# GERAR
lista_dedup = saida_h + saida_fast
lista_full = saida_h + saida_fast_full

g1 = montar(lista_dedup)
g2 = montar(lista_full)

salvar("super_lista.m3u", g1)
salvar("super_lista_full.m3u", g2)

relatorio("relatorio.txt", lista_dedup)

# GIT
subprocess.run("git add .", shell=True)
subprocess.run('git commit -m "fix grupos + relatorio"', shell=True)
subprocess.run("git push", shell=True)

print("✅ AGORA SIM: TUDO CORRIGIDO")
