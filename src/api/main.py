import http
from fastapi import FastAPI

app = FastAPI(title = "Ordering System API",
              description = "API for managing orders in the ordering system",
              version = "1.0.0")

@app.get("/")
def root() -> dict[str, str]:
    return {"status": "Ordering System API is running!"}

@app.get("/hello/{name}")
def hello(name: str) -> dict[str, str]:
    return {"message": f"Hello, {name}!"}

@app.get("/search")
def search(q: str = "", limit: int = 10) -> dict[str, str | int]:
    return {"q": q, "limit": limit}

@app.get("/status/{code}")
def get_status(code: int) -> dict[str, int | str]:
    try:
        phrase = http.HTTPStatus(code).phrase
    except ValueError:
        phrase = "Unknown status code"
    return {"code": code, "phrase": phrase}

