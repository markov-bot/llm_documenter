import os
import sys
from dotenv import load_dotenv
from openai import OpenAI
import json
import asyncio

# Import tiktoken for accurate token estimation
try:
    import tiktoken
except ImportError:
    print("tiktoken library not found. Please install it using 'pip install tiktoken'")
    sys.exit(1)

print("Starting script execution...")

try:
    load_dotenv()
    print("Environment variables loaded successfully.")
except Exception as e:
    print(f"Error loading environment variables: {e}")

EXCLUDE_DIRS = {
    'node_modules', '.vercel', 'postcss.config.js',
    'dist', 'build', '__tests__', '.env', '.env.local',
    'readme.md', '.gitignore', '.git',
    'package-lock.json', 'venv',
    'tailwind.config.ts',
    'tool.py',
    'paths.txt',
    'migrations', 'readme.md',
    'venv', '.DS_Store',
    # Additional directories to exclude
    '__pycache__', '.pytest_cache', '.mypy_cache',
    '.vscode', '.idea', 'logs', 'temp', 'tmp',
    'coverage', 'htmlcov', '.tox', '.eggs',
    'build', 'dist', '*.egg-info',
    'docs', 'site-packages', 'env',
    'static', 'media', 'uploads',
    '.ipynb_checkpoints', 'notebooks'
}

EXCLUDE_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.gif', '.bmp',
    '.svg', '.ico', '.pdf', '.csv', '.yaml', '.yml',
    # Additional file extensions to exclude
    '.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe',
    '.log', '.cache', '.swp', '.swo', '.bak',
    '.tmp', '.temp', '.obj', '.class',
    '.ipynb', '.pkl', '.pickle', '.npy', '.npz',
    '.db', '.sqlite', '.sqlite3',
    '.mo', '.pot', '.po',  # Translation files
    '.min.js', '.min.css',  # Minified files
    '.map',  # Source map files
    '.lock',  # Lock files (e.g., poetry.lock, Pipfile.lock)
    '.whl', '.egg',  # Python package files
    '.pth',  # Python path configuration files
    '.pyi',  # Python interface files
    '.coverage', '.coveragerc',  # Coverage related files
    '.dockerignore', 'Dockerfile',  # Docker related files
    '.eslintrc', '.prettierrc',  # Linting and formatting config files
    '.editorconfig',  # Editor configuration files
    'requirements.txt', 'Pipfile',  # Dependency files (might want to keep these, depending on your needs)
    '.flake8', '.pylintrc', 'mypy.ini',  # Python linting configuration files
    '.pyre_configuration', '.watchmanconfig',  # Facebook's Pyre and Watchman config files
    '.pre-commit-config.yaml',  # Pre-commit hooks configuration
}

OUTPUT_MARKDOWN = "CODEBASE_DOCUMENTATION.md"

# Set the maximum tokens for the model
MODEL_MAX_TOKENS = {
    "o1-mini": 128000,
    # Add other models and their max tokens if needed
}

API_KEY = os.getenv("OPENAI_API_KEY")
if API_KEY:
    print("API key loaded successfully.")
else:
    print("Error: OPENAI_API_KEY environment variable not set.")
    sys.exit(1)

try:
    client = OpenAI()
    print("OpenAI client initialized successfully.")
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")
    sys.exit(1)

def generate_directory_structure(root_dir):
    print(f"Generating directory structure for: {root_dir}")
    tree = ""
    try:
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Exclude directories in EXCLUDE_DIRS
            dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
            level = dirpath.replace(root_dir, '').count(os.sep)
            indent = ' ' * 4 * level
            tree += f"{indent}├── {os.path.basename(dirpath)}/\n"
            for filename in filenames:
                if filename not in EXCLUDE_DIRS and os.path.splitext(filename)[1].lower() not in EXCLUDE_EXTENSIONS:
                    tree += f"{indent}    ├── {filename}\n"
        print("Directory structure generated successfully.")
    except Exception as e:
        print(f"Error generating directory structure: {e}")
    return tree

def estimate_tokens(text):
    # Use tiktoken to accurately estimate the number of tokens
    # Replace 'cl100k_base' with the appropriate encoding for your model
    encoding = tiktoken.get_encoding('cl100k_base')
    return len(encoding.encode(text))

