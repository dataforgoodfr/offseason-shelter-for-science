# coding: utf-8

import argparse
import datetime
import pathlib
import json
import time
from typing import List, Dict, Any

from ai.api.manager import APIManagerInterface, get_instance as get_manager_instance
from ai.api.spending import SpendingEstimator
from user_input.question import yn_question

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
    return prompt_files[:limit] if limit else prompt_files

def send_prompt(
    manager: APIManagerInterface,
    model: str,
    prompts_directory: pathlib.Path,
    file_limit: int,
    prompt_limit: int,
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

    if not model:
        model = manager.get_default_model_id()

    print(f"Processing {len(prompt_files)} prompt file(s) with model {model}")

    manager.set_spending_estimator(SpendingEstimator.create_instance(spending_limit))

    # Process each prompt file
    all_responses = []
    for prompt_file in prompt_files:
        print(f"\n----\nProcessing: {prompt_file.name}")

        # Read the prompt content
        prompt_content = prompt_file.read_text(encoding='utf-8')

        # Split the prompt content into prompts
        prompts = prompt_content.split(PROMPT_DELIMITER)
        if prompt_limit:
            prompts = prompts[:prompt_limit]

        print(f"\nSending prompts to API {manager.get_name()}, model {model}...")
        for i, prompt in enumerate(prompts):
            print(f"\n*** {i + 1} ***\n{prompt}\n***")

        # prompts = [
        #     f"Hello, the random number is 45588771122. How are you?",
        #     "What is the random number? I forgot it.",
        #     "Just reverse it."
        # ]
        response_data = manager.send_prompts(
            model,
            prompts,
            context={
                "prompt_file": prompt_file.name,
                "prompt_limit": prompt_limit
                }
            )
        all_responses.append(response_data)

        if response_data.success:
            print(f"Response received ({response_data.usage.get_total_tokens()} tokens)")
            print(f"- Prompt: {response_data.usage.get_prompt_tokens()} tokens")
            print(f"- Response: {response_data.usage.get_completion_tokens()} tokens")
            print(f"\n***\n{response_data.responses}\n***")
        else:
            print(f"!!! Error: {response_data.error}")
    
        # Small pause between requests
        time.sleep(1)
        
    # Display a summary
    successful = sum(1 for r in all_responses if r.success)
    failed = len(all_responses) - successful
    
    print(f"\n=== Summary ===")
    print(f"Files processed: {len(prompt_files)}")
    print(f"Prompts processed: {len(all_responses)}")
    print(f"Success: {successful}")
    print(f"Failed: {failed}")
    
    if successful > 0:
        total_tokens = sum(r.usage.get_total_tokens() for r in all_responses if r.success)
        print(f"Total tokens used: {total_tokens}")

        total_spending = SpendingEstimator.get_instance().estimate_spending()
        print(f"Total spending = {total_spending}")

def print_arg_once(vargs: Dict[str, Any], arg_name: str):
    if arg_name not in print_arg_once.args_printed:
        print(f" - {arg_name} = {vargs[arg_name]}")
        print_arg_once.args_printed.add(arg_name)

print_arg_once.args_printed = set()

def display_args(args: argparse.Namespace):
    vargs = vars(args)
    print_arg_once(vargs, "api")
    print_arg_once(vargs, "model")
    print_arg_once(vargs, "spending_limit")
    print_arg_once(vargs, "file_limit")
    print_arg_once(vargs, "prompt_limit")

    # Do not print cmd
    print_arg_once.args_printed.add("cmd")

    for arg in vargs:
        print_arg_once(vargs, arg)

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

    spending_parser = cmd_parser.add_parser(
        "spending",
        help="Estimate current spending"
    )
    spending_parser.set_defaults(cmd="spending")

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
        default=1.,
        help="Spending limit for the API manager"
    )
  
    args = parser.parse_args()

    # Checking that a command is provided
    if "cmd" not in args:
        parser.print_help()
        return 1

    manager = get_manager_instance(args.api)
    if args.cmd == "list":
        print(f"Manager: {manager.get_name()} : available models")
        models = manager.get_available_models()
        for model_id in models.keys():
            print(f"- {model_id}")
        return
    elif args.cmd == "spending":
        print("Total spending =", SpendingEstimator.create_instance(0.).estimate_spending())
    elif args.cmd == "prompt":
        if args.model is None:
            args.model = manager.get_default_model_id()

        display_args(args)
        if yn_question("Do you wish to continue ?"):
            if args.file_limit == 0 or args.prompt_limit == 0:
                if not yn_question("Warning : at least one limit is lifted, are you sure ?"):
                    return

            if args.spending_limit > 10:
                if not yn_question("Warning : spending limit is high, are you sure ?"):
                    return
            manager.set_output_directory(args.output_dir)
            send_prompt(manager, args.model, args.prompts_directory, args.file_limit, args.prompt_limit, args.spending_limit)

if __name__ == "__main__":
    exit(main())
