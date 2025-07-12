import openai
import json
from .config import OPENAI_API_KEY
from .visual_interface import VisualInterface

# Initialize OpenAI API client
openai.api_key = OPENAI_API_KEY

# Initialize visual interface for error handling
ui = VisualInterface()

def call_openai(messages, context, temperature, frequency_penalty, presence_penalty, response_format=None):
    """
    Generalized function to call the OpenAI API with specified parameters.
    """
    context.extend(messages)

    # Prepare parameters for the API call
    params = {
        "model": "gpt-4.1",
        "messages": context,
        "max_tokens": 1500,  # Encourage conciseness
        "temperature": temperature,
        "top_p": 0.95,  # Slightly more focused than 1.0
        "frequency_penalty": frequency_penalty,
        "presence_penalty": presence_penalty
    }
    # Add response_format if specified (for JSON mode)
    if response_format:
        params["response_format"] = response_format

    try:
        response = openai.ChatCompletion.create(**params)

        if response.choices and len(response.choices) > 0:
            generated_text = response.choices[0].message['content']
            # Update the context with the assistant's response
            context.append({"role": "assistant", "content": generated_text})
            return generated_text, context
        else:
            return "No response generated or an error occurred.", context

    except openai.error.OpenAIError as e:
        ui.print_error(f"OpenAI API Error: {str(e)}")
        return f"Error: {str(e)}", context

def generate_cover_letter(job_description, skills, resume_text, criteria, context, current_date, memory=None):
    """
    Generates a natural, human-like cover letter that avoids AI detection while remaining professional.
    """
    system_message = {
        "role": "system",
        "content": (
            "You are an experienced professional writing a cover letter. Write naturally and authentically, "
            "as if you're personally explaining your background to a hiring manager over coffee. "
            "Use varied sentence lengths, include contractions when natural (I've, I'm, that's, it's), and write with the subtle "
            "imperfections that make human writing authentic. Avoid overly polished or perfect prose. "
            "Be conversational yet professional, confident but not robotic. "
            "Use the exact phrasing and style from the narrative bank provided - don't rewrite it in formal language."
        )
    }

    # Prepare job-aware memory context if available
    memory_context = ""
    if memory:
        # Use intelligent memory selection based on job relevance
        job_aware_summary = memory.get_job_aware_memory_summary(job_description)
        temporal_context = memory.temporal_manager.get_temporal_context_for_generation()
        
        if job_aware_summary.strip():
            memory_context += f"**RELEVANT LEARNED PREFERENCES FOR THIS JOB:**\n{job_aware_summary}\n\n"
        
        if temporal_context.strip():
            memory_context += f"**CURRENT LIFE CONTEXT:**\n{temporal_context}\n\n"
    
    user_message = {
        "role": "user",
        "content": (
            f"Write a cover letter for this position. Write naturally—like a human would, using whatever length is most effective to showcase the candidate's qualifications.\n\n"
            f"**Today's Date:** {current_date}\n\n"
            f"{memory_context}"
            f"**Job Description:**\n{job_description}\n\n"
            f"**My Resume:**\n{resume_text}\n\n"
            f"**My Skills:** {skills}\n\n"
            f"**Writing Guidelines & Experience Bank:**\n{criteria}\n\n"
            f"**Critical Instructions:**\n"
            "- Use the EXACT phrasing from the narrative bank sections - don't rewrite them formally\n"
            "- Include contractions (I've, I'm, that's, it's, haven't, don't)\n"
            "- Write as if you're talking to someone, not writing a formal document\n"
            "- Mix short and long sentences naturally\n"
            "- Use the candidate's authentic voice from the narrative bank\n"
            "- Avoid perfect grammar and overly structured sentences\n"
            "- If you don't have direct experience with something mentioned, acknowledge it honestly but show relevant experience\n"
            "- Focus on the CORE JOB FUNCTION rather than industry context\n"
            "- IMPORTANT: Apply any learned preferences from previous feedback to improve this cover letter"
        )
    }
    
    messages = [system_message, user_message]
    
    # Parameters optimized for natural, human-like writing
    temperature = 0.9         # Higher for more creative variation
    frequency_penalty = 0.2   # Moderate to allow some repetition (humans do this)
    presence_penalty = 0.1    # Low to allow natural topic flow
    
    return call_openai(messages, context, temperature, frequency_penalty, presence_penalty)

