import numpy as np
import time
import sys
import random
import threading
from opcua import Client
from opcua import ua
from bokeh.models import ColumnDataSource, PreText, Toggle, Button, Slider, RadioGroup, TextInput
from bokeh.layouts import layout, column
from bokeh.plotting import curdoc, figure
from bokeh.events import ButtonClick
from bokeh.models.widgets import Tabs, Panel
from PID import PID

#MODIFICABLES

manual = True
extension = ".csv"
guardar = False
ref_H1 = 0
ref_H2 = 0
Kd = 0
Ki = 0
Kp = 0

######################## Interfaz Grafica ###############################


DataSource = ColumnDataSource(dict(time=[], H1=[], H2=[], H3=[], H4=[], ref_H1 = [], ref_H2 = [])) # SE DEFINE EL DATASOURCE

#FIGURAS CORRESPONDIENTES A CADA ALTURA
fig_H1 = figure(title='H1', plot_width=600, plot_height=200, tools="reset,xpan,xwheel_zoom,xbox_zoom", y_axis_location="left")
fig_H1.line(x='time', y='H1', alpha=0.8, line_width=3, color='blue', source=DataSource, legend_label='H1')
fig_H1.line(x='time', y='ref_H1', alpha=0.8, line_width=3, color='yellow', source=DataSource, legend_label='ref_H1')
fig_H1.xaxis.axis_label = 'Tiempo (S)'
fig_H1.yaxis.axis_label = 'Valores'

fig_H2 = figure(title='H2', plot_width=600, plot_height=200, tools="reset,xpan,xwheel_zoom,xbox_zoom", y_axis_location="left")
fig_H2.line(x='time', y='H2', alpha=0.8, line_width=3, color='red', source=DataSource, legend_label='H2')
fig_H2.line(x='time', y='ref_H2', alpha=0.8, line_width=3, color='yellow', source=DataSource, legend_label='ref_H2')
fig_H2.xaxis.axis_label = 'Tiempo (S)'
fig_H2.yaxis.axis_label = 'Valores'

fig_H3 = figure(title='H3', plot_width=600, plot_height=200, tools="reset,xpan,xwheel_zoom,xbox_zoom", y_axis_location="left")
fig_H3.line(x='time', y='H3', alpha=0.8, line_width=3, color='green', source=DataSource, legend_label='H3')
fig_H3.xaxis.axis_label = 'Tiempo (S)'
fig_H3.yaxis.axis_label = 'Valores'

fig_H4 = figure(title='H4', plot_width=600, plot_height=200, tools="reset,xpan,xwheel_zoom,xbox_zoom", y_axis_location="left")
fig_H4.line(x='time', y='H4', alpha=0.8, line_width=3, color='black', source=DataSource, legend_label='H4')
fig_H4.xaxis.axis_label = 'Tiempo (S)'
fig_H4.yaxis.axis_label = 'Valores'

#TEXTOS
estilo  = {'color':'black', 'font': '15px bold arial, sans-serif', 'background-color': '#FFAC9A', 'text-align': 'center','border-radius': '7px'}
v1_text = PreText(text=f"Voltaje válvula 1: 0", width=300, style=estilo)
v2_text = PreText(text=f"Voltaje válvula 2: 0", width=300, style=estilo)
gamma1_text = PreText(text=f"Gamma 1: 0", width=300, style=estilo)
gamma2_text = PreText(text=f"Gamma 2: 0", width=300, style=estilo)
manual_text = PreText(text=f"{manual}", width=300, style=estilo)

ref_H1_text = PreText(text=f"Referencia H1: 0", width=300, style=estilo)
ref_H2_text = PreText(text=f"Referencia H2: 0", width=300, style=estilo)
Kp_text = PreText(text=f"Kp: 0", width=300, style=estilo)
Ki_text = PreText(text=f"Ki: 0", width=300, style=estilo)
Kd_text = PreText(text=f"Kd: 0", width=300, style=estilo)
windup_text = PreText(text=f"Wind-Up", width=300, style=estilo)
filtro_text = PreText(text=f"Filtro", width=300, style=estilo)


