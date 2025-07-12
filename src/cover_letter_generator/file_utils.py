import os
import re
import csv
import json
from datetime import datetime
from PyPDF2 import PdfReader
from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

from .config import (
    OUTPUT_COVER_LETTERS_PATH,
    COVER_LETTER_RECORDS_FILE_PATH,
    LOG_FILE_PATH,
)

def read_file(file_path):
    """Reads a file and returns its content."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def read_skills(file_path):
    """Reads a TSV file and returns its content as a string of comma-separated values."""
    with open(file_path, 'r', encoding='utf-8') as file:
        skills = file.read().strip().split('\t')  # Split by tab
    return ', '.join(skills)  # Join into a string separated by commas

def read_criteria(file_path):
    """Reads the criteria file and returns its content."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def extract_pdf_text(file_path):
    """Extracts text from a given PDF file."""
    text = ''
    with open(file_path, 'rb') as file:
        reader = PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

def sanitize_filename(name):
    """Remove or replace invalid filename characters for Windows and clean whitespace."""
    # Remove characters: \\ / : * ? " < > | and newline characters
    cleaned = re.sub(r'[\\/:*?"<>|\n\r]', '', name)
    # Replace multiple spaces with a single space
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip()

def save_cover_letter_text(cover_letter, company_name, job_title):
    """Saves the cover letter as a text file in the specified path."""
    sanitized_company_name = sanitize_filename(company_name)
    sanitized_job_title = sanitize_filename(job_title)

    # Define the directory structure based on the company name and sanitized job title
    text_dir = os.path.join(OUTPUT_COVER_LETTERS_PATH, sanitized_company_name)
    os.makedirs(text_dir, exist_ok=True)  # Ensure the directory exists

    # Create the filename for the cover letter text file
    text_file_name = f"{sanitized_job_title.replace(' ', '_')}_CoverLetter.txt"
    text_file_path = os.path.join(text_dir, text_file_name)

    # Save the cover letter to a text file
    with open(text_file_path, 'w', encoding='utf-8') as file:
        file.write(cover_letter)

    return text_file_path

def save_cover_letter_pdf(cover_letter, company_name, job_title):
    """Saves the cover letter as a nicely formatted PDF file in the specified path."""
    sanitized_company_name = sanitize_filename(company_name)
    sanitized_job_title = sanitize_filename(job_title)

    # Create the directory if it doesn't exist
    pdf_dir = os.path.join(OUTPUT_COVER_LETTERS_PATH, sanitized_company_name)
    os.makedirs(pdf_dir, exist_ok=True)

    # Define the file name and path for the PDF
    pdf_file_name = f"{sanitized_job_title.replace(' ', '_')}_CoverLetter.pdf"
    pdf_file_path = os.path.join(pdf_dir, pdf_file_name)

    # Create a PDF with professional formatting
    doc = SimpleDocTemplate(pdf_file_path, pagesize=LETTER,
                            rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()
    story = []
    for para in cover_letter.split('\n\n'):
        story.append(Paragraph(para.strip().replace('\n', '<br/>'), styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))
    doc.build(story)
    return pdf_file_path

def record_cover_letter(job_title, company_name, cover_letter, text_path):
    """Appends the final cover letter to a record file."""
    file_exists = os.path.exists(COVER_LETTER_RECORDS_FILE_PATH)
    with open(COVER_LETTER_RECORDS_FILE_PATH, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists or os.stat(COVER_LETTER_RECORDS_FILE_PATH).st_size == 0:
            writer.writerow(['Job Title', 'Company URL', 'Date', 'Cover Letter'])
        writer.writerow([job_title, company_name, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), cover_letter])

def log_file_creation(file_path, description):
    """
    Creates a dictionary entry for logging file creation events.

    Args:
    file_path (str): The path to the file that was created.
    description (str): A description of the file's purpose or contents.

    Returns:
    dict: A dictionary containing the file creation log entry.
    """
    return {
        "file_created": file_path,
        "description": description,
        "creation_timestamp": datetime.now().isoformat()
    }

def structured_log(user_request, gpt_response, created_files):
    """
    Logs the session data in a structured JSON format to the log file.
    This function is enhanced to better capture the conversational context and important events.

    Args:
    user_request (str): The user's input or request to the GPT.
    gpt_response (str): The GPT's response to the user's request.
    created_files (list of dict): A list of dictionaries with details of created files during the session.
    """
    # Prepare the log entry
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "user_request": user_request,
        "gpt_response": gpt_response,
        "created_files": created_files
    }

    # Write the structured log entry to the log file
    with open(LOG_FILE_PATH, "a") as log_file:
        json.dump(log_entry, log_file)
        log_file.write('\\n')  # Ensure each log entry is on a new line for readability

def clear_temporary_files(file_paths):
    """
    Clears the content of temporary files.

    Args:
    file_paths (list of str): A list of file paths to be cleared.
    """
    for file_path in file_paths:
        try:
            with open(file_path, 'w') as file:
                file.write("")  # Clears the content of the file
        except Exception as e:
            print(f"Error clearing temporary file {file_path}: {e}")