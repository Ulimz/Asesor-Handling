# ⚠️ MANTRA OBLIGATORIO

Estos tres principios DEBEN ser seguidos SIEMPRE, sin excepciones:

### 1️⃣ Verificar Archivos Existentes ANTES de Crear Nuevos

```
ANTES DE CREAR CUALQUIER ARCHIVO:

❌ INCORRECTO: Crear archivo nuevo sin revisar
✅ CORRECTO: 
   1. Buscar si ya existe con file_search o grep_search
   2. Verificar en docs/active/, docs/deprecated/, root
   3. Si existe: ACTUALIZAR, no crear nuevo
   4. Si no existe: proceder con creación
### 2️⃣ Seguir la Estructura (v1.1 - OFICIAL)
**Estructura de Carpetas Permitida**:

*   📂 **root/**: Configuración del proyecto (`package.json`, `.env`, `docker-compose.yml`, `README.md`).
    *   ❌ PROHIBIDO: Documentación suelta (.md) o scripts sueltos (mover a `scripts/`).
*   📂 **docs/active/**: ÚNICA ubicación para documentación viva (`PROJECT_STATUS.md`, `MANTRA.md`).
*   📂 **docs/deprecated/**: Cementerio de archivos antiguos.
*   📂 **backend/**:
    *   `app/`: Código fuente API.
    *   `scripts/`: Scripts de utilidad Python (`seed_*.py`, `extract_*.py`).
    *   `data/`: Archivos JSON/XML de referencia.
*   📂 **src/**: Código fuente Frontend (Next.js).
*   📂 **scripts/**: Scripts de mantenimiento general del proyecto.
*   📂 **auditoria_resultados/**: Reportes temporales de análisis.

**Regla de oro**:
- ❌ NO crear archivos .md en root (Solo permitido `README.md`).
- ✅ SÍ crear archivos .md en `docs/active/`.
- ❌ NO mezclar scripts de backend en root (usar `backend/scripts/`).
- ✅ SÍ mantener limpieza absoluta en el directorio raíz.
### 3️⃣ Evitar Duplicados Completamente

```
PROTOCOLO ANTI-DUPLICADOS:

1. Antes de crear archivo X:
   - Buscar "X.md" en TODO el proyecto
   - Buscar contenido similar con keywords
   - Revisar docs/deprecated/ para historiales
   
2. Si encontrars algo similar:
   - ACTUALIZAR lo existente
   - O REEMPLAZAR si está obsoleto
   - NUNCA crear segunda copia

3. Después de crear/actualizar:
   - Verificar con: git status
   - Comprobar no hay archivos .md innecesarios en root
   - Confirmar con: Get-ChildItem -Filter "*.md" -Recurse
```

---

## 🛑 CASOS DE USO COMÚN - PREGUNTAS ANTES DE ACTUAR

### Caso 1: "Debo crear NUEVA_DOC.md"

**Checklist OBLIGATORIO** (en este orden):

```
☐ ¿Ya existe NUEVA_DOC.md en algún lado?
  → grep_search "NUEVA_DOC"
  → file_search "*NUEVA_DOC*"
  
☐ ¿Existe contenido similar con otro nombre?
  → grep_search "palabras clave del contenido"
  
☐ ¿En qué carpeta debería ir?
  → Si es documentación → docs/active/
  → Si es configuración → root/ o docs/
  → Si es script → app/utils/categoría
  → Si es obsoleto → docs/deprecated/
  
☐ ¿Necesita referencias en otros archivos?
  → Buscar si hay index/índice que actualizar
  → Buscar si hay README que mencione
  
☐ ¿Es realmente NECESARIO crear uno nuevo?
  → O podría actualizar uno existente?
```

### Caso 2: "He creado varios archivos, debo organizarlos"

**NUNCA DEJAR PARA DESPUÉS - HACER AHORA:**

```
DURANTE la creación:
✓ Crear en la carpeta CORRECTA desde el inicio
✓ Usar nombres CONSISTENTES con lo existente
✓ Actualizar DOCUMENTATION_INDEX.md mientras lo hago
✓ Hacer COMMIT después de CADA conjunto lógico

DESPUÉS de crear:
✓ Revisar: ls -la docs/active/ | grep ".md"
✓ Revisar: git status (no debe haber sorpresas)
✓ Revisar: No duplicados con get_changed_files
✓ Hacer commit CON EL MENSAJE CORRECTO
```

### Caso 3: "Necesito actualizar estructura"

**PERMITIDO SOLO SI:**

```
☐ Es DESPUÉS de validar cambios
☐ Es PARTE de un refactor planeado
☐ TODOS los cambios se hacen en UN COMMIT
☐ Se actualiza documentación de cambios
☐ NO es "reorganizar aquí, allá y acá"
```

**NO PERMITIDO:**

```
❌ Mover archivos sin razón clara
❌ Hacer 5 reorganizaciones en 1 sesión
❌ Cambiar estructura sin documentar
❌ Crear archivos "temporales" que se quedan
```

---

## 📋 CHECKLIST PRE-CREACIÓN DE ARCHIVOS

**LEER Y APLICAR SIEMPRE - 100% DE LAS VECES**

```
ARCHIVO PARA CREAR: ____________________

PRE-CREACIÓN:
□ ¿Existe ya?
  • Resultado de búsqueda: _____________
  • Ubicación: _________________________
  
□ ¿Carpeta correcta?
  • Carpeta elegida: ___________________
  • ¿Es la oficial en v1.1? □ Sí □ No
  
□ ¿Duplicado con...?
  • Archivos similares encontrados: ____
  • ¿Contenido diferente o igual? ______
  
