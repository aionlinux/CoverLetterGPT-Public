# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Cover Letter GPT is a Python-based AI-powered cover letter generation tool that creates personalized cover letters using OpenAI's GPT API. The application processes job descriptions, user skills, and resume data to generate tailored cover letters with an iterative refinement process.

## Core Architecture

### Main Components

- **main.py**: Primary entry point that orchestrates the full workflow
- **app.py**: Legacy standalone version with complete functionality (not used by main.py)
- **config.py**: Configuration constants and path definitions
- **context_manager.py**: Conversation context management for OpenAI API calls
- **file_utils.py**: File operations (PDF processing, text/PDF generation, logging)
- **openai_client.py**: OpenAI API interactions and prompt engineering

### Data Flow

1. User places job description in `working-data/job_listing.txt`
2. System loads resume (PDF), skills (CSV), and criteria from `knowledge-base/`
3. OpenAI extracts company name and job title from job description
4. System generates initial cover letter using GPT-4
5. User provides feedback in interactive loop until approval
6. Final cover letter saved as text/PDF in `records/text/[Company]/`
7. Session logged to `records/logs/structured_log.json`

### Directory Structure

- **knowledge-base/**: Static reference data (resume PDF, skills CSV, criteria)
- **working-data/**: Input files for current job application
- **temp-data/**: Temporary files during processing
- **records/**: Output files organized by company and logs

## Common Commands

### Running the Application

```bash
# Main application
python main.py

# Legacy standalone version
python app.py

# Install dependencies
pip install -r requirements.txt
```

### Environment Setup

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows
.venv\Scripts\activate
# Unix/MacOS
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Key Technical Details

### OpenAI Integration

- Uses GPT-4 model ("gpt-4.1") for all text generation
- Implements conversation context management to maintain state
- Employs specific prompt engineering for natural, human-like writing
- Uses JSON mode for reliable data extraction

### File Processing

- PDF text extraction using PyPDF2
- Professional PDF generation using ReportLab
- Filename sanitization for cross-platform compatibility
- CSV logging for cover letter records

### Context Management

- Maintains conversation history for iterative refinement
- Saves/loads context to `context.json` for session persistence
- Resets context between new job applications

## Configuration

Environment variables required:
- `OPENAI_API_KEY`: OpenAI API key for GPT access

Key file paths defined in config.py:
- Resume: `knowledge-base/ChristopherBurkeResume.pdf`
- Skills: `knowledge-base/skillset.csv` (tab-separated)
- Criteria: `knowledge-base/criteria.txt`
- Job listing: `working-data/job_listing.txt`

## Important Notes

- The application expects specific file formats and locations
- Skills file uses tab-separated values, not comma-separated
- Output files are organized by company name in sanitized directories
- Session logging captures all interactions for audit purposes
- Temporary files are cleared after successful completion