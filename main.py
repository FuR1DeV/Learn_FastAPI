from typing import Union

from fastapi import FastAPI
from fastapi.params import Body

app = FastAPI()


@app.get("/")
def any_def():
    return {"Hello": "World"}


@app.post("/posts")
def any_def2(payload: dict = Body(...)):
    return {"Created title!": f"You title is {payload['Title']} | Content {payload['Content']}"}

