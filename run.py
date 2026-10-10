import os
import sys
from pathlib import Path

# Add backend directory to path
project_root = Path(__file__).resolve().parent
backend_dir = project_root / "backend"

if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import uvicorn
from app.config import HOST, PORT

if __name__ == "__main__":
    print("=" * 60)
    print("    STARTING RAILMITRA-AI PRODUCTION APPLICATION SERVER")
    print(f"    Serving API & Web at http://{HOST}:{PORT}")
    print("=" * 60)
    uvicorn.run(
        "app.main:app",
        host=HOST,
        port=PORT,
        reload=False
    )
