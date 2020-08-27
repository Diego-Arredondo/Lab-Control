import numpy as np
from bokeh.models import ColumnDataSource, PreText
from bokeh.layouts import layout
from bokeh.plotting import curdoc, figure

#Seno
T = np.linspace(0,1000,1001)
sin = np.sin(T)
cos = np.cos(T)

#Data Source
DataSource = ColumnDataSource(dict(time=[],sin=[], cos=[]))

#Figura
fig_sin = figure(title = 'Seno y Coseno', plot_width = 600, plot_height = 200, \
    tools= "reset, xpan, xwheel_zoom, xbox_zoom", y_axis_location = "left")

fig_sin.line(x = 'time', y='sin', alpha = 0.8, line_width = 3, color= 'blue', \
    source = DataSource, legend = 'Seno')

fig_sin.line(x = 'time', y='cos', alpha = 0.8, line_width = 3, color= 'red', \
    source = DataSource, legend = 'Coseno')

fig_sin.xaxis.axis_label = 'Tiempo (S)'
fig_sin.yaxis.axis_label = 'Valores'

#Crear widget

estilo = {'color':'white', 'font':'15px bold arial, sans-serif', 'background-color':'green','text-align':'center','border-radius':'7px'}

SinText  = PreText(text= 'Valor del Seno: 0.00', width = 300, style = estilo)
CosText  = PreText(text= 'Valor del Coseno: 0.00', width = 300, style = estilo)

t = 0
def MainLoop():
    global t, sin, cos
    update = dict(time=[t], sin=[sin[t]], cos=[cos[t]])
    DataSource.stream(new_data = update, rollover=100) #visualizacion de ultimos 100 datos
    SinText.text = 'Valor del seno: {}'.format(round(sin[t],2))
    CosText.text = 'Valor del Coseno: {}'.format(round(cos[t],2))
    t += 1

l = layout([
    [fig_sin],
    [SinText, CosText]
    ])

curdoc().add_root(l)
curdoc().title = "Dashboard Ejemplo"
curdoc().add_periodic_callback(MainLoop, 300) #Se llama a la funcion cada 300 ms

