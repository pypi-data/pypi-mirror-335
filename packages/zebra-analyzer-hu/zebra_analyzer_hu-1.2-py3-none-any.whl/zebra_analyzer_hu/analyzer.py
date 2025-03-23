import os
import subprocess
import pandas as pd
import re
from pathlib import Path
import matplotlib.pyplot as plt
from itertools import cycle
from adjustText import adjust_text
from .utils import sanitize_filename
import importlib.resources as pkg_resources


class ZebraSimulationAnalyzer:
    def __init__(self, input_templates, zebra_dir=None, columns_primary=None, columns_primary_plot=None):
        """
        :param input_templates: Sözlük şeklinde simülasyon isimleri ve input şablonları.
        :param zebra_dir: Zebra dosyalarının bulunduğu dizin. Verilmezse kütüphaneye dahili zebra_files kullanılır.
        :param columns_primary: Birincil veri sütunları.
        :param columns_primary_plot: Grafik çizimi için kullanılacak sütunlar.
        """
        self.input_templates = input_templates

        # Eğer kullanıcı zebra_dir belirtmemişse, kütüphaneye dahil zebra_files klasörünü kullan.
        if zebra_dir is None:
            # Kütüphanedeki zebra_files klasörünü elde et:
            self.zebra_dir = Path(pkg_resources.files("zebra_analyzer_hu").joinpath("zebra_files_hu"))
        else:
            self.zebra_dir = Path(zebra_dir)

        self.columns_primary = columns_primary or [
            "Distance (ft)", "Coolant Temperature (°F) ", "Clad Outside Temperature (°F)",
            "Clad Inside Temperature (°F)", "Gap Temperature (°F)", "Fuel Surface Temperature (°F)",
            "Fuel Centerline Temperature (°F)", "Heat Flux (BTU/hr-ft²)",
            "Critical Power (BTU/hr-ft²)", "Lin. Heat Gen (kW/ft)",
            "Critical Power Ratio", "Coolant Quality", "Pressure Drop (PSI)", "Saturation Temperature (°F)"
        ]
        self.columns_primary_plot = columns_primary_plot or [
            "Coolant Temperature (°F) ", "Clad Outside Temperature (°F)",
            "Fuel Centerline Temperature (°F)", "Critical Power (BTU/hr-ft²)",
            "Critical Power Ratio", "Coolant Quality", "Pressure Drop (PSI)"
        ]
        self.results_dir = self._get_unique_results_dir()
        self.dfs = []
        self.labels = []
        print(f"Results will be saved in: {self.results_dir}")



    def _get_unique_results_dir(self):
        # Kullanıcının masaüstü dizinini elde et
        desktop_dir = Path(os.path.expanduser("~/Desktop"))
        base_results_dir = desktop_dir / "Zebra_Sim_Results"
        base_results_dir.mkdir(parents=True, exist_ok=True)  # Eğer klasör yoksa oluştur

        counter = 1
        while True:
            results_dir = base_results_dir / f"zebra_results_{counter}"
            if not results_dir.exists():
                results_dir.mkdir(parents=True, exist_ok=True)
                return results_dir
            counter += 1

    def _run_zebra_simulation(self, sim_name, input_template):
        input_file = self.zebra_dir / "zebra.in"
        output_file = self.results_dir / f"ZEBRA_{sim_name}.OUT"

        # Kullanıcıdan alınan input şablonunu zebra.in dosyasına yaz
        with open(input_file, "w") as f:
            f.write(input_template)

        print(f"Running ZEBRA simulation for {sim_name}...")

        try:
            # Kütüphane içine dahil edilen ZEBRA.exe'yi çalıştırıyoruz
            subprocess.run(
                str(self.zebra_dir / "ZEBRA.exe"),
                cwd=self.zebra_dir,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            os.rename(self.zebra_dir / "ZEBRA.OUT", output_file)
        except subprocess.CalledProcessError as e:
            print(f"Error running ZEBRA for {sim_name}: {e}")

    def _parse_primary_results(self, file_path):
        if not file_path.exists():
            print(f"Error: {file_path} not found.")
            return None

        data = []
        in_section = False
        skip_lines = 6

        with open(file_path, 'r') as file:
            for line in file:
                if "0PRIMARY RESULTS" in line:
                    in_section = True
                    skip_lines = 3
                    continue

                if in_section:
                    if "PAGE" in line or "PENN STATE UNIVERSITY" in line or not line.strip():
                        continue

                    if skip_lines > 0:
                        skip_lines -= 1
                        continue

                    if "0" in line and "RESULTS" in line and "PRIMARY" not in line:
                        break

                    clean_line = line.strip()
                    if clean_line and clean_line[0].isdigit():
                        parts = re.split(r'\s+', clean_line)
                        if len(parts) == len(self.columns_primary):
                            try:
                                converted = [float(p.replace('E+', 'e+').replace('E-', 'e-')) for p in parts]
                                data.append(converted)
                            except ValueError:
                                continue

        return pd.DataFrame(data, columns=self.columns_primary) if data else None

    def _plot_combined_results(self):
        plot_columns = [col for col in self.columns_primary_plot]
        num_columns = len(plot_columns)
        num_rows = (num_columns + 1) // 2

        combined_fig, combined_axes = plt.subplots(num_rows, 2, figsize=(15, 5 * num_rows))
        combined_fig.suptitle("Combined Simulation Results - All Plots", fontsize=16, y=1.02)
        combined_axes = combined_axes.flatten()

        markers = ['o', 's', '^', 'D', 'v', '>', '<', 'p', '*', 'H', 'x', '+']
        markevery = 10

        for idx, column in enumerate(plot_columns):
            plt.figure(figsize=(10, 6))
            marker_cycle = cycle(markers)
            texts = []
            arrow_info = []

            for df, label in zip(self.dfs, self.labels):
                current_marker = next(marker_cycle)
                line, = plt.plot(
                    df.index + 1, df[column],
                    label=label,
                    marker=current_marker,
                    markersize=4,
                    markevery=markevery
                )
                line_color = line.get_color()

                x_start = df.index[0] + 1
                y_start = df[column].iloc[0]
                x_end = df.index[-1] + 1
                y_end = df[column].iloc[-1]

                text_start = plt.text(x_start, y_start, f"{y_start:.4f}", color=line_color, bbox=dict(
                    facecolor='white', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.2'))
                text_end = plt.text(x_end, y_end, f"{y_end:.4f}", color=line_color, bbox=dict(
                    facecolor='white', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.2'))
                texts.extend([text_start, text_end])

                arrow_info.extend([
                    {'text': text_start, 'original_pos': (x_start, y_start), 'color': line_color},
                    {'text': text_end, 'original_pos': (x_end, y_end), 'color': line_color}
                ])

            adjust_text(
                texts,
                force_text=(0.3, 0.5),
                expand_points=(1.5, 1.5),
            )

            for info in arrow_info:
                text = info['text']
                new_x, new_y = text.get_position()
                orig_x, orig_y = info['original_pos']
                plt.annotate(
                    '',
                    xy=(new_x, new_y),
                    xytext=(orig_x, orig_y),
                    arrowprops=dict(
                        arrowstyle='->',
                        color=info['color'],
                        alpha=0.5,
                        lw=0.8
                    )
                )

            plt.title(f"{column} vs Distance (ft)")
            plt.xlabel("Distance (ft)")
            plt.ylabel(column)
            plt.legend()
            plt.grid(True)

            if len(self.dfs[0]) <= 20:
                plt.xticks(range(1, len(self.dfs[0]) + 1))

            sanitized_column = sanitize_filename(column)
            plot_path = self.results_dir / f"{sanitized_column}_comparison.png"
            plt.savefig(plot_path, bbox_inches='tight')
            plt.close()
            print(f"Individual plot for {column} saved to {plot_path}")

            for df, label in zip(self.dfs, self.labels):
                combined_axes[idx].plot(df.index + 1, df[column], label=label, marker='o', markersize=0.5)
            combined_axes[idx].set_title(f"{column} vs Distance (ft)")
            combined_axes[idx].set_xlabel("Distance (ft)")
            combined_axes[idx].set_ylabel(column)
            combined_axes[idx].legend()
            combined_axes[idx].grid(True)

            if len(self.dfs[0]) <= 20:
                combined_axes[idx].set_xticks(range(1, len(self.dfs[0]) + 1))

        for idx in range(num_columns, len(combined_axes)):
            combined_fig.delaxes(combined_axes[idx])

        combined_plot_path = self.results_dir / "all_plots_combined.png"
        plt.tight_layout()
        combined_fig.savefig(combined_plot_path, bbox_inches='tight')
        plt.close(combined_fig)
        print(f"All individual plots combined and saved to {combined_plot_path}")

    def run_analysis(self):
        self.dfs = []
        self.labels = []

        for sim_name, input_template in self.input_templates.items():
            sim_name = sanitize_filename(sim_name)
            self._run_zebra_simulation(sim_name, input_template)
            output_file = self.results_dir / f"ZEBRA_{sim_name}.OUT"
            df = self._parse_primary_results(output_file)

            if df is not None:
                self.dfs.append(df)
                self.labels.append(sim_name)
                excel_path = self.results_dir / f"{sim_name}.xlsx"
                df.to_excel(excel_path, index=False)
                print(f"Results saved to {excel_path}")

        if self.dfs:
            self._plot_combined_results()
