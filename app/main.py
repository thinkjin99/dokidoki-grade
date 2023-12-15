from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from fastapi.responses import JSONResponse

from code.scrap import (
    run_single_browser_scrap_now,
    run_single_browser_scrap_all,
)
from code.cookies import call_refresh_lambda


app = FastAPI()


class User(BaseModel):
    student_id: str
    password: str


@app.post("/grade/all")
async def _scrap_all(user: User):
    try:
        call_refresh_lambda(user.student_id, user.password)
        data = await run_single_browser_scrap_all(user.student_id)
        return JSONResponse(content=data, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/grade/now", status_code=200)
async def _scrap_now(user: User):
    try:
        call_refresh_lambda(user.student_id, user.password)
        data = await run_single_browser_scrap_now(user.student_id)
        return JSONResponse(content=data, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))