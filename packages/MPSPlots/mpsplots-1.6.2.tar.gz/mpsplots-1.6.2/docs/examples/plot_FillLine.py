"""
Fill Line
~~~~~~~~~
"""

# %%
# Importing the script dependencies
import numpy
from MPSPlots.render2D import SceneList


# %%
# Define data
x = numpy.arange(100)
y0 = numpy.random.rand(100) + x
y1 = numpy.random.rand(100) - x

# %%
# Creating the Scene
figure = SceneList(
    unit_size=(8, 4),
    title=''
)

# %%
# Adding an axis to the scene for the plots
ax = figure.append_ax(
    x_label='x data',
    y_label='y data',
    show_legend=True
)


# %%
# Adding a FillLine artist to axis
_ = ax.add_fill_line(
    x=x,
    y0=y0,
    y1=y1,
    label='Fill between lines',
    show_outline=True
)

# %%
# Adding a Table artist to axis
ax.add_table(
    table_values=['1', '2', '3', '4'],
)

# %%
# Showing the figure
_ = figure.show()
