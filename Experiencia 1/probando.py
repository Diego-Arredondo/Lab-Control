from opcua import Client
from opcua import ua
import time
from PID import PID


client= Client("opc.tcp://localhost:4840/freeopcua/server/")
contador=0

try:
    client.connect()
    
    objectsNode=client.get_objects_node()
    
    h1=objectsNode.get_child(['2:Proceso_Tanques','2:Tanques','2:Tanque1','2:h'])
    h2=objectsNode.get_child(['2:Proceso_Tanques','2:Tanques','2:Tanque2','2:h'])
    h3=objectsNode.get_child(['2:Proceso_Tanques','2:Tanques','2:Tanque3','2:h'])
    h4=objectsNode.get_child(['2:Proceso_Tanques','2:Tanques','2:Tanque4','2:h'])
    v1=objectsNode.get_child(['2:Proceso_Tanques','2:Valvulas','2:Valvula1','2:u'])
    v2=objectsNode.get_child(['2:Proceso_Tanques','2:Valvulas','2:Valvula2','2:u'])
    razon1=objectsNode.get_child(['2:Proceso_Tanques','2:Razones','2:Razon1','2:gamma'])
    razon2=objectsNode.get_child(['2:Proceso_Tanques','2:Razones','2:Razon2','2:gamma'])
    print('hola')
    
except:
    client.disconnect()
    print('error')


# v1.set_value(0.0)   
# v2.set_value(1.0)
#razon1.set_value(0.7)
#razon2.set_value(0.6)


pid1=PID()
pid2=PID()

pid1.setPoint=float(48)
pid2.setPoint=float(30)

pid1.Kp = float(0.6) #0.6 , 0.6, 0.2
pid1.Ki = float(0.8)
pid1.Kd = float(0.2)
pid1.Kw = float(0)

pid2.Kp = float(0.6)
pid2.Ki = float(0.8)
pid2.Kd = float(0.2)
pid2.Kw = float(0)


while True:

    valor_h1=h1.get_value()
    valor_h2=h2.get_value()
    valor_h3=h3.get_value()
    valor_h4=h4.get_value()
    valor_v1=v1.get_value()
    valor_v2=v2.get_value()
    valor_razon1=razon1.get_value()
    valor_razon2=razon2.get_value()
    razon1.set_value(0.8)
    razon2.set_value(0.8)
    print(f"Estanque 1={round(valor_h1,2)}, Estanque 2={round(valor_h2,2)}, Estanque 3={round(valor_h3,2)}, Estanque 4={round(valor_h4,2)}")
    print(f"Voltaje 1= {valor_v1}, Voltaje 2= {valor_v2}")
    print(f"Razon 1= {valor_razon1}, Razon 2= {valor_razon2}")

    control_v1 = pid1.update(valor_h1)
    control_v2 = pid2.update(valor_h2)

    v1.set_value(control_v1)
    v2.set_value(control_v2)


    
    






