from sshtunnel import SSHTunnelForwarder


class SSHTunnelManager:
    def __init__(self, ssh_host, ssh_username, ssh_pkey, remote_host, remote_port):
        self.ssh_host = ssh_host
        self.ssh_username = ssh_username
        self.ssh_pkey = ssh_pkey
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.tunnel = None

    def start_tunnel(self):
        self.tunnel = SSHTunnelForwarder(
            (self.ssh_host),
            ssh_username=self.ssh_username,
            ssh_pkey=self.ssh_pkey,
            host_pkey_directories=[],  # This is to silence an error https://stackoverflow.com/a/77869422/21915248
            remote_bind_address=(self.remote_host, self.remote_port)
        )
        self.tunnel.start()
        print("****SSH Tunnel Established****")
        return self.tunnel.local_bind_port

    def stop_tunnel(self):
        if self.tunnel:
            self.tunnel.stop()
            print("****SSH Tunnel Closed****")

    def close_tunnel_if_needed(self):
        if self.tunnel:
            self.stop_tunnel()

    def __enter__(self):
        self.start_tunnel()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_tunnel_if_needed()