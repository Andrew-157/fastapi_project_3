from fastapi import FastAPI

from .routers import users
from .schemas import RootModel

app = FastAPI(debug=True)


app.include_router(users.router)


@app.get("/")
async def root() -> RootModel:
    model = RootModel()
    return model