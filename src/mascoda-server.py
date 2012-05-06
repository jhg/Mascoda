#-*- coding: UTF-8 -*-
"Servidor de Mascoda"


import socket


if __name__=="__main__":
    # Iniciamos el socket de escucha del servidor
    _socket = socket.socket()
    _socket.bind(('localhost', 16311))
    _socket.listen(5)
    _socket.settimeout(0.5)
    # Esperamos conexiones indefinidamente
    while True:
        try:
            _cliente, _direccion = _socket.accept()
            print 'Direccion'
            print _direccion
            _recibido = _cliente.recv(1024)
            print 'Recibido'
            print _recibido
            _socket.send(_recibido)
            _cliente.close()
            del _cliente
        except:
            print 'Sin clientes'
    # Cerramos el socket
    _socket.close()

