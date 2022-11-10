import time
import psycopg2
from fastapi import FastAPI
from psycopg2.extras import RealDictCursor

import config
from . import models
from .database import engine
from .routers import user, post

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

"""Database connect"""
while True:
    try:
        conn = psycopg2.connect(host=config.HOST,
                                database=config.DATABASE,
                                user=config.POSTGRESQL_USER,
                                password=config.POSTGRESQL_PASSWORD,
                                cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Databases connection successful")
        break
    except Exception as err:
        print(f"Connect failed | error - {err}")
        time.sleep(2)


app.include_router(user.router)
app.include_router(post.router)

@app.get("/")
def hello():
    return {"Hello": "World"}