def chunk_files(files, max_tokens_per_chunk, initial_prompt_tokens):
    chunks = []
    current_chunk = []
    current_tokens = initial_prompt_tokens  # Start with initial prompt tokens

    for file_info in files:
        file_tokens = file_info['tokens']
        if current_tokens + file_tokens > max_tokens_per_chunk:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = [file_info]
            current_tokens = initial_prompt_tokens + file_tokens  # Reset current tokens
        else:
            current_chunk.append(file_info)
            current_tokens += file_tokens

    if current_chunk:
        chunks.append(current_chunk)

    return chunks

async def generate_documentation(root_dir):
    print(f"Starting documentation generation for: {root_dir}")
    documentation = "# Codebase Overview\n\n"

    # Add Directory Structure Overview
    print("Generating directory structure.")
    documentation += "## Directory Structure\n\n"
    documentation += "```\n"
    documentation += generate_directory_structure(root_dir)
    documentation += "```\n\n"

    all_files = []
    try:
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Exclude directories in EXCLUDE_DIRS
            dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
            for filename in filenames:
                if (filename not in EXCLUDE_DIRS and
                    os.path.splitext(filename)[1].lower() not in EXCLUDE_EXTENSIONS and
                    filename != 'postcss.config.js'):  # Explicitly exclude postcss.config.js
                    file_path = os.path.join(dirpath, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as file:
                            content = file.read()
                        # Build the per-file prompt segment
                        file_prompt = f"**File Path:** {file_path}\n```{os.path.splitext(file_path)[1][1:]}\n{content}\n```\n\n"
                        # Estimate tokens including the prompt structure
                        file_info = {
                            'path': file_path,
                            'content': content,
                            'extension': os.path.splitext(file_path)[1][1:],
                            'tokens': estimate_tokens(file_prompt)
                        }
                        all_files.append(file_info)
                        print(f"Added file: {file_path} (Estimated tokens: {file_info['tokens']})")
                    except Exception as e:
                        print(f"Error reading file {file_path}: {e}")
    except Exception as e:
        print(f"Error walking directory structure: {e}")
        return

    # Now chunk the files
    print("Chunking files to fit within the context window.")
    model_name = "o1-mini"
    max_model_tokens = MODEL_MAX_TOKENS.get(model_name, 128000)
    max_completion_tokens = 60000  # Set a reasonable completion size
    max_tokens_per_chunk = max_model_tokens - max_completion_tokens  # Max tokens for input prompt
    initial_prompt = "Provide concise and clear descriptions for the following files. For each file, list the file path and its purpose.\n\n"
    initial_prompt_tokens = estimate_tokens(initial_prompt)

    # Update file token estimation with accurate counts
    for file_info in all_files:
        # Recalculate tokens if needed
        file_prompt = f"**File Path:** {file_info['path']}\n```{file_info['extension']}\n{file_info['content']}\n```\n\n"
        file_info['tokens'] = estimate_tokens(file_prompt)

    file_chunks = chunk_files(all_files, max_tokens_per_chunk, initial_prompt_tokens)

    print(f"Total number of chunks: {len(file_chunks)}")

    # Process each chunk
    all_responses = []

    async def process_chunk(idx, chunk):
        nonlocal max_completion_tokens  # Allow modification of the outer variable
        print(f"Processing chunk {idx + 1}/{len(file_chunks)}")
        prompt = initial_prompt
        for file_info in chunk:
            prompt += f"**File Path:** {file_info['path']}\n```{file_info['extension']}\n{file_info['content']}\n```\n\n"

        # Estimate tokens for this chunk
        prompt_tokens = estimate_tokens(prompt)
        total_tokens = prompt_tokens + max_completion_tokens

        if total_tokens > max_model_tokens:
            print(f"Chunk {idx + 1} exceeds maximum tokens. Adjusting max_completion_tokens.")
            max_completion_tokens = max_model_tokens - prompt_tokens - 1000  # Leave a buffer
            if max_completion_tokens <= 0:
                print(f"Chunk {idx + 1} is too large even after adjustments. Skipping.")
                return

        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=max_completion_tokens
            )
            print(f"Received response for chunk {idx + 1}")
            all_responses.append(completion.choices[0].message.content)
        except Exception as e:
            print(f"Error processing chunk {idx + 1}: {e}")

    # Create tasks for each chunk
    tasks = [asyncio.create_task(process_chunk(idx, chunk)) for idx, chunk in enumerate(file_chunks)]
    await asyncio.gather(*tasks)

    if not all_responses:
        print("No responses received from any chunks. Exiting.")
        return

    # Combine all responses
    print("Combining responses from all chunks.")
    documentation += "\n".join(all_responses)

    # Write the combined documentation to the markdown file
    print(f"Writing combined documentation to {OUTPUT_MARKDOWN}")
    try:
        with open(OUTPUT_MARKDOWN, 'w', encoding='utf-8') as md_file:
            md_file.write(documentation)
        print(f"Documentation successfully written to {OUTPUT_MARKDOWN}")
    except Exception as e:
        print(f"Error writing to markdown file: {e}")

    # Now refine the documentation
    refined_documentation = await refine_documentation(documentation)
    print(f"Writing refined documentation to {OUTPUT_MARKDOWN}")
    try:
        with open(OUTPUT_MARKDOWN, 'w', encoding='utf-8') as md_file:
            md_file.write(refined_documentation)
        print(f"Refined documentation successfully written to {OUTPUT_MARKDOWN}")
    except Exception as e:
        print(f"Error writing refined documentation to markdown file: {e}")

