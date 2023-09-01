from fastapi import FastAPI

from .routers import users, questions, answers
from .schemas import RootModel

app = FastAPI(debug=True)


app.include_router(users.router)
app.include_router(questions.router)
app.include_router(answers.router)


@app.get("/")
async def root() -> RootModel:
    model = RootModel()
    return model
