import os
import subprocess
import venv
from pathlib import Path
from holisticai_sdk.utils.logger import get_logger
from holisticai_sdk.assessments.model_context import Model
import shutil
import pickle, os, tempfile
import json
import sys   

logger = get_logger(__name__)

def get_default_requirements_path():
    requirements = ["holisticai[bias]>=1.0.14", "pydantic==2.10.6"]
    text = "\n".join(requirements)
    temp_path = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
    with open(temp_path.name, "w") as f:
        f.write(text)
    return temp_path.name

def get_env_dir(env_name: str):
    home = Path.home()
    return os.path.join(home, ".hai","envs",env_name)

def get_run_assessment_script_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "run_assessment.py")

def create_virtual_environment(env_name: str):
    """Create a virtual environment in the specified directory."""
    env_dir = get_env_dir(env_name)
    
    # Create parent directories if they don't exist
    os.makedirs(os.path.dirname(env_dir), exist_ok=True)
    
    try:
        # First attempt: use venv with pip
        builder = venv.EnvBuilder(with_pip=True, system_site_packages=False)
        builder.create(env_dir)
        logger.info(f"Virtual environment created at: {env_dir}")
    except subprocess.CalledProcessError:
        logger.warning("Failed to create environment with pip. Trying alternative approach...")
        try:
            # Second attempt: use venv without pip, then install pip manually
            builder = venv.EnvBuilder(with_pip=False, system_site_packages=False)
            builder.create(env_dir)
            
            # Determine the Python executable path
            if os.name == "nt":  # Windows
                python_executable = os.path.join(env_dir, "Scripts", "python.exe")
            else:  # Linux / macOS
                python_executable = os.path.join(env_dir, "bin", "python")
                
            # Install pip using get-pip.py
            import urllib.request
            temp_file = os.path.join(tempfile.gettempdir(), "get-pip.py")
            urllib.request.urlretrieve("https://bootstrap.pypa.io/get-pip.py", temp_file)
            
            subprocess.run([python_executable, temp_file], check=True)
            os.remove(temp_file)
            logger.info(f"Virtual environment created at: {env_dir} with manually installed pip")
        except Exception as e:
            logger.error(f"Failed to create virtual environment: {e}")
            raise


def delete_virtualenv(env_name):
    """
    Delete the specified directory if it exists.
    """
    env_path = get_env_dir(env_name)

    if os.path.exists(env_path):
        try:
            shutil.rmtree(env_path)
            logger.info(f"The virtual environment in '{env_path}' has been deleted.")
        except Exception as e:
            logger.error(f"Error deleting the virtual environment: {e}")
    else:
        logger.info(f"The virtual environment '{env_path}' does not exist.")

def run_client_in_env(env_name: str, client_script: str, input_path: str, output_path: str, client_port: int):
    """
    Execute a Python script using the specified virtual environment interpreter, capturing output and errors.

    Returns:
        A tuple (success: bool, output: str, error: str)
    """
    env_dir = get_env_dir(env_name)
    if os.name == "nt":
        python_executable = os.path.join(env_dir, "Scripts", "python.exe")
    else:
        python_executable = os.path.join(env_dir, "bin", "python")

    command = [python_executable, client_script, '--input_path', input_path,
               '--output_path', output_path, '--client_port', str(client_port)]
    cwd = env_dir#os.path.dirname(os.path.dirname(os.path.dirname(client_script)))
    logger.info(f"Running {client_script} using {python_executable} in {cwd}")
    #env = os.environ.copy()
    #env['PYTHONPATH'] = cwd + os.pathsep + env.get('PYTHONPATH', '')
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            logger.info("Script executed successfully.")
            logger.info(f"Output: {result.stdout}")
            return True, result.stdout, ""
        else:
            error_message = result.stderr if result.stderr else f"Process exited with code {result.returncode}"
            logger.error(f"Script execution failed: {error_message}")
            logger.error(f"Output: {result.stdout}")
            return False, result.stdout, error_message

    except Exception as e:
        error_message = str(e)
        logger.error(f"Script execution failed with exception: {error_message}")
        return False, "", error_message


def install_dependencies(env_dir: str, requirements_file: str):
    """
    Install the dependencies listed in 'requirements_file' using the pip
    of the virtual environment located in 'env_dir'.
    """
    # Determine the path to the Python executable of the virtual environment
    if os.name == "nt":  # Windows
        python_executable = os.path.join(env_dir, "Scripts", "python.exe")
    else:  # Linux / macOS
        python_executable = os.path.join(env_dir, "bin", "python")
    
    # Execute the pip install -r requirements.txt command
    try:
        result = subprocess.run(
        [python_executable, "-m", "pip", "install", "--force-reinstall", "--no-cache-dir", "-r", requirements_file],
        capture_output=True, text=True, check=False
        )
        
        result = subprocess.run(
        [python_executable, "-m", "pip", "install", "--upgrade", "holisticai-sdk"],
        capture_output=True, text=True, check=False
        )
        
        # Always log the return code
        logger.info(f"Return code: {result.returncode}")
        
        if result.returncode == 0:
            logger.info("Dependencies installed successfully.")
            logger.info(f"Standard Output:\n {result.stdout}")
        else:
            logger.error(f"Failed to install dependencies. Exit code: {result.returncode}")
            logger.error(f"Standard Error:\n {result.stderr}")
            logger.info(f"Standard Output:\n {result.stdout}")
            
    except Exception as e:
        logger.error(f"Error installing dependencies: {e}")


def is_env_installed(env_name: str):
    return os.path.exists(get_env_dir(env_name))

def create_submit_env(env_name: str, reset_env: bool = False):
    logger.debug(f"Creating virtual environment {env_name}.")
    if is_env_installed(env_name) and reset_env:
        logger.debug(f"Resetting virtual environment {env_name}.")
        delete_virtualenv(env_name)
        logger.debug(f"Virtual environment {env_name} deleted.")
        create_virtual_environment(env_name)
        requirements_path = get_default_requirements_path()
        logger.debug(f"Installing dependencies from {requirements_path}")
        install_dependencies(get_env_dir(env_name), requirements_path)
        logger.debug(f"Environment {env_name} created and dependencies installed.")

    elif not is_env_installed(env_name):
        logger.debug(f"Creating virtual environment {env_name}.")
        create_virtual_environment(env_name)
        requirements_path = get_default_requirements_path()
        logger.debug(f"Installing dependencies from {requirements_path}")
        install_dependencies(get_env_dir(env_name), requirements_path)
        logger.debug(f"Environment {env_name} created and dependencies installed.")

    else:
        logger.debug(f"Environment {env_name} already exists.")

def submit_assessment_in_env(env_name: str, model: Model, params: dict, client_port: int = 8000, reset_env: bool = False):
    logger.info(f"Submitting assessment in environment {env_name}.")
    create_submit_env(env_name, reset_env)

    run_assessment_script_path = get_run_assessment_script_path()
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pkl") as temp_file:
        input_path = temp_file.name 
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as output_file:
        output_path = output_file.name

    pickle.dump({"params": params, "model_metadata": model.get_metadata()}, open(input_path, "wb"))
    run_client_in_env(env_name, run_assessment_script_path, input_path, output_path, client_port)
    result = json.load(open(output_path))

    os.remove(input_path)
    os.remove(output_path)
    return result