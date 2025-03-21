from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .ssh_tunnel import SSHTunnelManager


class DatabaseConnection:
    """
    A class to manage database connections with optional SSH tunneling support.

    This class provides functionality to establish and manage database connections,
    optionally through an SSH tunnel. It supports both direct connections and
    tunneled connections using SQLAlchemy as the database interface.

    Attributes:
        db_user (str): Database username for authentication
        db_password (str): Database password for authentication
        db_host (str): Host address of the database server
        db_port (int): Port number for the database connection
        engine (Engine): SQLAlchemy engine instance
        Session (sessionmaker): SQLAlchemy session factory
        use_ssh_tunnel (bool): Flag indicating whether to use SSH tunneling
        ssh_tunnel_manager (SSHTunnelManager): Manager for SSH tunnel if enabled
    """

    def __init__(self, db_user, db_password, db_host, db_port, use_ssh_tunnel=False, ssh_tunnel_params=None):
        """
        Initialize a new DatabaseConnection instance.

        Args:
            db_user (str): Database username
            db_password (str): Database password
            db_host (str): Database host address
            db_port (int): Database port number
            use_ssh_tunnel (bool, optional): Whether to use SSH tunneling. Defaults to False.
            ssh_tunnel_params (dict, optional): Parameters for SSH tunnel configuration.
                Should contain ssh_host, ssh_username, ssh_pkey, remote_host, and remote_port.
        """
        self.db_user = db_user
        self.db_password = db_password
        self.db_host = db_host
        self.db_port = db_port
        self.engine = None
        self.Session = None
        self.use_ssh_tunnel = use_ssh_tunnel
        self.ssh_tunnel_manager = None

        if self.use_ssh_tunnel and ssh_tunnel_params:
            self.ssh_tunnel_manager = SSHTunnelManager(**ssh_tunnel_params)

    def start_tunnel_if_needed(self):
        """
        Start SSH tunnel if tunneling is enabled.

        This method initializes the SSH tunnel connection if tunneling is enabled
        and updates the database port to use the local forwarded port.
        """
        if self.use_ssh_tunnel and self.ssh_tunnel_manager:
            self.db_port = self.ssh_tunnel_manager.start_tunnel()

    def create_engine(self):
        """
        Create and configure the SQLAlchemy engine.

        This method sets up the database connection engine, establishing the SSH tunnel
        if needed, and creates a session factory for database operations.
        """
        self.start_tunnel_if_needed()
        self.engine = create_engine(
            f"mysql+pymysql://{self.db_user}:{self.db_password}@127.0.0.1:{self.db_port}" if self.use_ssh_tunnel else
            f"mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}"
        )
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        """
        Get a new SQLAlchemy session.

        Returns:
            Session: A new SQLAlchemy session instance

        Raises:
            Exception: If create_engine() hasn't been called before getting a session
        """
        if self.Session is None:
            raise Exception("Session not initialized. Call 'create_engine()' first.")
        return self.Session()

    def close_tunnel_if_needed(self):
        """
        Close the SSH tunnel if it's active.

        This method safely closes the SSH tunnel connection if tunneling is enabled
        and the tunnel is active.
        """
        if self.use_ssh_tunnel and self.ssh_tunnel_manager:
            self.ssh_tunnel_manager.stop_tunnel()

    def __enter__(self):
        """
        Context manager entry point.

        Creates the database engine and returns self for use in with statements.

        Returns:
            DatabaseConnection: The current instance
        """
        self.create_engine()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit point.

        Ensures proper cleanup of resources, particularly the SSH tunnel if it's in use.

        Args:
            exc_type: Exception type if an error occurred
            exc_val: Exception value if an error occurred
            exc_tb: Exception traceback if an error occurred
        """
        self.close_tunnel_if_needed()
