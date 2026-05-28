import uvicorn
from src.config import SERVER_HOST, SERVER_PORT
from src.logger import agent_logger

if __name__ == "__main__":
    agent_logger.info("====================================================")
    agent_logger.info("           ALPHAForge QUANT AGENT BOOTSTRAP         ")
    agent_logger.info("====================================================")
    agent_logger.info(f"Dashboard console starting at: http://{SERVER_HOST}:{SERVER_PORT}")
    agent_logger.info("Open this URL in your web browser to manage the agent.")
    agent_logger.info("====================================================")
    
    uvicorn.run("src.server:app", host=SERVER_HOST, port=SERVER_PORT, log_level="warning")
