# TP1 — Motor de Búsqueda sobre Sokoban

**72.27 — Sistemas de Inteligencia Artificial · Grupo 9**

---

## Índice

1. [Descripción](#descripción)
2. [Configuración del entorno](#configuración-del-entorno)
3. [Archivos del proyecto](#archivos-del-proyecto)
4. [Ejecución](#ejecución)
5. [Configuración del motor de búsqueda](#configuración-del-motor-de-búsqueda)

---

## Descripción

Implementación de un motor de búsqueda que resuelve niveles del juego Sokoban. Soporta los métodos de búsqueda **BFS**, **DFS**, **Greedy** y **A\***, con heurísticas **Manhattan** y **Húngara**. Incluye visualización con pygame, registro de métricas en CSV y generación automática de gráficos comparativos.

---

## Configuración del entorno

### 1. Crear el entorno virtual

```bash
python -m venv venv
```

### 2. Activar el entorno virtual

**Linux / macOS**
```bash
source venv/bin/activate
```

**Windows (PowerShell)**
```powershell
venv\Scripts\Activate.ps1
```

**Windows (CMD)**
```cmd
venv\Scripts\activate.bat
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

| Paquete      | Versión mínima | Uso                                    |
|--------------|----------------|----------------------------------------|
| `numpy`      | 1.22           | Cálculo de la heurística húngara       |
| `scipy`      | 1.9.0          | Asignación óptima (algoritmo húngaro)  |
| `pygame`     | 2.6            | Visualización gráfica del juego        |
| `pandas`     | 2.0            | Lectura y procesamiento del CSV        |
| `matplotlib` | 3.8            | Generación de gráficos                 |

---

## Archivos del proyecto

```
SIA-TP1/
│
├── main.py                  # Punto de entrada: modo AI o jugador interactivo
├── run_all_solutions.py     # Corre todas las combinaciones algoritmo × nivel N veces
├── generate_graphs.py       # Genera gráficos a partir de search_runs.csv
├── search_run_record.py     # Registro y persistencia de métricas en CSV
│
├── search_methods/
│   ├── config.json          # Configuración por defecto del motor de búsqueda
│   ├── settings.py          # Carga y gestión de la configuración en runtime
│   ├── tree.py              # Lógica del árbol de búsqueda
│   ├── node.py              # Nodo del árbol de búsqueda
│   └── heuristics/
│       ├── Manhattan.py     # Distancia Manhattan como heurística
│       ├── Hungarian.py     # Asignación óptima como heurística
│       └── mixed.py         # Heurística combinada
│
├── sokoban_engine/          # Lógica del juego (tablero, entidades, reglas)
├── sokoban_pygame/          # Visualización con pygame
│
├── resources/
│   └── maps/                # Niveles del juego en formato .txt
│       ├── LEVEL1-86.txt
│       ├── LEVEL2-150.txt
│       ├── LEVEL3-167.txt
│       ├── LEVEL4-210.txt
│       └── LEVEL5-341.txt
│
├── search_runs.csv          # Generado automáticamente al correr búsquedas
└── results_charts/          # Generado automáticamente por generate_graphs.py
```

---

## Ejecución

### Corrida individual — `main.py`

Ejecuta el motor de búsqueda sobre un nivel y algoritmo específicos.

```bash
python main.py [opciones]
```

| Flag | Valores posibles | Por defecto | Descripción |
|------|-----------------|-------------|-------------|
| `--mode` | `ai`, `player` | `ai` | `ai`: el motor resuelve el nivel; `player`: modo interactivo WASD |
| `--search-method` | `bfs`, `dfs`, `greedy`, `a*` | según `config.json` | Algoritmo de búsqueda |
| `--heuristic` | `manhattan`, `hungarian`, `mixed` | según `config.json` | Heurística (solo para `greedy` y `a*`) |
| `--map` | ruta al `.txt` | `LEVEL1-86.txt` | Nivel a resolver |
| `--replay` | — | desactivado | Anima la solución en pygame al finalizar |
| `--config` | ruta al `.json` | `search_methods/config.json` | Archivo de configuración alternativo |

**Ejemplos:**

```bash
# A* con heurística húngara sobre el nivel 2, con animación
python main.py --search-method a* --heuristic hungarian --map resources/maps/LEVEL2-150.txt --replay

# BFS sobre el nivel 1 (sin animación)
python main.py --search-method bfs --map resources/maps/LEVEL1-86.txt

# Modo jugador interactivo
python main.py --mode player --map resources/maps/LEVEL1-86.txt
```

Cada corrida escribe un registro en `search_runs.csv` con las métricas de la búsqueda (tiempo, nodos expandidos, costo de la solución, etc.). Si el archivo ya existe, el registro se agrega al final.

---

### Corrida masiva — `run_all_solutions.py`

Ejecuta **todas** las combinaciones de algoritmo × heurística × nivel, **10 veces cada una**, y acumula los resultados en `search_runs.csv`. Este es el paso previo a la generación de gráficos.

```bash
python run_all_solutions.py [opciones]
```

| Flag | Por defecto | Descripción |
|------|-------------|-------------|
| `--runs N` | `10` | Número de repeticiones por combinación |
| `--continue-on-error` | desactivado | Continúa aunque alguna corrida falle |
| `--replay` | desactivado | Activa la animación pygame en cada corrida |

**Ejemplo:**

```bash
python run_all_solutions.py
```

Salida esperada:

```
┌──────────────────────────────────────────────────────────┐
│                  SIA-TP1  ·  BULK SOLVER                 │
└──────────────────────────────────────────────────────────┘

  Levels       : 5
  Combos       : 30
  Runs / combo : 10
  Total runs   : 300

────────────────────────────────────────────────────────────
  [1/30]    LEVEL1-86.txt  ·  bfs  ·  —
────────────────────────────────────────────────────────────
    ▶  run  1/10  ·  ok   (0.423s)
    ▶  run  2/10  ·  ok   (0.418s)
    ...
  ✓  10/10 passed

════════════════════════════════════════════════════════════
  DONE  ·  300 runs  ·  300 ok  ·  ALL PASSED
════════════════════════════════════════════════════════════
```

> **Nota:** Este paso puede tardar varios minutos dependiendo del hardware y del tiempo límite configurado por nivel.

---

### Generación de gráficos — `generate_graphs.py`

Lee `search_runs.csv` y produce todos los gráficos comparativos en la carpeta `results_charts/`.

> **Requisito:** ejecutar primero `run_all_solutions.py` para que exista el archivo `search_runs.csv`.

```bash
# Paso 1: generar los datos
python run_all_solutions.py

# Paso 2: generar los gráficos
python generate_graphs.py
```

Se generan dos conjuntos de gráficos:

**Por nivel** — 4 archivos PNG por cada uno de los 5 niveles:

| Archivo | Métrica |
|---------|---------|
| `time_<NIVEL>.png` | Tiempo de procesamiento promedio por algoritmo |
| `expanded_nodes_<NIVEL>.png` | Nodos expandidos promedio por algoritmo |
| `frontier_nodes_<NIVEL>.png` | Nodos insertados en la frontera por algoritmo |
| `cost_bars_<NIVEL>.png` | Costo de la solución por algoritmo |

**De escalabilidad** — 1 archivo PNG por algoritmo:

| Archivo | Descripción |
|---------|-------------|
| `scalability_time_<ALGORITMO>.png` | Tiempo promedio vs. dificultad del nivel, con barras de error estándar |

Todos los archivos se guardan en `results_charts/`.

---

## Configuración del motor de búsqueda

El archivo `search_methods/config.json` define los parámetros por defecto:

```json
{
  "search_method": "a*",
  "heuristic": "hungarian",
  "max_tree_depth": 10000,
  "search_timeout_seconds": 150
}
```

| Campo | Descripción |
|-------|-------------|
| `search_method` | Algoritmo por defecto: `bfs`, `dfs`, `greedy`, `a*` |
| `heuristic` | Heurística por defecto para métodos informados |
| `max_tree_depth` | Profundidad máxima del árbol de búsqueda |
| `search_timeout_seconds` | Tiempo límite por corrida en segundos |

Cualquier valor en `config.json` puede sobreescribirse con los flags de `main.py`.
