# coding: utf-8

import argparse
import pathlib
import json
import time
from typing import List, Dict, Any
from ai.api.manager import create_manager, APIManagerInterface

import importlib
PROMPT_DELIMITER = importlib.import_module("3_datasets_to_use_case_prompt").PROMPT_DELIMITER

_SCRIPT_DIR = pathlib.Path(__file__).parent
_DATA_DIR = _SCRIPT_DIR / "data"
_DEFAULT_OUTPUT_DIR = _DATA_DIR / "output"

def list_prompts_from_directory(directory: pathlib.Path, limit: int = 1) -> List[pathlib.Path]:
    """
    Reads prompt files from a directory.
    
    Args:
        directory: Directory containing prompt files
        limit: Maximum number of prompts to process
    
    Returns:
        List of paths to prompt files
    """
    if not directory.exists():
        raise FileNotFoundError(f"Directory {directory} does not exist.")
    
    if not directory.is_dir():
        raise ValueError(f"{directory} is not a directory.")
    
    # Search for prompt files (supports .txt, .md, .prompt)
    prompt_extensions = ['.txt', '.md', '.prompt']
    prompt_files = []
    
    for ext in prompt_extensions:
        prompt_files.extend(directory.glob(f"*{ext}"))
    
    # Sort by filename for deterministic order
    prompt_files.sort(key=lambda x: x.name)
    
    # Limit the number of files
    return prompt_files[:limit]

def save_response(response_data: Dict[str, Any], output_dir: pathlib.Path):
    """Saves the response to a JSON file."""
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"ai_response_{timestamp}.json"
    
    with output_file.open('w', encoding='utf-8') as f:
        json.dump(response_data, f, indent=2, ensure_ascii=False)
    
    print(f"Response saved to {output_file}")

def send_prompt(
    manager: APIManagerInterface,
    model: str,
    prompts_directory: pathlib.Path,
    file_limit: int,
    prompt_limit: int,
    output_dir: pathlib.Path,
    spending_limit: float
    ):
    """Sends prompts to the AI API and saves responses."""

    # Check that the prompts directory exists
    prompts_directory = prompts_directory.resolve()
    
    # Read prompt files
    try:
        prompt_files = list_prompts_from_directory(prompts_directory, file_limit)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        return 1
    
    if not prompt_files:
        print(f"No prompt files found in {prompts_directory}")
        return 1
    
    # Initialize the API manager
    try:
        manager.init()
    except Exception as e:
        print(f"Error initializing API client: {e}")
        return 1

    if model is None:
        model = manager.get_default_model_id()

    print(f"Processing {len(prompt_files)} prompt file(s) with model {model}")

    # Process each prompt file
    all_responses = []
    for prompt_file in prompt_files:
        print(f"\n----\nProcessing: {prompt_file.name}")

        # Read the prompt content
        prompt_content = prompt_file.read_text(encoding='utf-8')

        # Split the prompt content into prompts
        prompts = prompt_content.split(PROMPT_DELIMITER)

        for i, prompt in enumerate(prompts):
            if i >= prompt_limit:
                break

            print(f"\nSending prompt to API {manager.get_name()}, model {model}...")
            print(f"\n```\n{prompt}\n```")
            response_data = manager.send_prompt(model, prompt, spending_limit)
            all_responses.append(response_data)

            if response_data.success:
                print(f"Response received ({response_data.usage.total_tokens} tokens)")
                print(f"- Prompt: {response_data.usage.prompt_tokens} tokens")
                print(f"- Response: {response_data.usage.completion_tokens} tokens")
                print(f"\n```\n{response_data.response}\n```")
            else:
                print(f"!!! Error: {response_data.error}")
        
            # Small pause between requests
            time.sleep(1)
    
    # Save all responses
    if all_responses:
        save_response({
            "responses": json.dumps(all_responses, default=lambda o: o.__dict__),
            "settings": {
                "model": model,
                "prompts_directory": str(prompts_directory),
                "file_limit": file_limit,
                "prompt_limit": prompt_limit,
            }
        }, output_dir)
    
    # Display a summary
    successful = sum(1 for r in all_responses if r.success)
    failed = len(all_responses) - successful
    
    print(f"\n=== Summary ===")
    print(f"Files processed: {len(prompt_files)}")
    print(f"Prompts processed: {len(all_responses)}")
    print(f"Success: {successful}")
    print(f"Failed: {failed}")
    
    if successful > 0:
        total_tokens = sum(r.usage.total_tokens for r in all_responses if r.success)
        print(f"Total tokens used: {total_tokens}")

def main():
    """Main function of the script."""
    parser = argparse.ArgumentParser(
        description="Sends prompts to ChatGPT API and saves responses"
    )
    parser.add_argument(
        "--api",
        "-a",
        type=str,
        default="mock",
        choices=["openai", "mock"],
        help="Manager to use (default: mock)"
    )

    cmd_parser = parser.add_subparsers(
        title="commands",
    )

    list_models_parser = cmd_parser.add_parser(
        "list",
        help="List available models"
    )
    list_models_parser.set_defaults(cmd="list")

    send_prompt_parser = cmd_parser.add_parser(
        "prompt",
        help="Send prompt to AI"
    )
    send_prompt_parser.set_defaults(cmd="prompt")

    send_prompt_parser.add_argument(
        "prompts_directory",
        type=pathlib.Path,
        help="Directory containing prompt files"
    )
    send_prompt_parser.add_argument(
        "--prompt-limit",
        "-p",
        type=int,
        default=1,
        help="Maximum number of prompts to process (default: 1)"
    )
    send_prompt_parser.add_argument(
        "--file-limit",
        "-f",
        type=int,
        default=1,
        help="Maximum number of prompt files to process (default: 1)"
    )
    send_prompt_parser.add_argument(
        "--model",
        "-m",
        type=str,
        help="Model to use"
    )
    send_prompt_parser.add_argument(
        "--output-dir",
        "-o",
        type=pathlib.Path,
        default=_DEFAULT_OUTPUT_DIR,
        help=f"Output directory for responses {_DEFAULT_OUTPUT_DIR}"
    )
    send_prompt_parser.add_argument(
        "--spending-limit",
        "-s",
        type=float,
        default=5,
        help="Spending limit for the API manager"
    )
  
    args = parser.parse_args()

    # Checking that a command is provided
    if "cmd" not in args:
        parser.print_help()
        return 1

    manager = create_manager(args.api)
    if args.cmd == "list":
        print(f"Manager: {manager.get_name()} : list models")
        models = manager.get_available_models()
        print("Available models:")
        for model_id in models.keys():
            print(f"- {model_id}")
        return
    elif args.cmd == "prompt":
        send_prompt(manager, args.model, args.prompts_directory, args.file_limit, args.prompt_limit, args.output_dir, args.spending_limit)

if __name__ == "__main__":
    exit(main())
