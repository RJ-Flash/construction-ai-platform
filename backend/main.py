import uvicorn
import os
from app.main import app

if __name__ == "__main__":
    # Get port from environment variable or use default
    port = int(os.environ.get("PORT", 8000))
    
    # Run the application
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        workers=4
    )
