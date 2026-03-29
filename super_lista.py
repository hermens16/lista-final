import os
import subprocess
import unicodedata
import re
import requests

print("🚀 GERANDO SUPER LISTA (DEDUP + FULL + POSIÇÃO CULTURA OK)")

playlists = [
    ("H", "https://raw.githubusercontent.com/hermens16/h/refs/heads/main/h.m3u8"),
    ("PLUTO", r"C:\Users\User\Dev\pluto-tv\pluto_br_final.m3u8"),
    ("PLEX", r"C:\Users\User\Dev\plex-tv\playlist_final.m3u"),
    ("LG", r"C:\Users\User\Dev\lg-tv\lg_channels_final.m3u"),
    ("SAMSUNG", r"C:\Users\User\Dev\samsung-tv\samsung_final.m3u")
]

saida_dedup = "super_lista.m3u"
saida_full = "super_lista_full.m3u"

ALVO_FIXO = {"TV CULTURA", "CANAL UOL"}

# NORMALIZAÇÃO
def normalizar_nome(nome):
    nome = nome.upper().strip()
    nome = unicodedata.normalize('NFKD', nome)
    nome = nome.encode('ASCII', 'ignore').decode()
    nome = re.sub(r'\s+', ' ', nome)
    return nome

# LEITURA
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

# 🔥 SUA FUNÇÃO ORIGINAL (SEM ALTERAÇÃO)
def reposicionar_tv_aberta(lista):

    base = []
    pluto_alvo = []

    for extinf, url in lista:
        nome = normalizar_nome(extinf.split(",")[-1])

        # 👇 força pegar esses canais independente da origem
        if nome in ALVO_FIXO:
            pluto_alvo.append((extinf, url))
        else:
            base.append((extinf, url))

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

# PROCESSAMENTO
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

            canais.append((nome_norm, extinf, url))
            i += 2
        else:
            i += 1

    dados[tipo] = canais

# 🔥 FULL
lista_full = []

for tipo in ["H", "PLUTO", "PLEX", "LG", "SAMSUNG"]:
    canais = [(e, u) for _, e, u in dados.get(tipo, [])]

    if tipo == "H":
        canais = reposicionar_tv_aberta(canais)

    lista_full.extend(canais)

# 🔥 DEDUP
lista_dedup = []

# H
lista_h = [(e, u) for _, e, u in dados.get("H", [])]
lista_h = reposicionar_tv_aberta(lista_h)

vistos = set()

for extinf, url in lista_h:
    nome = normalizar_nome(extinf.split(",")[-1])
    lista_dedup.append((extinf, url))
    vistos.add(nome)

# PLUTO
pluto_nomes = set()

for nome, extinf, url in dados.get("PLUTO", []):
    lista_dedup.append((extinf, url))
    pluto_nomes.add(nome)
    vistos.add(nome)

# PLEX
plex_nomes = set()

for nome, extinf, url in dados.get("PLEX", []):
    if nome not in pluto_nomes:
        lista_dedup.append((extinf, url))
        plex_nomes.add(nome)
        vistos.add(nome)

# LG
lg_nomes = set()

for nome, extinf, url in dados.get("LG", []):
    if nome not in pluto_nomes and nome not in plex_nomes:
        lista_dedup.append((extinf, url))
        lg_nomes.add(nome)
        vistos.add(nome)

# SAMSUNG
for nome, extinf, url in dados.get("SAMSUNG", []):
    if nome not in pluto_nomes and nome not in plex_nomes and nome not in lg_nomes:
        lista_dedup.append((extinf, url))
        vistos.add(nome)

# SALVAR
def salvar(nome, lista):
    with open(nome, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for extinf, url in lista:
            f.write(extinf)
            f.write(url)

salvar(saida_dedup, lista_dedup)
salvar(saida_full, lista_full)

# GIT
def git(cmd):
    subprocess.run(cmd, shell=True)

git("git add -A")
git('git commit --allow-empty -m "fix final cultura posicao correta"')
git("git push origin main")

print("✅ FINALIZADO COM SUCESSO")
