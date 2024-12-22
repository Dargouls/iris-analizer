from fastapi import FastAPI, UploadFile, File, HTTPException, APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict
import cv2
import numpy as np
from PIL import Image
import io
import base64

app = APIRouter()

# Utilitários

def pil_to_cv2(pil_image):
    return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

def cv2_to_base64(image):
    _, buffer = cv2.imencode(".jpg", image)
    return base64.b64encode(buffer).decode("utf-8")

def pre_processar_imagem(cv2_image):
    # Pré-processamento fictício
    return cv2_image

def detectar_esclera(image):
    # Detecção fictícia de esclera
    return np.zeros(image.shape[:2], dtype=np.uint8)

def detectar_iris_pupila(image, mask):
    # Detecção fictícia de íris e pupila
    return (100, 100, 50), (100, 100, 30)  # (ix, iy, ir), (px, py, pr)

def classificar_caracteristica(valor, estrutura, caracteristica):
    return f"{caracteristica} de {estrutura}: valor {valor:.2f} classificado como normal"

def gerar_interpretacao(metricas):
    return {
        "pupila": "Tamanho e forma da pupila são normais.",
        "iris": "Densidade e textura da íris estão adequadas.",
        "collarette": "Collarette apresenta regularidade satisfatória."
    }

# Modelo de Resposta
class AnaliseResponse(BaseModel):
    """Modelo de resposta da análise"""
    informacoes_imagem: Dict[str, str]
    medidas_estruturais: Dict[str, Dict[str, str]]
    interpretacao: Dict[str, str]
    imagem_processada: str

# Endpoint principal
@app.post("/analisar-iris", response_model=AnaliseResponse)
async def analisar_iris(file: UploadFile = File(...)):
    try:
        # Ler e converter imagem
        contents = await file.read()
        pil_image = Image.open(io.BytesIO(contents))
        cv2_image = pil_to_cv2(pil_image)

        # Processamento da imagem
        imagem_processada = pre_processar_imagem(cv2_image)
        mask_esclera = detectar_esclera(imagem_processada)
        iris_info, pupil_info = detectar_iris_pupila(imagem_processada, mask_esclera)

        if iris_info is None or pupil_info is None:
            raise HTTPException(
                status_code=400,
                detail="Não foi possível detectar íris ou pupila na imagem"
            )

        # Criar visualização
        output_img = cv2_image.copy()
        ix, iy, ir = iris_info
        px, py, pr = pupil_info

        # Desenhar marcações
        cv2.circle(output_img, (ix, iy), ir, (0, 255, 0), 2)
        cv2.circle(output_img, (px, py), pr, (255, 0, 0), 2)

        # Preparar métricas
        metricas = {
            'pupila': {
                'tamanho': pr,
                'forma': pr / ir
            },
            'iris': {
                'densidade': ir / px,
                'textura': 0.75
            },
            'collarette': {
                'regularidade': 350,
                'circularidade': 0.85
            }
        }

        # Gerar relatório estruturado
        interpretacao = gerar_interpretacao(metricas)

        response_data = {
            "informacoes_imagem": {
                "formato": pil_image.format,
                "dimensoes": f"{pil_image.size[0]}x{pil_image.size[1]}"
            },
            "medidas_estruturais": {
                "pupila": {
                    "raio": f"{pr}px",
                    "tamanho_relativo": classificar_caracteristica(pr, "pupila", "tamanho"),
                    "forma": classificar_caracteristica(pr / ir, "pupila", "forma")
                },
                "iris": {
                    "raio": f"{ir}px",
                    "densidade": classificar_caracteristica(ir / px, "iris", "densidade"),
                    "textura": classificar_caracteristica(0.75, "iris", "textura")
                },
                "collarette": {
                    "regularidade": classificar_caracteristica(350, "collarette", "regularidade"),
                    "circularidade": classificar_caracteristica(0.85, "collarette", "circularidade")
                }
            },
            "interpretacao": interpretacao,
            "imagem_processada": cv2_to_base64(output_img)
        }

        return response_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
