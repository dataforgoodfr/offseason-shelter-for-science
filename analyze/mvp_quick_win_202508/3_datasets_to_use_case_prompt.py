# coding: utf-8

import argparse
import datetime
import pathlib
import json

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = SCRIPT_DIR / "data"

PLACEHOLDER_ORG_NAME = "{{ORG_NAME}}"
PLACEHOLDER_ORG_TITLE = "{{ORG_TITLE}}"
PLACEHOLDER_ORG_DESC = "{{ORG_DESC}}"
PLACEHOLDER_ORG_KEYWORDS = "{{ORG_KEYWORDS}}"
PLACEHOLDER_DATASETS = "{{DATASETS}}"
PLACEHOLDERS = [
    PLACEHOLDER_ORG_NAME,
    PLACEHOLDER_ORG_TITLE,
    PLACEHOLDER_ORG_DESC,
    PLACEHOLDER_ORG_KEYWORDS,
    PLACEHOLDER_DATASETS
]

PROMPT_DELIMITER = "// --------------------\n"

def format_datasets_for_prompt(datasets):
    """
    Format datasets for prompt output.
    
    Args:
        datasets (list): List of dataset dictionaries.
    
    Returns:
        str: JSON string of formatted datasets.
    """
    return json.dumps(datasets, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("input_file", type=pathlib.Path, help="Path to the JSON file containing dataset information")
    argparser.add_argument(
        "prompt_template_path",
        type=pathlib.Path,
        help="Path to the prompt template file"
    )
    argparser.add_argument(
        "--output-dir",
        type=pathlib.Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory to save the output prompt file"
    )
    argparser.add_argument(
        "--organizations",
        nargs="*",
        default=None,
        help="List of organization names to filter datasets by"
    )
    argparser.add_argument(
        "--limit",
        "-l",
        type=int,
        default=100,
        help="Maximum number of datasets to include in the prompt"
    )
    argparser.add_argument(
        "--prompt-newline",
        "-n",
        type=str,
        default="\n\n",
        help="Newline string to use in the prompt template"
    )
    argparser.add_argument(
        "--enforce-block-separation",
        "-S",
        action='store_true',
        help="Enforce separation between different blocks of the prompt"
    )

    args = argparser.parse_args()

    if args.enforce_block_separation and args.prompt_newline.strip() == "":
        args.prompt_newline = "\n# # # #\n"

    if not args.limit or args.limit < 0:
        raise ValueError("Limit must be a positive integer.")

    args.input_file = args.input_file.resolve(strict=True)
    args.prompt_template_path = args.prompt_template_path.resolve(strict=True)

    if not args.prompt_template_path.is_file():
        raise FileNotFoundError(f"Prompt template file {args.prompt_template_path} does not exist.")

    prompt_template = args.prompt_template_path.read_text(encoding='utf-8')

    # Checking if the template contains the necessary placeholders
    for placeholder in PLACEHOLDERS:
        if placeholder not in prompt_template:
            raise ValueError(f"Prompt template must contain the placeholder '{placeholder}'.")

    file_datetime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    output_dir = args.output_dir.resolve() / "prompts" / f"most_popular_datasets_{file_datetime}"
    if not output_dir.is_dir():
        output_dir.mkdir(parents=True, exist_ok=True)

    prompt_newline = args.prompt_newline

    with args.input_file.open('r', encoding='utf-8') as f:
        most_popular_datasets = json.load(f)
        
        targeted_datasets = {}
        if args.organizations is None:
            targeted_datasets = most_popular_datasets
        else:
            for org_name in args.organizations:
                if org_name not in most_popular_datasets:
                    raise ValueError(f"Organization '{org_name}' not found in the input data.")

                targeted_datasets[org_name] = most_popular_datasets[org_name]

        for org_name, organization in targeted_datasets.items():
            prompt = (
                prompt_template.replace(PLACEHOLDER_ORG_NAME, org_name)
                .replace(PLACEHOLDER_ORG_TITLE, organization['title'])
                .replace(PLACEHOLDER_ORG_DESC, organization['description'])
                .replace(PLACEHOLDER_ORG_KEYWORDS, ', '.join(organization['keywords']))
            )

            minified_datasets = []
            
            org_datasets = organization['datasets']['items']
            
            chunks_of_datasets = []

            datasets_count = len(org_datasets)

            # Split the datasets in limit chunks if needed
            if datasets_count > args.limit:
                chunks_of_datasets = [org_datasets[i:i + args.limit] for i in range(0, datasets_count, args.limit)]
            else:
                chunks_of_datasets = [org_datasets]

            prompted_datasets = []

            for chunk in chunks_of_datasets:
                minified_datasets = []
                for dataset in chunk:
                    # Reducing the number of characters in the prompt
                    minified_datasets.append({
                        'I': dataset['id'],
                        'N': dataset['dg_name'],
                        'T': dataset['dg_title'],
                        'D': dataset['dg_notes']
                    })
                prompted_datasets.append(minified_datasets)

            prompt = prompt.replace(PLACEHOLDER_DATASETS, format_datasets_for_prompt(prompted_datasets[0]))

            if len(prompted_datasets) > 1:
                prompt += f"{prompt_newline}{PROMPT_DELIMITER}Note: The datasets are split into multiple chunks due to the limit set.{prompt_newline}"
                # prompt += f"Do not include previous datasets in the next results. Do not repeat headers from now.{prompt_newline}"

                for datasets in prompted_datasets[1:]:
                    prompt += f"Here is the next chunk of datasets:{prompt_newline}"
                    prompt += format_datasets_for_prompt(datasets)
                    prompt += f"{prompt_newline}{PROMPT_DELIMITER}{prompt_newline}"

            output_file = output_dir / f"{org_name}_{file_datetime}.txt"
            with output_file.open('w', encoding='utf-8') as out_f:
                out_f.write(prompt)
            print(f"Prompt for organization '{org_name}' saved to {output_file}")

