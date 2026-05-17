"""FastAPI application for AI Video Studio."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.health import router as health_router
from app.routes.parse import router as parse_router
from app.routes.storyboard import router as storyboard_router
from app.routes.generate import router as generate_router
from app.routes.assets import router as assets_router
from app.routes.upload import router as upload_router
app=FastAPI(title='AI Video Studio API', version='0.1.0')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])
for r in [health_router, parse_router, storyboard_router, generate_router, assets_router, upload_router]: app.include_router(r)
