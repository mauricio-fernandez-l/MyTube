# %%

import logging

# %%


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())
    formatter = logging.Formatter("%(name)s:%(levelname)s: %(message)s")
    for handler in logger.handlers:
        handler.setFormatter(formatter)
    return logger
