import uvicorn
from shopAPI.server import app

if __name__ == "__main__":
    uvicorn.run(app, port=8000)
