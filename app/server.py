from fastapi import FastAPI, Request


app = FastAPI()


@app.get("/")
async def starter(request: Request):
    return {
        "msg": "ok"
    }