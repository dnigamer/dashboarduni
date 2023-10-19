"""
Dashboard Gastos
(c) 2023 by DniGamer @dnigamer

"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse

from modules.logger import Logger

from sqlalchemy import create_engine
import json

log: Logger = Logger(headerEnabled=False)

with open("secrets.json", "r") as f:
    secrets = json.loads(f.read())
    f.close()

engine = create_engine('mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}'.format(
    user=secrets["login"],
    password=secrets["password"],
    host=secrets["host"],
    port=secrets["port"],
    database=secrets["database"]
))

# connect to the database
try:
    db = engine.raw_connection()
    log.light_green("database", "Connected to MySQL database")
    cursor = db.cursor()
    cursor.execute(
        f"CREATE TABLE IF NOT EXISTS `{secrets['database']}`.`registos` (`id` INT NOT NULL AUTO_INCREMENT, `data` TEXT NOT NULL, `valor` FLOAT NOT NULL DEFAULT '0.0', `tipo` FLOAT NOT NULL DEFAULT '0.0', `descricao` TEXT NOT NULL DEFAULT '', PRIMARY KEY (`id`)) ENGINE = InnoDB;"
    )
except Exception as e:
    log.red("database", "Failed to connect to MySQL database: " + str(e))
    exit(1)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/hi", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


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
        content={"httpCode": 200, "httpState": "OK", "saldo": saldo}
    )


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
            "INSERT INTO registos (data, valor, tipo, descricao) VALUES (%s, %s, %s, %s)",
            (data["data"], data["valor"], data["tipo"], data["descricao"]),
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
            "UPDATE registos SET data = %s, valor = %s, tipo = %s, descricao = %s WHERE id = %s",
            (data["data"], data["valor"], data["tipo"], data["descricao"], id),
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
            jsondata.append({
                    "id": registos[i][0],
                    "data": str(registos[i][1]),
                    "valor": str(registos[i][2]),
                    "tipo": registos[i][3],
                    "descricao": str(registos[i][4]),
                })

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


@app.post("/api/consulta/{id}", response_class=JSONResponse)
async def consultar_single_api(id: int):

    try:
        cursor.execute(
            "SELECT * FROM registos WHERE `id` = %s;", (id, ),
        )
        registos = cursor.fetchall()

        jsondata = []
        for i in range(len(registos)):
            jsondata.append({
                    "id": registos[i][0],
                    "data": str(registos[i][1]),
                    "valor": str(registos[i][2]),
                    "tipo": registos[i][3],
                    "descricao": str(registos[i][4]),
                })

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


@app.delete("/api/apagar/{id}", response_class=JSONResponse)
async def apagar_api(id: int):
    try:
        cursor.execute(
            "DELETE FROM registos WHERE `id` = %s;", (id, ),
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


@app.post("/api/consintervalo", response_class=JSONResponse)
async def consultar_intervalo_api(request: Request):
    data = await request.json()

    try:
        if data["tipo"] == "3":
            cursor.execute(
                "SELECT * FROM registos WHERE STR_TO_DATE(data, '%d/%m/%Y') BETWEEN STR_TO_DATE(%s, '%d/%m/%Y') AND STR_TO_DATE(%s, '%d/%m/%Y') AND (tipo = 1 OR tipo = 2) ORDER BY STR_TO_DATE(data, '%d/%m/%Y') ASC", 
                (data["dataInicio"], data["dataFim"], )
            )
        else:
            cursor.execute(
                "SELECT * FROM registos WHERE STR_TO_DATE(data, '%d/%m/%Y') BETWEEN STR_TO_DATE(%s, '%d/%m/%Y') AND STR_TO_DATE(%s, '%d/%m/%Y') AND tipo = %s ORDER BY STR_TO_DATE(data, '%d/%m/%Y') ASC", 
                (data["dataInicio"], data["dataFim"], data["tipo"], )
            )
        
        registos = cursor.fetchall()

        jsondata = []
        for i in range(len(registos)):
            jsondata.append({
                    "id": registos[i][0],
                    "data": str(registos[i][1]),
                    "valor": str(registos[i][2]),
                    "tipo": registos[i][3],
                    "descricao": str(registos[i][4]),
                })

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
        content={"httpCode": 200, "httpState": "OK", "data": jsondata}
    )