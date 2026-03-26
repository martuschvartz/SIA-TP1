import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os


# =============================================================================
# CONFIGURACIÓN GLOBAL
# Estas constantes definen dónde están los datos de entrada y dónde se guardan
# los gráficos generados. Cambiar estas variables afecta todo el script.
# =============================================================================

# Nombre del archivo CSV que contiene los resultados de las corridas de búsqueda.
# Este archivo lo genera run_all_solutions.py / search_run_record.py.
INPUT_CSV_FILEPATH = "search_runs.csv"

# Carpeta donde se van a guardar todas las imágenes PNG generadas.
OUTPUT_CHARTS_FOLDER = "results_charts"

# Valor de timeout
TIMEOUT_VALUE = 1200

# Si la carpeta no existe, la creamos. exist_ok=True evita error si ya existe.
os.makedirs(OUTPUT_CHARTS_FOLDER, exist_ok=True)


# =============================================================================
# FUNCIÓN: load_and_clean_dataframe
# Lee el CSV de resultados y lo prepara para graficar:
#   - Rellena heurísticas vacías (BFS/DFS no usan heurística).
#   - Crea una columna 'full_method' con etiquetas legibles por humanos,
#     ej: "A* (hungarian)", "BFS", "GREEDY (manhattan)".
#   - Convierte columnas numéricas que pandas puede haber leído como texto.
# =============================================================================
def load_and_clean_dataframe(csv_filepath):
    """Carga el CSV y construye etiquetas combinadas para cada algoritmo."""

    # Leemos el archivo CSV completo en un DataFrame de pandas.
    raw_results_dataframe = pd.read_csv(csv_filepath)

    # Los algoritmos sin heurística (BFS, DFS) tienen la columna 'heuristic' vacía (NaN).
    # La reemplazamos por el string "None" para poder comparar con == más adelante.
    raw_results_dataframe['heuristic'] = raw_results_dataframe['heuristic'].fillna("None")

    # -------------------------------------------------------------------------
    # Función interna: build_algorithm_display_label
    # Recibe una fila del DataFrame y devuelve la etiqueta que aparecerá en el
    # eje X de los gráficos.
    # Ejemplo de resultado:
    #   - BFS              → "BFS"
    #   - A* con hungarian → "A* (hungarian)"
    #   - GREEDY con mixed → "GREEDY (mixed)"
    # -------------------------------------------------------------------------
    def build_algorithm_display_label(dataframe_row):
        # Solo A* y Greedy tienen heurística; el resto muestra solo el nombre del método.
        if dataframe_row['search_method'].lower() in ['a*', 'greedy'] and dataframe_row['heuristic'] != "None":
            return f"{dataframe_row['search_method'].upper()} ({dataframe_row['heuristic']})"
        return dataframe_row['search_method'].upper()

    # Aplicamos build_algorithm_display_label a cada fila y guardamos el resultado en
    # una nueva columna 'full_method'. axis=1 significa "aplicar por fila".
    raw_results_dataframe['full_method'] = raw_results_dataframe.apply(build_algorithm_display_label, axis=1)

    # Convertimos las columnas numéricas clave a tipo numérico.
    # errors='coerce' convierte valores no-numéricos (texto roto, vacíos) a NaN
    # en lugar de lanzar una excepción.
    raw_results_dataframe['processing_time_seconds'] = pd.to_numeric(raw_results_dataframe['processing_time_seconds'], errors='coerce')
    raw_results_dataframe['expanded_nodes']           = pd.to_numeric(raw_results_dataframe['expanded_nodes'],           errors='coerce')
    raw_results_dataframe['frontier_nodes_inserted']  = pd.to_numeric(raw_results_dataframe['frontier_nodes_inserted'],  errors='coerce')
    raw_results_dataframe['solution_cost'] = pd.to_numeric(raw_results_dataframe['solution_cost'], errors='coerce')

    return raw_results_dataframe.drop_duplicates()


import math

# =============================================================================
# FUNCIÓN: get_scale
# Calcula el límite máximo para usar en el eje y en función del timeout
# =============================================================================

import math

import math

