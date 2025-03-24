"""
Contour
~~~~~~~
"""

# %%
# Importing the script dependencies
import numpy
from MPSPlots.render2D import SceneList


# %%
# Define data
x_grid, y_grid = numpy.mgrid[0:100, 0:100]
scalar = numpy.sqrt(x_grid**2 + y_grid**2)


# %%
# Creating the Scene
figure = SceneList(
    unit_size=(8, 4),
    title='random data contour line'
)

# %%
# Adding an axis to the scene for the plots
ax = figure.append_ax(
    x_label='x data',
    y_label='y data',
    show_legend=False
)

# %%
# Adding a contour artist to axis
_ = ax.add_contour(
    scalar=scalar,
    x=x_grid,
    y=y_grid,
    iso_values=numpy.linspace(0, 100, 20),
    fill_contour=True
)

# %%
# Showing the figure
_ = figure.show()
