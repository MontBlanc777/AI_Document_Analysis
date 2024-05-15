import os
import uvicorn
from dotenv import load_dotenv

# Import application factory
from src.api.app import create_app

# Import database initialization
from src.core.database import init_db

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', '.env'))

# Initialize the database
init_db()

# Create the application
app = create_app()

# Run the server
if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 5000))
    uvicorn.run("src.main:app", host="0.0.0.0", port=port, reload=True)