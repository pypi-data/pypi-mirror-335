import boto3, os, yaml
import json
from typing import Dict, Any
from botocore.exceptions import EndpointConnectionError, NoCredentialsError

def load_yaml_text(contents) -> Dict[str, Any]:
    """
    Fetching profiles/connections from aws secrets manager using the user name.

    Args:
        Dict of filenames loaded from profiles.yml
    
    Returns:
        Profiles/Connections as Dict
    """
    user = os.environ.get("HOSTNAME").split('-')[1]
    try:
        secrets_manager_client = boto3.client('secretsmanager', region_name="us-east-1")
    except EndpointConnectionError as e:
        raise Exception(f"Failed to initialize SecretsManagerClient: Unable to connect to the endpoint. {e}")
    except NoCredentialsError as e:
        raise Exception(f"Failed to initialize SecretsManagerClient: No AWS credentials found. {e}")

    try:
        profiles = yaml.load(contents, Loader=yaml.SafeLoader)
    except Exception as e:
        return f"Unable to load profiles: {e}"
    
    connection_names = [connection_name for connection_name in profiles]
    
    for connection_name in connection_names:
        secret_value = secrets_manager_client.get_secret_value(SecretId=f"{user}/connections/{connection_name}")
        secrets      = json.loads(secret_value['SecretString'])
        
        if secrets['is_active']=="Y":
            profiles[connection_name] = {
                'target' : 'default',
                'outputs': {
                    'default': {
                        'host'   : f'{secrets["host"]}',
                        'user'   : f'{secrets["login"]}',
                        'pass'   : f'{secrets["password"]}',
                        'port'   : secrets["port"],
                        'threads': 1,
                        'type'   : 'postgres',
                        'dbname' : f'{secrets["schemas"]}',
                        'schema' : 'public'
                    }
                }
            }
    return profiles