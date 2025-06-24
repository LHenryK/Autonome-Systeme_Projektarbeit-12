import numpy as np
import math

def lidar_data_to_cartesian_array(angles, distances, resolution=0.1):
    """Konvertiert Lidar-Daten in ein 2D-Cartesisches Array."""
    points_x = []
    points_y = []
    for i in range(len(angles)):
        angle_rad = -float(angles[i]) + math.pi / 2
        distance = float(distances[i])
        x = distance * math.cos(angle_rad)
        y = distance * math.sin(angle_rad)
        points_x.append(x)
        points_y.append(y)

    if not points_x or not points_y:
        return np.zeros((1, 1))

    min_x, max_x = min(points_x), max(points_x)
    min_y, max_y = min(points_y), max(points_y)

    width = int((max_x - min_x) / resolution) + 3  # Puffer hinzufügen
    height = int((max_y - min_y) / resolution) + 3 # Puffer hinzufügen

    grid = np.zeros((height, width))
    offset_x = -min_x / resolution + 1
    offset_y = -min_y / resolution + 1

    for i in range(len(points_x)):
        x_idx = int(points_x[i] / resolution + offset_x)
        y_idx = int(points_y[i] / resolution + offset_y)
        if 0 <= y_idx < height and 0 <= x_idx < width:
            grid[y_idx, x_idx] = 1

    return grid, (offset_x, offset_y)

def create_similarity_field(old_grid, resolution=0.1, sr=5):
    """Erstellt ein verschmiertes Ähnlichkeitsfeld um die Punkte im alten Grid."""
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

def calculate_similarity_score(similarity_field, new_grid):
    """Berechnet den Ähnlichkeits-Score zwischen dem Feld und dem neuen Grid."""
    new_points_y, new_points_x = np.where(new_grid == 1)
    total_similarity = 0
    num_new_points = len(new_points_y)

    if num_new_points == 0:
        return 0

    for y_new, x_new in zip(new_points_y, new_points_x):
        if 0 <= y_new < similarity_field.shape[0] and 0 <= x_new < similarity_field.shape[1]:
            total_similarity += similarity_field[y_new, x_new]

    return total_similarity / num_new_points if num_new_points > 0 else 0

def rotate_lidar_data(angles, distances, angle_degrees):
    """Dreht die Lidar-Daten um den angegebenen Winkel (Grad)."""
    rotated_angles = [angle + math.radians(angle_degrees) for angle in angles]
    return {"angles": rotated_angles, "distances": distances}

def find_best_match(old_data, new_data, resolution=0.1, sr=5, rotation_steps=36):
    """Findet die beste Übereinstimmung zwischen zwei Lidar-Datensätzen."""
    old_grid, old_offset = lidar_data_to_cartesian_array(old_data["angles"], old_data["distances"], resolution)
    similarity_field = create_similarity_field(old_grid, resolution, sr)
    best_score = -1
    best_rotation = 0

    for rotation in range(rotation_steps):
        rotated_new_data = rotate_lidar_data(new_data["angles"], new_data["distances"], rotation * (360 / rotation_steps))
        new_grid, new_offset = lidar_data_to_cartesian_array(rotated_new_data["angles"], rotated_new_data["distances"], resolution)

        # Hier müsstest du die Überlagerung der Ursprünge und die spiralförmige Suche implementieren
        # Ein einfacherer erster Schritt wäre, die Grids zentriert zu vergleichen.
        # Für eine genauere Implementierung der Ursprungsverschiebung und spiralförmigen Suche
        # wäre eine Funktion notwendig, die verschiedene relative Positionen testet.

        score = calculate_similarity_score(similarity_field, new_grid)

        if score > best_score:
            best_score = score
            best_rotation = rotation * (360 / rotation_steps)

    return best_score, best_rotation

# Beispielhafte Nutzung
if __name__ == "__main__":
    # old_scan = {"angles": [0.1, 0.2, 1.5, 1.6], "distances": [1.0, 1.5, 0.4, 1.2]}
    # new_scan = {"angles": [0.15, 0.25, 1.55, 1.65], "distances": [1.05, 1.55, 0.85, 1.25]}
    old_scan = {"angles": [0.1, 0.2, 1.5, 1.6], "distances": [1.0, 1.5, 0.4, 1.2]}
    new_scan = {"angles": [0.1, 0.2, 1.5, 1.6], "distances": [1.0, 1.5, 0.4, 1.2]}

    similarity, rotation = find_best_match(old_scan, new_scan)
    print(f"Ähnlichkeits-Score: {similarity:.4f}, Beste Rotation: {rotation:.2f} Grad")

    # Erstelle zur Visualisierung die Grids
    resolution = 0.1
    old_grid, old_offset = lidar_data_to_cartesian_array(old_scan["angles"], old_scan["distances"], resolution)
    new_grid, new_offset = lidar_data_to_cartesian_array(new_scan["angles"], new_scan["distances"], resolution)
    similarity_field = create_similarity_field(old_grid, resolution)

    import matplotlib.pyplot as plt

    plt.figure(figsize=(15, 5))

    plt.subplot(1, 3, 1)
    plt.imshow(old_grid, origin='lower', cmap='binary')
    plt.title('Alter Scan (Grid)')

    plt.subplot(1, 3, 2)
    plt.imshow(similarity_field, origin='lower', cmap='viridis')
    plt.title('Ähnlichkeitsfeld (Alter Scan)')

    plt.subplot(1, 3, 3)
    plt.imshow(new_grid, origin='lower', cmap='binary')
    plt.title('Neuer Scan (Grid)')

    plt.tight_layout()
    plt.show()

