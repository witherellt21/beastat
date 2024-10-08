from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.nbastats.web.app import router

app = FastAPI(debug=True)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)  # type: config

app.include_router(router, prefix="/nbastats", tags=["nbastats"])
