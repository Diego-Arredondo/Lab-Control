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
import pandas as pd
import datetime

#MODIFICABLES

manual = True
extension = ".csv"
guardar = False
ref_H1 = 0
ref_H2 = 0
Kd = 0
Ki = 0
Kp = 0
Kw = 0
filtro = 0
memoria = []
alarma = False
evento_alarma = 0

# ENTRADA MANUAL
frecMax = 1 # FRECUENCIA MAXIMA SINUSOIDE
valor_fijo = True # BOOL QUE DETERMINA SI ES VALOR FIJO O SINUSOIDE
amp = 1
frec = frecMax/4
fase = 0
offset = 0
V1 = 0
V2 = 0


######################## Interfaz Grafica ###############################


DataSource = ColumnDataSource(dict(time=[], H1=[], H2=[], H3=[], H4=[], V1=[], V2=[], ref_H1 = [], ref_H2 = [], ref_0=[])) # SE DEFINE EL DATASOURCE

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
fig_H3.line(x='time', y='ref_0', alpha=0.8, line_width=3, color='white', source=DataSource)
fig_H3.xaxis.axis_label = 'Tiempo (S)'
fig_H3.yaxis.axis_label = 'Valores'

fig_H4 = figure(title='H4', plot_width=600, plot_height=200, tools="reset,xpan,xwheel_zoom,xbox_zoom", y_axis_location="left")
fig_H4.line(x='time', y='H4', alpha=0.8, line_width=3, color='black', source=DataSource, legend_label='H4')
fig_H4.line(x='time', y='ref_0', alpha=0.8, line_width=3, color='white', source=DataSource)
fig_H4.xaxis.axis_label = 'Tiempo (S)'
fig_H4.yaxis.axis_label = 'Valores'

fig_V1 = figure(title='V1', plot_width=600, plot_height=200, tools="reset,xpan,xwheel_zoom,xbox_zoom", y_axis_location="left")
fig_V1.line(x='time', y='V1', alpha=0.8, line_width=3, color='black', source=DataSource, legend_label='Voltaje 1')
fig_V1.xaxis.axis_label = 'Tiempo (S)'
fig_V1.yaxis.axis_label = 'Valores'

fig_V2 = figure(title='V2', plot_width=600, plot_height=200, tools="reset,xpan,xwheel_zoom,xbox_zoom", y_axis_location="left")
fig_V2.line(x='time', y='V2', alpha=0.8, line_width=3, color='black', source=DataSource, legend_label='Voltaje 2')
fig_V2.xaxis.axis_label = 'Tiempo (S)'
fig_V2.yaxis.axis_label = 'Valores'

#TEXTOS
estilo  = {'color':'black', 'font': '15px bold arial, sans-serif', 'background-color': '#FFAC9A', 'text-align': 'center','border-radius': '7px'}
estilo_alarma_inactivo = {'color':'black', 'font': '30px bold arial, sans-serif', 'background-color': 'green', 'text-align': 'center','border-radius': '12px'}
estilo_alarma_activo = {'color':'black', 'font': '30px bold arial, sans-serif', 'background-color': 'red', 'text-align': 'center','border-radius': '12px'}
alarma_text = PreText(text=f"Alarma inactiva :)", width = 600, style = estilo_alarma_inactivo)


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
Kw_text = PreText(text=f"Kw: 0", width=300, style=estilo)
#windup_text = PreText(text=f"Wind-Up", width=300, style=estilo)
filtro_text = PreText(text=f"Filtro: 0", width=300, style=estilo)

mv = {'v1': 0, 'v2': 0, 'g1': 0.6, 'g2': 0.7}

def callback_v1(attr,old, new):
    global V1
    V1 = new

def callback_v2(attr,old, new):
    global V2
    V2 = new

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

def callback_Kw(attr, old, new):
    global Kw
    Kw = new

def callback_filtro(attr, old, new):
    global filtro
    filtro = new

def callback_amp(attr, old, new):
    global amp
    amp = new

def callback_offset(attr, old, new):
    global offset
    offset = new

def callback_frec(attr, old, new):
    global frec
    frec = new

def callback_fase(attr, old, new):
    global fase
    fase = new
    
# SLIDERS
slider_v1 = Slider(start=-1, end=1, value=mv['v1'], step=0.1, title="Voltaje 1")
slider_v1.on_change('value', callback_v1)

slider_v2 = Slider(start=-1, end=1, value=mv['v2'], step=0.1, title="Voltaje 2")
slider_v2.on_change('value', callback_v2)