def refine_cover_letter(cover_letter, feedback, criteria, context, memory=None, job_description=""):
    """
    Refines the cover letter while maintaining natural, human-like qualities.
    """
    system_message = {
        "role": "system",
        "content": (
            "You are refining a cover letter based on feedback. Maintain a natural, human writing style. "
            "Keep contractions, varied sentence lengths, and the authentic voice. Don't make it more formal. "
            "Make improvements but keep the natural imperfections that make writing feel human. "
            "Respond ONLY with the complete, revised cover letter text."
        )
    }

    # Prepare job-aware memory context for refinement
    memory_context = ""
    if memory:
        if job_description.strip():
            # Use job-aware memory selection for refinement too
            job_aware_summary = memory.get_job_aware_memory_summary(job_description)
            if job_aware_summary.strip():
                memory_context = f"**RELEVANT LEARNED PREFERENCES FOR THIS JOB:**\n{job_aware_summary}\n\n"
        else:
            # Fallback to general memory if no job description
            memory_summary = memory.get_memory_summary()
            if memory_summary.strip():
                memory_context = f"**LEARNED USER PREFERENCES:**\n{memory_summary}\n\n"
    
    user_message = {
        "role": "user",
        "content": (
            f"Please revise this cover letter based on the feedback. Keep it natural and human-sounding.\n\n"
            f"{memory_context}"
            f"**Current Draft:**\n{cover_letter}\n\n"
            f"**Feedback:**\n{feedback}\n\n"
            f"**Guidelines:**\n{criteria}\n\n"
            f"Remember: \n"
            "- Keep contractions (I've, I'm, that's, haven't)\n"
            "- Write naturally with varied sentence structures\n"
            "- Avoid overly polished language\n"
            "- Maintain the conversational tone\n"
            "- Apply learned preferences from previous interactions"
        )
    }

    messages = [system_message, user_message]

    # Parameters for natural revision
    temperature = 0.85        # Higher for more creative revision
    frequency_penalty = 0.2   # Moderate to prevent repetition
    presence_penalty = 0.2    # Moderate to encourage new ideas

    return call_openai(messages, context, temperature, frequency_penalty, presence_penalty)

