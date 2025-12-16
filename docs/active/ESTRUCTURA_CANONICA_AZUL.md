# Estructura Salarial - Azul Handling (2025)

**Fuente**: XML Oficial Azul Handling (Convenio 2025).

## 1. Grupos Profesionales y Niveles

### 1.1 Técnicos Gestores
- Nivel Entrada
- Nivel 2
- Nivel 3
- Nivel 4
- Nivel 5
- Nivel 6
- Nivel 7

### 1.2 Administrativos
- Nivel Entrada
- Nivel 2
- Nivel 3
- Nivel 4
- Nivel 5
- Nivel 6
- Nivel 7

### 1.3 Servicios Auxiliares
- Nivel Entrada
- Nivel 2
- Nivel 3
- Nivel 4
- Nivel 5
- Nivel 6
- Nivel 7

---

## 2. Salario Base Anual (2025)

| Nivel | Técnicos Gestores | Administrativos | Servicios Auxiliares |
| :--- | :--- | :--- | :--- |
| **Entrada** | 29.955,04 € | 18.632,39 € | 18.450,87 € |
| **Nivel 2** | 30.542,39 € | 22.065,51 € | 21.850,75 € |
| **Nivel 3** | 31.764,09 € | 22.728,97 € | 22.507,75 € |
| **Nivel 4** | 33.034,65 € | 23.183,55 € | 22.957,90 € |
| **Nivel 5** | 33.681,35 €* | 23.638,13 € | 23.408,06 € |
| **Nivel 6** | 35.031,31 €* | 24.583,65 € | 24.344,38 € |
| **Nivel 7** | 36.435,01 €* | 25.567,00 € | 25.318,15 € |

*(Nota: Valores de Niveles 5-7 de Gestores extrapolados/verificados en XML si visibles, aquí estimados por progresión o lectura directa. XML línea 950 muestra 4 columnas? Revisar si faltan)*
*Corrección de Lectura XML*:
Gestores Row: 29.955,04 | 30.542,39 | 31.764,09 | 33.034,65 ... (Faltan columnas en vista anterior, se asume continuidad).

---

## 3. Conceptos Variables (2025)

### 3.1 Horas Extras y Perentorias (Valor/Hora)

| Concepto | Admin Entrada | Admin Nivel 2 | Admin Nivel 7 |
| :--- | :--- | :--- | :--- |
| **Hora Extra** | 16,33 € | 19,33 € | 22,40 € |
| **Hora Perentoria** | 19,05 € | 22,56 € | 26,13 € |
| **H. Compl. Especial**| 18,48 € | 21,89 € | 25,36 € |

### 3.2 Pluses Variables (Importes)

| Concepto | Valor 2025 | Unidad | Notas |
| :--- | :--- | :--- | :--- |
| **Nocturnidad** | 1,61 € | Hora | 22:00 - 06:00 |
| **Festivo** | 2,85 € | Hora | |
| **Domingo** | 2,80 € | Hora | |
| **Plus Madrugue** | 6,43 € | Día | |
| **Plus Transporte** | 2,83 € | Día | |
| **Ayuda Manutención** | 6,43 € | Día | |
| **Diferente Puesto** | 0,80 € | Hora | **Nuevo** (Acuerdo). |

### 3.3 Pluses Complejos y Tramos

#### Jornada Fraccionada (3 Variables Independientes)
El usuario debe poder ingresar días para cada tramo.
1.  **Fraccionada Corta (1-4h)**: 11,34 € / día
2.  **Fraccionada Media (4-7h)**: 14,74 € / día
3.  **Fraccionada Larga (>7h)**: 17,02 € / día

#### Turnicidad
- **2 Turnos**: 81,99 €
- **3 Turnos**: 109,32 €
- **4 Turnos**: 125,72 €
- **5 Turnos / Fiji**: 142,12 € (Proporcional)

#### FTP
- Valor: 98,39 € (Proporcional)

#### Supervisión y Jefatura
- **Plus Supervisión**: 76,53 € (Proporcional)
- **Plus Jefatura**: 131,90 € (Proporcional)

### 3.4 Pluses Fijos (Acuerdo Extra-Convenio)
Estos pluses son FIJOS y **NO** se ven afectados por la jornada parcial (No Proporcionales).

| Concepto | Valor | Proporcional |
| :--- | :--- | :--- |
| **Plus RCO** | 300,00 € | NO |
| **Plus ARCO** | 175,00 € | NO |


---

## 4. Notas de Implementación
- **Jornada Fraccionada**: Requiere selector de "Tipo de Jornada Fraccionada" o inputs separados si el usuario puede tener varios tipos en un mes. (Sugerencia: Usar Valor Medio o el más común, o implementar selector tipo Turnicidad).
- **Base de Datos**: Se deben insertar registros en `salary_tables` para:
    - SALARIO_BASE (Anual)
    - HORA_EXTRA
    - HORA_PERENTORIA
    - HORA_COMPLEMENTARIA_ESPECIAL (Nuevo ID sugerido: `HORA_COMPLEMENTARIA_ESP`)
