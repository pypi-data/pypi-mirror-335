import os


def get_klu_env():
    return os.getenv("KLU_ENV", "prod")


def get_api_url():
    env = get_klu_env()
    if env == "dev":
        return "http://localhost:4000/v1"
    elif env == "staging":
        return "https://staging-api.klu.ai/v1"
    else:
        return "https://data-api.klu.ai/v1"


def get_gateway_url():
    env = get_klu_env()
    if env == "dev":
        return "http://localhost:8787/v1"
    else:
        return "https://gateway.optimizedata.app/v1"
