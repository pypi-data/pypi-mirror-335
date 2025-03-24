"""
Simple Line plus Scatter plot
=============================
"""

# %%
# Importing the script dependencies
import numpy
from MPSPlots.render2D import SceneList

# %%
# Define data
x = numpy.arange(100)
y0 = numpy.random.rand(100)
y1 = numpy.random.rand(100)

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
    show_legend=True,
    line_width=2
)

# %%
# Adding a Line artist to first axis
_ = ax.add_line(x=x, y=y0, label='line 0')

# %%
# Adding a Scatter artist to first axis
_ = ax.add_scatter(x=x, y=y0, label='line 1')

# %%
# Showing the figure
_ = figure.show()
