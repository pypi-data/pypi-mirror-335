"""
Mesh - Matrix
~~~~~~~~~~~~~
"""

# %%
# Importing the script dependencies
import numpy
from MPSPlots.render2D import SceneMatrix


# %%
# Define data
x, y, = numpy.mgrid[0:100, 0:100]

# %%
# Creating the Scene
figure = SceneMatrix(
    unit_size=(4, 2),
    title='random data simple lines'
)

# %%
# Adding a first axis to the scene for the plots
ax_0 = figure.append_ax(
    row=0,
    column=0,
    x_label='x data',
    y_label='y data',
    show_legend=False
)

# %%
# Adding a second axis to the scene for the plots
ax_1 = figure.append_ax(
    row=1,
    column=0,
    x_label='x data',
    y_label='y data',
    show_legend=False
)

# %%
# Adding a third axis to the scene for the plots
ax_2 = figure.append_ax(
    row=1,
    column=1,
    x_label='x data',
    y_label='y data',
    show_legend=False,
)

# %%
# Adding a Mesh artist to first axis
artist_0 = ax_0.add_mesh(
    scalar=x + y,
    x=x,
    y=y,
)

ax_2.add_colorbar(artist=artist_0)

# %%
# Adding a Mesh artist to second axis
_ = ax_1.add_mesh(
    scalar=(x - 50)**2 + (y - 50)**2,
    x=x,
    y=y,
)


# %%
# Adding a Mesh artist to third axis
_ = ax_2.add_mesh(
    scalar=x**2 + y**2,
    x=x,
    y=y,
)

# %%
# Extra decoration of the axes
figure.annotate_axis()

# %%
# Showing the figure
_ = figure.show()
