import threading
import time
import socket
import logging
import paramiko
from stub_sftp import StubServer\
    ,StubSFTPServer
HOST , PORT ='localhost', 22
# HOST , PORT ='192.168.1.46', 22
KEYFILE ='./test_rsa.key'

class ConnHandlerThd(threading.Thread):
    def __init__(self, conn, addr, serverkeyfile ):
        threading.Thread.__init__(self)
        self._conn = conn
        self._addr = addr
        self._serverkeyfile = serverkeyfile

    def run(self):
        server_key = paramiko.RSAKey.from_private_key_file(self._serverkeyfile)
        name = server_key.get_name()
        transport = paramiko.Transport(self._conn)
        transport.add_server_key(server_key)

        transport.set_subsystem_handler( 'sftp', paramiko.SFTPServer, StubSFTPServer)

        server = StubServer()
        transport.start_server(server=server)

        channel = transport.accept()
        while transport.is_active():
            time.sleep(1)

def main():
    paramiko.common.logging.basicConfig(level=logging.INFO)  
    server_socket =socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    
    while True:
        conn, addr = server_socket.accept()
        srv_thd = ConnHandlerThd(conn, addr, KEYFILE )
        srv_thd.setDaemon(True)
        srv_thd.start()
    
if __name__ == '__main__':
    main()