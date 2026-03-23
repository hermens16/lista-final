import os
from collections import defaultdict

print("🚀 Gerando SUPER LISTA...")

# 📂 CAMINHOS (ORDEM DE PRIORIDADE)
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

# 🔥 LER TODAS AS PLAYLISTS NA ORDEM
for arquivo in playlists:

    if not os.path.exists(arquivo):
        print(f"⚠️ Não encontrado: {arquivo}")
        continue

    print(f"📂 Processando: {arquivo}")

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

            # 🎯 REMOVE DUPLICADOS COM PRIORIDADE
            if nome not in canais_vistos:
                canais_vistos.add(nome)
                saida_temp.append(extinf)
                saida_temp.append(url)

            i += 2
            continue

        i += 1

# 🎯 ORGANIZAR POR GRUPOS
grupos = defaultdict(list)

i = 0
while i < len(saida_temp):

    extinf = saida_temp[i]
    url = saida_temp[i+1]

    grupo = extrair_grupo(extinf)
    grupos[grupo].append((extinf, url))

    i += 2

# 📊 SUA ORDEM PADRÃO
ORDEM_GRUPOS = [
    "EVENTOS",
    "TV ABERTA",
    "ESPORTES",
    "FILMES",
    "SÉRIES",
    "DOCUMENTÁRIOS",
    "ANIME & TOKUSATSU",
    "DESENHOS 24H"
    "INFANTIL",
    "MÚSICA",
    "NOTÍCIAS",
    "RELIGIOSO",
    "VARIEDADES"
    "RÁDIO"
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

print(f"✅ SUPER LISTA pronta! Total: {len(canais_vistos)} canais")
