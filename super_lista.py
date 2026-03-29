import os
import subprocess
import unicodedata
import re
import requests

print("🚀 SUPER LISTA FINAL (COM AJUSTES FINOS)")

playlists = [
    ("H", "https://raw.githubusercontent.com/hermens16/h/refs/heads/main/h.m3u8"),
    ("PLUTO", r"C:\Users\User\Dev\pluto-tv\pluto_br_final.m3u8"),
    ("PLEX", r"C:\Users\User\Dev\plex-tv\playlist_final.m3u"),
    ("LG", r"C:\Users\User\Dev\lg-tv\lg_channels_final.m3u"),
    ("SAMSUNG", r"C:\Users\User\Dev\samsung-tv\samsung_final.m3u")
]

saida = "super_lista.m3u"

# ==============================
# NORMALIZAÇÃO
# ==============================
def normalizar(nome):
    nome = nome.upper().strip()
    nome = unicodedata.normalize('NFKD', nome)
    nome = nome.encode('ASCII', 'ignore').decode()
    return re.sub(r'\s+', ' ', nome)

# ==============================
# IDENTIFICAR COMÉDIA (INTELIGENTE)
# ==============================
def eh_comedia(nome):

    nome = normalizar(nome)

    palavras = [
        "CHAVES","CHAPOLIN","MR BEAN","BEAN",
        "TODO MUNDO ODEIA O CHRIS","EVERYBODY HATES CHRIS",
        "THE OFFICE","BROOKLYN","BROOKLYN 99",
        "SOUTH PARK","SIMPSONS","FAMILY GUY",
        "AMERICAN DAD","RICK E MORTY","BOJACK",
        "PEGADINHA","PEGADINHAS","HUMOR","COMEDY",
        "FAIL","LAUGHS","STAND UP","PORTA DOS FUNDOS",
        "PORTATV"
    ]

    return any(p in nome for p in palavras)

# ==============================
# LEITURA
# ==============================
def ler(caminho):
    if caminho.startswith("http"):
        try:
            return requests.get(caminho, timeout=20).text.splitlines(keepends=True)
        except:
            return []
    else:
        if not os.path.exists(caminho):
            return []
        with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
            return f.readlines()

# ==============================
# PROCESSAMENTO + DEDUP
# ==============================
vistos = set()
lista = []

for tipo, caminho in playlists:

    linhas = ler(caminho)
    i = 0

    while i < len(linhas):
        if linhas[i].startswith("#EXTINF"):

            extinf = linhas[i]
            url = linhas[i+1]

            nome = extinf.split(",")[-1].strip()
            nome_norm = normalizar(nome)

            if nome_norm not in vistos:
                vistos.add(nome_norm)
                lista.append((extinf, url))

            i += 2
        else:
            i += 1

# ==============================
# AJUSTES
# ==============================
resultado = []
comedia_extra = []

for extinf, url in lista:

    nome = extinf.split(",")[-1].strip()
    nome_norm = normalizar(nome)

    grupo = ""
    if 'group-title="' in extinf:
        grupo = extinf.split('group-title="')[1].split('"')[0]

    # 🎯 SE FOR COMÉDIA E NÃO ESTÁ EM COMÉDIA → MOVER
    if eh_comedia(nome) and "COMEDIA" not in normalizar(grupo):
        extinf = re.sub(r'group-title="[^"]*"', 'group-title="COMÉDIA"', extinf)
        comedia_extra.append((extinf, url))
    else:
        resultado.append((extinf, url))

# ==============================
# REPOSICIONAR TV CULTURA / UOL
# ==============================
final = []
inseridos = False

for extinf, url in resultado:

    final.append((extinf, url))

    nome = normalizar(extinf.split(",")[-1])

    if not inseridos and nome == "CULTURA":
        # adiciona logo depois
        for e,u in resultado:
            n = normalizar(e.split(",")[-1])
            if n in ["TV CULTURA","CANAL UOL"]:
                final.append((e,u))
        inseridos = True

# adiciona comédia corrigida no final
final.extend(comedia_extra)

# ==============================
# SALVAR
# ==============================
with open(saida, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    for e,u in final:
        f.write(e)
        f.write(u)

# ==============================
# GIT
# ==============================
def git(cmd):
    subprocess.run(cmd, shell=True)

git("git add -A")
git('git commit -m "fix: ajuste fino comedia + cultura/uol"')
git("git push origin main")

print("✅ FINALIZADO PERFEITAMENTE")
