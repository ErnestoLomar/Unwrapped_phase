import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import imageio.v2 as imageio

# Funciones goldstein_unwrap y phase_to_height se definen aquí (como se mostró anteriormente)

# Main script
ruta_imagenes = ['ref1.jpg', 'ref2.jpg', 'ref3.jpg', 'ref4.jpg', 
                'def1.jpg', 'def2.jpg', 'def3.jpg', 'def4.jpg']
etiquetas = ['ref', 'def']

imagenes = {}
for etiqueta in etiquetas:
    imagenes[etiqueta] = sorted([ruta for ruta in ruta_imagenes if etiqueta in ruta], key=lambda x: int(x.split('/')[-1].split(etiqueta)[1].split('.')[0]))

if len(imagenes['ref']) != 4 or len(imagenes['def']) != 4:
    raise ValueError("Faltan imágenes de referencia o deformación.")

# Leer las imágenes de referencia y deformación
R_images = [imageio.imread(image).astype(float) for image in imagenes['ref']]
D_images = [imageio.imread(image).astype(float) for image in imagenes['def']]

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

print("El valor de d_pi2; ", d_phi2)

# Main script
distance_reference_plane = 120  # m
distance_CCD_projector = 10  # cm
period = 100  # Fringe period (in arbitrary units, could be pixels)

# Assuming d_phi2 is your input phase map
# d_phi2 = ...

############################### Unwrap phase using Goldstein algorithm

# Verificar la forma de d_phi2
if d_phi2.ndim != 2:
    print(d_phi2.ndim)
    raise ValueError("d_phi2 debe ser una matriz 2D.")

rows, cols = d_phi2.shape

# Initialize the unwrapped phase map
fase_desenvuelta = np.zeros((rows, cols))

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
                        delta_r += np.sin(d_phi2[r_neighbor, c_neighbor] - d_phi2[r, c])
                        delta_c += np.cos(d_phi2[r_neighbor, c_neighbor] - d_phi2[r, c])

        # Calculate the unwrapped phase value
        fase_desenvuelta[r, c] = d_phi2[r, c] + np.arctan2(delta_r, delta_c)

        # Perform 2π jumps corrections
        while (fase_desenvuelta[r, c] - d_phi2[r, c]) > threshold:
            fase_desenvuelta[r, c] -= 2 * np.pi

        while (fase_desenvuelta[r, c] - d_phi2[r, c]) < -threshold:
            fase_desenvuelta[r, c] += 2 * np.pi

############################### END Unwrap phase using Goldstein algorithm

############################### Perform phase-to-height conversion and get the point cloud

############################### Unwrap the phase using Takeda's algorithm

# Calculate gradient of the wrapped phase
gx, gy = np.gradient(fase_desenvuelta)

# Compute the Laplacian of the gradient
laplacian = np.gradient(gx)[0] + np.gradient(gy)[1]#np.del2(gx + 1j * gy)

# Compute the 2D unwrapped phase using Fourier transform
unwrapped_phase_map = np.real(np.fft.ifft2(-laplacian))

# Adjust the phase to be in the range [-pi, pi]
unwrapped_phase_map = np.mod(fase_desenvuelta + np.pi, 2 * np.pi) - np.pi

############################### END Unwrap the phase using Takeda's algorithm

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

############################### END Perform phase-to-height conversion and get the point cloud

# Filtrar los datos en el rango de -4 a 4 en el eje z
mask = (point_cloud[:, 2] >= -4) & (point_cloud[:, 2] <= 4)
filtered_point_cloud = point_cloud[mask]

# Display the height map and point cloud
fig, ax = plt.subplots(1, 2, figsize=(12, 6))
ax[0].imshow(height_map, cmap='gray')
ax[0].set_title('Height Map')

ax[1] = plt.subplot(1, 2, 2, projection='3d')
sc = ax[1].scatter(filtered_point_cloud[:, 0], filtered_point_cloud[:, 1], filtered_point_cloud[:, 2], c=filtered_point_cloud[:, 2], cmap='gray')
ax[1].set_title('Point Cloud')

# Set z-axis limit to [-4, 4]
ax[1].set_zlim([-4, 4])

plt.show()