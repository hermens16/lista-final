import os
from collections import defaultdict, Counter
import subprocess
import unicodedata
import re
import requests

print("🚀 SUPER LISTA FINAL + CORREÇÃO ABSOLUTA DE GRUPOS")

playlists = [
    ("H", "https://raw.githubusercontent.com/hermens16/h/refs/heads/main/h.m3u8"),
    ("PLUTO", r"C:\Users\User\Dev\pluto-tv\pluto_br_final.m3u8"),
    ("PLEX", r"C:\Users\User\Dev\plex-tv\playlist_final.m3u"),
    ("LG", r"C:\Users\User\Dev\lg-tv\lg_channels_final.m3u"),
    ("SAMSUNG", r"C:\Users\User\Dev\samsung-tv\samsung_final.m3u")
]

saida_dedup = "super_lista.m3u"
saida_full = "super_lista_full.m3u"

relatorio_dedup = "relatorio_dedup.txt"
relatorio_full = "relatorio_full.txt"

saida_h = []
saida_fast = []
saida_fast_full = []

canais_fast_vistos = set()
contador_nomes = Counter()

total_lidos = 0

contador_origem_bruto = defaultdict(int)
contador_origem_final = defaultdict(int)

ALVO_FIXO = {"TV CULTURA", "CANAL UOL"}

# 🔧 NORMALIZAÇÃO
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

# 🔥 CLASSIFICAÇÃO ULTRA INTELIGENTE
def normalizar_grupo(grupo, nome_canal):

    g = grupo.upper()
    n = normalizar_nome(nome_canal)

    # 🔴 CORREÇÃO FORTE (CASOS REAIS)
    if any(x in n for x in [
        "FOLHA POLITICA",
        "AGRO MAIS",
        "TV ASSEMBLEIA",
        "TV CAMARA",
        "TV ALEGO"
    ]):
        return "NOTÍCIAS"

    # 📰 POLÍTICA / INSTITUCIONAL / RURAL
    if any(x in n for x in [
        "POLITICA","POLITICO","CAMARA","SENADO",
        "ASSEMBLEIA","GOVERNO","CONGRESSO",
        "AGRO","RURAL"
    ]):
        return "NOTÍCIAS"

    # 📰 NOTÍCIAS GERAIS
    if any(x in n for x in [
        "NEWS","JORNAL","REPORT","CNN",
        "GLOBO NEWS","GLOBONEWS","BAND NEWS",
        "RECORD NEWS","JP NEWS","JOVEM PAN NEWS",
        "BLOOMBERG"
    ]):
        return "NOTÍCIAS"

    # ⚽ ESPORTES
    if any(x in n for x in [
        "ESPN","SPORT","FUTEBOL","PREMIERE"
    ]):
        return "ESPORTES"

    # ⛪ RELIGIOSO
    if any(x in n for x in [
        "IGREJA","GOSPEL","BIBLIA","VATICANO"
    ]):
        return "RELIGIOSO"

    # 🎬 FILMES
    if any(x in n for x in [
        "CINEMA","FILME","MOVIE"
    ]):
        return "FILMES"

    # 🎵 MÚSICA
    if any(x in n for x in [
        "MUSIC","HITS","MTV"
    ]):
        return "MÚSICA"

    # fallback por grupo original
    if any(x in g for x in ["NEWS","NOTIC","JORNAL"]):
        return "NOTÍCIAS"

    if "EVENT" in g:
        return "EVENTOS"
    if "ABERTA" in g:
        return "TV ABERTA"
    if "SPORT" in g:
        return "ESPORTES"
    if "MOVIE" in g:
        return "FILMES"
    if any(x in g for x in ["SERIE","DRAMA","COMED"]):
        return "SÉRIES"
    if "DOC" in g:
        return "DOCUMENTÁRIOS"
    if "ANIME" in g:
        return "ANIME & TOKUSATSU"
    if "DESENHO" in g or "CARTOON" in g:
        return "DESENHOS 24H"
    if "INFANT" in g or "KIDS" in g:
        return "INFANTIL"
    if "MUSIC" in g:
        return "MÚSICA"
    if "RELIG" in g:
        return "RELIGIOSO"
    if "RADIO" in g:
        return "RÁDIO"
    if "ADULT" in g:
        return "ADULTO"

    return "VARIEDADES"

