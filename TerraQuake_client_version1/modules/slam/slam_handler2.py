import numpy as np
import math
import matplotlib.pyplot as plt

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
        return np.zeros((1, 1)), (0, 0)

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

def rotate_lidar_data(angles, distances, angle_degrees):
    """Dreht die Lidar-Daten um den angegebenen Winkel (Grad)."""
    rotated_angles = [angle + math.radians(angle_degrees) for angle in angles]
    return {"angles": rotated_angles, "distances": distances}

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

def find_best_match_with_translation(old_data, new_data, resolution=0.1, sr=5, max_translation=5, rotation_steps=36):
    """Findet die beste Übereinstimmung zwischen zwei Lidar-Datensätzen mit Translation und Rotation."""
    old_grid, old_offset = lidar_data_to_cartesian_array(old_data["angles"], old_data["distances"], resolution)
    similarity_field = create_similarity_field(old_grid, resolution, sr)
    best_score = -1
    best_translation = (0, 0)
    best_rotation = 0

    old_center_y = old_grid.shape[0] // 2
    old_center_x = old_grid.shape[1] // 2

    for dist in range(max_translation + 1):
        for angle_deg in range(0, 360, 45 if dist > 0 else 1): # Weniger Winkel bei Distanz 0
            dy = int(dist * math.sin(math.radians(angle_deg)))
            dx = int(dist * math.cos(math.radians(angle_deg)))

            for rotation in range(rotation_steps):
                rotated_new_data = rotate_lidar_data(new_data["angles"], new_data["distances"], rotation * (360 / rotation_steps))
                new_grid_rotated, new_offset_rotated = lidar_data_to_cartesian_array(rotated_new_data["angles"], rotated_new_data["distances"], resolution)

                # Berechne die Verschiebung, um den neuen Ursprung relativ zum alten zu positionieren
                translation_y = old_center_y + dy - new_grid_rotated.shape[0] // 2
                translation_x = old_center_x + dx - new_grid_rotated.shape[1] // 2

                score = calculate_similarity_at_offset(similarity_field, new_grid_rotated, (translation_y, translation_x))

                if score > best_score:
                    best_score = score
                    best_translation = (dy, dx)
                    best_rotation = rotation * (360 / rotation_steps)

    return best_score, best_translation, best_rotation

# Beispielhafte Nutzung mit einer Rotation von ca. 15 Grad
if __name__ == "__main__":
    old_scan = {
        "angles": [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5],
        "distances": [2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0]
    }
    # Neuer Scan ist um 15 Grad gedreht und leicht verschoben
    new_scan_rotated = rotate_lidar_data(old_scan["angles"], old_scan["distances"], 15)
    new_scan = {
        "angles": new_scan_rotated["angles"],
        "distances": [2.1, 2.1, 2.1, 2.1, 2.1, 2.1, 2.1, 2.1, 2.1, 2.1, 2.1, 2.1]
    }

    resolution = 0.1
    sr = 5
    max_translation = 5
    rotation_steps = 36

    best_similarity, best_translation, best_rotation = find_best_match_with_translation(
        old_scan, new_scan, resolution, sr, max_translation, rotation_steps
    )

    print(f"Bester Ähnlichkeits-Score: {best_similarity:.4f}")
    print(f"Beste Translation (dy, dx): {best_translation}")
    print(f"Beste Rotation: {best_rotation:.2f} Grad")

    # Visualisierung (optional)
    old_grid, old_offset = lidar_data_to_cartesian_array(old_scan["angles"], old_scan["distances"], resolution)
    similarity_field = create_similarity_field(old_grid, resolution, sr)
    rotated_new_data = rotate_lidar_data(new_scan["angles"], new_scan["distances"], best_rotation)
    new_grid_rotated, new_offset_rotated = lidar_data_to_cartesian_array(rotated_new_data["angles"], rotated_new_data["distances"], resolution)

    translated_y = old_grid.shape[0] // 2 + best_translation[0] - new_grid_rotated.shape[0] // 2
    translated_x = old_grid.shape[1] // 2 + best_translation[1] - new_grid_rotated.shape[1] // 2

    overlap_grid = np.zeros_like(similarity_field)
    overlap_grid += similarity_field

    new_points_y, new_points_x = np.where(new_grid_rotated == 1)
    for y_new, x_new in zip(new_points_y, new_points_x):
        plot_y = y_new + translated_y
        plot_x = x_new + translated_x
        if 0 <= plot_y < overlap_grid.shape[0] and 0 <= plot_x < overlap_grid.shape[1]:
            overlap_grid[plot_y, plot_x] = 2

    plt.figure(figsize=(10, 10))
    plt.imshow(overlap_grid, origin='lower', cmap='viridis')
    plt.title('Überlagerung')
    plt.colorbar(label='Ähnlichkeit')
    plt.show()