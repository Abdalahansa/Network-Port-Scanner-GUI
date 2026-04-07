import socket
import threading
from queue import Queue

COMMON_PORTS = {
    21: 'FTP', 22: 'SSH', 80: 'HTTP',
    443: 'HTTPS', 3306: 'MySQL', 8080: 'HTTP-Alt'
}

class PortScanner:
    def __init__(self, target, ports, timeout=0.5, threads=100):
        self.target = socket.gethostbyname(target)
        self.ports = ports
        self.timeout = timeout
        self.threads = threads
        self.queue = Queue()
        self.open_ports = []

    def scan_port(self):
        while not self.queue.empty():
            port = self.queue.get()
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(self.timeout)

                result = s.connect_ex((self.target, port))
                if result == 0:
                    service = COMMON_PORTS.get(port, "Unknown")
                    self.open_ports.append((port, service))

                s.close()
            except:
                pass
            self.queue.task_done()

    def run(self):
        for port in self.ports:
            self.queue.put(port)

        threads = []
        for _ in range(self.threads):
            t = threading.Thread(target=self.scan_port)
            t.daemon = True
            t.start()
            threads.append(t)

        self.queue.join()
        return sorted(self.open_ports)