slider_g1 = Slider(start=0, end=1, value=mv['g1'], step=0.05, title="Gamma 1")
slider_g1.on_change('value', callback_g1)

slider_g2 = Slider(start=0, end=1, value=mv['g2'], step=0.05, title="Gamma 2")
slider_g2.on_change('value', callback_g2)

slider_H1 = Slider(start=0, end=50, value=0, step=1, title="Ref H1")
slider_H1.on_change('value', callback_H1)

slider_H2 = Slider(start=0, end=50, value=0, step=1, title="Ref H2")
slider_H2.on_change('value', callback_H2)

slider_filtro = Slider(start=0, end=1, value=0, step=0.05, title="Factor filtro derivativo")
slider_filtro.on_change('value', callback_filtro)

slider_windup = Slider(start=0, end=1, value=0, step=0.05, title="Factor Wind-up")
slider_windup.on_change('value', callback_Kw)

slider_frec = Slider(start=frecMax/25, end=frecMax/2, value=frecMax/4, step=0.05, title="Frecuencia sinusoide")
slider_frec.on_change('value', callback_frec)

slider_amp = Slider(start=0.1, end=1, value=1, step=0.05, title="Amplitud sinusoide")
slider_amp.on_change('value', callback_amp)

slider_offset = Slider(start=-1, end=1, value=0, step=0.05, title="Offset sinusoide")
slider_offset.on_change('value', callback_offset)

slider_fase = Slider(start=0, end=6.28, value=0, step=0.05, title="Fase sinusoide")
slider_fase.on_change('value', callback_fase)



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

def callback_voltajes(attr, old, new):
    global valor_fijo
    if str(new) == '0':
        valor_fijo = True
    elif str(new) == '1':
        valor_fijo = False 

LABELS_V = ['Valor fijo', 'Sinusoide']
voltajes_rg = RadioGroup(labels=LABELS_V, active=0)
voltajes_rg.on_change('active', callback_voltajes)


#BOTON INICIAR
def activador(active):
    global manual
    manual = not manual

act = Toggle(label="Manual/Automático", button_type="success")
act.on_click(activador)

#BOTON GUARDAR
def guardador(active):
    global guardar, t, T_init
    guardar = not guardar
    if guardar:
        T_init = time.time() - t

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

######################## CONFIGURACION DEL CLIENTE #######################

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
rootNode = client.get_root_node()

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

#ALARMAS

# Función que se suscribe
def funcion_handler(node, val):
    key = node.get_parent().get_display_name().Text
    variables_manipuladas[key] = val # Se cambia globalmente el valor de las variables manipuladas cada vez que estas cambian
    print('key: {} | val: {}'.format(key, val))



class SubHandler(object): # Clase debe estar en el script porque el thread que comienza debe mover variables globales
    def datachange_notification(self, node, val, data):
        thread_handler = threading.Thread(target=funcion_handler, args=(node, val))  # Se realiza la descarga por un thread
        thread_handler.start()

    def event_notification(self, event):
        global evento_alarma
        evento_alarma = event
        #print(event)


eventos = rootNode.get_child(["0:Types", "0:EventTypes", "0:BaseEventType", "2:Alarma_nivel"]) # TIPO DE EVENTO
obj_evento = objectsNode.get_child(['2:Proceso_Tanques', '2:Alarmas', '2:Alarma_nivel']) # OBJETO EVENTO
handler_event = SubHandler()
sub_event = client.create_subscription(100, handler_event) #Subscripción al evento
handle_event = sub_event.subscribe_events(obj_evento, eventos)

#########################################################################

def funcion_guardado(mem_pd, T_init, T_now):
    global extension
    nombre = f"{T_init} - {T_now}{extension}"
    if extension == '.csv':
        mem_pd.to_csv(nombre)
    elif extension == '.txt':
        mem_npy = mem_pd.to_numpy()
        np.savetxt(nombre, mem_npy, fmt = '%s')
    elif extension == '.npy':
        mem_npy = mem_pd.to_numpy()
        np.save(nombre, mem_npy)
    print(f"Se ha guardado el archivo {nombre}")

pid1=PID()
pid2=PID()