async def refine_documentation(initial_documentation):
    print("Starting refinement of the documentation.")

    # Estimate tokens in the initial documentation
    total_tokens = estimate_tokens(initial_documentation)

    # Define the model and token limits
    model_name = "o1-preview"
    max_model_tokens = MODEL_MAX_TOKENS.get(model_name, 128000)
    max_completion_tokens = 32000  # Set a reasonable completion size
    max_tokens_per_chunk = max_model_tokens - max_completion_tokens  # Max tokens for input prompt

    # Split the documentation into chunks if necessary
    if total_tokens > max_tokens_per_chunk:
        print("Documentation exceeds the token limit, splitting into chunks.")
        # Split the documentation into chunks of max_tokens_per_chunk
        chunks = []
        current_chunk = ''
        current_tokens = 0
        lines = initial_documentation.split('\n')
        for line in lines:
            line += '\n'
            line_tokens = estimate_tokens(line)
            if current_tokens + line_tokens > max_tokens_per_chunk:
                chunks.append(current_chunk)
                current_chunk = line
                current_tokens = line_tokens
            else:
                current_chunk += line
                current_tokens += line_tokens
        if current_chunk:
            chunks.append(current_chunk)
    else:
        chunks = [initial_documentation]

    print(f"Total number of chunks for refinement: {len(chunks)}")

    # Process each chunk
    refined_responses = []

    async def refine_chunk(idx, chunk):
        nonlocal max_completion_tokens  # Allow modification of the outer variable
        print(f"Refining chunk {idx + 1}/{len(chunks)}")
        prompt = "Improve the following documentation to make it more coherent, clear, and well-organized. Ensure that it provides a comprehensive overview of the codebase.\n\n"
        prompt += chunk

        # Estimate tokens for this chunk
        prompt_tokens = estimate_tokens(prompt)
        total_tokens = prompt_tokens + max_completion_tokens

        if total_tokens > max_model_tokens:
            print(f"Chunk {idx + 1} exceeds maximum tokens after adding prompt. Skipping.")
            return

        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=max_completion_tokens
            )
            print(f"Received refined response for chunk {idx + 1}")
            refined_responses.append(completion.choices[0].message.content)
        except Exception as e:
            print(f"Error refining chunk {idx + 1}: {e}")

    # Create tasks for each refinement chunk
    tasks = [asyncio.create_task(refine_chunk(idx, chunk)) for idx, chunk in enumerate(chunks)]
    await asyncio.gather(*tasks)

    # Combine all refined responses
    refined_documentation = "\n".join(refined_responses)
    print("Refinement of documentation completed.")
    return refined_documentation

if __name__ == "__main__":
    try:
        asyncio.run(generate_documentation(os.getcwd()))
        print("Documentation generation completed successfully.")
    except Exception as e:
        print(f"An error occurred during documentation generation: {e}")
