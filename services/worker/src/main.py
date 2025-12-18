"""Background worker service for X5 Hiring Bootcamp."""

import asyncio
import logging
import os
import signal
import sys

# Configuration from environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Shutdown flag
shutdown_event = asyncio.Event()


def signal_handler(sig, frame):
    """Handle shutdown signals gracefully."""
    logger.info(f"Received signal {sig}, initiating shutdown...")
    shutdown_event.set()


async def worker_loop():
    """Main worker loop."""
    logger.info(f"Worker starting in {ENVIRONMENT} environment")
    
    iteration = 0
    while not shutdown_event.is_set():
        iteration += 1
        logger.info(f"Worker alive - iteration {iteration} [{ENVIRONMENT}]")
        
        # TODO: Add actual work here
        # For now, just a heartbeat
        
        try:
            await asyncio.wait_for(shutdown_event.wait(), timeout=1.0)
        except asyncio.TimeoutError:
            # Normal timeout, continue loop
            pass
    
    logger.info("Worker shutting down gracefully")


async def main():
    """Main entry point."""
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("=" * 50)
    logger.info("X5 Hiring Worker Service")
    logger.info(f"Environment: {ENVIRONMENT}")
    logger.info(f"Log Level: {LOG_LEVEL}")
    logger.info("=" * 50)
    
    try:
        await worker_loop()
    except Exception as e:
        logger.exception(f"Worker crashed: {e}")
        sys.exit(1)
    
    logger.info("Worker stopped")


if __name__ == "__main__":
    asyncio.run(main())

