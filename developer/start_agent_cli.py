import sys
import logging
from src.orchestrator import AlphaOrchestrator
from src.logger import agent_logger

if __name__ == "__main__":
    # Ensure stdout/stderr formatting is readable
    print("====================================================")
    print("           AlphaForge Quant Agent Runner            ")
    print("====================================================")
    print("Starting orchestrator CLI loop...")
    
    try:
        orchestrator = AlphaOrchestrator()
        orchestrator.run_loop()
    except KeyboardInterrupt:
        print("\nShutdown signal received. Stopping orchestrator cleanly...")
        if 'orchestrator' in locals():
            orchestrator.stop()
    except Exception as e:
        print(f"Orchestrator encountered error: {e}")
        sys.exit(1)
