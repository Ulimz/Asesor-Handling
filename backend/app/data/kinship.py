
# Tabla de Verdad de Parentescos (Fuente: Imágenes Usuario)
# Se usa para blindar a la IA contra alucinaciones sobre grados de parentesco.

KINSHIP_DATA = {
    "consanguinidad": {
        1: ["Padres", "Hijos"],
        2: ["Hermanos", "Abuelos", "Nietos"],
        3: ["Tíos", "Sobrinos"],
        4: ["Primos hermanos"]
    },
    "afinidad": {
        1: ["Suegros", "Yernos", "Nueras", "Hijastros"],
        2: ["Cuñados", "Abuelos del cónyuge", "Nietos del cónyuge"],
        3: ["Tíos del cónyuge", "Sobrinos del cónyuge"],
        4: ["Primos del cónyuge"]
    }
}

def get_kinship_table_markdown():
    """Genera la tabla en formato Markdown para inyectar al prompt"""
    md = """
### 🛑 TABLA OFICIAL DE GRADOS DE PARENTESCO (CONSULTAR OBLIGATORIAMENTE)

| GRADO | CONSANGUINIDAD (Sangre) | AFINIDAD (Político/Cónyuge) |
|-------|-------------------------|-----------------------------|
| **1º** | Padres, Hijos | Suegros, Yernos, Nueras, Hijastros |
| **2º** | Hermanos, Abuelos, Nietos | Cuñados, Abuelos del cónyuge, Nietos del cónyuge |
| **3º** | Tíos, Sobrinos | Tíos del cónyuge, Sobrinos del cónyuge |
| **4º** | Primos hermanos | Primos del cónyuge |
"""
    return md

# Lista plana de términos para detección rápida (keywords)
KINSHIP_KEYWORDS = [
    "padre", "madre", "papá", "mamá", "hijo", "hija",
    "hermano", "hermana", "abuelo", "abuela", "nieto", "nieta",
    "tío", "tía", "sobrino", "sobrina",
    "primo", "prima",
    "suegro", "suegra", "yerno", "nuera", "hijastro", "hijastra",
    "cuñado", "cuñada",
    "cónyuge", "pareja", "marido", "mujer", "esposo", "esposa",
    "familiar", "pariente", "grado", "consanguinidad", "afinidad"
]
