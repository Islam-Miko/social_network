from fastapi import FastAPI, Request


def get_application():

    app = FastAPI()
    return app


app = get_application()


@app.get("/")
async def starter(request: Request):
    return {"msg": "ok"}