□ ¿Necesario realmente?
  • Justificación: ____________________
  • ¿Podría actualizar existente? □ Sí □ No

□ ¿Referencias necesarias?
  • Debo actualizar: __________________
  • Debo mencionar en: _________________

DECISIÓN FINAL:
☐ CREAR nuevo archivo (ubicación: _______)
☐ ACTUALIZAR archivo existente (cual: ___)
☐ CANCELAR (razón: ____________________)
```

---

## 🚨 COMPORTAMIENTOS PROHIBIDOS (A PARTIR DE AHORA)

```
❌ NO hacer esto:

1. Crear archivo X sin buscar si ya existe
2. Guardar documentación en root (excepto README.md, .env)
3. Tener 2+ versiones de "mismo contenido" en diferentes carpetas
4. Reorganizar carpetas "para ver cómo queda"
5. Cambiar estructura después de haber hecho commit
6. Crear DOCUMENTACION_INDEX, DOCUMENTATION_INDEX, Doc_Index (3 versiones)
7. Mover archivos más de 1 vez por sesión
8. No actualizar referencias después de crear archivo

✅ HACER esto en su lugar:

1. Verificar PRIMERO si existe (5 segundos extra)
2. Guardar TODO en docs/active/ salvo excepciones
3. Si existe similar → ACTUALIZAR o REEMPLAZAR
4. Pensar estructura ANTES de crear
5. Cambiar estructura EN UN COMMIT (no 3 commits)
6. Un solo index bien hecho: DOCUMENTATION_INDEX.md
7. Reorganizar UNA SOLA VEZ correctamente
8. Actualizar referencias MIENTRAS creo
```

---

## 📊 MÉTRICAS DE ÉXITO

Estas métricas indican si estoy siguiendo las directivas:

```
INDICADOR                          META            ESTADO
├─ Archivos duplicados             0               ✅
├─ Archivos .md en root            ≤ 3             ✅
├─ Documentación en docs/active/   100%            ✅
├─ Reorganizaciones por sesión     ≤ 1             ✅
├─ Búsquedas ANTES de crear        100%            ✅
├─ Commits reorganización          ≤ 2             ✅
└─ Estructura v1.1 seguida         100%            ✅
```

---

## 🎯 FLUJO CORRECTO PARA CREAR ARCHIVO

**SIEMPRE HACER EN ESTE ORDEN:**

```
1. ANALIZAR
   └─ ¿Qué necesito crear/actualizar?
   
2. BUSCAR
   └─ grep_search + file_search
   └─ ¿Existe? → Ir a paso 5
   
3. PLANIFICAR
   └─ ¿Dónde va (carpeta)?
   └─ ¿Nombre correcto?
   └─ ¿Qué debe contener?
   
4. CREAR
   └─ create_file en ubicación correcta
   └─ Contenido de calidad
   
5. ACTUALIZAR REFERENCIAS
   └─ DOCUMENTATION_INDEX.md
   └─ Otros archivos que mencionen
   
6. VERIFICAR
   └─ git status (verificar donde está)
   └─ No duplicados
   └─ Estructura correcta
   
7. COMMIT
   └─ Mensaje claro
   └─ Una sola operación lógica
```

---

## 💡 EJEMPLO: CREAR ARCHIVO CORRECTAMENTE

**ESCENARIO**: Necesito crear guía de "Optimización de BD"

**INCORRECTO** (antigua forma):
```
1. Crear "DB_OPTIMIZATION.md" en root
2. Luego mover a docs/active
3. Luego crear "DATABASE_OPTIMIZATION.md" en otro lado
4. Resultado: 2 versiones, confusión, reorganización
```

**CORRECTO** (nueva forma):
```
1. Buscar si existe:
   grep_search "optimización base datos"
   → No encuentra nada existente
   
2. Buscar archivos similares:
   grep_search "performance"
   → Encuentra PROJECT_STATUS.md menciona algo
   → Pero es contenido diferente
   
3. Decidir ubicación:
   → Es documentación técnica
   → Va en docs/active/
   
4. Nombrar correctamente:
   → Consistente con otros: "DATABASE_OPTIMIZATION.md"
   
5. Crear:
   create_file en docs/active/DATABASE_OPTIMIZATION.md
   
6. Actualizar índice:
   DOCUMENTATION_INDEX.md → agregar referencia
   
7. Verificar:
   git status → muestra:
   A docs/active/DATABASE_OPTIMIZATION.md
   M docs/active/DOCUMENTATION_INDEX.md
   
8. Commit:
   git add -A
   git commit -m "docs: Add DATABASE_OPTIMIZATION.md guide"
   
✅ RESULTADO: Archivo en lugar correcto, no duplicado
```

---

## ✅ CONFIRMACIÓN

**Confirmo que entiendo estas directivas:**

- ✅ Verificar SIEMPRE si existe antes de crear
- ✅ NUNCA crear en root (excepto README.md, .env)
- ✅ SIEMPRE seguir estructura v1.1
- ✅ NUNCA tener duplicados
- ✅ NUNCA reorganizar múltiples veces
- ✅ BUSCAR PRIMERO, crear después
- ✅ ACTUALIZAR referencias automáticamente
- ✅ UN COMMIT POR OPERACIÓN LÓGICA

**Estado**: 🔴 EN VIGOR DESDE AHORA

Estas reglas NO SON sugerencias.  
Estas reglas SON OBLIGATORIAS.  
Sin excepciones.

---
 
**Vigencia**: Indefinida (hasta que se actualice explícitamente)  
**Aplicable**: Todos los futuros cambios del proyecto
