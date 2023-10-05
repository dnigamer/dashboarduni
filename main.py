"""
Dashboard Gastos
(c) 2023 by DniGamer @dnigamer

"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse

from modules.logger import Logger

import mysql.connector
import json

log: Logger = Logger(headerEnabled=False)

with open("secrets.json", "r") as f:
    secrets = json.loads(f.read())
    f.close()

db = mysql.connector.connect(
    host=secrets["host"],
    user=secrets["login"],
    password=secrets["password"],
    database=secrets["database"],
)

if db.is_connected():
    log.light_green("database", "Connected to MySQL database")
else:
    log.red("database", "Failed to connect to MySQL database")


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/hi", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/saldo", response_class=JSONResponse)
async def saldo_api():
    saldo: float = 100.6
    return {"saldo": saldo}


@app.post("/api/registar", response_class=JSONResponse)
async def registar_api(request: Request):
    data = await request.json()
    print(data)

    # fmt: off
    if data["valor"] == "" or data["tipo"] == "" or data["data"] == "" or data["hora"] == "":
        raise HTTPException(
            status_code=400,
            detail={
                "httpCode": 400,
                "httpState": "Bad Request",
                "errorData": "Missing parameters.",
            },
        )
    # fmt: on

    return JSONResponse(
        status_code=200, content={"httpCode": 200, "httpState": "OK", "idRecord": 1}
    )
