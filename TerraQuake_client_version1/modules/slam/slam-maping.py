import numpy as np
import math
import json
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm

def progressBar(iterable, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iterable    - Required  : iterable object (Iterable)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    total = len(iterable)
    # Progress Bar Printing Function
    def printProgressBar (iteration):
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Initial Call
    printProgressBar(0)
    # Update Progress Bar
    for i, item in enumerate(iterable):
        yield item
        printProgressBar(i + 1)
    # Print New Line on Complete
    print()

def lidar_data_to_cartesian_array(all_points, resolution=0.008, max_grid_size=6000): # Auflösung auf 0.008 gesetzt
    """Konvertiert eine Liste aller gesammelten kartesischen Punkte in ein 2D-Cartesisches Array mit maximaler Größe."""
    if not all_points:
        return np.zeros((1, 1)), (0, 0), (0, 0)

    points_x, points_y = zip(*all_points)

    min_x, max_x = min(points_x), max(points_x)
    min_y, max_y = min(points_y), max(points_y)

    width_needed = int((max_x - min_x) / resolution) + 3
    height_needed = int((max_y - min_y) / resolution) + 3

    width = min(width_needed, max_grid_size)
    height = min(height_needed, max_grid_size)

    grid = np.zeros((height, width))

    # Berechne den Offset basierend auf dem tatsächlichen Grid und den minimalen Koordinaten
    offset_x = -min_x / resolution + 1
    offset_y = -min_y / resolution + 1

    for x, y in all_points:
        x_idx_raw = x / resolution + offset_x
        y_idx_raw = y / resolution + offset_y

        # Überprüfe, ob die Indizes innerhalb der tatsächlichen Grid-Grenzen liegen
        if 0 <= int(y_idx_raw) < height and 0 <= int(x_idx_raw) < width:
            grid[int(y_idx_raw), int(x_idx_raw)] = 1

    return grid, (offset_x, offset_y), (min_x, min_y)

def create_similarity_field(old_grid, resolution=0.008, sr_mm=50): # Auflösung auf 0.008 gesetzt
    """Erstellt ein verschmiertes Ähnlichkeitsfeld um die Punkte im alten Grid."""
    sr = int(sr_mm / (resolution * 1000)) # Umrechnung sr in Zellen
    similarity_field = np.zeros_like(old_grid, dtype=float)
    old_points_y, old_points_x = np.where(old_grid == 1)

    for y_old, x_old in zip(old_points_y, old_points_x):
        for dy in range(-sr, sr + 1):
            for dx in range(-sr, sr + 1):
                y_new, x_new = y_old + dy, x_old + dx
                if 0 <= y_new < similarity_field.shape[0] and 0 <= x_new < similarity_field.shape[1]:
                    distance = math.sqrt(dy**2 + dx**2)
                    if distance <= sr:
                        similarity_field[y_new, x_new] += (sr - distance) / sr

    return similarity_field

def lidar_data_to_cartesian_points(angles, distances):
    """Konvertiert Lidar-Daten in eine Liste von kartesischen Punkten."""
    points = []
    for i in range(len(angles)):
        angle_rad = -float(angles[i]) + math.pi / 2
        distance = float(distances[i])
        x = distance * math.cos(angle_rad)
        y = distance * math.sin(angle_rad)
        points.append((x, y))
    return points

def rotate_points(points, angle_rad):
    """Dreht eine Liste von kartesischen Punkten um den Ursprung."""
    rotated_points = []
    for x, y in points:
        new_x = x * math.cos(angle_rad) - y * math.sin(angle_rad)
        new_y = x * math.sin(angle_rad) + y * math.cos(angle_rad)
        rotated_points.append((new_x, new_y))
    return rotated_points

def calculate_similarity_at_offset(similarity_field, new_grid, offset):
    """Berechnet den Ähnlichkeits-Score für eine gegebene relative Verschiebung."""
    offset_y, offset_x = offset
    total_similarity = 0
    num_new_points = np.sum(new_grid)

    if num_new_points == 0:
        return 0

    new_points_y, new_points_x = np.where(new_grid == 1)

    for y_new, x_new in zip(new_points_y, new_points_x):
        shifted_y = y_new + offset_y
        shifted_x = x_new + offset_x
        if 0 <= shifted_y < similarity_field.shape[0] and 0 <= shifted_x < similarity_field.shape[1]:
            total_similarity += similarity_field[shifted_y, shifted_x]

    return total_similarity / num_new_points if num_new_points > 0 else 0

def find_best_match_within_radius(old_points, new_points, resolution=0.008, sr_mm=50, max_translation_mm=1000, rotation_steps=36, max_grid_size=2000, search_radius_meter=1.0):
    """Findet die beste Übereinstimmung lokal um die neuen Punkte."""
    if not new_points:
        return 1.0, (0, 0), 0.0

    new_points_x, new_points_y = zip(*new_points)
    min_new_x, max_new_x = min(new_points_x), max(new_points_x)
    min_new_y, max_new_y = min(new_points_y), max(new_points_y)

    # Definiere den Suchbereich im alten Grid
    search_min_x = min_new_x - search_radius_meter
    search_max_x = max_new_x + search_radius_meter
    search_min_y = min_new_y - search_radius_meter
    search_max_y = max_new_y + search_radius_meter

    relevant_old_points = [p for p in old_points if search_min_x <= p[0] <= search_max_x and search_min_y <= p[1] <= search_max_y]

    if not relevant_old_points:
        return 0.5, (0, 0), 0.0 # Wenn keine relevanten alten Punkte gefunden wurden

    old_grid_relevant, old_offset_relevant, old_min_coords_relevant = lidar_data_to_cartesian_array(
        relevant_old_points, resolution, max_grid_size
    )
    similarity_field = create_similarity_field(old_grid_relevant, resolution, sr_mm)

    best_score = -1
    best_translation_relevant_cells = (0, 0)
    best_rotation_rad = 0

    max_translation_cells = int(max_translation_mm / (resolution * 1000))

    old_center_y = old_grid_relevant.shape[0] // 2
    old_center_x = old_grid_relevant.shape[1] // 2

    # Konvertiere neue Punkte in ein Grid
    new_grid, new_offset, new_min_coords = lidar_data_to_cartesian_array(new_points, resolution, max_grid_size)
    new_center_y = new_grid.shape[0] // 2
    new_center_x = new_grid.shape[1] // 2

    print("Starte die lokale Suche nach der besten Übereinstimmung:")
    for dist_cells in progressBar(range(max_translation_cells + 1), prefix='Fortschritt:', suffix='Distanz abgeschlossen', length=50):
        angle_step = 45 if dist_cells > 0 else 1
        for angle_idx, angle_deg in enumerate(range(0, 360, angle_step)):
            dy_cells = int(dist_cells * math.sin(math.radians(angle_deg)))
            dx_cells = int(dist_cells * math.cos(math.radians(angle_deg)))

            for rotation_step in range(rotation_steps):
                rotation_rad = rotation_step * (2 * math.pi / rotation_steps)
                rotated_new_points = rotate_points(new_points, rotation_rad)
                new_grid_rotated, _, _ = lidar_data_to_cartesian_array(rotated_new_points, resolution, max_grid_size)

                # Berechne die Verschiebung im relevanten Koordinatensystem
                translation_y = old_center_y + dy_cells - new_center_y
                translation_x = old_center_x + dx_cells - new_center_x

                score = calculate_similarity_at_offset(similarity_field, new_grid_rotated, (translation_y, translation_x))

                if score > best_score:
                    best_score = score
                    best_translation_relevant_cells = (dy_cells, dx_cells)
                    best_rotation_rad = rotation_rad

    print("\nLokale Suche abgeschlossen.")

    # Umrechnung der Translation zurück in das globale Koordinatensystem (ungefähr)
    best_translation_global_mm = (
        best_translation_relevant_cells[0] * resolution * 1000,
        best_translation_relevant_cells[1] * resolution * 1000
    )

    return best_score, best_translation_global_mm, best_rotation_rad



# --- Funktion zum Messen des Abstands mit ESCAPE zum Löschen ---
class DistanceTool:
    def __init__(self, ax, resolution_meter):
        self.ax = ax
        self.resolution_meter = resolution_meter
        self.points = []
        self.lines = []
        self.texts = []
        self.point_artists = []
        self.cid_click = self.ax.figure.canvas.mpl_connect('button_press_event', self)
        self.cid_key = self.ax.figure.canvas.mpl_connect('key_press_event', self.on_key)

    def __call__(self, event):
        if event.inaxes == self.ax:
            self.points.append((event.xdata, event.ydata))
            point, = self.ax.plot(event.xdata, event.ydata, 'ro') # Erster oder zweiter Punkt
            self.point_artists.append(point)
            self.ax.figure.canvas.draw()
            if len(self.points) == 2:
                x1, y1 = self.points[0]
                x2, y2 = self.points[1]
                distance_meter = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                distance_cm = distance_meter * 100

                # Zeichne Linie und Text
                line, = self.ax.plot([x1, x2], [y1, y2], 'r--')
                text = self.ax.text((x1 + x2) / 2, (y1 + y2) / 2, f'{distance_cm:.2f} cm', color='red')
                self.lines.append(line)
                self.texts.append(text)
                self.ax.figure.canvas.draw()
                self.points = [] # Zurücksetzen für die nächste Messung

    def on_key(self, event):
        if event.key == 'escape':
            for line in self.lines:
                line.remove()
            for text in self.texts:
                text.remove()
            for point in self.point_artists:
                point.remove()
            self.points = []
            self.lines = []
            self.texts = []
            self.point_artists = []
            self.ax.figure.canvas.draw()


# Hauptteil des Skripts zum Laden der Daten, Anpassen und Visualisieren
if __name__ == "__main__":
    try:
        with open("./modules/slam/old-scan.json", "r") as f:
            old_scan_data = json.load(f)
        with open("./modules/slam/new-scan.json", "r") as f:
            new_scan_data = json.load(f)

        resolution_mm = 4
        sr_mm = 40
        max_translation_mm_local = 1000 # Reduzierter Suchbereich
        rotation_steps_local = 72      # Feinere lokale Rotation
        max_grid_size = 2000
        search_radius_meter = 1

        old_points = lidar_data_to_cartesian_points(old_scan_data["angles"], old_scan_data["distances"])
        new_points = lidar_data_to_cartesian_points(new_scan_data["angles"], new_scan_data["distances"])

        best_similarity, best_translation_mm, best_rotation_rad = find_best_match_within_radius(
            old_points, new_points, resolution_mm / 1000, sr_mm, max_translation_mm_local, rotation_steps_local, max_grid_size, search_radius_meter
        )

        best_rotation_deg = math.degrees(best_rotation_rad)
        print(f"Bester Ähnlichkeits-Score (lokal): {best_similarity:.4f}")
        print(f"Beste Translation (dy, dx) in mm (lokal): {best_translation_mm}")
        print(f"Beste Rotation (lokal): {best_rotation_deg:.2f} Grad")

        # --- Aktualisiere die globale Karte ---
        global all_measured_points # Stelle sicher, dass die globale Variable existiert
        if 'all_measured_points' not in globals():
            all_measured_points = list(old_points)

        rotated_new_points = rotate_points(new_points, best_rotation_rad)
        translated_new_points = [(x + best_translation_mm[1] / 1000, y + best_translation_mm[0] / 1000) for x, y in rotated_new_points]

        all_measured_points.extend(translated_new_points)

        # Erstelle die globale Karte neu (oder effizienter: füge nur die neuen Punkte hinzu und erweitere bei Bedarf)
        global_grid, global_offset, global_min_coords = lidar_data_to_cartesian_array(all_measured_points, resolution_mm / 1000, max_grid_size)

        # --- Visualisierung der globalen Karte mit Distanzmesswerkzeug ---
        fig, ax = plt.subplots(figsize=(12, 12))
        cmap = ListedColormap(['black', 'gray', 'lightcoral']) # Schwarz für Hindernisse, Grau für Ursprung, Hellrot für neuer Scan
        bounds = [0, 0.6, 0.76, 1] # Angepasste Bounds
        norm = BoundaryNorm(bounds, cmap.N)
        img = ax.imshow(global_grid, origin='lower', cmap=cmap, norm=norm,
                           extent=[global_min_coords[0],
                                   global_min_coords[0] + global_grid.shape[1] * (resolution_mm / 1000),
                                   global_min_coords[1],
                                   global_min_coords[1] + global_grid.shape[0] * (resolution_mm / 1000)])
        ax.set_title('Globale Karte der Umgebung (Schwarz=Hindernis, Grau=Ursprung, Hellrot=Neuer Scan)')
        ax.set_xlabel('X (m)') # Beschriftung in Metern
        ax.set_ylabel('Y (m)') # Beschriftung in Metern
        cbar = fig.colorbar(img, cmap=cmap, norm=norm, boundaries=bounds, ticks=[0.3, 0.68, 0.88])
        cbar.ax.set_yticklabels(['Hindernis', 'Ursprung', 'Neuer Scan'])

        # Aktiviere das Distanzmesswerkzeug
        resolution_meter = resolution_mm / 1000
        distance_tool = DistanceTool(ax, resolution_meter)

        plt.show()

    except FileNotFoundError:
        print("Fehler: Die Dateien 'old-scan.json' oder 'new-scan.json' wurden nicht im aktuellen Ordner gefunden.")
    except json.JSONDecodeError:
        print("Fehler: Die JSON-Dateien konnten nicht dekodiert werden. Stellen Sie sicher, dass sie gültiges JSON enthalten.")
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")