from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import logger
from app.api.v1 import webhooks, disputes, simulate

app = FastAPI(
    title="ShieldAgent - Autonomous PayPal Dispute Defense Engine",
    description="Multi-agent dispute representment, forensics, and Visa CE 3.0 compliance for PayPal merchants.",
    version="0.1.0"
)

# Enable CORS for frontend dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(webhooks.router, prefix="/api/v1")
app.include_router(disputes.router, prefix="/api/v1")
app.include_router(simulate.router, prefix="/api/v1")


@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "service": "ShieldAgent Backend",
        "environment": settings.ENVIRONMENT,
        "paypal_env": settings.PAYPAL_ENV,
        "autonomous_submission": settings.ENABLE_AUTONOMOUS_SUBMISSION
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
