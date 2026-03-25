import os
from collections import defaultdict, Counter
import subprocess
import unicodedata
import re
import requests

print("🚀 SUPER LISTA FINAL (CORRIGIDA DE VERDADE)")

playlists = [
    ("H", "https://raw.githubusercontent.com/hermens16/h/refs/heads/main/h.m3u8"),
    ("PLUTO", r"C:\Users\User\Dev\pluto-tv\pluto_br_final.m3u8"),
    ("PLEX", r"C:\Users\User\Dev\plex-tv\playlist_final.m3u"),
    ("SAMSUNG", r"C:\Users\User\Dev\samsung-tv\samsung_final.m3u")
]

# arquivos
saida_dedup = "super_lista.m3u"
saida_full = "super_lista_full.m3u"

relatorio_dedup = "relatorio_dedup.txt"
relatorio_full = "relatorio_full.txt"

# estruturas
saida_h = []
saida_fast = []
saida_fast_full = []

canais_fast_vistos = set()
contador_nomes = Counter()

total_lidos = 0

# NORMALIZAÇÃO
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

# 🔥 CORREÇÃO DEFINITIVA NOTÍCIAS
def normalizar_grupo(grupo, nome_canal):

    g = grupo.strip().upper()
    n = nome_canal.upper()

    # 🔴 PRIORIDADE MÁXIMA: NOME
    if any(x in n for x in [
        "CNN", "GLOBO NEWS", "GLOBONEWS", "BLOOMBERG",
        "RECORD NEWS", "BAND NEWS", "JP NEWS",
        "JOVEM PAN NEWS", "NEWS"
    ]):
        return "NOTÍCIAS"

    # 🟡 SEGUNDA CAMADA: GRUPO
    if any(x in g for x in ["NEWS", "NOTIC", "JORNAL"]):
        return "NOTÍCIAS"

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
    if "RELIG" in g:
        return "RELIGIOSO"
    if "RADIO" in g:
        return "RÁDIO"
    if "ADULT" in g:
        return "ADULTO"

    return "VARIEDADES"

# 🔥 NÃO REMOVE MAIS NADA
def canal_valido(nome):
    return True

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

# PROCESSAMENTO
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

            nome = extinf.split(",")[-1].strip()

            if not nome:
                nome = "SEM NOME"

            nome_norm = normalizar_nome(nome)

            contador_nomes[nome_norm] += 1
            total_lidos += 1

            # 🟢 H intacta
            if tipo == "H":
                saida_h.append((extinf, url))

            # 🔵 FAST
            else:
                saida_fast_full.append((extinf, url))

                if nome_norm not in canais_fast_vistos:
                    canais_fast_vistos.add(nome_norm)
                    saida_fast.append((extinf, url))

            i += 2
            continue

        i += 1

# AGRUPAMENTO
def montar_lista(saida_total):

    grupos = defaultdict(list)

    for extinf, url in saida_total:

        nome_canal = extinf.split(",")[-1].strip()
        grupo = normalizar_grupo(extrair_grupo(extinf), nome_canal)

        if 'group-title="' in extinf:
            extinf = re.sub(r'group-title="[^"]*"', f'group-title="{grupo}"', extinf)
        else:
            extinf = extinf.strip() + f' group-title="{grupo}"\n'

        grupos[grupo].append((extinf, url))

    return grupos

ORDEM = [
    "EVENTOS","TV ABERTA","ESPORTES","FILMES","SÉRIES",
    "DOCUMENTÁRIOS","ANIME & TOKUSATSU","DESENHOS 24H",
    "INFANTIL","MÚSICA","NOTÍCIAS","RELIGIOSO",
    "VARIEDADES","RÁDIO","ADULTO"
]

def salvar(nome_arquivo, grupos):
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")

        for g in ORDEM:
            if g in grupos:
                for e,u in grupos[g]:
                    f.write(e)
                    f.write(u)

# LISTAS
lista_dedup = saida_h + saida_fast
lista_full = saida_h + saida_fast_full

grupos_dedup = montar_lista(lista_dedup)
grupos_full = montar_lista(lista_full)

salvar(saida_dedup, grupos_dedup)
salvar(saida_full, grupos_full)

# RELATÓRIO COMPLETO
def gerar_relatorio(nome, grupos, lista_final):

    duplicados_total = sum(qtd - 1 for qtd in contador_nomes.values() if qtd > 1)
    canais_unicos = len(contador_nomes)
    total_final = len(lista_final)

    with open(nome, "w", encoding="utf-8") as f:

        f.write("📊 RELATÓRIO IPTV\n\n")

        f.write(f"Total lido (bruto): {total_lidos}\n")
        f.write(f"Total final: {total_final}\n")
        f.write(f"Canais únicos: {canais_unicos}\n")
        f.write(f"Duplicados encontrados: {duplicados_total}\n")
        f.write(f"Removidos (dedup): {total_lidos - total_final}\n\n")

        f.write(f"Total grupos: {len(grupos)}\n\n")

        f.write("📂 CANAIS POR GRUPO:\n")
        for g in sorted(grupos):
            f.write(f"{g} -> {len(grupos[g])}\n")

        f.write("\n🔁 DUPLICADOS (TOP 20):\n")
        for nome_canal, qtd in contador_nomes.most_common(20):
            if qtd > 1:
                f.write(f"{nome_canal} -> {qtd}\n")

gerar_relatorio(relatorio_dedup, grupos_dedup, lista_dedup)
gerar_relatorio(relatorio_full, grupos_full, lista_full)

# GIT
def git(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(r.stdout)
    print(r.stderr)

git("git add -A")
git('git commit --allow-empty -m "Super lista FINAL corrigida (noticias + contagem real)"')
git("git push origin main")

print("✅ FINALIZADO COM SUCESSO")
