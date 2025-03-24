"""
3D Unstructured mesh
~~~~~~~~~~~~~~~~~~~~
"""

# %%
# Importing the script dependencies
import numpy
from MPSPlots.render3D import SceneList


# %%
# Define data
n_points = 100
x = numpy.arange(n_points) / 10
y = numpy.arange(n_points) / 10
z = numpy.random.rand(n_points) * 3

coordinates = numpy.c_[x, y, z].T


# %%
# Creating the Scene
figure = SceneList(unit_size=(700, 700))

# %%
# Adding an axis to the scene for the plots
ax = figure.append_ax()

# %%
# Adding a contour artist to axis
ax.add_unstructured_mesh(
    coordinates=coordinates,
    scalar_coloring=coordinates[0]
)

ax.add_unit_sphere(radius=10, opacity=0.3)

ax.add_unit_axis(show_label=False)

# %%
# Showing the figure
_ = figure.show()
