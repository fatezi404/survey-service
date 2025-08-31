from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from app.api.v1.routers import user, permission, response, option, survey, role, login, question


app = FastAPI(docs_url='/api/v1/docs')


@app.get('/', include_in_schema=False)
async def root():
    return JSONResponse(status_code=status.HTTP_200_OK, content='Root page')


@app.get('/api/v1/healthcheck', include_in_schema=False)
async def healthcheck():
    return JSONResponse(status_code=status.HTTP_200_OK, content='OK')


app.include_router(router=user.router, prefix='/api/v1/user', tags=['User'])
app.include_router(router=survey.router, prefix='/api/v1/survey', tags=['Survey'])
app.include_router(router=permission.router, prefix='/api/v1/permission', tags=['Permission'])
app.include_router(router=response.router, prefix='/api/v1/response', tags=['Response'])
app.include_router(router=option.router, prefix='/api/v1/option', tags=['Option'])
app.include_router(router=role.router, prefix='/api/v1/role', tags=['Role'])
app.include_router(router=login.router, prefix='/api/v1/login', tags=['Login'])
app.include_router(router=question.router, prefix='/api/v1/question', tags=['Question'])
