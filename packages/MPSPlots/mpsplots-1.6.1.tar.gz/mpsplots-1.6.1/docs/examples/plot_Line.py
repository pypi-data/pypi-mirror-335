"""
Simple Line
~~~~~~~~~~~
"""

# %%
# Importing the script dependencies
import numpy
from MPSPlots.render2D import SceneList


# %%
# Define data
x = numpy.linspace(-10, 10, 100)

figure = SceneList(
    unit_size=(8, 4),
    title='random data simple lines'
)


# %%
# Creating the Scene
ax = figure.append_ax(
    x_label='x data',
    y_label='y data',
    show_legend=True,
    line_width=2,
)

# %%
# Adding few Line artist to axis
_ = ax.add_line(x=x, y=x**2, label=r'y=x^2', color='blue')

_ = ax.add_line(x=x, y=x**3, label=r'y=x^3', color='red')

_ = ax.add_line(x=x, y=x**4, label=r'y=x^4', color='green')

# %%
# Showing the figure
_ = figure.show()
