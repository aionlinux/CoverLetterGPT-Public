import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI API key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Get the project root directory (two levels up from src/cover_letter_generator/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# Define paths for the various components of the application
DATA_PROFILE_PATH = os.path.join(PROJECT_ROOT, 'data', 'profile')
DATA_INPUT_PATH = os.path.join(PROJECT_ROOT, 'data', 'input')
TEMP_PATH = os.path.join(PROJECT_ROOT, 'temp')
OUTPUT_PATH = os.path.join(PROJECT_ROOT, 'output')
OUTPUT_LOGS_PATH = os.path.join(OUTPUT_PATH, 'logs')
OUTPUT_COVER_LETTERS_PATH = os.path.join(OUTPUT_PATH, 'cover_letters')

# Ensure required directories exist
os.makedirs(DATA_PROFILE_PATH, exist_ok=True)
os.makedirs(DATA_INPUT_PATH, exist_ok=True)
os.makedirs(TEMP_PATH, exist_ok=True)
os.makedirs(OUTPUT_PATH, exist_ok=True)
os.makedirs(OUTPUT_LOGS_PATH, exist_ok=True)
os.makedirs(OUTPUT_COVER_LETTERS_PATH, exist_ok=True)

# Define the LOG_FILE_PATH variable
LOG_FILE_PATH = os.path.join(OUTPUT_LOGS_PATH, 'structured_log.json')

# Paths to the individual files needed for the cover letter generation
RESUME_FILE_PATH = os.path.join(DATA_PROFILE_PATH, 'ChristopherBurkeResume.pdf')
FEEDBACK_FILE_PATH = os.path.join(DATA_PROFILE_PATH, 'feedback.txt')
SKILLS_FILE_PATH = os.path.join(DATA_PROFILE_PATH, 'skillset.csv')
JOB_LISTING_FILE_PATH = os.path.join(DATA_INPUT_PATH, 'job_listing.txt')
COVER_LETTER_RECORDS_FILE_PATH = os.path.join(OUTPUT_PATH, 'records.csv')
COVER_LETTER_TEMP_PATH = os.path.join(TEMP_PATH, 'cover-letter.txt')
CRITERIA_FILE_PATH = os.path.join(DATA_PROFILE_PATH, 'criteria.txt')

# Legacy path compatibility (for backward compatibility during transition)
KNOWLEDGE_BASE_PATH = DATA_PROFILE_PATH
WORKING_DATA_PATH = DATA_INPUT_PATH
TEMP_DATA_PATH = TEMP_PATH
RECORDS_PATH = OUTPUT_PATH
LOGS_PATH = OUTPUT_LOGS_PATH
TEXT_RECORDS_PATH = OUTPUT_COVER_LETTERS_PATH
