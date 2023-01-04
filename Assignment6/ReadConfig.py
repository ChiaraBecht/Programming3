import yaml

def get_config():
    """
    
    """
    with open("assignment6_config.yaml", "r") as stream:
        config = yaml.safe_load(stream)
    return config