def get_scale(max_value):
    """
    Calcula un límite superior para el eje Y.
    Toma el valor máximo observado en los datos y retorna
    un valor mayor o igual a max_value, redondeada un número "lindo".
    """

    # Caso borde: si el valor es 0 o inválido, se devuelve la escala mínima
    if pd.isna(max_value) or max_value <= 0:
        return 1

    # -----------------------------------------------------------------------------------
    # Paso 1: encontrar el orden de magnitud del número -> en qué escala estoy trabajando
    # Ej: si el nro es 1.2 estoy trabajando en 10^0 -> orden magnitud = 1
    # -----------------------------------------------------------------------------------
    magnitude = 10 ** math.floor(math.log10(max_value))

    # ---------------------------------------------------------------------
    # Paso 2: normalizar el valor
    # Dividimos por la magnitud para llevar el número al rango [1, 10)
    # ---------------------------------------------------------------------
    normalized = max_value / magnitude

    # -----------------------------------------------------
    # Paso 3: Se elige un número de la siguiente secuencia
    #
    # Se usa la secuencia:
    #   1, 2, 5, 10
    # -----------------------------------------------------
    if normalized <= 1:
        nice = 1
    elif normalized <= 2:
        nice = 2
    elif normalized <= 5:
        nice = 5
    else:
        nice = 10

    # --------------------------------------------------------
    # Paso 4: Se multiplica el número "lindo" por la magnitud
    # para llevarlo a la escala original del valor máximo
    # --------------------------------------------------------
    return nice * magnitude

