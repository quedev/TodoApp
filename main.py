from fastapi import FastAPI
import models
from database import engine

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', reload=True)
