import pandas as pd
import matplotlib.pyplot as plt
import os


CSV_FILE = "search_runs.csv"
CHARTS_FOLDER = "results_charts"

os.makedirs(CHARTS_FOLDER, exist_ok=True)
TIMEOUT_SECONDS = 120


def load_and_clean_data(filepath):
    """Loads the CSV and creates combined labels for the algorithms."""
    df = pd.read_csv(filepath)

    df['heuristic'] = df['heuristic'].fillna("None")

    def create_label(row):
        if row['search_method'].lower() in ['a*', 'greedy'] and row['heuristic'] != "None":
            return f"{row['search_method'].upper()} ({row['heuristic']})"
        return row['search_method'].upper()

    df['full_method'] = df.apply(create_label, axis=1)

    df['processing_time_seconds'] = pd.to_numeric(df['processing_time_seconds'], errors='coerce')
    df['expanded_nodes'] = pd.to_numeric(df['expanded_nodes'], errors='coerce')
    df['frontier_nodes_inserted'] = pd.to_numeric(df['frontier_nodes_inserted'], errors='coerce')

    return df


# ====================================
# SET 1: INDIVIDUAL METRICS PER LEVEL
# ====================================
def plot_metrics_per_level(df, level_name):
    """Generates 3 separate image files (Time, Expanded, Frontier) for a specific level."""
    df_map = df[df['level_name'] == level_name].copy()

    if df_map.empty:
        print(f"No data found for map: {level_name}")
        return

    df_grouped = df_map.groupby('full_method').agg(
        time=('processing_time_seconds', 'mean'),
        expanded_nodes=('expanded_nodes', 'mean'),
        frontier_nodes=('frontier_nodes_inserted', 'mean'),
        result=('result', lambda x: x.mode()[0])
    ).reset_index()

    methods = df_grouped['full_method']
    results = df_grouped['result']

    time_colors = ['skyblue' if str(r).lower() == 'success' else 'salmon' if str(r).lower() == 'timeout' else 'silver'
                   for r in results]

    # ---------------------------------------------------------
    # 1. INDIVIDUAL CHART: Processing Time
    # ---------------------------------------------------------
    plt.figure(figsize=(8, 6))
    bars_t = plt.bar(methods, df_grouped['time'], color=time_colors, edgecolor='black')
    plt.ylabel("Seconds", fontsize=12)
    plt.axhline(y=TIMEOUT_SECONDS, color='red', linestyle='--', alpha=0.5, label=f"Timeout Limit ({TIMEOUT_SECONDS}s)")
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.xticks(rotation=25, ha='right', fontsize=10)
    plt.legend()

    for i, bar in enumerate(bars_t):
        height = bar.get_height()
        text = f"{height:.1f}s"
        if str(results.iloc[i]).lower() == 'timeout':
            text = "T.O.\n" + text
        elif str(results.iloc[i]).lower() == 'oom':
            text = "OOM\n" + text
        plt.annotate(text, xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_FOLDER, f"time_{level_name}.png"), dpi=300)
    plt.close()

    # ---------------------------------------------------------
    # 2. INDIVIDUAL CHART: Expanded Nodes
    # ---------------------------------------------------------
    plt.figure(figsize=(8, 6))
    bars_e = plt.bar(methods, df_grouped['expanded_nodes'], color='orange', edgecolor='black')
    plt.ylabel("Node Count", fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.xticks(rotation=25, ha='right', fontsize=10)

    for bar in bars_e:
        height = bar.get_height()
        if pd.notna(height):
            plt.annotate(f"{int(height):,}", xy=(bar.get_x() + bar.get_width() / 2, height),
                         xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_FOLDER, f"expanded_nodes_{level_name}.png"), dpi=300)
    plt.close()

    # ---------------------------------------------------------
    # 3. INDIVIDUAL CHART: Frontier Nodes
    # ---------------------------------------------------------
    plt.figure(figsize=(8, 6))
    bars_f = plt.bar(methods, df_grouped['frontier_nodes'], color='mediumpurple', edgecolor='black')
    plt.ylabel("Node Count", fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.xticks(rotation=25, ha='right', fontsize=10)

    for bar in bars_f:
        height = bar.get_height()
        if pd.notna(height):
            plt.annotate(f"{int(height):,}", xy=(bar.get_x() + bar.get_width() / 2, height),
                         xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_FOLDER, f"frontier_nodes_{level_name}.png"), dpi=300)
    plt.close()

    print(f"Saved 3 individual charts (Time, Expanded, Frontier) for {level_name}.")


# =====================================================================
# CHART SET 2: SCALABILITY LINES (INDIVIDUAL GRAPHS PER ALGORITHM)
# =====================================================================
def plot_algorithm_individual_lines(df, difficulty_map):
    """Generates a separate line chart image for EACH algorithm's execution time."""
    df['difficulty'] = df['level_name'].map(difficulty_map)
    df = df.dropna(subset=['difficulty'])  # Ignore levels not in our top 10

    df_grouped = df.groupby(['level_name', 'difficulty', 'full_method']).agg(
        time=('processing_time_seconds', 'mean')
    ).reset_index()

    df_grouped = df_grouped.sort_values(by='difficulty')

    unique_methods = df_grouped['full_method'].unique()

    for method in unique_methods:
        method_data = df_grouped[df_grouped['full_method'] == method]

        plt.figure(figsize=(8, 6))

        # Plot the line for this specific algorithm
        plt.plot(method_data['difficulty'], method_data['time'],
                 marker='o', linewidth=2, markersize=8, color='dodgerblue', alpha=0.8, label=method)

        # Formatting the Axis
        plt.title(f"Scalability Progression: {method}", fontsize=14, fontweight='bold')
        plt.xlabel("Difficulty Score (Moves + 20*Boxes)", fontsize=12)
        plt.ylabel("Average Time (Seconds)", fontsize=12)
        plt.axhline(y=TIMEOUT_SECONDS, color='red', linestyle='--', alpha=0.5,
                    label=f'Timeout Limit ({TIMEOUT_SECONDS}s)')

        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()

        # Sanitize the method name so it can be saved as a valid filename
        # E.g., "A* (hungarian)" becomes "Astar_hungarian"
        safe_filename = method.replace('*', 'star').replace(' ', '_').replace('(', '').replace(')', '')

        output_path = os.path.join(CHARTS_FOLDER, f"scalability_time_{safe_filename}.png")
        plt.savefig(output_path, dpi=300)
        plt.close()

        print(f"Scalability line chart saved for {method}: {output_path}")

# =====================================================================
# MAIN EXECUTION
# =====================================================================
if __name__ == "__main__":
    if not os.path.exists(CSV_FILE):
        print(f"File {CSV_FILE} not found. Please run your experiment first.")
    else:
        df_results = load_and_clean_data(CSV_FILE)

        levels_to_plot = ['LEVEL1', 'LEVEL3']
        for level in levels_to_plot:
            plot_metrics_per_level(df_results, level)

        CALCULATED_DIFFICULTIES = {
            'LEVEL1': 110,
            'LEVEL3': 250,
        }

        plot_algorithm_individual_lines(df_results, CALCULATED_DIFFICULTIES)
        print("\nAll charts generated successfully! Check the 'results_charts' folder.")