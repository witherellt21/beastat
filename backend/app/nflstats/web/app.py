import logging
import os

from fastapi import APIRouter
from scrapp.example.settings import API_PREFIX

# Create a logging format for any app logs
main_formatter = logging.Formatter(
    "[{levelname:^10}] [ {asctime} ] [{threadName:^20}]  {message}",
    "%I:%M:%S %p",
    style="{",
)

# Create a Stream Handler to output logs to the standard out
main_stream_handler = logging.StreamHandler()
main_stream_handler.setFormatter(main_formatter)

# Create the main logger and set its level
main_logger = logging.getLogger(os.path.basename(__file__))
main_logger.setLevel(logging.DEBUG)
main_logger.addHandler(main_stream_handler)

# Create a router
router = APIRouter(prefix=API_PREFIX)

# Add all app routes to the router


# Gets the operational status of the hosted application
@router.get("/")
async def get_status():
    return {
        "status": True,
    }
