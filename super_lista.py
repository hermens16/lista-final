import os
from collections import defaultdict
import subprocess

print("🚀 Gerando SUPER LISTA...")

playlists = [
    r"C:\Users\User\Dev\h\h.m3u8",
    r"C:\Users\User\Dev\pluto-tv\pluto_br_final.m3u8",
    r"C:\Users\User\Dev\plex-tv\playlist_final.m3u",
    r"C:\Users\User\Dev\samsung-tv\samsung_final.m3u"
]

saida_arquivo = "super_lista.m3u"

canais_vistos = set()
saida_temp = []

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

# 🔥 LER PLAYLISTS
for arquivo in playlists:

    if not os.path.exists(arquivo):
        continue

    with open(arquivo, "r", encoding="utf-8", errors="ignore") as f:
        linhas = f.readlines()

    i = 0

    while i < len(linhas):

        if linhas[i].startswith("#EXTINF"):

            if i + 1 >= len(linhas):
                break

            extinf = linhas[i]
            url = linhas[i+1]

            nome = extinf.split(",")[-1].strip().upper()

            if nome not in canais_vistos:
                canais_vistos.add(nome)
                saida_temp.append((extinf, url))

            i += 2
            continue

        i += 1

# 🎯 AGRUPAR
grupos = defaultdict(list)

for extinf, url in saida_temp:

    grupo_original = extrair_grupo(extinf)
    grupo = normalizar_grupo(grupo_original)

    # 🔥 NÃO QUEBRA EXTINF — só substitui grupo se existir
    if 'group-title="' in extinf:
        extinf = extinf.split('group-title="')[0] + f'group-title="{grupo}",' + extinf.split(",")[-1]
    else:
        extinf = extinf.strip() + f' group-title="{grupo}"\n'

    grupos[grupo].append((extinf, url))

# 📊 ORDEM
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

# 🔥 GIT PUSH (INVISÍVEL)
try:
    subprocess.run("git add .", shell=True)
    subprocess.run('git commit --allow-empty -m "Atualização automática super lista"', shell=True)
    subprocess.run("git push", shell=True)
except:
    pass

print(f"✅ SUPER LISTA pronta! Total: {len(canais_vistos)} canais")
