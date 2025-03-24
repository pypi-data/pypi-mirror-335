"""
STD line
========
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
    title='random data simple lines'
)

# %%
# Adding an axis to the scene for the plots
ax = figure.append_ax(
    x_label='x data',
    y_label='y data',
    show_legend=True
)

# %%
# Adding a STDLine artist to first axis
_ = ax.add_std_line(
    x=x,
    y_mean=y_mean,
    y_std=y_std,
    label='Fill between lines',
)

# %%
# Showing the figure
_ = figure.show()
