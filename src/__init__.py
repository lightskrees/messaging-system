from fastapi import FastAPI
from auth.routes import router

version = "v1"

description = """
A simple messaging system API that allows users to send, receive, and manage messages.
    """

version_prefix =f"/api/{version}"

app = FastAPI(
    title="Messaging System API",
    description=description,
    version=version,
    contact={
        "name": "thedude",
        "email": "nchris3010@gmail.com",
        "url": "https://github.com/lightskrees",
    }
)

app.include_router(router)