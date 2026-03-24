import os
from collections import defaultdict
import subprocess
import unicodedata
import re
import requests

print("🚀 SUPER LISTA (H VIA GITHUB + FAST CONTROLADO)")

# 🔥 PLAYLISTS (H AGORA VIA GITHUB)
playlists = [
    ("H", "https://raw.githubusercontent.com/hermens16/h/refs/heads/main/h.m3u8"),
    ("PLUTO", r"C:\Users\User\Dev\pluto-tv\pluto_br_final.m3u8"),
    ("PLEX", r"C:\Users\User\Dev\plex-tv\playlist_final.m3u"),
    ("SAMSUNG", r"C:\Users\User\Dev\samsung-tv\samsung_final.m3u")
]

saida_arquivo = "super_lista.m3u"

# 🔥 separação
saida_h = []
saida_fast = []

canais_fast_vistos = set()

total_lidos = 0
total_final = 0

# 🧠 NORMALIZAÇÃO
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

def normalizar_grupo(grupo):
    g = grupo.strip().upper()

    if "EVENT" in g:
        return "EVENTOS"
    if "ABERTA" in g:
        return "TV ABERTA"
    if "SPORT" in g or "ESPORTE" in g:
        return "ESPORTES"
    if "MOVIE" in g or "FILME" in g:
        return "FILMES"
    if any(x in g for x in ["SERIE", "SÉRIE", "DRAMA", "COMED"]):
        return "SÉRIES"
    if "DOC" in g:
        return "DOCUMENTÁRIOS"
    if "ANIME" in g:
        return "ANIME & TOKUSATSU"
    if "DESENHO" in g or "CARTOON" in g:
        return "DESENHOS 24H"
    if "INFANT" in g or "KIDS" in g:
        return "INFANTIL"
    if "MUSIC" in g or "MÚSICA" in g:
        return "MÚSICA"
    if "NEWS" in g or "NOTIC" in g:
        return "NOTÍCIAS"
    if "RELIG" in g:
        return "RELIGIOSO"
    if "RADIO" in g:
        return "RÁDIO"
    if "ADULT" in g:
        return "ADULTO"

    return "VARIEDADES"

def canal_valido(nome):
    lixo = ["INFORMACOES EM BREVE", "EM BREVE", ""]
    return nome not in lixo

# 🔥 FUNÇÃO UNIVERSAL DE LEITURA (LOCAL + URL)
def ler_playlist(caminho):
    if caminho.startswith("http"):
        try:
            response = requests.get(caminho, timeout=20)
            response.raise_for_status()
            return response.text.splitlines(keepends=True)
        except Exception as e:
            print(f"❌ Erro ao baixar {caminho}: {e}")
            return []
    else:
        if not os.path.exists(caminho):
            print(f"⚠️ Não encontrado: {caminho}")
            return []
        with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
            return f.readlines()

# 🔥 PROCESSAMENTO
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

            nome_original = extinf.split(",")[-1].strip()
            nome_norm = normalizar_nome(nome_original)

            total_lidos += 1

            # 🟢 H = NÃO REMOVE NADA
            if tipo == "H":
                saida_h.append((extinf, url))
                total_final += 1

            # 🔵 FAST (Pluto, Plex, Samsung)
            else:
                if not canal_valido(nome_norm):
                    i += 2
                    continue

                if nome_norm not in canais_fast_vistos:
                    canais_fast_vistos.add(nome_norm)
                    saida_fast.append((extinf, url))
                    total_final += 1

            i += 2
            continue

        i += 1

# 🔥 ORDEM GARANTIDA
saida_temp = saida_h + saida_fast

# 🎯 AGRUPAR
grupos = defaultdict(list)

for extinf, url in saida_temp:

    grupo_original = extrair_grupo(extinf)
    grupo = normalizar_grupo(grupo_original)

    # 🔥 NÃO QUEBRA EXTINF
    if 'group-title="' in extinf:
        extinf = re.sub(r'group-title="[^"]*"', f'group-title="{grupo}"', extinf)
    else:
        extinf = extinf.strip() + f' group-title="{grupo}"\n'

    grupos[grupo].append((extinf, url))

# 📊 ORDEM FINAL
ORDEM_GRUPOS = [
    "EVENTOS",
    "TV ABERTA",
    "ESPORTES",
    "FILMES",
    "SÉRIES",
    "DOCUMENTÁRIOS",
    "ANIME & TOKUSATSU",
    "DESENHOS 24H",
    "INFANTIL",
    "MÚSICA",
    "NOTÍCIAS",
    "RELIGIOSO",
    "VARIEDADES",
    "RÁDIO",
    "ADULTO"
]

# 💾 SALVAR
with open(saida_arquivo, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")

    for grupo in ORDEM_GRUPOS:
        if grupo in grupos:
            for extinf, url in grupos[grupo]:
                f.write(extinf)
                f.write(url)

    # fallback
    for grupo in grupos:
        if grupo not in ORDEM_GRUPOS:
            for extinf, url in grupos[grupo]:
                f.write(extinf)
                f.write(url)

# 🔥 GIT PUSH COM LOG
def git(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(r.stdout)
    print(r.stderr)

try:
    git("git add -A")
    git('git commit --allow-empty -m "Super lista auto update (H via GitHub + FAST dedup)"')
    git("git push origin main")
except Exception as e:
    print(f"❌ Erro no git: {e}")

print("\n📊 RELATÓRIO FINAL:")
print(f"➡️ Canais lidos: {total_lidos}")
print(f"➡️ Canais finais: {total_final}")
print(f"➡️ Removidos (apenas FAST): {total_lidos - total_final}")
