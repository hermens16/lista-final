import os
from collections import defaultdict, Counter
import subprocess
import unicodedata
import re
import requests

print("🚀 SUPER LISTA FINAL (SEM ALTERAR GRUPOS)")

playlists = [
    ("H", "https://raw.githubusercontent.com/hermens16/h/refs/heads/main/h.m3u8"),
    ("PLUTO", r"C:\Users\User\Dev\pluto-tv\pluto_br_final.m3u8"),
    ("PLEX", r"C:\Users\User\Dev\plex-tv\playlist_final.m3u"),
    ("LG", r"C:\Users\User\Dev\lg-tv\lg_channels_final.m3u"),
    ("SAMSUNG", r"C:\Users\User\Dev\samsung-tv\samsung_final.m3u")
]

saida_final = "super_lista.m3u"

saida_h = []
saida_outros = []

canais_vistos = set()
contador_nomes = Counter()

# 🔧 NORMALIZAÇÃO
def normalizar_nome(nome):
    nome = nome.upper().strip()
    nome = unicodedata.normalize('NFKD', nome)
    nome = nome.encode('ASCII', 'ignore').decode()
    nome = re.sub(r'\s+', ' ', nome)
    return nome

# 📥 LEITURA
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

            if tipo == "H":
                # H entra direto (prioridade máxima)
                saida_h.append((extinf, url))
                canais_vistos.add(nome_norm)
            else:
                # deduplicação respeitando H
                if nome_norm not in canais_vistos:
                    canais_vistos.add(nome_norm)
                    saida_outros.append((extinf, url))

            i += 2
            continue

        i += 1

# 🔥 AJUSTE ESPECÍFICO (TV CULTURA / CANAL UOL)
def ajustar_cultura(lista):

    resultado = []
    cultura = None
    extras = []

    for extinf, url in lista:
        nome = normalizar_nome(extinf.split(",")[-1])

        if nome == "CULTURA":
            cultura = (extinf, url)
        elif nome in ["TV CULTURA", "CANAL UOL"]:
            extras.append((extinf, url))
        else:
            resultado.append((extinf, url))

    final = []
    inserido = False

    for item in resultado:
        final.append(item)

        nome = normalizar_nome(item[0].split(",")[-1])

        if not inserido and nome == "CULTURA":
            if cultura:
                final.append(cultura)
            final.extend(extras)
            inserido = True

    if not inserido:
        final = extras + final

    return final

# 🧠 JUNTA LISTA FINAL
lista_final = saida_h + saida_outros

# aplica ajuste cultura
lista_final = ajustar_cultura(lista_final)

# 💾 SALVAR
with open(saida_final, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    for extinf, url in lista_final:
        f.write(extinf)
        f.write(url)

# 🚀 GIT
def git(cmd):
    subprocess.run(cmd, shell=True)

git("git add -A")
git('git commit --allow-empty -m "ordem correta sem alterar grupos"')
git("git push origin main")

print("✅ FINALIZADO PERFEITAMENTE")
