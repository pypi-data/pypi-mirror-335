import os
from .db_connection import DatabaseConnection


def create_db_connection(
        db_user=None,
        db_password=None,
        db_host=None,
        db_port=None,
        use_ssh_tunnel=None,
        ssh_host=None,
        ssh_username=None,
        ssh_pkey=None,
        remote_host=None,
        remote_port=None
):
    """
    Create a database connection with optional SSH tunneling support.

    This function creates a DatabaseConnection instance with the provided credentials
    and configuration. It supports both direct database connections and connections
    through SSH tunnels. All parameters can be provided either directly or through
    environment variables.

    Args:
        db_user (str, optional): Database username. Falls back to DB_USER env var.
        db_password (str, optional): Database password. Falls back to DB_PASSWORD env var.
        db_host (str, optional): Database host. Falls back to DB_HOST env var.
        db_port (int, optional): Database port. Falls back to DB_PORT env var.
        use_ssh_tunnel (bool, optional): Whether to use SSH tunneling. Falls back to USE_SSH_TUNNEL env var.
        ssh_host (str, optional): SSH tunnel host. Required if use_ssh_tunnel is True.
        ssh_username (str, optional): SSH username. Required if use_ssh_tunnel is True.
        ssh_pkey (str, optional): Path to SSH private key. Required if use_ssh_tunnel is True.
        remote_host (str, optional): Remote database host for SSH tunnel. Defaults to db_host if not specified.
        remote_port (int, optional): Remote database port for SSH tunnel. Defaults to db_port if not specified.

    Returns:
        DatabaseConnection: A configured database connection object.

    Example:
        >>> # Direct database connection
        >>> db = create_db_connection(
        ...     db_user="user",
        ...     db_password="pass",
        ...     db_host="localhost",
        ...     db_port=3306
        ... )
        >>> 
        >>> # Connection with SSH tunnel
        >>> db = create_db_connection(
        ...     db_user="user",
        ...     db_password="pass",
        ...     db_host="db.internal",
        ...     db_port=3306,
        ...     use_ssh_tunnel=True,
        ...     ssh_host="bastion.example.com",
        ...     ssh_username="ssh_user",
        ...     ssh_pkey="/path/to/key"
        ... )
    """
    # Check if SSH tunneling should be used based on an environment variable or passed parameter
    use_ssh_tunnel = use_ssh_tunnel if use_ssh_tunnel is not None else os.getenv('USE_SSH_TUNNEL',
                                                                                 'false').lower() == 'true'

    ssh_tunnel_params = None
    if use_ssh_tunnel:
        ssh_tunnel_params = {
            "ssh_host": ssh_host or os.getenv('SSH_HOST'),
            "ssh_username": ssh_username or os.getenv('SSH_USERNAME'),
            "ssh_pkey": ssh_pkey or os.getenv('SSH_PKEY'),
            "remote_host": remote_host or db_host or os.getenv('DB_HOST'),
            "remote_port": remote_port or db_port or os.getenv('DB_PORT')
        }

    return DatabaseConnection(
        db_user=db_user or os.getenv('DB_USER'),
        db_password=db_password or os.getenv('DB_PASSWORD'),
        db_host=db_host or os.getenv('DB_HOST'),
        db_port=db_port or int(os.getenv('DB_PORT')),
        use_ssh_tunnel=use_ssh_tunnel,
        ssh_tunnel_params=ssh_tunnel_params
    )
