from opcua import Client
from opcua import ua
from cliente import Cliente
import threading
import time
## PROTOCOLO OPC-UA
# Se declaran después cuando se haga el controlador
variables_manipuladas = {'Valvula1': 0, 'Valvula2':0 , 'Razon1':0, 'Razon2':0}

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
        #print("Python: New event", event)
        pass

#Clase PID
class PID:
    def __init__(self, voltmax=1):
        self.Kp = 0.2
        self.Ki = 0.2
        self.Kd = 0.2
        self.Kw = 0
        self.umax = voltmax
        self.sample_time = 0
        self.current_time = time.time()
        self.last_time = self.current_time
        self.setPoint = 38
        self.P = 0
        self.I = 0
        self.D = 0
        self.last_error = 0
        self.int_error = 0
        self.u = 0
        self.uOriginal = 0

    def update(self, value): 
        error = self.setPoint - value
        self.current_time = time.time()
        delta_time = self.current_time - self.last_time
        delta_error = error - self.last_error

        if delta_time < self.sample_time:
            time.sleep(self.sample_time - delta_time)

        self.P = self.Kp*error
        self.I += (self.Ki*error + self.Kw*(self.u - self.uOriginal))*delta_time
        #Anti Windup
        if error < 0.5:
            self.I = 0
        if delta_time > 0:
            self.D = self.Kd*delta_error/delta_time

        
        self.uOriginal = self.P + self.I + self.D
        #print('Uoriginal: {}'.format(self.uOriginal))
        if self.uOriginal > self.umax:
            self.u = self.umax
        elif self.uOriginal < -self.umax:
            self.u = -self.umax
        else:
            self.u = self.uOriginal

        self.last_time = self.current_time
        self.last_error = error
        return self.u



## CONECTAR A SERVIDOR
cliente = Cliente("opc.tcp://localhost:4840/freeopcua/server/", suscribir_eventos=True, SubHandler=SubHandler)
cliente.conectar()
objetcnode = cliente.objects
v11 = objetcnode.get_child(['2:Proceso_Tanques', '2:Valvulas','2:Valvula1','2:u'])
h11 = objetcnode.get_child(['2:Proceso_Tanques', '2:Tanques','2:Tanque1','2:h'])
h22 = objetcnode.get_child(['2:Proceso_Tanques', '2:Tanques','2:Tanque2','2:h'])
h33 = objetcnode.get_child(['2:Proceso_Tanques', '2:Tanques','2:Tanque3','2:h'])
h44 = objetcnode.get_child(['2:Proceso_Tanques', '2:Tanques','2:Tanque4','2:h'])

gamma_1 = objetcnode.get_child(['2:Proceso_Tanques', '2:Razones','2:Razon1','2:gamma'])
gamma_2 = objetcnode.get_child(['2:Proceso_Tanques', '2:Razones','2:Razon2','2:gamma'])

gamma_1.set_value(0.8)
gamma_2.set_value(0.8)

#CONTROLADOR
controlador = PID()
controlador.setPoint = 37
controlador_2 = PID()
controlador_2.setPoint = 36
while True:
    h1 = h11.get_value()
    h2 = h22.get_value()
    h3 = h33.get_value()
    h4 = h44.get_value()
    h1 = round(h1,2)
    h2 = round(h2,2)
    h3 = round(h3,2)
    h4 = round(h4,2)
    valor_1 = controlador.update(h1)
    valor_2 = controlador.update(h2)
    v11.set_value(valor_1)
    v11.set_value(valor_2)


    print(f'Altura 1 :{h1}  || Altura 2 :{h2}  || Altura 3 :{h3}  || Altura 4 :{h4}  ')