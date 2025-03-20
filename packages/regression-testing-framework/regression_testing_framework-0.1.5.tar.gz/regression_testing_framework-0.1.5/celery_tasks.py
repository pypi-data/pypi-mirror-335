import subprocess
import os
from typing import List, Dict, Optional, Tuple

def run_test_command(
    base_command: str,
    params: Optional[List[str]] = None,
    environment: Optional[Dict[str, str]] = None
) -> Tuple[int, str, str]:
    """
    Run a command with parameters and environment variables.
    
    Args:
        base_command: The base command to run
        params: List of parameters to pass to the command
        environment: Dict of environment variables to set
        
    Returns:
        Tuple of (return_code, stdout, stderr)
    """
    # Set up environment variables
    env = os.environ.copy()
    if environment:
        env.update(environment)
    
    params = params or []

    # Create the full command string
    # Treat the base_command as a single string and append params
    full_cmd = base_command
    if params:
        full_cmd = f"{full_cmd} {' '.join(str(p) for p in params)}"

    full_cmd = full_cmd.split()

    try:
        # Pass the full command to bash to handle the execution
        process = subprocess.run(
            args=full_cmd,  # Pass the full command as a single string
            env=env,
            text=True,
            capture_output=True
        )
        return process.returncode, process.stdout, process.stderr
    except Exception as e:
        return 1, "", f"Error executing command: {str(e)}"


def process_test_configuration(test_config: Dict) -> Tuple[int, str, str]:
    """
    Process a test configuration from the YAML file.
    
    Args:
        test_config: Dictionary with test configuration
        
    Returns:
        Tuple of (return_code, stdout, stderr)
    """
    base_command = test_config.get('base_command')
    params = test_config.get('params', [])
    
    # Convert environment list to dictionary
    env_list = test_config.get('environment', [])
    environment = {}
    for env_var in env_list:
        if '=' in env_var:
            key, value = env_var.split('=', 1)
            environment[key] = value
    
    return run_test_command(base_command, params, environment)
