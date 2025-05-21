from fastapi import FastAPI
from app.routers import routers

app = FastAPI(
    title="Inventory Management System API",
    description="A simple API for managing inventory in a store across multiple locations.",
    version="1.0.0",
)

for router in routers:
    app.include_router(router)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint to verify the API is running."""
    return {
        "status": "online",
        "message": "Inventory Management System API is running."
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
