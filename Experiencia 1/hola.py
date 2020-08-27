from opcua import Client
from opcua import ua


cliente = Client("opc.tcp://localhost:4840/freeopcua/server/")
print(type(cliente))
try:
    print(2)
    cliente.connect()
    print("hola")
    objectsNode = cliente.get_objects_node()
    h1 = objectsNode.get_child(['1:Proceso Tanques', '1:Tanques','Tanque1','1:h'])
    valor = h1.get_value()
except:
    cliente.disconnect()
