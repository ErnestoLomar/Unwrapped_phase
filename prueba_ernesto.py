import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import imageio

def goldstein_unwrap(phase_map):
    rows, cols = phase_map.shape

    # Initialize the unwrapped phase map
    unwrapped_phase = np.zeros((rows, cols))

    # Phase difference thresholds
    threshold = np.pi

    # Loop through each pixel in the phase map
    for r in range(rows):
        for c in range(cols):
            # Calculate differences between neighboring pixels
            delta_r = 0
            delta_c = 0
            for dr in range(-1, 2):
                for dc in range(-1, 2):
                    if dr != 0 or dc != 0:
                        r_neighbor = r + dr
                        c_neighbor = c + dc
                        if 0 <= r_neighbor < rows and 0 <= c_neighbor < cols:
                            delta_r += np.sin(phase_map[r_neighbor, c_neighbor] - phase_map[r, c])
                            delta_c += np.cos(phase_map[r_neighbor, c_neighbor] - phase_map[r, c])

            # Calculate the unwrapped phase value
            unwrapped_phase[r, c] = phase_map[r, c] + np.arctan2(delta_r, delta_c)

            # Perform 2π jumps corrections
            while (unwrapped_phase[r, c] - phase_map[r, c]) > threshold:
                unwrapped_phase[r, c] -= 2 * np.pi

            while (unwrapped_phase[r, c] - phase_map[r, c]) < -threshold:
                unwrapped_phase[r, c] += 2 * np.pi

    return unwrapped_phase

def takeda_phase_unwrap(wrapped_phase):
    # Calculate gradient of the wrapped phase
    gx, gy = np.gradient(wrapped_phase)

    # Compute the Laplacian of the gradient
    laplacian = np.gradient(gx)[0] + np.gradient(gy)[1]#np.del2(gx + 1j * gy)

    # Compute the 2D unwrapped phase using Fourier transform
    unwrapped_phase = np.real(np.fft.ifft2(-laplacian))

    # Adjust the phase to be in the range [-pi, pi]
    unwrapped_phase = np.mod(unwrapped_phase + np.pi, 2 * np.pi) - np.pi

    return unwrapped_phase

def phase_to_height(data, distance_reference_plane, distance_CCD_projector, period):
    # Unwrap the phase using Takeda's algorithm
    unwrapped_phase_map = takeda_phase_unwrap(data)

    # Convert unwrapped phase to height distribution
    height_map = (unwrapped_phase_map * period) / (2 * np.pi)

    # Convert height to real-world coordinates (in meters)
    height_map = (height_map * distance_reference_plane) / distance_CCD_projector

    # Reconstruct the 3D object
    rows, cols = height_map.shape
    X, Y = np.meshgrid(np.arange(1, cols+1), np.arange(1, rows+1))
    X = X - (cols + 1) / 2  # Centering X and Y coordinates
    Y = Y - (rows + 1) / 2
    point_cloud = np.vstack((X.ravel(), Y.ravel(), height_map.ravel())).T

    return height_map, point_cloud

def cargar_imagenes(ruta_imagenes, etiquetas):
    imagenes = {}
    for etiqueta in etiquetas:
        imagenes[etiqueta] = sorted([ruta for ruta in ruta_imagenes if etiqueta in ruta], key=lambda x: int(x.split('/')[-1].split(etiqueta)[1].split('.')[0]))
    return imagenes

def leer_imagenes(imagenes):
    return [imageio.imread(image).astype(float) for image in imagenes]

# Funciones goldstein_unwrap y phase_to_height se definen aquí (como se mostró anteriormente)

# Main script
ruta_imagenes = ['./img/ref1.jpg', './img/ref2.jpg', './img/ref3.jpg', './img/ref4.jpg', 
                './img/def1.jpg', './img/def2.jpg', './img/def3.jpg', './img/def4.jpg']
etiquetas = ['ref', 'def']

imagenes = cargar_imagenes(ruta_imagenes, etiquetas)

if len(imagenes['ref']) != 4 or len(imagenes['def']) != 4:
    raise ValueError("Faltan imágenes de referencia o deformación.")

# Leer las imágenes de referencia y deformación
R_images = leer_imagenes(imagenes['ref'])
D_images = leer_imagenes(imagenes['def'])

# Asignar las imágenes a las variables correspondientes
R1, R2, R3, R4 = R_images
D1, D2, D3, D4 = D_images

# Evaluar expresiones (en lugar de QLineEdit, se usan variables directas)
NR = (R1 - R2) / (R1 + R2)  # Ejemplo de expresión
DR = (R3 - R4) / (R3 + R4)  # Ejemplo de expresión
ND = (D1 - D2) / (D1 + D2)  # Ejemplo de expresión
DD = (D3 - D4) / (D3 + D4)  # Ejemplo de expresión

# Evaluar las expresiones para obtener los valores
expresiones_fase_dif = ['ND', 'DD']

if len(expresiones_fase_dif) != 2:
    raise ValueError("Se deben ingresar exactamente dos expresiones separadas por coma.")

# Evaluar las expresiones para obtener los valores
d_phi = np.arctan2(eval(expresiones_fase_dif[0]), eval(expresiones_fase_dif[1]))
d_phi2 = d_phi

# Main script
distance_reference_plane = 120  # m
distance_CCD_projector = 10  # cm
period = 100  # Fringe period (in arbitrary units, could be pixels)

# Assuming d_phi2 is your input phase map
# d_phi2 = ...

# Unwrap phase using Goldstein algorithm
fase_desenvuelta = goldstein_unwrap(d_phi2)

# Perform phase-to-height conversion and get the point cloud
height_map, point_cloud = phase_to_height(fase_desenvuelta, distance_reference_plane, distance_CCD_projector, period)

print("El valor de height_map: ", height_map)
print("El valor de point_cloud: ", point_cloud)

# Display the height map and point cloud
fig, ax = plt.subplots(1, 2, figsize=(12, 6))
ax[0].imshow(height_map, cmap='gray')
ax[0].set_title('Height Map')

ax[1] = plt.subplot(1, 2, 2, projection='3d')
ax[1].scatter(point_cloud[:, 0], point_cloud[:, 1], point_cloud[:, 2], c=point_cloud[:, 2], cmap='gray')
ax[1].set_title('Point Cloud')
plt.show()