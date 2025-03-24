"""
Mesh - Line
~~~~~~~~~~~
"""

# %%
# Importing the script dependencies
import numpy
from MPSPlots.render2D import SceneList

# %%
# Define data
x, y, = numpy.mgrid[0:100, 0:100]

# %%
# Creating the Scene
figure = SceneList(
    unit_size=(8, 4),
    title='random data simple lines'
)

# %%
# Adding few axis to the scene for the plots
ax_0 = figure.append_ax(
    x_label='x data',
    y_label='y data',
    show_legend=False
)

ax_1 = figure.append_ax(
    x_label='x data',
    y_label='y data',
    show_legend=False
)

# %%
# Adding a Mesh artist to first axis
artist_0 = ax_0.add_mesh(
    scalar=x + y,
    x=x,
    y=y,
)

ax_0.add_colorbar(artist=artist_0)

# %%
# Adding a Mesh artist to second axis
artist_1 = ax_1.add_mesh(
    scalar=x**2,
    x=x,
    y=y,
)

# %%
# Extra decoration of the axes
figure.annotate_axis(numerotation_type='roman')

# %%
# Showing the figure
_ = figure.show()
