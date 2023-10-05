"""
Dashboard Gastos
(c) 2023 by DniGamer @dnigamer

"""

from fastapi import FastAPI, Request, HTTPException

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/hi", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/saldo", response_class=JSONResponse)
async def saldo():
    saldo: float = 100.6
    return {"saldo": saldo}

@app.post("/api/registar", response_class=JSONResponse)
async def registar(request: Request):
    # return with 400 error code model
    #    raise HTTPException(status_code=400, detail={"httpCode": 400, "httpState": "Bad Request", "errorData": "Invalid data"})
    
    return {"state": "OK", "http_code": 200, "idRecord": 2, "successData": "hello"}