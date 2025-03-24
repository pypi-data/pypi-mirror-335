"""
STD line
~~~~~~~~
"""

# %%
# Importing the script dependencies
import numpy
from MPSPlots.render2D import SceneList

# %%
# Define data
x = numpy.arange(100)
y = numpy.random.rand(10, 100)
y_mean = numpy.mean(y, axis=0)
y_std = numpy.std(y, axis=0)

# %%
# Creating the Scene
figure = SceneList(
    unit_size=(8, 4),
    title='Polygon'
)

# %%
# Adding an axis to the scene for the plots
ax = figure.append_ax(
    x_label='x data',
    y_label='y data',
    show_legend=True,
    equal_limits=True,
    aspect_ratio='equal'
)

coordinates = [(0, -1), (0, 1), (4, 1), (4, -1)]

# %%
# Adding a Polygon artist to first axis
_ = ax.add_polygon(
    coordinates=coordinates,
    edgecolor='black',
    facecolor='red'
)


# %%
# Adding a Polygon artist to first axis
_ = ax.add_circle(
    position=(0, 1),
    radius=1,
    edgecolor='black',
    facecolor='red'
)

# %%
# Showing the figure
_ = figure.show()
