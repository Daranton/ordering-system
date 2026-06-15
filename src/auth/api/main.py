from fastapi import FastAPI

app = FastAPI(
    title="Auth Service",
    description="Authentication service: registration, login, JWT issuance",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
