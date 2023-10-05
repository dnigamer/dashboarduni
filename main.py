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

cursor = db.cursor()

if db.is_connected():
    log.light_green("database", "Connected to MySQL database")
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS `dashgastos`.`registos` (`id` INT NOT NULL AUTO_INCREMENT , `data` TEXT NOT NULL , `hora` TEXT NOT NULL , `credito` FLOAT NULL DEFAULT '0.0' , `debito` FLOAT NULL DEFAULT '0.0' , `saldo` FLOAT NOT NULL , `descricao` TEXT NOT NULL , PRIMARY KEY (`id`)) ENGINE = InnoDB;"
    )
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

    cursor.execute("SELECT saldo FROM registos ORDER BY id DESC LIMIT 1")
    saldo_atual: float = cursor.fetchone()[0]

    try:
        if data["tipo"] == 1: # debito
            cursor.execute(
                "INSERT INTO registos (data, hora, debito, saldo, descricao) VALUES (%s, %s, %s, %s, %s)", (
                    data["data"], data["hora"], data["valor"],
                    saldo_atual - data["valor"], data["descricao"],
                ),
            )
            db.commit()
        elif data["tipo"] == 2: # credito
            cursor.execute(
                "INSERT INTO registos (data, hora, credito, saldo, descricao) VALUES (%s, %s, %s, %s, %s)", (
                    data["data"], data["hora"], data["valor"],
                    saldo_atual + data["valor"], data["descricao"],
                ),
            )
            db.commit()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "httpCode": 500,
                "httpState": "Internal Server Error",
                "errorData": str(e),
            },
        )

    cursor.execute("SELECT id FROM registos ORDER BY id DESC LIMIT 1")
    return JSONResponse(
        status_code=200,
        content={"httpCode": 200, "httpState": "OK", "idRecord": cursor.fetchone()[0]},
    )