# =============================================================================
# SET DE GRÁFICOS 1: MÉTRICAS INDIVIDUALES POR NIVEL
# Para un nivel dado, genera 3 archivos PNG separados:
#   1. Tiempo de procesamiento por algoritmo.
#   2. Nodos expandidos por algoritmo.
#   3. Nodos insertados en la frontera por algoritmo.
#   4. Costo hasta la solución por algoritmo
# =============================================================================
def plot_individual_metrics_per_level(full_results_dataframe, target_level_name):
    """Genera 3 imágenes separadas (Tiempo, Expandidos, Frontera) para un nivel."""

    # Filtramos el DataFrame completo para quedarnos solo con las filas
    # que corresponden al nivel que nos interesa.
    # .copy() evita el warning de pandas sobre modificar una vista.
    single_level_dataframe = full_results_dataframe[full_results_dataframe['level_name'] == target_level_name].copy()

    # Si no hay datos para este nivel, avisamos y salimos sin generar nada.
    if single_level_dataframe.empty:
        print(f"No se encontraron datos para el mapa: {target_level_name}")
        return

    # -------------------------------------------------------------------------
    # Agrupamos por algoritmo (full_method) y calculamos el promedio de cada
    # métrica numérica. Para 'result' (éxito/timeout/oom) tomamos la moda,
    # es decir, el resultado más frecuente en las corridas de ese algoritmo.
    # reset_index() convierte el índice de agrupación de vuelta a columna normal.
    # -------------------------------------------------------------------------
    per_algorithm_aggregated_stats = single_level_dataframe.groupby('full_method').agg(
        time=('processing_time_seconds', 'mean'),
        max_time=('processing_time_seconds', 'max'),
        expanded_nodes=('expanded_nodes', 'mean'),
        expanded_nodes_max=('expanded_nodes', 'max'),
        frontier_nodes=('frontier_nodes_inserted', 'mean'),
        frontier_nodes_max=('frontier_nodes_inserted', 'max'),
        cost=('solution_cost', 'mean'),
        cost_max=('solution_cost', 'max'),
        result=('result', lambda x: x.mode()[0])
    ).reset_index()

    # Extraemos las columnas que más usamos como Series de pandas.
    algorithm_name_labels = per_algorithm_aggregated_stats['full_method']
    algorithm_result_labels = per_algorithm_aggregated_stats['result']

    # -------------------------------------------------------------------------
    # Definimos los colores de las barras de TIEMPO según el resultado:
    #   - 'success' → azul cielo (la búsqueda terminó bien)
    #   - 'timeout' → salmón     (se agotó el tiempo)
    #   - cualquier otra cosa (ej: 'oom') → gris plata
    # Usamos una list comprehension para construir la lista de colores en orden.
    # -------------------------------------------------------------------------
    time_bar_colors_by_result = [
        'skyblue' if str(result).lower() == 'success'
        else 'salmon' if str(result).lower() == 'timeout'
        else 'silver'
        for result in algorithm_result_labels
    ]

    # =========================================================================
    # GRÁFICO 1 de 3: Tiempo de Procesamiento
    # =========================================================================
    plt.figure(figsize=(8, 6))

    # Dibujamos las barras. Cada barra = un algoritmo. El color ya refleja resultado.
    processing_time_bars = plt.bar(
        algorithm_name_labels,
        per_algorithm_aggregated_stats['time'],
        color=time_bar_colors_by_result,
        edgecolor='black'
    )

    plt.ylabel("Seconds", fontsize=12)

    # Se define como la altura máxima el valor mayor de tiempo de procesamiento
    plt.ylim(0, get_scale(per_algorithm_aggregated_stats['time'].max()))

    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.xticks(rotation=25, ha='right', fontsize=10)

    # Anotamos cada barra con su valor numérico encima.
    for bar_index, time_bar in enumerate(processing_time_bars):
        bar_height_value = time_bar.get_height()

        # Etiqueta base: el tiempo en segundos con decimales según el número.
        if bar_height_value < 0.01:
            bar_annotation_text = f"{bar_height_value:.4f}s"
        elif bar_height_value < 1:
            bar_annotation_text = f"{bar_height_value:.3f}s"
        else:
            bar_annotation_text = f"{bar_height_value:.2f}s"

        # Si el resultado fue timeout u OOM, lo indicamos explícitamente
        # encima del número para que sea obvio al leer el gráfico.
        if str(algorithm_result_labels.iloc[bar_index]).lower() == 'timeout':
            bar_annotation_text = "T.O.\n" + bar_annotation_text
        elif str(algorithm_result_labels.iloc[bar_index]).lower() == 'oom':
            bar_annotation_text = "OOM\n" + bar_annotation_text

        # Colocamos la etiqueta 3 puntos por encima del tope de la barra.
        plt.annotate(
            bar_annotation_text,
            xy=(time_bar.get_x() + time_bar.get_width() / 2, bar_height_value),
            xytext=(0, 3),
            textcoords="offset points",
            ha='center',
            va='bottom',
            fontsize=10
        )

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_CHARTS_FOLDER, f"time_{target_level_name}.png"), dpi=300)
    plt.close()  # Cerramos la figura para liberar memoria antes del siguiente gráfico.

    # =========================================================================
    # GRÁFICO 2 de 3: Nodos Expandidos
    # Un nodo "expandido" es aquel que fue sacado de la frontera y procesado.
    # Cuantos más nodos expande un algoritmo, más trabajo hizo.
    # =========================================================================
    plt.figure(figsize=(8, 6))

    # Todas las barras en naranja; aquí no hay distinción por resultado.
    expanded_nodes_bars = plt.bar(
        algorithm_name_labels, per_algorithm_aggregated_stats['expanded_nodes'], color='orange', edgecolor='black'
    )

    # Se define como la altura máxima el valor mayor de nodos expandidos
    plt.ylim(0, get_scale(per_algorithm_aggregated_stats['expanded_nodes_max'].max()))

    plt.ylabel("Expanded Nodes Count", fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.xticks(rotation=25, ha='right', fontsize=10)

    # Anotamos el valor entero con separador de miles (ej: 1,234,567) encima de cada barra.
    for expanded_nodes_bar in expanded_nodes_bars:
        bar_height_value = expanded_nodes_bar.get_height()
        # pd.notna verifica que el valor no sea NaN (puede pasar si hubo timeout).
        if pd.notna(bar_height_value):
            plt.annotate(
                f"{int(bar_height_value):,}",
                xy=(expanded_nodes_bar.get_x() + expanded_nodes_bar.get_width() / 2, bar_height_value),
                xytext=(0, 3),
                textcoords="offset points",
                ha='center',
                va='bottom',
                fontsize=10
            )

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_CHARTS_FOLDER, f"expanded_nodes_{target_level_name}.png"), dpi=300)
    plt.close()

    # =========================================================================
    # GRÁFICO 3 de 4: Nodos Insertados en la Frontera
    # La frontera es la estructura (cola, pila, heap) que contiene los nodos
    # pendientes de expandir. Este contador mide cuántos nodos fueron
    # añadidos en total durante toda la búsqueda.
    # =========================================================================
    plt.figure(figsize=(8, 6))

    frontier_nodes_bars = plt.bar(
        algorithm_name_labels, per_algorithm_aggregated_stats['frontier_nodes'], color='mediumpurple', edgecolor='black'
    )

    # Se define como la altura máxima el valor máximo de nodos frontera
    plt.ylim(0, get_scale(per_algorithm_aggregated_stats['frontier_nodes_max'].max()))

    plt.ylabel("Frontier Nodes Count", fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.xticks(rotation=25, ha='right', fontsize=10)

    for frontier_nodes_bar in frontier_nodes_bars:
        bar_height_value = frontier_nodes_bar.get_height()
        if pd.notna(bar_height_value):
            plt.annotate(
                f"{int(bar_height_value):,}",
                xy=(frontier_nodes_bar.get_x() + frontier_nodes_bar.get_width() / 2, bar_height_value),
                xytext=(0, 3),
                textcoords="offset points",
                ha='center',
                va='bottom',
                fontsize=10
            )

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_CHARTS_FOLDER, f"frontier_nodes_{target_level_name}.png"), dpi=300)
    plt.close()

    # =========================================================================
    # GRÁFICO 4 de 4: Costo hasta la solución
    # El costo hacia la solución es la cantidad de movimientos realizados
    # =========================================================================
    plt.figure(figsize=(8, 6))

    cost_bars = plt.bar(
        algorithm_name_labels, per_algorithm_aggregated_stats['cost'], color='palegreen', edgecolor='black'
    )

    # Se define como la altura máxima el valor máximo de solución
    plt.ylim(0, get_scale(per_algorithm_aggregated_stats['cost_max'].max()))

    plt.ylabel("Solution Cost", fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.xticks(rotation=25, ha='right', fontsize=10)

    for i, bar in enumerate(cost_bars):
        h = bar.get_height()

        if pd.notna(h) and h > 0:
            # Caso Éxito: Mostramos el costo numérico
            plt.annotate(f"{int(h):,}", xy=(bar.get_x() + bar.get_width() / 2, h),
                         xytext=(0, 3), textcoords="offset points", ha='center', va='bottom')
        else:
            # Caso Fallo (NaN): Sería cuando no se encontró una solución
            result_label = str(algorithm_result_labels.iloc[i]).upper()
            plt.annotate(f"no solution\n({result_label})",
                         xy=(bar.get_x() + bar.get_width() / 2, 0),
                         xytext=(0, 5), textcoords="offset points",
                         ha='center', va='bottom', color='red',
                         fontweight='bold', fontsize=8)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_CHARTS_FOLDER, f"cost_bars_{target_level_name}.png"), dpi=300)
    plt.close()

    print(f"Guardados 4 gráficos individuales (Tiempo, Expandidos, Frontera, Costos) para {target_level_name}.")


