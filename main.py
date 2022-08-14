from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def index():
    return {"data": {"name": 'TROLOLO'}}


@app.get("/about")
def about():
    return "it's about me"
