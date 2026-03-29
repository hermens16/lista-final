import os
import subprocess
import unicodedata
import re
import requests

print("🚀 GERANDO SUPER LISTA (DEDUP + FULL + AJUSTE CULTURA OK)")

playlists = [
    ("H", "https://raw.githubusercontent.com/hermens16/h/refs/heads/main/h.m3u8"),
    ("PLUTO", r"C:\Users\User\Dev\pluto-tv\pluto_br_final.m3u8"),
    ("PLEX", r"C:\Users\User\Dev\plex-tv\playlist_final.m3u"),
    ("LG", r"C:\Users\User\Dev\lg-tv\lg_channels_final.m3u"),
    ("SAMSUNG", r"C:\Users\User\Dev\samsung-tv\samsung_final.m3u")
]

saida_dedup = "super_lista.m3u"
saida_full = "super_lista_full.m3u"

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

# 🔥 AJUSTE SEGURO CULTURA
def ajustar_cultura(lista):

    def get_nome(item):
        return normalizar_nome(item[0].split(",")[-1])

    nomes = [get_nome(i) for i in lista]

    # tenta localizar
    try:
        idx_cultura = nomes.index("CULTURA")
        idx_globo = nomes.index("GLOBOPLAY NOVELAS")
    except ValueError:
        return lista  # não mexe se não encontrar

    # remove extras da lista
    lista_limpa = []
    extras = []

    for item in lista:
        nome = get_nome(item)

        if nome in ["TV CULTURA", "CANAL UOL"]:
            extras.append(item)
        else:
            lista_limpa.append(item)

    # recalcula posições
    nomes_limpos = [get_nome(i) for i in lista_limpa]

    try:
        idx_cultura = nomes_limpos.index("CULTURA")
        idx_globo = nomes_limpos.index("GLOBOPLAY NOVELAS")
    except ValueError:
        return lista

    # posição correta
    if idx_cultura < idx_globo:
        pos = idx_cultura + 1
    else:
        pos = idx_globo

    # insere exatamente no meio
    nova_lista = (
        lista_limpa[:pos] +
        extras +
        lista_limpa[pos:]
    )

    return nova_lista

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
        canais = ajustar_cultura(canais)

    lista_full.extend(canais)

# 🔥 DEDUP
lista_dedup = []

# H
lista_h = [(e, u) for _, e, u in dados.get("H", [])]
lista_h = ajustar_cultura(lista_h)

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

# 💾 SALVAR
def salvar(nome, lista):
    with open(nome, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for extinf, url in lista:
            f.write(extinf)
            f.write(url)

salvar(saida_dedup, lista_dedup)
salvar(saida_full, lista_full)

# 🚀 GIT
def git(cmd):
    subprocess.run(cmd, shell=True)

git("git add -A")
git('git commit --allow-empty -m "dedup + full + cultura fix final"')
git("git push origin main")

print("✅ GERADO COM SUCESSO:")
print("✔ super_lista.m3u")
print("✔ super_lista_full.m3u")
