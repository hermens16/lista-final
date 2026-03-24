import os

arquivo = "super_lista.m3u"
saida = "lista_completa_canais.txt"

print("📋 Gerando lista completa de canais...")

if not os.path.exists(arquivo):
    print("❌ Arquivo não encontrado!")
    exit()

canais = []

with open(arquivo, "r", encoding="utf-8", errors="ignore") as f:
    linhas = f.readlines()

i = 0

while i < len(linhas):

    if linhas[i].startswith("#EXTINF"):

        extinf = linhas[i]

        nome = extinf.split(",")[-1].strip()

        grupo = "SEM GRUPO"
        if 'group-title="' in extinf:
            grupo = extinf.split('group-title="')[1].split('"')[0]

        canais.append((grupo, nome))

        i += 2
        continue

    i += 1

# ordenar por grupo + nome
canais.sort()

with open(saida, "w", encoding="utf-8") as f:

    grupo_atual = ""

    for grupo, nome in canais:

        if grupo != grupo_atual:
            f.write(f"\n=== {grupo} ===\n")
            grupo_atual = grupo

        f.write(nome + "\n")

print("✅ Lista completa gerada:", saida)
