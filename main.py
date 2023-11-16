"""
Dashboard Gastos
(c) 2023 by DniGamer @dnigamer

"""

from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse

from modules.logger import Logger

from sqlalchemy import create_engine
import json
import os

log: Logger = Logger(headerEnabled=False)

secrets = {
    "host": os.environ.get("DB_HOST"),
    "port": os.environ.get("DB_PORT"),
    "login": os.environ.get("DB_LOGIN"),
    "password": os.environ.get("DB_PASSWORD"),
    "database": os.environ.get("DB_DATABASE"),
}

if any([secrets[x] is None for x in secrets]):
    log.red("error", "Not all secrets are set.")
    log.red(
        "error",
        "Program will not start without them. Please check if you have set all the environment variables.",
    )
    exit(1)

engine = create_engine(
    "mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}".format(
        user=secrets["login"],
        password=secrets["password"],
        host=secrets["host"],
        port=secrets["port"],
        database=secrets["database"],
    )
)

# connect to the database
try:
    db = engine.raw_connection()
    log.light_green("database", "Connected to MySQL database")
    cursor = db.cursor()
    cursor.execute(
        f"CREATE TABLE IF NOT EXISTS `{secrets['database']}`.`registos` (`id` INT NOT NULL AUTO_INCREMENT, `data` TEXT NOT NULL, `valor` FLOAT NOT NULL DEFAULT '0.0', `tipo` FLOAT NOT NULL DEFAULT '0.0', `descricao` TEXT NOT NULL DEFAULT '', `fatura_id` TEXT NULL, PRIMARY KEY (`id`)) ENGINE = InnoDB;"
    )
except Exception as e:
    log.red("database", "Failed to connect to MySQL database: " + str(e))


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Middleware
# Define the middleware function


async def log_requests(request: Request, call_next):
    now = datetime.now()
    if request.headers.get("x-real-ip") == None:
        realIP = "0.0.0.0"
    else:
        realIP = request.headers.get("x-real-ip")
    try:
        cursor.execute(
            "INSERT INTO `dashgastos`.hits (date, IP, `real-IP`, method, path, useragent) VALUES (%s, %s, %s, %s, %s, %s)",
            (
                now.strftime("%d/%m/%Y %H:%M:%S"),
                request.client.host,
                realIP,
                request.method,
                request.url.path,
                request.headers.get("user-agent"),
            ),
        )
        db.commit()
    except Exception as e:
        log.red("database", "Failed to save log to MySQL database: " + str(e))
    response = await call_next(request)
    return response


app.middleware("http")(log_requests)


# Site principal
@app.get("/home", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# API Saldo
@app.get("/api/saldo", response_class=JSONResponse)
async def saldo_api():
    try:
        cursor.execute(
            "SELECT ROUND(ABS(SUM(CASE WHEN tipo = 1 THEN valor ELSE 0 END) - SUM(CASE WHEN tipo = 2 THEN valor ELSE 0 END)), 2) AS saldo FROM registos;"
        )
        saldo: float = cursor.fetchone()[0]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            headers={"Content-Type": "application/json; charset=utf-8"},
            detail={
                "httpCode": 500,
                "httpState": "Internal Server Error",
                "errorData": str(e),
            },
        )

    return JSONResponse(
        status_code=200,
        headers={"Content-Type": "application/json; charset=utf-8"},
        content={"httpCode": 200, "httpState": "OK", "saldo": saldo},
    )


# API Registo debito/crédito
@app.post("/api/registar", response_class=JSONResponse)
async def registar_api(request: Request):
    data = await request.json()
    print(data)

    # fmt: off
    if data["valor"] == "" or data["tipo"] == "" or data["data"] == "":
        raise HTTPException(
            status_code=400,
            headers={"Content-Type": "application/json; charset=utf-8"},
            detail={
                "httpCode": 400,
                "httpState": "Bad Request",
                "errorData": "Missing parameters.",
            },
        )

    try:
        cursor.execute(
            "INSERT INTO registos (data, valor, tipo, descricao, fatura_id) VALUES (%s, %s, %s, %s, %s)",
            (data["data"], data["valor"], data["tipo"], data["descricao"], data["fatura_id"]),
        )
        # fmt: on
        db.commit()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            headers={"Content-Type": "application/json; charset=utf-8"},
            detail={
                "httpCode": 500,
                "httpState": "Internal Server Error",
                "errorData": str(e),
            },
        )

    cursor.execute("SELECT id FROM registos ORDER BY id DESC LIMIT 1")
    return JSONResponse(
        status_code=200,
        headers={"Content-Type": "application/json; charset=utf-8"},
        content={"httpCode": 200, "httpState": "OK", "idRecord": cursor.fetchone()[0]},
    )


# API Editar registo por ID
@app.put("/api/editar/{id}", response_class=JSONResponse)
async def editar_api(request: Request, id: int):
    data = await request.json()

    # fmt: off
    if data["valor"] == "" or data["tipo"] == "" or data["data"] == "":
        raise HTTPException(
            status_code=400,
            headers={"Content-Type": "application/json; charset=utf-8"},
            detail={
                "httpCode": 400,
                "httpState": "Bad Request",
                "errorData": "Missing parameters.",
            },
        )
    
    try:
        cursor.execute(
            "UPDATE registos SET data = %s, valor = %s, tipo = %s, descricao = %s, fatura_id = %s WHERE id = %s",
            (data["data"], data["valor"], data["tipo"], data["descricao"], data["fatura_id"], id),
        )
        # fmt: on
        db.commit()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            headers={"Content-Type": "application/json; charset=utf-8"},
            detail={
                "httpCode": 500,
                "httpState": "Internal Server Error",
                "errorData": str(e),
            },
        )


    return JSONResponse(
        status_code=200,
        headers={"Content-Type": "application/json; charset=utf-8"},
        content={"httpCode": 200, "httpState": "OK", "data": data},
    )


