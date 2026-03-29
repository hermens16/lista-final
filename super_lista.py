import os
from collections import defaultdict, Counter
import subprocess
import unicodedata
import re
import requests

print("🚀 SUPER LISTA FINAL + CLASSIFICAÇÃO INTELIGENTE + CULTURA FIX")

playlists = [
    ("H", "https://raw.githubusercontent.com/hermens16/h/refs/heads/main/h.m3u8"),
    ("PLUTO", r"C:\Users\User\Dev\pluto-tv\pluto_br_final.m3u8"),
    ("PLEX", r"C:\Users\User\Dev\plex-tv\playlist_final.m3u"),
    ("LG", r"C:\Users\User\Dev\lg-tv\lg_channels_final.m3u"),
    ("SAMSUNG", r"C:\Users\User\Dev\samsung-tv\samsung_final.m3u")
]

saida_dedup = "super_lista.m3u"
saida_full = "super_lista_full.m3u"

# ==============================
# NORMALIZAÇÃO
# ==============================
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

# ==============================
# 🎯 CLASSIFICADOR INTELIGENTE
# ==============================
def classificar_canal(nome, grupo_original):

    nome = normalizar_nome(nome)

    # NÃO MEXE NA COMÉDIA ORIGINAL (corrige seu bug)
    if "COMEDIA" in grupo_original.upper() or "COMÉDIA" in grupo_original.upper():
        return "COMÉDIA"

    # COMÉDIA por nome
    if any(x in nome for x in [
        "COMEDY","HUMOR","PEGADINHA","STAND UP","FAIL","LAUGH",
        "CHAVES","CHAPOLIN","MR BEAN","TRAPALHOES",
        "TODO MUNDO ODEIA O CHRIS","THE OFFICE","BROOKLYN",
        "SOUTH PARK","OS SIMPSONS","FAMILY GUY"
    ]):
        return "COMÉDIA"

    # NOTÍCIAS
    if any(x in nome for x in [
        "CNN","GLOBO NEWS","GLOBONEWS","BAND NEWS",
        "RECORD NEWS","JP NEWS","JOVEM PAN"
    ]):
        return "NOTÍCIAS"

    # ESPORTES
    if any(x in nome for x in [
        "SPORT","ESPN","FUTEBOL","NBA","UFC"
    ]):
        return "ESPORTES"

    # FILMES
    if any(x in nome for x in [
        "CINE","MOVIE","FILME","TELECINE","HBO"
    ]):
        return "FILMES"

    return grupo_original.upper()

# ==============================
# 🔥 REPOSICIONAMENTO CULTURA / UOL
# ==============================
ALVO_FIXO = {"TV CULTURA", "CANAL UOL"}

def reposicionar_tv_aberta(lista):

    base = []
    alvo = []

    for extinf, url, origem in lista:
        nome = normalizar_nome(extinf.split(",")[-1])

        if nome in ALVO_FIXO:
            alvo.append((extinf, url, origem))
        else:
            base.append((extinf, url, origem))

    resultado = []
    inserido = False

    for item in base:
        resultado.append(item)

        nome = normalizar_nome(item[0].split(",")[-1])

        # 🔥 INSERE LOGO APÓS QUALQUER "CULTURA"
        if not inserido and "CULTURA" in nome:
            resultado.extend(alvo)
            inserido = True

    if not inserido:
        resultado = alvo + resultado

    return resultado

# ==============================
# LEITURA
# ==============================
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

# ==============================
# PROCESSAMENTO
# ==============================
dados = {}

for tipo, caminho in playlists:
    print(f"📂 {tipo}")
    linhas = ler_playlist(caminho)

    canais = []
    i = 0

    while i < len(linhas):
        if linhas[i].startswith("#EXTINF") and i + 1 < len(linhas):

            extinf = linhas[i]
            url = linhas[i+1]

            nome = extinf.split(",")[-1].strip()
            nome_norm = normalizar_nome(nome)

            canais.append((nome_norm, extinf, url, tipo))
            i += 2
        else:
            i += 1

    dados[tipo] = canais

# ==============================
# DEDUP
# ==============================
lista_dedup = []
vistos = set()

for tipo in ["H", "PLUTO", "PLEX", "LG", "SAMSUNG"]:
    for nome, extinf, url, origem in dados.get(tipo, []):
        if nome not in vistos:
            lista_dedup.append((extinf, url, origem))
            vistos.add(nome)

# FULL
lista_full = []
for tipo in ["H", "PLUTO", "PLEX", "LG", "SAMSUNG"]:
    lista_full.extend([(e,u,t) for _,e,u,t in dados.get(tipo, [])])

# ==============================
# AGRUPAMENTO
# ==============================
def montar_lista(lista):

    grupos = defaultdict(list)

    for extinf, url, origem in lista:

        nome = extinf.split(",")[-1].strip()
        grupo_original = extrair_grupo(extinf)

        grupo = classificar_canal(nome, grupo_original)

        if 'group-title="' in extinf:
            extinf = re.sub(r'group-title="[^"]*"', f'group-title="{grupo}"', extinf)
        else:
            extinf = extinf.strip() + f' group-title="{grupo}"\n'

        grupos[grupo].append((extinf, url, origem))

    if "TV ABERTA" in grupos:
        grupos["TV ABERTA"] = reposicionar_tv_aberta(grupos["TV ABERTA"])

    return grupos

ORDEM = [
    "TV ABERTA","ESPORTES","FILMES","SÉRIES",
    "DOCUMENTÁRIOS","INFANTIL","COMÉDIA",
    "NOTÍCIAS","VARIEDADES"
]

def salvar(nome, grupos):
    with open(nome, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for g in ORDEM:
            if g in grupos:
                for e,u,_ in grupos[g]:
                    f.write(e)
                    f.write(u)

# ==============================
# EXECUÇÃO
# ==============================
grupos_dedup = montar_lista(lista_dedup)
grupos_full = montar_lista(lista_full)

salvar(saida_dedup, grupos_dedup)
salvar(saida_full, grupos_full)

# ==============================
# GIT (CORRIGIDO)
# ==============================
def git(cmd):
    subprocess.run(cmd, shell=True)

git("git add -A")
git('git commit -m "fix: comedia + cultura + uol + ordem corrigida"')
git("git push origin main")

print("✅ FINALIZADO COM SUCESSO")
