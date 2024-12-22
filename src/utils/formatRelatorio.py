import re

def parse_relatorio(relatorio: str) -> dict:
    # Parsing das medidas estruturais
    medidas_structural = re.search(
        r"Pupila: Centro \((\d+), (\d+)\), Raio (\d+)px\nIris: Centro \((\d+), (\d+)\), Raio (\d+)px",
        relatorio
    )
    pupila = {
        "centro": (int(medidas_structural.group(1)), int(medidas_structural.group(2))),
        "raio": int(medidas_structural.group(3)),
    }
    iris = {
        "centro": (int(medidas_structural.group(4)), int(medidas_structural.group(5))),
        "raio": int(medidas_structural.group(6)),
    }

    # Parsing da análise setorial
    setores = []
    setor_pattern = r"setor_(\d+):\n- Contraste: ([\d.]+)\n- Homogeneidade: ([\d.]+)\n  \* ([^\n]+)(\n  \* ([^\n]+))?"
    for match in re.finditer(setor_pattern, relatorio):
        setor = {
            "setor": int(match.group(1)),
            "contraste": float(match.group(2)),
            "homogeneidade": float(match.group(3)),
            "observacoes": [match.group(4)],
        }
        if match.group(6):
            setor["observacoes"].append(match.group(6))
        setores.append(setor)

    # Parsing do Collarette
    collarette = re.search(
        r"Regularidade: ([\d.]+)\n- Circularidade: ([\d.]+)",
        relatorio
    )
    collarette_data = {
        "regularidade": float(collarette.group(1)),
        "circularidade": float(collarette.group(2)),
    }

    # Parsing da interpretação
    interpretacao_pattern = r"• ([^\n]+): ([^\n]+)"
    interpretacao = {}
    for match in re.finditer(interpretacao_pattern, relatorio):
        interpretacao[match.group(1).lower().replace(" ", "_")] = match.group(2)

    # Estruturar o JSON
    return {
        "medidas_estruturais": {
            "pupila": pupila,
            "iris": iris,
        },
        "analise_setorial": setores,
        "analise_collarette": collarette_data,
        "interpretacao": interpretacao,
    }