# API Consultar registo
# (usado por editar registo para obter lista de registos numa data)
@app.post("/api/consulta", response_class=JSONResponse)
async def consultar_api(request: Request):
    data = await request.json()

    try:
        cursor.execute(
            "SELECT * FROM registos WHERE `data` = %s", (data["dataConsulta"],)
        )
        registos = cursor.fetchall()

        jsondata = []
        for i in range(len(registos)):
            jsondata.append(
                {
                    "id": registos[i][0],
                    "data": str(registos[i][1]),
                    "valor": str(registos[i][2]),
                    "tipo": registos[i][3],
                    "descricao": str(registos[i][4]),
                    "fatura_id": str(registos[i][5]),
                }
            )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            headers={"Content-Type": "application/json; charset=utf-8"},
            detail={
                "httpCode": 500,
                "httpState": "Internal Server Error",
                "errorData": str(e),
            },
        )

    return JSONResponse(
        status_code=200,
        headers={"Content-Type": "application/json; charset=utf-8"},
        content={"httpCode": 200, "httpState": "OK", "data": jsondata},
    )


# API Consultar registo por ID
@app.post("/api/consulta/{id}", response_class=JSONResponse)
async def consultar_single_api(request: Request, id):
    if id == "intervalo":
        data = await request.json()

        try:
            if data["tipo"] == "3":
                cursor.execute(
                    "SELECT * FROM registos WHERE STR_TO_DATE(data, '%d/%m/%Y') BETWEEN STR_TO_DATE(%s, '%d/%m/%Y') AND STR_TO_DATE(%s, '%d/%m/%Y') AND (tipo = 1 OR tipo = 2) ORDER BY STR_TO_DATE(data, '%d/%m/%Y') ASC",
                    (
                        data["dataInicio"],
                        data["dataFim"],
                    ),
                )
            else:
                cursor.execute(
                    "SELECT * FROM registos WHERE STR_TO_DATE(data, '%d/%m/%Y') BETWEEN STR_TO_DATE(%s, '%d/%m/%Y') AND STR_TO_DATE(%s, '%d/%m/%Y') AND tipo = %s ORDER BY STR_TO_DATE(data, '%d/%m/%Y') ASC",
                    (
                        data["dataInicio"],
                        data["dataFim"],
                        data["tipo"],
                    ),
                )

            registos = cursor.fetchall()

            jsondata = []
            for i in range(len(registos)):
                jsondata.append(
                    {
                        "id": registos[i][0],
                        "data": str(registos[i][1]),
                        "valor": str(registos[i][2]),
                        "tipo": registos[i][3],
                        "descricao": str(registos[i][4]),
                        "fatura_id": str(registos[i][5]),
                    }
                )

        except Exception as e:
            raise HTTPException(
                status_code=500,
                headers={"Content-Type": "application/json; charset=utf-8"},
                detail={
                    "httpCode": 500,
                    "httpState": "Internal Server Error",
                    "errorData": str(e),
                },
            )

        return JSONResponse(
            status_code=200,
            headers={"Content-Type": "application/json; charset=utf-8"},
            content={"httpCode": 200, "httpState": "OK", "data": jsondata},
        )

    # parse id to int
    try:
        id = int(id)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            headers={"Content-Type": "application/json; charset=utf-8"},
            detail={
                "httpCode": 400,
                "httpState": "Bad Request",
                "errorData": "Invalid id.",
            },
        )
    try:
        cursor.execute(
            "SELECT * FROM registos WHERE `id` = %s;",
            (id,),
        )
        registos = cursor.fetchall()

        jsondata = []
        for i in range(len(registos)):
            jsondata.append(
                {
                    "id": registos[i][0],
                    "data": str(registos[i][1]),
                    "valor": str(registos[i][2]),
                    "tipo": registos[i][3],
                    "descricao": str(registos[i][4]),
                    "fatura_id": str(registos[i][5]),
                }
            )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            headers={"Content-Type": "application/json; charset=utf-8"},
            detail={
                "httpCode": 500,
                "httpState": "Internal Server Error",
                "errorData": str(e),
            },
        )

    return JSONResponse(
        status_code=200,
        headers={"Content-Type": "application/json; charset=utf-8"},
        content={"httpCode": 200, "httpState": "OK", "data": jsondata},
    )


# API Apagar registo por ID
@app.delete("/api/apagar/{id}", response_class=JSONResponse)
async def apagar_api(id: int):
    try:
        cursor.execute(
            "DELETE FROM registos WHERE `id` = %s;",
            (id,),
        )
        db.commit()

    except Exception as e:
        raise HTTPException(
            status_code=500,
            headers={"Content-Type": "application/json; charset=utf-8"},
            detail={
                "httpCode": 500,
                "httpState": "Internal Server Error",
                "errorData": str(e),
            },
        )

    return JSONResponse(
        status_code=200,
        headers={"Content-Type": "application/json; charset=utf-8"},
        content={"httpCode": 200, "httpState": "OK"},
    )
