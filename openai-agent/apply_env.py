import os

def apply_env():
    """
    Apply environment variables from .env file to the current environment.
    """
    env_file = "../.env"
    
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                # Ignore comments and empty lines
                if line.startswith("#") or not line.strip():
                    continue
                
                key, value = line.strip().split("=", 1)

                os.environ[key] = value
                
                print(f"{env_file} environment variables applied.")
    else:
        print(f"{env_file} file not found. No environment variables applied.")

apply_env()
    