# =============================================================================
# SET DE GRÁFICOS 2: ESCALABILIDAD — UNA LÍNEA POR ALGORITMO
# Muestra cómo aumenta el tiempo de cada algoritmo a medida que el nivel
# se vuelve más difícil. Genera UN archivo PNG por algoritmo.
#
# El "score de dificultad" es un número calculado externamente que combina
# la longitud de la solución óptima y la cantidad de cajas, por ejemplo:
#   dificultad = movimientos_solución + 20 * cantidad_de_cajas
# =============================================================================
def plot_scalability_line_per_algorithm(full_results_dataframe, level_name_to_difficulty_score_map):
    """Genera un gráfico de líneas de tiempo vs dificultad para CADA algoritmo."""

    # Agregamos una columna 'difficulty' mapeando el nombre del nivel a su score numérico.
    # Los niveles que no estén en level_name_to_difficulty_score_map quedarán con NaN.
    full_results_dataframe['difficulty'] = full_results_dataframe['level_name'].map(level_name_to_difficulty_score_map)

    # Descartamos las filas de niveles que no están en nuestro mapa de dificultades.
    # Son niveles extras que no queremos mostrar en el gráfico de escalabilidad.
    full_results_dataframe = full_results_dataframe.dropna(subset=['difficulty'])

    # Agrupamos por (nombre_nivel, dificultad, algoritmo) y promediamos el tiempo. Se agrega
    # también los valores de desvío estándar y de cantidad de corridas para poder calcular luego el error.
    # Incluimos 'difficulty' en el groupby para que quede disponible en el resultado.
    per_level_per_algorithm_aggregated_stats = full_results_dataframe.groupby(['level_name', 'difficulty', 'full_method']).agg(
        time_mean=('processing_time_seconds', 'mean'),
        time_std=('processing_time_seconds', 'std'),
        n_runs=('processing_time_seconds', 'count')
    ).reset_index()

    # Ordenamos por dificultad ascendente para que la línea vaya de izquierda
    # (fácil) a derecha (difícil).
    per_level_per_algorithm_aggregated_stats = per_level_per_algorithm_aggregated_stats.sort_values(by='difficulty')

    # Se agrega una nueva columna para el error
    per_level_per_algorithm_aggregated_stats['time_se'] = (
            per_level_per_algorithm_aggregated_stats['time_std'] /
            np.sqrt(per_level_per_algorithm_aggregated_stats['n_runs'])
    )

    # Obtenemos la lista de algoritmos únicos para iterar y generar un PNG por cada uno.
    unique_algorithm_method_names = per_level_per_algorithm_aggregated_stats['full_method'].unique()

    for algorithm_method_name in unique_algorithm_method_names:
        # Filtramos solo las filas de este algoritmo en particular.
        single_algorithm_dataframe = per_level_per_algorithm_aggregated_stats[
            per_level_per_algorithm_aggregated_stats['full_method'] == algorithm_method_name
        ]

        plt.figure(figsize=(8, 6))

        # Dibujamos la línea. El eje X es el score de dificultad; el Y es el tiempo promedio.
        # marker='o' pone un punto en cada nivel medido. Se agregan las barras de error
        plt.errorbar(
            single_algorithm_dataframe['difficulty'],
            single_algorithm_dataframe['time_mean'],
            yerr=single_algorithm_dataframe['time_se'],
            marker='o',
            linewidth=2,
            markersize=8,
            capsize=5
        )

        plt.ylim(0, get_scale(single_algorithm_dataframe['time_mean'].max()))
        plt.title(f"Scalability Progression: {algorithm_method_name}", fontsize=14, fontweight='bold')
        plt.xlabel("Difficulty Score (Moves + 20*Boxes)", fontsize=12)
        plt.ylabel("Average Time (Seconds)", fontsize=12)

        # Línea roja de referencia del timeout, igual que en los gráficos de barras.
        plt.axhline(
            y=TIMEOUT_VALUE,
            color='red',
            linestyle='--',
            alpha=0.5,
            label=f'Timeout Limit ({TIMEOUT_VALUE}s)'
        )

        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()

        # ---------------------------------------------------------------------
        # Sanitizamos el nombre del algoritmo para usarlo como nombre de archivo.
        # Los caracteres especiales como '*', espacios, paréntesis no son válidos
        # en nombres de archivo en Windows/Linux.
        # Ejemplo: "A* (hungarian)" → "Astar_hungarian"
        # ---------------------------------------------------------------------
        sanitized_algorithm_name_for_filename = (
            algorithm_method_name
            .replace('*', 'star')
            .replace(' ', '_')
            .replace('(', '')
            .replace(')', '')
        )

        output_chart_filepath = os.path.join(OUTPUT_CHARTS_FOLDER, f"scalability_time_{sanitized_algorithm_name_for_filename}.png")
        plt.savefig(output_chart_filepath, dpi=300)
        plt.close()

        print(f"Gráfico de escalabilidad guardado para {algorithm_method_name}: {output_chart_filepath}")


