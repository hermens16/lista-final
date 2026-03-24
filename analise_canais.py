import os
import re
from collections import defaultdict, Counter
from urllib.parse import urlparse

arquivo = "super_lista.m3u"
relatorio = "relatorio_canais.txt"

print("📊 Analisando playlist...")

if not os.path.exists(arquivo):
    print("❌ Arquivo não encontrado!")
    exit()

def normalizar_nome(nome):
    nome = nome.upper()
    nome = re.sub(r'\b(HD|FHD|SD|4K|UHD)\b', '', nome)
    nome = re.sub(r'[^A-Z0-9 ]', '', nome)
    nome = re.sub(r'\s+', ' ', nome)
    return nome.strip()

with open(arquivo, "r", encoding="utf-8", errors="ignore") as f:
    linhas = f.readlines()

total_canais = 0
grupos = defaultdict(int)
nomes = []
nomes_normalizados = []
dominios = []

i = 0

while i < len(linhas):

    if linhas[i].startswith("#EXTINF"):

        extinf = linhas[i]
        url = linhas[i+1].strip()

        nome = extinf.split(",")[-1].strip()
        nome_norm = normalizar_nome(nome)

        grupo = "SEM GRUPO"
        if 'group-title="' in extinf:
            grupo = extinf.split('group-title="')[1].split('"')[0]

        try:
            dominio = urlparse(url).netloc
        except:
            dominio = "erro"

        total_canais += 1
        grupos[grupo] += 1
        nomes.append(nome)
        nomes_normalizados.append(nome_norm)
        dominios.append(dominio)

        i += 2
        continue

    i += 1

# 🔥 CONTAGENS
duplicados_nome = Counter(nomes)
duplicados_norm = Counter(nomes_normalizados)
top_dominios = Counter(dominios)

# 🔥 FILTRAR DUPLICADOS
repetidos = {k: v for k, v in duplicados_nome.items() if v > 1}
repetidos_norm = {k: v for k, v in duplicados_norm.items() if v > 1}

# 🔥 GERAR RELATÓRIO
with open(relatorio, "w", encoding="utf-8") as f:

    f.write("📊 RELATÓRIO IPTV\n\n")

    f.write(f"Total de canais: {total_canais}\n")
    f.write(f"Total de grupos: {len(grupos)}\n\n")

    f.write("📂 CANAIS POR GRUPO:\n")
    for g, c in sorted(grupos.items(), key=lambda x: -x[1]):
        f.write(f"{g} -> {c}\n")

    f.write("\n🔁 DUPLICADOS EXATOS (TOP 20):\n")
    for k, v in sorted(repetidos.items(), key=lambda x: -x[1])[:20]:
        f.write(f"{k} -> {v}\n")

    f.write("\n🧠 DUPLICADOS NORMALIZADOS (TOP 20):\n")
    for k, v in sorted(repetidos_norm.items(), key=lambda x: -x[1])[:20]:
        f.write(f"{k} -> {v}\n")

    f.write("\n🌐 TOP SERVIDORES:\n")
    for d, c in top_dominios.most_common(15):
        f.write(f"{d} -> {c}\n")

print("✅ Relatório gerado:", relatorio)
