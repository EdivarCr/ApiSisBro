import asyncio
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apisisbro.routers import (
    auth_router,
    client_router,
    dashboards_router,
    entrada_insumo_router,
    insumo_router,
    product_router,
    production_router,
    pvd_router,
    user_router,
    venda_router,
)

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


app = FastAPI(title='ApiSisBro')

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://localhost:5173',  # Acesso do front
        'http://127.0.0.1:5500',  # Live Server (Formato IP)
        'http://localhost:5500',  # Live Server (Formato Localhost)\
        'https://front-sigbro.vercel.app',
        'https://catalogo-brobro.vercel.app'
    ],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(auth_router.router)
app.include_router(user_router.router)
app.include_router(product_router.router)
app.include_router(insumo_router.router)
app.include_router(entrada_insumo_router.router)
app.include_router(production_router.router)
app.include_router(client_router.router)
app.include_router(pvd_router.router)
app.include_router(venda_router.router)
app.include_router(dashboards_router.router)
