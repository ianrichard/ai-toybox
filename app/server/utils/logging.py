import os
import logging

def setup_logging():
    log_level = logging.ERROR  # override as needed per module or env
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )