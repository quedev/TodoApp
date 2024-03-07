import logging

from fastapi import FastAPI

import models
from database import engine
from routers import auth, todos, admin, users

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

logging.getLogger('passlib').setLevel(logging.ERROR)

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', reload=True)
