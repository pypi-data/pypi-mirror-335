"""
3D Unstructured mesh
~~~~~~~~~~~~~~~~~~~~
"""

# %%
# Importing the script dependencies
import numpy
from MPSPlots.render3D import SceneList


# %%
# Transform spherical to cartesian
def spherical_to_cartesian(phi: numpy.ndarray, theta: numpy.ndarray, r: numpy.ndarray = None) -> tuple:
    phi = numpy.asarray(phi)
    theta = numpy.asarray(theta)
    r = r if r is not None else numpy.ones(phi.shape)

    x = r * numpy.cos(phi) * numpy.cos(theta)
    y = r * numpy.cos(phi) * numpy.sin(theta)
    z = r * numpy.sin(phi)
    return x, y, z


# %%
# Define data
x = y = z = numpy.linspace(-100, 100, 100)

theta = numpy.linspace(0, 360, 100)
phi = numpy.linspace(-90, 90, 100)

theta = numpy.deg2rad(theta)
phi = numpy.deg2rad(phi)

phi, theta = numpy.meshgrid(phi, theta)

# %%
# Creating the Scene
scene = SceneList(unit_size=(800, 800))
ax = scene.append_ax()
ax.add_unit_sphere(opacity=0.1)
ax.add_unit_axis()

scalar = (numpy.cos(phi))**2

x, y, z = spherical_to_cartesian(phi=phi, theta=theta, r=scalar)

ax.add_mesh(x=x, y=y, z=z)

_ = scene.show()
