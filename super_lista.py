
import os
from collections import defaultdict, Counter
import subprocess
import unicodedata
import re
import requests

print("🚀 SUPER LISTA FINAL + COMÉDIA + CULTURA (SEM QUEBRAR FULL)")

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
# 🎯 DETECÇÃO DE COMÉDIA (SUAVE)
# ==============================
def eh_comedia(nome):
    nome = normalizar_nome(nome)

    palavras = [
        "CHAVES","CHAPOLIN","MR BEAN",
        "TODO MUNDO ODEIA O CHRIS",
        "THE OFFICE","BROOKLYN",
        "SOUTH PARK","SIMPSONS","FAMILY GUY",
        "PORTA DOS FUNDOS","HUMOR","COMEDY",
        "PEGADINHA","FAIL"
    ]

    return any(p in nome for p in palavras)

# ==============================
# 🔥 REPOSICIONAMENTO CULTURA
# ==============================
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

            # 🔥 AJUSTE DE COMÉDIA (SEM QUEBRAR GRUPO ORIGINAL)
            grupo = extrair_grupo(extinf)

            if eh_comedia(nome) and "COMEDIA" not in normalizar_nome(grupo):
                extinf = re.sub(r'group-title="[^"]*"', 'group-title="COMÉDIA"', extinf)

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

# ==============================
# AGRUPAMENTO
# ==============================
def montar_lista(saida_total):

    grupos = defaultdict(list)

    for extinf, url, origem in saida_total:

        grupo = extrair_grupo(extinf).upper().strip()

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
    "COMÉDIA","DOCUMENTÁRIOS","ANIME & TOKUSATSU",
    "DESENHOS 24H","INFANTIL","MÚSICA","NOTÍCIAS",
    "RELIGIOSO","VARIEDADES","RÁDIO","ADULTO"
]

def salvar(nome, grupos):
    with open(nome, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")

        usados = set()

        for g in ORDEM:
            if g in grupos:
                usados.add(g)
                for e,u,_ in grupos[g]:
                    f.write(e)
                    f.write(u)

        for g in sorted(grupos):
            if g not in usados:
                for e,u,_ in grupos[g]:
                    f.write(e)
                    f.write(u)

# ==============================
# LISTAS
# ==============================
lista_dedup = saida_h + saida_fast
lista_full = saida_h + saida_fast_full

grupos_dedup = montar_lista(lista_dedup)
grupos_full = montar_lista(lista_full)

salvar(saida_dedup, grupos_dedup)
salvar(saida_full, grupos_full)

# ==============================
# GIT
# ==============================
def git(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(r.stdout)
    print(r.stderr)

git("git add -A")
git('git commit --allow-empty -m "fix: comedia sem quebrar full + cultura ok"')
git("git push origin main")

print("✅ FINAL PERFEITO (DEDUP + FULL OK)")
