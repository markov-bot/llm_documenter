# LLM_Documenter - Codebase Documentation Generator

An innovative script designed to automatically generate comprehensive documentation for your entire codebase using OpenAI's language models. Created to assist developers who utilize natural language programming, this tool simplifies the process of understanding and navigating complex applications.

## Overview

In modern development environments, especially when leveraging tools like Cursor (a VS Code fork with AI functionalities), it's common to find yourself in unfamiliar territory. Asking questions to a Language Model (LLM) can be incredibly helpful, but providing the necessary context is often a challenge. `LLM_Documenter` addresses this by generating a detailed documentation file of your codebase, which can then be used as context when seeking assistance from LLMs for new implementations.

### Key Benefits

- **Facilitates Natural Language Programming**: Ideal for developers who code using natural language, enabling easier transition into new or unfamiliar codebases.
- **Enhances LLM Interactions**: Provides detailed context to LLMs, improving the quality of responses for development queries.
- **Streamlines Onboarding**: Helps new team members understand the codebase quickly through comprehensive documentation.

## Features

- **Automated Documentation Generation**: Scans your entire codebase and generates an organized markdown file with descriptions for each file.
- **Directory Structure Visualization**: Constructs a visual tree of your project's directory structure.
- **File Purpose Summarization**: Utilizes OpenAI's latest models (`o1-mini` and `o1-preview`) to summarize the purpose and functionality of each file.
- **Asynchronous Processing**: Employs `asyncio` for efficient concurrent processing of files and API requests.
- **Customizable Exclusions**: Allows specification of directories and file types to include or exclude during the documentation process.
- **Accurate Token Management with `tiktoken`**: Manages API request sizes through precise token estimation to comply with OpenAI's model limitations.

## How It Works

1. **Traverse the Codebase**: The script walks through all directories and files, building a representation of the structure while excluding specified directories and files.
2. **Read and Analyze Files**: Reads the content of each relevant file, considering custom exclusion rules.
3. **Estimate Tokens**: Uses `tiktoken` to estimate the number of tokens for each file to manage OpenAI API limits effectively.
4. **Chunk Files**: Divides files into chunks that fit within the maximum context window of the OpenAI models to optimize API calls.
5. **Summarize Content**: Sends the content to OpenAI's API using the `o1-mini` model to generate concise summaries of each file's purpose.
6. **Generate Documentation**: Compiles the directory structure and summaries into a `CODEBASE_DOCUMENTATION.md` file.
7. **Refine Documentation**: Optionally refines the initial documentation using the `o1-preview` model to enhance coherence and organization.
8. **Provide Context for LLMs**: The generated documentation can be used as context when consulting LLMs for development assistance.

## Installation

### Prerequisites

- **Python 3.7+**
- **OpenAI API Key**
- **Access to OpenAI's `o1-mini` and `o1-preview` models**

### Steps

1. **Place the Script in Your Repository Root**

   - Copy `main.py` into the **root directory** of your code repository. This placement is crucial for the script to correctly traverse and document your entire codebase.

2. **Set Up a Virtual Environment (Optional but Recommended)**

   ```bash
   python -m venv venv
   source venv/bin/activate    # On Windows use `venv\Scripts\activate`
   ```

3. **Install Required Dependencies**

   ```bash
   pip install python-dotenv openai tiktoken asyncio
   ```

   - **Note**: Ensure that all dependencies, especially `tiktoken`, are installed for accurate token estimation.

4. **Configure Environment Variables**

   - Create a `.env` file in the root directory.
   - Add your OpenAI API key:

     ```env
     OPENAI_API_KEY=your-openai-api-key-here
     ```

5. **Run the Script**

   ```bash
   python main.py
   ```

   - Replace `main.py` with the actual filename if different.

6. **View the Documentation**

   - Open `CODEBASE_DOCUMENTATION.md` in the root directory to view the generated documentation.

## Configuration

