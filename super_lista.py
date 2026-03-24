import os
from collections import defaultdict
import subprocess
import unicodedata
import re

print("🚀 SUPER LISTA (H 100% INTACTA)")

playlists = [
    ("H", r"C:\Users\User\Dev\h\h.m3u8"),
    ("PLUTO", r"C:\Users\User\Dev\pluto-tv\pluto_br_final.m3u8"),
    ("PLEX", r"C:\Users\User\Dev\plex-tv\playlist_final.m3u"),
    ("SAMSUNG", r"C:\Users\User\Dev\samsung-tv\samsung_final.m3u")
]

saida_arquivo = "super_lista.m3u"

canais_fast_vistos = set()
saida_temp = []

total_lidos = 0
total_final = 0

# 🧠 NORMALIZAÇÃO
def normalizar_nome(nome):
    nome = nome.upper().strip()
    nome = unicodedata.normalize('NFKD', nome)
    nome = nome.encode('ASCII', 'ignore').decode()
    nome = re.sub(r'[^A-Z0-9 ]', '', nome)
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

# 🚫 filtro só para FAST
def canal_valido(nome):
    lixo = ["INFORMACOES EM BREVE", "EM BREVE", ""]
    return nome not in lixo

# 🔥 PROCESSAMENTO
for tipo, arquivo in playlists:

    if not os.path.exists(arquivo):
        print(f"⚠️ Não encontrado: {arquivo}")
        continue

    print(f"📂 {tipo}: {arquivo}")

    with open(arquivo, "r", encoding="utf-8", errors="ignore") as f:
        linhas = f.readlines()

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

            # 🟢 REGRA H (INTACTA)
            if tipo == "H":
                saida_temp.append((extinf, url))
                total_final += 1

            # 🔵 REGRA FAST
            else:

                # remove lixo só aqui
                if not canal_valido(nome_norm):
                    i += 2
                    continue

                # deduplicação só FAST
                if nome_norm not in canais_fast_vistos:
                    canais_fast_vistos.add(nome_norm)
                    saida_temp.append((extinf, url))
                    total_final += 1

            i += 2
            continue

        i += 1

# 🎯 AGRUPAR
grupos = defaultdict(list)

for extinf, url in saida_temp:

    grupo_original = extrair_grupo(extinf)
    grupo = normalizar_grupo(grupo_original)

    if 'group-title="' in extinf:
        inicio = extinf.split('group-title="')[0]
        nome = extinf.split(",")[-1]
        extinf = f'{inicio}group-title="{grupo}",{nome}'
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

# 🔥 GIT PUSH
try:
    subprocess.run("git add .", shell=True)
    subprocess.run('git commit --allow-empty -m "Super lista corrigida (H 100% intacta)"', shell=True)
    subprocess.run("git push", shell=True)
except:
    pass

print("\n📊 RELATÓRIO FINAL:")
print(f"➡️ Canais lidos: {total_lidos}")
print(f"➡️ Canais finais: {total_final}")
print(f"➡️ Removidos (apenas FAST): {total_lidos - total_final}")
