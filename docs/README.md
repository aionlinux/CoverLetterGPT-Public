# Cover Letter GPT

## Project Description
Cover Letter GPT is a Python-based project designed to assist with generating and managing cover letters using AI technologies. It leverages the OpenAI API along with various utilities for handling PDFs, web scraping, and data processing to streamline the cover letter creation process.

## Features
- Integration with OpenAI API for AI-powered text generation
- PDF processing and generation capabilities
- Environment variable management with python-dotenv
- Web scraping utilities using BeautifulSoup and requests
- Data handling with pandas
- Colorized terminal output with colorama

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd coverletter_gpt
   ```

2. (Optional but recommended) Create and activate a virtual environment:
   ```bash
   python -m venv myenv
   # On Windows
   myenv\Scripts\activate
   # On Unix or MacOS
   source myenv/bin/activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

- Configure your environment variables in a `.env` file as needed (e.g., OpenAI API key).
- Run the main application:
  ```bash
  python main.py
  ```
- Additional scripts such as `app.py` and utilities can be run or imported as needed.

## Project Structure

- `main.py` - Main entry point for the application
- `app.py` - Application logic and orchestration
- `config.py` - Configuration settings
- `context_manager.py` - Context handling utilities
- `file_utils.py` - File processing utilities
- `openai_client.py` - OpenAI API client wrapper
- `requirements.txt` - Python dependencies
- `README.md` - Project documentation
- `knowledge-base/` - Reference documents and data
- `records/` - Generated records and logs
- `working-data/` - Temporary working files

## Contributing
Contributions are welcome. Please open issues or submit pull requests for improvements.

## License
This project is licensed under the MIT License.

---------------------------------------------------------------

# Delete the corrupted .venv folder
Remove-Item -Recurse -Force .\.venv

# Create new virtual environment
python -m venv .venv

# Activate it
.\.venv\Scripts\Activate.ps1