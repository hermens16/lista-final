import os
from collections import defaultdict, Counter
import subprocess
import unicodedata
import re
import requests

print("🚀 SUPER LISTA FINAL + FULL + RELATÓRIOS")

playlists = [
    ("H", "https://raw.githubusercontent.com/hermens16/h/refs/heads/main/h.m3u8"),
    ("PLUTO", r"C:\Users\User\Dev\pluto-tv\pluto_br_final.m3u8"),
    ("PLEX", r"C:\Users\User\Dev\plex-tv\playlist_final.m3u"),
    ("SAMSUNG", r"C:\Users\User\Dev\samsung-tv\samsung_final.m3u")
]

ALVO_FIXO = {"TV CULTURA", "CANAL UOL"}

saida_h = []
saida_fast = []
saida_fast_full = []

canais_fast_vistos = set()

contador_nomes = Counter()
contador_origem_bruto = defaultdict(int)
contador_origem_final_dedup = defaultdict(int)
contador_origem_final_full = defaultdict(int)

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

def normalizar_grupo(g):
    g = g.upper()
    if "ABERTA" in g: return "TV ABERTA"
    if "EVENT" in g: return "EVENTOS"
    if "SPORT" in g: return "ESPORTES"
    if "MOVIE" in g: return "FILMES"
    if "SERIE" in g: return "SÉRIES"
    if "DOC" in g: return "DOCUMENTÁRIOS"
    if "ANIME" in g: return "ANIME & TOKUSATSU"
    if "DESENHO" in g: return "DESENHOS 24H"
    if "INFANT" in g: return "INFANTIL"
    if "MUSIC" in g: return "MÚSICA"
    if "NEWS" in g or "NOTIC" in g: return "NOTÍCIAS"
    return "VARIEDADES"

def ler_playlist(caminho):
    try:
        if caminho.startswith("http"):
            r = requests.get(caminho, timeout=15)
            return r.text.splitlines()
        else:
            with open(caminho, encoding="utf-8", errors="ignore") as f:
                return f.read().splitlines()
    except:
        print(f"❌ Erro ao ler: {caminho}")
        return []

# 🔥 LEITURA ROBUSTA
for tipo, caminho in playlists:

    print(f"📥 Lendo {tipo}")
    linhas = ler_playlist(caminho)

    i = 0
    while i < len(linhas):

        if linhas[i].strip().startswith("#EXTINF"):

            extinf = linhas[i].strip()

            j = i + 1
            while j < len(linhas) and not linhas[j].strip():
                j += 1

            if j >= len(linhas):
                break

            url = linhas[j].strip()

            nome = extinf.split(",")[-1].strip()
            nome_norm = normalizar_nome(nome)

            contador_nomes[nome_norm] += 1
            contador_origem_bruto[tipo] += 1
            total_lidos += 1

            if tipo == "H":
                saida_h.append((extinf, url, tipo))
                contador_origem_final_dedup["H"] += 1
                contador_origem_final_full["H"] += 1
            else:
                # FULL
                saida_fast_full.append((extinf, url, tipo))
                contador_origem_final_full[tipo] += 1

                # DEDUP
                if nome_norm not in canais_fast_vistos:
                    canais_fast_vistos.add(nome_norm)
                    saida_fast.append((extinf, url, tipo))
                    contador_origem_final_dedup[tipo] += 1

            i = j + 1
            continue

        i += 1

# 🔥 REPOSICIONAMENTO
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

# AGRUPAMENTO
def montar_lista(lista_total):

    grupos = defaultdict(list)

    for extinf, url, origem in lista_total:

        grupo = normalizar_grupo(extrair_grupo(extinf))

        if 'group-title="' in extinf:
            extinf = re.sub(r'group-title="[^"]*"', f'group-title="{grupo}"', extinf)
        else:
            extinf += f' group-title="{grupo}"'

        grupos[grupo].append((extinf, url, origem))

    if "TV ABERTA" in grupos:
        grupos["TV ABERTA"] = reposicionar_tv_aberta(grupos["TV ABERTA"])

    return grupos

ORDEM = [
    "TV ABERTA","EVENTOS","ESPORTES","FILMES","SÉRIES",
    "DOCUMENTÁRIOS","ANIME & TOKUSATSU","DESENHOS 24H",
    "INFANTIL","MÚSICA","NOTÍCIAS","RELIGIOSO","VARIEDADES"
]

# 🔥 SALVAR (BLINDADO)
def salvar(nome, grupos):

    with open(nome, "w", encoding="utf-8", newline="\n") as f:

        f.write("#EXTM3U\n")

        for g in ORDEM:
            if g in grupos:
                for e, u, _ in grupos[g]:

                    e = e.strip()
                    u = u.strip()

                    if not e.startswith("#EXTINF"):
                        continue
                    if "," not in e:
                        continue
                    if not u.startswith("http"):
                        continue

                    f.write(e + "\n")
                    f.write(u + "\n")

# 🔥 RELATÓRIO COMPLETO
def gerar_relatorio(nome, grupos, lista_final, tipo):

    duplicados_total = sum(qtd - 1 for qtd in contador_nomes.values() if qtd > 1)

    with open(nome, "w", encoding="utf-8") as f:

        f.write("📊 RELATÓRIO IPTV\n\n")

        f.write(f"Total lido: {total_lidos}\n")
        f.write(f"Total final: {len(lista_final)}\n")
        f.write(f"Duplicados removidos: {duplicados_total}\n\n")

        f.write("📡 POR FONTE (BRUTO):\n")
        for k,v in contador_origem_bruto.items():
            f.write(f"{k} -> {v}\n")

        f.write("\n📡 POR FONTE (FINAL):\n")

        origem = contador_origem_final_dedup if tipo == "DEDUP" else contador_origem_final_full

        for k,v in origem.items():
            f.write(f"{k} -> {v}\n")

        f.write("\n📂 POR GRUPO:\n")
        for g in grupos:
            f.write(f"{g} -> {len(grupos[g])}\n")

# 🔥 GERAR LISTAS
lista_dedup = saida_h + saida_fast
lista_full = saida_h + saida_fast_full

grupos_dedup = montar_lista(lista_dedup)
grupos_full = montar_lista(lista_full)

salvar("super_lista.m3u", grupos_dedup)
salvar("super_lista_full.m3u", grupos_full)

# RELATÓRIOS
gerar_relatorio("relatorio_dedup.txt", grupos_dedup, lista_dedup, "DEDUP")
gerar_relatorio("relatorio_full.txt", grupos_full, lista_full, "FULL")

# GIT
subprocess.run("git add -A", shell=True)
subprocess.run('git commit -m "final completo com relatorios"', shell=True)
subprocess.run("git push", shell=True)

print("✅ LISTAS + RELATÓRIOS GERADOS COM SUCESSO")