mv = {'v1': 0, 'v2': 0, 'g1': 0.6, 'g2': 0.7}

def callback_v1(attr,old, new):
    global mv
    mv['v1'] = new

def callback_v2(attr,old, new):
    global mv
    mv['v2'] = new

def callback_g1(attr,old, new):
    global mv
    mv['g1'] = new

def callback_g2(attr,old, new):
    global mv
    mv['g2'] = new
    
def callback_H1(attr,old, new):
    global ref_H1
    ref_H1 = new

def callback_H2(attr,old, new):
    global ref_H2
    ref_H2 = new
    
# SLIDERS
slider_v1 = Slider(start=0, end=1, value=0, step=0.1, title="Voltaje 1")
slider_v1.on_change('value', callback_v1)

slider_v2 = Slider(start=0, end=1, value=0, step=0.1, title="Voltaje 2")
slider_v2.on_change('value', callback_v2)

slider_g1 = Slider(start=0, end=1, value=0, step=0.05, title="Gamma 1")
slider_g1.on_change('value', callback_g1)

slider_g2 = Slider(start=0, end=1, value=0, step=0.05, title="Gamma 2")
slider_g2.on_change('value', callback_g2)

slider_H1 = Slider(start=0, end=50, value=0, step=1, title="Ref H1")
slider_H1.on_change('value', callback_H1)

slider_H2 = Slider(start=0, end=50, value=0, step=1, title="Ref H2")
slider_H2.on_change('value', callback_H2)


#RADIOGROUP
def callback_extension(attr, old, new):
    global extension
    if str(new) == '0':
        extension = '.csv'
    elif str(new) == '1':
        extension = '.txt'
    elif str(new) == '2':
        extension = '.npy'

LABELS = [".csv", ".txt", ".npy"]

extensiones_rg = RadioGroup(labels=LABELS, active=0)
extensiones_rg.on_change('active', callback_extension)


#BOTON INICIAR
def activador(active):
    global manual
    manual = not manual

act = Toggle(label="Manual/Automático", button_type="success")
act.on_click(activador)

#BOTON GUARDAR
def guardador(active):
    global guardar
    guardar = not guardar

boton_guardar = Toggle(label="Guardar", button_type="success")
boton_guardar.on_click(guardador)

# TEXT INPUT
def Kp_callback(attr, old, new):
    global Kp
    Kp = new

def Ki_callback(attr, old, new):
    global Ki
    Ki = new

def Kd_callback(attr, old, new):
    global Kd
    Kd = new

Kp_input = TextInput(value = "", title = "Enter Kp")
Kp_input.on_change("value", Kp_callback)
Ki_input = TextInput(value = "", title = "Enter Ki")
Ki_input.on_change("value", Ki_callback)
Kd_input = TextInput(value = "", title = "Enter Kd")
Kd_input.on_change("value", Kd_callback)




client = Client("opc.tcp://localhost:4840/freeopcua/server/")
try:
    client.connect()

    print("Se conecta")
except:
    print("No se conecta")
    client.disconnect()
    sys.exit()

alturas = {'H1': 0, 'H2': 0, 'H3': 0, 'H4': 0}
objectsNode = client.get_objects_node()

# ALTURAS
h1 = objectsNode.get_child(['2:Proceso_Tanques', '2:Tanques', '2:Tanque1', '2:h'])
h2 = objectsNode.get_child(['2:Proceso_Tanques', '2:Tanques', '2:Tanque2', '2:h'])
h3 = objectsNode.get_child(['2:Proceso_Tanques', '2:Tanques', '2:Tanque3', '2:h'])
h4 = objectsNode.get_child(['2:Proceso_Tanques', '2:Tanques', '2:Tanque4', '2:h'])
#VALVULAS
v1 = objectsNode.get_child(['2:Proceso_Tanques', '2:Valvulas', '2:Valvula1', '2:u'])
v2 = objectsNode.get_child(['2:Proceso_Tanques', '2:Valvulas', '2:Valvula2', '2:u'])
g1 = objectsNode.get_child(['2:Proceso_Tanques', '2:Razones', '2:Razon1', '2:gamma'])
g2 = objectsNode.get_child(['2:Proceso_Tanques', '2:Razones', '2:Razon2', '2:gamma'])

