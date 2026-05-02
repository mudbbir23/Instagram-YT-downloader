import uvicorn
from interfaces.api import app
import yaml

if __name__ == "__main__":
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    host = config.get("api", {}).get("host", "127.0.0.1")
    port = config.get("api", {}).get("port", 8000)

    print(f"Starting Web UI Server on http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)