### Customizing Exclusions

Modify the `EXCLUDE_DIRS` and `EXCLUDE_EXTENSIONS` sets in `main.py` to include or exclude specific directories and file types, enhancing the script's flexibility to suit your project's needs.

```python
# Directories to exclude
EXCLUDE_DIRS = {
    'node_modules', '.git', 'venv', 'dist', 'build',
    # ... other directories
}

# File extensions to exclude
EXCLUDE_EXTENSIONS = {
    '.jpg', '.png', '.gif', '.exe', '.dll',
    # ... other file extensions
}
```

### Adjusting OpenAI Model Settings

The script uses OpenAI's `o1-mini` and `o1-preview` models. Update the `MODEL_MAX_TOKENS` dictionary in `main.py` if needed:

```python
MODEL_MAX_TOKENS = {
    "o1-mini": 128000,
    "o1-preview": 128000,
    # Add other models and their max tokens if needed
}
```

**Note**: Ensure you have access to these models and adjust the `max_completion_tokens` accordingly within the script.

### Adjusting Token Limits

You can adjust the maximum tokens for completions in the script to match the limitations of the models you are using:

```python
# For summarization with o1-mini model
max_completion_tokens = 60000

# For refinement with o1-preview model
max_completion_tokens = 32000
```

Be careful when adjusting token limits to avoid exceeding the model's maximum context length.

## Logging and Error Handling

- **Logging**: Outputs informative messages during execution to the console for easy tracking of the process.
- **Error Handling**: Includes try-except blocks to gracefully handle exceptions and provide informative error messages, ensuring the script can handle unexpected issues without crashing.

## Use Cases

- **Enhanced LLM Queries**: Use the generated documentation as context when interacting with LLMs to get more accurate and relevant answers for development queries.
- **Team Collaboration**: Share the comprehensive documentation with team members to improve understanding and collaboration on the codebase.
- **Project Onboarding**: Assists new developers in quickly getting up to speed with the project structure and purpose of each component through detailed documentation.

## About markov

`LLM_Documenter` is developed by [markov](https://markov.bot), an AI studio based in Antwerp dedicated to creating tools that bridge the gap between natural language and code. Our mission is to empower developers by simplifying complex processes through AI.

- **Website**: [https://markov.bot](https://markov.bot)
- **Contact**: [olivier@markov.bot](mailto:olivier@markov.bot)

## Contribution

We welcome contributions! If you have suggestions for improvements, encounter bugs, or want to add features, please open an issue or submit a pull request to our repository.

## License

This project is licensed under the [MIT License](LICENSE), making it freely available for both personal and commercial use.

---

**Important Notes**:

- **Security**: Keep your OpenAI API key secure. Do not share it publicly or commit it to version control.
- **Model Access**: Verify that you have access to the OpenAI models specified in the script (`o1-mini` and `o1-preview`).
- **Token Limits**: Be mindful of the token limits for the models you're using to prevent exceeding the maximum context length.
- **Dependencies**: Ensure all required dependencies are installed, including `tiktoken` for accurate token estimation.

**Disclaimer**: This script is provided "as is" without warranty of any kind. Use at your own risk.

# Short Installation Guide

1. **Place the Script in Your Repository Root**:

   - Ensure that `main.py` is located in the **root directory** of your code repository.

2. **Install Dependencies**:

   ```bash
   pip install python-dotenv openai tiktoken asyncio
   ```

3. **Set Up OpenAI API Key**:

   - Create a `.env` file in the root directory.
   - Add your API key:

     ```env
     OPENAI_API_KEY=your-openai-api-key-here
     ```

4. **Run the Script**:

   ```bash
   python main.py
   ```

5. **Access the Documentation**:

   - Open `CODEBASE_DOCUMENTATION.md` to view the generated documentation.

---

**For any questions or support, please contact [olivier@markov.bot](mailto:olivier@markov.bot).**