t = 0

def funcion_guardado():
    global guardar, extension
    nombre = f"archivo{extension}"
    with open(nombre, 'w') as archivo:
        archivo.write("Esta escribiendo?")

pid1=PID()
pid2=PID()



# Se le agrega Wind-up 
pid1.Kw = float(1)
pid2.Kw = float(1)
pid2.filtro = False
def MainLoop():
    global t, manual, mv, extension, guardar, ref_H1, ref_H2
    global Kp, Ki, Kd
    value_H1 = h1.get_value()
    value_H2 = h2.get_value()
    value_H3 = h3.get_value()
    value_H4 = h4.get_value()
    t += 1

    update = dict(time=[t], H1=[value_H1], H2=[value_H2], H3=[value_H3], H4=[value_H4], ref_H1=[ref_H1], ref_H2=[ref_H2])
    DataSource.stream(new_data=update, rollover=100) # Se ven los ultimos 100 datos

    if manual:
        manual_text.text = "Manual"
        v1.set_value(mv['v1'])
        v2.set_value(mv['v2'])
        g1.set_value(mv['g1'])
        g2.set_value(mv['g2'])
    else:
        manual_text.text = "Automático"
        # SET REFERENCIAS Y Ki, Kp, Kd
        pid1.setPoint=float(ref_H1)
        pid2.setPoint=float(ref_H2)

        pid1.Kp = float(Kp)
        pid1.Ki = float(Ki)
        pid1.Kd = float(Kd)
        pid2.Kp = float(Kp)
        pid2.Ki = float(Ki)
        pid2.Kd = float(Kd)

        control_v1 = pid1.update(value_H1)
        control_v2 = pid2.update(value_H2)
        # SET DEL CONTROLADOR SOBRE V1 Y V2
        mv['v1'] = control_v1
        mv['v2'] = control_v2
        v1.set_value(control_v1)
        v2.set_value(control_v2)
        g1.set_value(mv['g1'])
        g2.set_value(mv['g2'])        
        v1.set_value(control_v1)
        v2.set_value(control_v2)

    v1_text.text = f"Voltaje válvula 1: {mv['v1']}"
    v2_text.text = f"Voltaje válvula 2: {mv['v2']}"
    gamma1_text.text = f"Gamma 1: {mv['g1']}"
    gamma2_text.text = f"Gamma 2: {mv['g2']}"

    ref_H1_text.text = f"Referencia H1: {ref_H1}"
    ref_H2_text.text = f"Referencia H2: {ref_H2}"
    Kp_text.text = f"Kp: {Kp}"
    Kd_text.text = f"Kd: {Kd}"
    Ki_text.text = f"Ki: {Ki}"



    if guardar:
        funcion_guardado()













l1 = layout([
   [fig_H1, column(act,slider_v1, slider_v2, slider_g1, slider_g2)],
   [fig_H2],
   [fig_H3, column(extensiones_rg, boton_guardar)],
   [fig_H4],
   [manual_text, v1_text, v2_text, gamma1_text, gamma2_text]])

l2 = layout([fig_H1, fig_H2],
    [slider_H1, slider_H2],
    [column(ref_H1_text, ref_H2_text, Kp_text, Ki_text, Kd_text), 
    column(windup_text, filtro_text), column(Kp_input, Ki_input, Kd_input)],)

tab1 = Panel(child=l1,title="Control Manual")
tab2 = Panel(child=l2,title="Control Automático")

tabs = Tabs(tabs=[ tab1, tab2 ])

curdoc().add_root(tabs)
curdoc().title = "Test"
curdoc().add_periodic_callback(MainLoop, 500) # Cada 100 milisegundos se llama a la funcion y se actualiza el grafico

