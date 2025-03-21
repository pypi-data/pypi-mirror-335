# DBTunnelBridge

DBTunnelBridge is a Python package that simplifies database connections with optional SSH tunneling support. It provides a clean, Pythonic interface for managing both local and remote database connections through SSH tunnels, with basic automatic resource management and environment variable integration.

## Features

- 🔌 Simple database connection management
- 🔒 Secure SSH tunneling support
- 🔑 Environment variable configuration
- 🛠 SQLAlchemy integration
- 📦 Context manager support for automatic resource cleanup
- 🔄 Automatic port forwarding management

## Installation

```bash
pip install dbtunnelbridge
```

## Quick Start

### Basic Local Connection
```python
from dbtunnelbridge import create_db_connection
# Create a direct database connection
with create_db_connection(
        db_user="your_user",
        db_password="your_password",
        db_host="localhost",
        db_port=3306
        ) as db:
    session = db.get_session()
    # Your database operations here
```
### Create a connection through SSH tunnel
```python
from dbtunnelbridge import create_db_connection

with create_db_connection(
    db_user="your_user",
    db_password="your_password",
    db_host="internal.database.host",
    db_port=3306,
    use_ssh_tunnel=True,
    ssh_host="bastion.example.com",
    ssh_username="ssh_user",
    ssh_pkey="/path/to/private/key"
) as db:
    session = db.get_session()
    # Your database operations here
```


## Environment Variables Support

DBTunnelBridge supports configuration through environment variables:

### Database Configuration
- `DB_USER`: Database username
- `DB_PASSWORD`: Database password
- `DB_HOST`: Database host
- `DB_PORT`: Database port

### SSH Tunnel Configuration
- `USE_SSH_TUNNEL`: Enable/disable SSH tunneling ('true'/'false')
- `SSH_HOST`: SSH tunnel host
- `SSH_USERNAME`: SSH username
- `SSH_PKEY`: Path to SSH private key

## Advanced Usage

### Manual Resource Management
```python
db = create_db_connection(
    db_user="your_user",
    db_password="your_password",
    db_host="localhost",
    db_port=3306
)
try:
    db.create_engine()
    session = db.get_session()
    # Your database operations here
finally:
    db.close_tunnel_if_needed()
```

## Requirements

- Python 3.10+
- SQLAlchemy
- PyMySQL
- sshtunnel
- paramiko