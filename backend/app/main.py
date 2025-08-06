from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from app.api.v1.routers import user

app = FastAPI(docs_url="/api/v1/docs")


@app.get("/", include_in_schema=False)
async def root():
    return JSONResponse(status_code=status.HTTP_200_OK, content="Root page")


@app.get("/api/v1/healthcheck", include_in_schema=False)
async def healthcheck():
    return JSONResponse(status_code=status.HTTP_200_OK, content="OK")

app.include_router(router=user.router, prefix='/api/v1/user')