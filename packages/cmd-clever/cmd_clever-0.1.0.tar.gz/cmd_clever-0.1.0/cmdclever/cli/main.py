#!/usr/bin/env python
import argparse
import sys
from agno.utils.pprint import pprint_run_response
from cmdclever.agent import CmdAgent
from cmdclever import __version__


def main():
    """Main entry point for the command-line interface."""
    parser = argparse.ArgumentParser(
        description="Command-line tool for generating terminal commands",
        prog="cmd-clever",
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version=f"%(prog)s {__version__}"
    )
    
    parser.add_argument(
        "--api-key", 
        help="API key for the Agno API (overrides AGNO_API_KEY environment variable)",
        default=None
    )
    
    parser.add_argument(
        "--api-base", 
        help="Base URL for the Agno API (overrides AGNO_API_BASE environment variable)",
        default=None
    )
    
    parser.add_argument(
        "--model-id", 
        help="Model ID to use (defaults to qwen-plus)",
        default="qwen-plus"
    )
    
    parser.add_argument(
        "--no-stream", 
        help="Disable streaming responses",
        action="store_true",
        default=False
    )
    
    parser.add_argument(
        "query", 
        nargs="*", 
        help="Query to send to the command agent"
    )
    
    args = parser.parse_args()
    
    # If no query provided, enter interactive mode
    if not args.query:
        print("Entering interactive mode. Type 'exit' or 'quit' to exit.")
        print("Type your command queries in Chinese or English:")
        print()
        
        while True:
            try:
                query = input("> ")
                if query.lower() in ("exit", "quit", "退出"):
                    break
                
                if not query.strip():
                    continue
                
                agent = CmdAgent(
                    api_key=args.api_key,
                    api_base=args.api_base,
                    model_id=args.model_id
                )
                
                result = agent.run(query, stream=not args.no_stream)
                pprint_run_response(result)
                print()
                
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")
    else:
        # Process the command-line query
        query = " ".join(args.query)
        try:
            agent = CmdAgent(
                api_key=args.api_key,
                api_base=args.api_base,
                model_id=args.model_id
            )
            
            result = agent.run(query, stream=not args.no_stream)
            pprint_run_response(result)
            
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main() 