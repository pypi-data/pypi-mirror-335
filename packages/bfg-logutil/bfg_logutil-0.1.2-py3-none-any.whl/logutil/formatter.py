def format_params(params):
    if params is None:
        return ""
    return " ".join(f"{k}={v}" for k, v in params.items())