# =============================================================================
# PUNTO DE ENTRADA PRINCIPAL
# Solo se ejecuta cuando corremos este archivo directamente (python generate_graphs.py).
# Si otro módulo lo importa, este bloque no se ejecuta.
# =============================================================================
if __name__ == "__main__":

    # Verificamos que el archivo CSV exista antes de intentar abrirlo.
    if not os.path.exists(INPUT_CSV_FILEPATH):
        print(f"Archivo {INPUT_CSV_FILEPATH} no encontrado. Primero corré los experimentos.")
    else:
        # Cargamos y limpiamos todos los datos del CSV.
        cleaned_results_dataframe = load_and_clean_dataframe(INPUT_CSV_FILEPATH)

        # -----------------------------------------------------------------
        # SET 1: Gráficos de barras por nivel.
        # Agregamos aquí todos los niveles para los que queremos generar
        # los 3 gráficos individuales (tiempo, expandidos, frontera).
        # -----------------------------------------------------------------
        levels_to_plot = [
            'LEVEL1-86',
            'LEVEL2-150',
            'LEVEL3-167',
            'LEVEL4-210',
            'LEVEL5-341'
        ]
        for level_name in levels_to_plot:
            plot_individual_metrics_per_level(cleaned_results_dataframe, level_name)

        # -----------------------------------------------------------------
        # SET 2: Gráficos de escalabilidad por algoritmo.
        # El diccionario mapea nombre_nivel → score_de_dificultad.
        # El score es un número que refleja qué tan difícil es el nivel;
        # permite ordenar los niveles en el eje X del gráfico de líneas.
        # -----------------------------------------------------------------
        CALCULATED_LEVEL_DIFFICULTY_SCORES = {
            'LEVEL1-86' : 86,
            'LEVEL2-150': 150,
            'LEVEL3-167': 167,
            'LEVEL4-210': 210,
            'LEVEL5-341': 341 
        }

        plot_scalability_line_per_algorithm(cleaned_results_dataframe, CALCULATED_LEVEL_DIFFICULTY_SCORES)
        print("\n¡Todos los gráficos generados exitosamente! Revisá la carpeta 'results_charts'.")
