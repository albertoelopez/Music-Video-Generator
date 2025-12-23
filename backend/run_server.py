#!/usr/bin/env python3
import argparse
from src.api import create_app
from src.utils import Config


def main():
    parser = argparse.ArgumentParser(description="Audio to Music Video API Server")
    parser.add_argument("--host", type=str, default=None, help="Host to bind to")
    parser.add_argument("--port", type=int, default=None, help="Port to bind to")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    config = Config.from_env()

    host = args.host or config.api_host
    port = args.port or config.api_port
    debug = args.debug or config.debug

    app = create_app()

    print(f"Starting Audio to Music Video API Server")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Debug: {debug}")
    print(f"API Documentation: http://{host}:{port}/api/health")

    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()