def regenerate_cover_letter(rejected_cover_letter, job_description, skills, resume_text, criteria, context, current_date, memory=None):
    """
    Generates a completely new cover letter when the user rejects the previous one entirely.
    This function emphasizes that the user completely rejected the previous attempt.
    """
    system_message = {
        "role": "system",
        "content": (
            "You are an expert cover letter writer. The user has COMPLETELY REJECTED the previous cover letter, "
            "which means it was entirely unsuitable and needs to be completely rewritten from scratch. "
            "Focus on creating a significantly better, more compelling, and more targeted cover letter. "
            "Write naturally and authentically, as if you're personally explaining your background to a hiring manager. "
            "Use varied sentence lengths, include contractions when natural, and write with authentic human imperfections. "
            "Be conversational yet professional, confident but not robotic. "
            "This is your chance to create something much better than the rejected version."
        )
    }

    # Prepare job-aware memory context for regeneration
    memory_context = ""
    if memory:
        # Use intelligent memory selection for regeneration
        job_aware_summary = memory.get_job_aware_memory_summary(job_description)
        temporal_context = memory.temporal_manager.get_temporal_context_for_generation()
        
        if job_aware_summary.strip():
            memory_context += f"**RELEVANT LEARNED PREFERENCES (to apply to new version):**\n{job_aware_summary}\n\n"
        
        if temporal_context.strip():
            memory_context += f"**CURRENT LIFE CONTEXT:**\n{temporal_context}\n\n"
    
    user_message = {
        "role": "user",
        "content": (
            f"The user has COMPLETELY REJECTED the following cover letter:\n\n"
            f"--- REJECTED COVER LETTER ---\n{rejected_cover_letter}\n--- END REJECTED COVER LETTER ---\n\n"
            f"The user doesn't want refinements - they want a COMPLETELY NEW and MUCH BETTER cover letter. "
            f"Please create an entirely new cover letter that is significantly better, more compelling, and more targeted.\n\n"
            f"**Today's Date:** {current_date}\n\n"
            f"{memory_context}"
            f"**Job Description:**\n{job_description}\n\n"
            f"**My Resume:**\n{resume_text}\n\n"
            f"**My Skills:** {skills}\n\n"
            f"**Writing Guidelines & Experience Bank:**\n{criteria}\n\n"
            f"**Critical Instructions for the NEW cover letter:**\n"
            "- Create something COMPLETELY DIFFERENT from the rejected version\n"
            "- Make it significantly more compelling and targeted\n"
            "- Use the EXACT phrasing from the narrative bank sections\n"
            "- Include contractions (I've, I'm, that's, it's, haven't, don't)\n"
            "- Write as if you're talking to someone, not writing a formal document\n"
            "- Mix short and long sentences naturally\n"
            "- Use the candidate's authentic voice from the narrative bank\n"
            "- Focus on the CORE JOB FUNCTION and what makes this candidate special\n"
            "- Use whatever length is most effective to create a compelling, impactful cover letter that's much better than the rejected version\n"
            "- Show genuine enthusiasm and connection to the role\n"
            "- Apply learned preferences to make this version better"
        )
    }
    
    messages = [system_message, user_message]
    
    # Parameters optimized for creative regeneration with high quality
    temperature = 0.95        # Higher for maximum creativity and variation
    frequency_penalty = 0.1   # Lower to encourage fresh phrasing
    presence_penalty = 0.3    # Higher to encourage exploring new topics/angles
    
    return call_openai(messages, context, temperature, frequency_penalty, presence_penalty)

def extract_company_and_title(job_listing, context):
    """
    Extracts company name and job title using GPT-4o's JSON mode for reliable parsing.
    """
    messages = [
        {
            "role": "system",
            "content": "You are a highly accurate data extraction assistant. Your task is to extract the company name and job title from the provided job listing and return the data in JSON format."
        },
        {
            "role": "user",
            "content": f"Here is the job listing:\n\n---\n{job_listing}\n---\n\nPlease extract the company name and job title. Your response must be a valid JSON object with the keys 'company_name' and 'job_title'."
        }
    ]

    # Parameters for precise, deterministic output
    temperature = 0.0
    frequency_penalty = 0.0
    presence_penalty = 0.0
    response_format = {"type": "json_object"}

    return call_openai(messages, context, temperature, frequency_penalty, presence_penalty, response_format)

def process_extracted_info(extracted_info):
    """
    Processes the JSON output from the extraction function to get the company name and job title.
    """
    try:
        # The extracted_info is now a JSON string, so we parse it.
        data = json.loads(extracted_info)
        company_name = data.get("company_name", "").strip()
        job_title = data.get("job_title", "").strip()
        
        # A fallback in case the model returns empty values
        if not company_name and not job_title:
             ui.print_warning("Could not parse company name and job title from JSON. Retrying with text parsing.")
             return process_extracted_info_fallback(extracted_info)

        return company_name, job_title
    except (json.JSONDecodeError, TypeError):
        # Fallback to the old method if JSON parsing fails
        ui.print_warning("JSON parsing failed. Retrying with text parsing.")
        return process_extracted_info_fallback(extracted_info)

def process_extracted_info_fallback(extracted_info):
    """A fallback function that mimics the original text parsing logic."""
    company_name = ""
    job_title = ""
    lines = extracted_info.split('\n')
    for line in lines:
        if "Company Name:" in line:
            company_name = line.split("Company Name:", 1)[1].strip()
        elif "Job Title:" in line:
            job_title = line.split("Job Title:", 1)[1].strip()
    return company_name, job_title