def ler_playlist(caminho):
    if caminho.startswith("http"):
        try:
            r = requests.get(caminho, timeout=20)
            return r.text.splitlines(keepends=True)
        except:
            print(f"❌ Erro ao baixar: {caminho}")
            return []
    else:
        if not os.path.exists(caminho):
            print(f"⚠️ Não encontrado: {caminho}")
            return []
        with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
            return f.readlines()

# 🔄 PROCESSAMENTO
for tipo, caminho in playlists:

    print(f"📂 Processando: {tipo}")

    linhas = ler_playlist(caminho)
    i = 0

    while i < len(linhas):

        if linhas[i].startswith("#EXTINF"):

            if i + 1 >= len(linhas):
                break

            extinf = linhas[i]
            url = linhas[i+1]

            nome = extinf.split(",")[-1].strip() or "SEM NOME"
            nome_norm = normalizar_nome(nome)

            contador_nomes[nome_norm] += 1
            total_lidos += 1
            contador_origem_bruto[tipo] += 1

            if tipo == "H":
                saida_h.append((extinf, url, tipo))
                contador_origem_final["H"] += 1
            else:
                saida_fast_full.append((extinf, url, tipo))
                contador_origem_final[tipo] += 1

                if nome_norm not in canais_fast_vistos:
                    canais_fast_vistos.add(nome_norm)
                    saida_fast.append((extinf, url, tipo))

            i += 2
            continue

        i += 1

# 📦 AGRUPAMENTO FINAL
def montar_lista(saida_total):

    grupos = defaultdict(list)

    for extinf, url, origem in saida_total:

        nome = extinf.split(",")[-1].strip()
        nome_norm = normalizar_nome(nome)

        grupo = normalizar_grupo(extrair_grupo(extinf), nome)

        # 🔥 FORÇA FINAL (IMPOSSÍVEL ERRAR)
        if any(x in nome_norm for x in [
            "FOLHA POLITICA",
            "AGRO MAIS",
            "TV ASSEMBLEIA",
            "TV CAMARA",
            "TV ALEGO"
        ]):
            grupo = "NOTÍCIAS"

        if 'group-title="' in extinf:
            extinf = re.sub(r'group-title="[^"]*"', f'group-title="{grupo}"', extinf)
        else:
            extinf = extinf.strip() + f' group-title="{grupo}"\n'

        grupos[grupo].append((extinf, url, origem))

    if "TV ABERTA" in grupos:
        grupos["TV ABERTA"] = reposicionar_tv_aberta(grupos["TV ABERTA"])

    return grupos

ORDEM = [
    "TV ABERTA","EVENTOS","ESPORTES","FILMES","SÉRIES",
    "DOCUMENTÁRIOS","ANIME & TOKUSATSU","DESENHOS 24H",
    "INFANTIL","MÚSICA","NOTÍCIAS","RELIGIOSO",
    "VARIEDADES","RÁDIO","ADULTO"
]

def salvar(nome, grupos):
    with open(nome, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for g in ORDEM:
            if g in grupos:
                for e,u,_ in grupos[g]:
                    f.write(e)
                    f.write(u)

# 🎯 GERAR LISTAS
lista_dedup = saida_h + saida_fast
lista_full = saida_h + saida_fast_full

grupos_dedup = montar_lista(lista_dedup)
grupos_full = montar_lista(lista_full)

salvar(saida_dedup, grupos_dedup)
salvar(saida_full, grupos_full)

# 🚀 GIT AUTO
def git(cmd):
    subprocess.run(cmd, shell=True)

git("git add -A")
git('git commit --allow-empty -m "fix grupos definitivo"')
git("git push origin main")

print("✅ LISTA FINAL PERFEITA GERADA")