t = time.time()
t_sin = 0
T_init = 0
def MainLoop():
    global t, manual, mv, extension, guardar, ref_H1, ref_H2
    global Kp, Ki, Kd, Kw, filtro, memoria, T_init
    global estilo_alarma_inactivo, estilo_alarma_activo, evento_alarma
    global offset, frec, amp, fase, valor_fijo, t_sin, V1, V2
    value_H1 = h1.get_value()
    value_H2 = h2.get_value()
    value_H3 = h3.get_value()
    value_H4 = h4.get_value()

    T_now = time.time() - t # TIEMPO ACTUAL


    update = dict(time=[round(T_now, 3)], H1=[value_H1], H2=[value_H2], H3=[value_H3], H4=[value_H4], V1 = [mv['v1']], V2 = [mv['v2']], ref_H1=[ref_H1], ref_H2=[ref_H2], ref_0=[0])
    DataSource.stream(new_data=update, rollover=100) # Se ven los ultimos 100 datos

    if manual:
        manual_text.text = "Manual"
        if valor_fijo:
            mv['v1'] = V1
            mv['v2'] = V2
        else:
            mv['v1'] = amp*np.cos(2*np.pi*frec*t_sin + fase) + offset
            mv['v2'] = amp*np.cos(2*np.pi*frec*t_sin + fase) + offset
            t_sin += 1/frecMax
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
        pid1.Kw = float(Kw)
        pid2.Kp = float(Kp)
        pid2.Ki = float(Ki)
        pid2.Kd = float(Kd)
        pid2.Kw = float(Kw)
        pid1.filtro = float(filtro)
        pid2.filtro = float(filtro)

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

    v1_text.text = f"Voltaje válvula 1: {round(mv['v1'], 3)}"
    v2_text.text = f"Voltaje válvula 2: {round(mv['v2'], 3)}"
    gamma1_text.text = f"Gamma 1: {mv['g1']}"
    gamma2_text.text = f"Gamma 2: {mv['g2']}"

    ref_H1_text.text = f"Referencia H1: {ref_H1}"
    ref_H2_text.text = f"Referencia H2: {ref_H2}"

    Kp_text.text = f"Kp: {Kp}"
    Kd_text.text = f"Kd: {Kd}"
    Ki_text.text = f"Ki: {Ki}"
    Kw_text.text = f"Kw: {Kw}"
    filtro_text.text = f"Filtro: {filtro}"

    if guardar:
        #APPEND A LA MEMORIA
        memoria.append(
                {'tiempo': round(T_now,3), 'H1': value_H1 , 'H2': value_H2, 'H3': value_H3, 'H4': value_H4,
                 'V1': mv['v1'], 'V2': mv['v2'], 'Gamma_1': mv['g1'], 'Gamma_2': mv['g2'], 'modo': manual_text.text, 'ref_H1': float(ref_H1), 'ref_H2': float(ref_H2),
                 'Ki': float(Ki),'Kd': float(Kd),'Kp': float(Kp),'Kw': float(Kw), 'Filtro': filtro})

    elif not guardar and len(memoria) > 0:
        #CUANDO HAYAN DATOS Y SE DEJE DE PRESIONAR GUARDAR  
        mem_pd = pd.DataFrame(memoria)
        mem_pd = mem_pd.set_index('tiempo')  
        funcion_guardado(mem_pd, round(T_init,3), round(T_now,3))
        T_init = round(time.time(),3) - t
        memoria = []

    # ALARMA
    if evento_alarma != 0:
        alarma_text.style = estilo_alarma_activo
        alarma_text.text = f"Alarma Activa!!!!"
        evento_alarma = 0
    else:
        alarma_text.style = estilo_alarma_inactivo
        alarma_text.text = f"Alarma Inactiva"


###########################

l1 = layout([
   [fig_H1, fig_H2, column(act, slider_v1, slider_v2)],
   [fig_H3, fig_H4, column(slider_g1, slider_g2)],
   [fig_V1, fig_V2, column(extensiones_rg, boton_guardar)],
   [manual_text, v1_text, v2_text, gamma1_text, gamma2_text],
   [alarma_text],
   [voltajes_rg, column(slider_frec, slider_amp), column(slider_offset, slider_fase)]])

l2 = layout([fig_H1, fig_H2],
    [slider_windup, slider_filtro, slider_H1, slider_H2],
    [column(ref_H1_text, ref_H2_text, Kp_text, Ki_text, Kd_text), 
    column(Kw_text, filtro_text), column(Kp_input, Ki_input, Kd_input)],[alarma_text])

tab1 = Panel(child=l1,title="Control Manual")
tab2 = Panel(child=l2,title="Control Automático")

tabs = Tabs(tabs=[ tab1, tab2 ])

curdoc().add_root(tabs)
curdoc().title = "Experiencia 1: Control de procesos"
curdoc().add_periodic_callback(MainLoop, 500) # Cada 100 milisegundos se llama a la funcion y se actualiza el grafico

