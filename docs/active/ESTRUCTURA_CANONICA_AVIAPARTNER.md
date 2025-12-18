# Estructura Salarial - Aviapartner (2025)

**Fuente**: BOE-A-2025-3081 (Convenio Aviapartner 2025), publicado el 17 de febrero de 2025.

## 1. Grupos Profesionales y Niveles

### 1.1 Técnicos Gestores
- Nivel entrada (Nivel 1)
- Nivel 2
- Nivel 3
- Nivel 4
- Nivel 5
- Nivel 6
- Nivel 7

### 1.2 Administrativos
- Agente Administrativo
- Niveles: Entrada (1) hasta 7.

### 1.3 Servicios Auxiliares
- Agente de Servicios Auxiliares
- Niveles: Entrada (1) hasta 7.

---

## 2. Salario Base Anual (2025)

| Nivel | Técnicos Gestores | Administrativos | Servicios Auxiliares |
| :--- | :--- | :--- | :--- |
| **Entrada** | 28.741,86 € | 18.816,45 € | 18.633,14 € |
| **Nivel 2** | 28.798,05 € | 22.283,49 € | 22.066,61 € |
| **Nivel 3** | 29.657,79 € | 22.953,50 € | 22.730,09 € |
| **Nivel 4** | 30.250,95 € | 23.412,57 € | 23.184,70 € |
| **Nivel 5** | 30.844,11 € | 23.871,64 € | 23.639,30 € |
| **Nivel 6** | 32.077,87 € | 24.826,50 € | 24.584,87 € |
| **Nivel 7** | 33.360,98 € | 25.819,57 € | 25.568,26 € |

---

## 3. Conceptos Variables (2025)

### 3.1 Horas Extras y Perentorias (Valor/Hora)

| Grupo Laboral | Entrada | Nivel 2 | Nivel 3 | Nivel 4 | Nivel 5 | Nivel 6 | Nivel 7 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Técnicos Gestores** | 29,38 € | 29,44 € | 30,32 € | 30,92 € | 31,53 € | 32,79 € | 34,10 € |
| **Administrativos** | 19,23 € | 22,78 € | 23,47 € | 23,93 € | 24,40 € | 25,38 € | 26,39 € |
| **Serv. Auxiliares** | 19,05 € | 22,56 € | 23,24 € | 23,70 € | 24,16 € | 25,13 € | 26,14 € |

*(Nota: Los valores de Hora Perentoria y Hora Complementaria Especial son idénticos en las tablas del Anexo II).*

### 3.2 Pluses Variables (Importes)

| Concepto | Valor 2025 | Unidad | Notas |
| :--- | :--- | :--- | :--- |
| **Nocturnidad** | 1,62 € | Hora | 22:00 - 06:00 |
| **Festivo** | 2,87 € | Hora | |
| **Domingo** | 2,83 € | Hora | |
| **Plus Madrugue** | 6,49 € | Día | Inicio 04:00 - 06:55 |
| **Plus Transporte** | 2,86 € | Asistencia | |
| **Ayuda Manutención** | 6,49 € | Día | Según horario (14-16 o 21-23) |
| **Plus Fraccionada** | 11,45 € | Día | |

### 3.3 Pluses Complejos y Tramos

#### Turnicidad (Fijo Mensual)
- **2 Turnos**: 82,81 €
- **3 Turnos**: 110,40 €
- **4 Turnos**: 126,96 €
- **5 o más Turnos**: 143,52 €
- **Plus Jornada Irregular (Fiji)**: 143,52 € (Incompatible con turnicidad)

#### FTP (Fijo Mensual)
- **Plus FTP**: 99,37 € (Incompatible con turnicidad y Fiji)

#### Funciones (Fijo Mensual)
- **Plus Jefe Servicio**: 134,55 €
- **Plus Supervisor**: 103,50 €

---

## 4. Notas de Implementación
- **Sincronización**: Se creará el archivo `backend/data/structure_templates/aviapartner.json` basándose en estos valores.
- **Seeder**: El script `backend/seed_production.py` deberá cargar estos valores para la compañía "aviapartner".
- **Calculadora**: Verificar que las incompatibilidades (FTP vs Turnicidad vs Fiji) se manejen correctamente en el frontend si es posible, o mediante los inputs.
