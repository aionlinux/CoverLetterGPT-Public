from .context_manager import (
    reset_conversation_context,
    save_context_to_file,
    load_context_from_file,
)
from .file_utils import (
    read_file,
    read_skills,
    extract_pdf_text,
    read_criteria,
    save_cover_letter_text,
    save_cover_letter_pdf,
    record_cover_letter,
    log_file_creation,
    structured_log,
    clear_temporary_files,
)
from .openai_client import (
    extract_company_and_title,
    process_extracted_info,
    generate_cover_letter,
    refine_cover_letter,
    regenerate_cover_letter,
)
from .config import (
    JOB_LISTING_FILE_PATH,
    SKILLS_FILE_PATH,
    RESUME_FILE_PATH,
    CRITERIA_FILE_PATH,
    COVER_LETTER_TEMP_PATH,
    COVER_LETTER_RECORDS_FILE_PATH,
)
from .visual_interface import VisualInterface
from .memory_core import MemoryCore
from .feedback_analyzer import FeedbackAnalyzer
from .file_monitor import FileMonitor

from datetime import datetime

def get_todays_date():
    """Returns today's date in the format 'Month Day, Year'."""
    return datetime.now().strftime('%B %d, %Y')

def main():
    # Initialize the visual interface
    ui = VisualInterface()
    
    # Initialize memory and learning system
    memory = MemoryCore()
    feedback_analyzer = FeedbackAnalyzer(memory)
    file_monitor = FileMonitor(memory)
    
    # Display banner
    ui.print_banner()
    ui.pause_for_effect(1.5)
    
    # Auto-sync files and update memory system
    ui.print_section_header("Memory System Initialization")
    ui.start_loading("Synchronizing files and updating memory")
    
    # Auto-sync files first
    sync_results = file_monitor.auto_sync_files()
    temporal_updates = memory.update_temporal_events()
    ui.stop_loading()
    
    # Report file changes
    if sync_results["changes_detected"]:
        ui.print_success("Files synchronized with memory!")
        if sync_results["skillset_changes"]:
            changes = sync_results["skillset_changes"]
            ui.print_info(f"Skills updated: +{changes['added']} -{changes['removed']} ~{changes['updated']}")
    
    # Report cleanup
    if sync_results["cleanup_results"]["invalid_skills_removed"] > 0:
        cleanup = sync_results["cleanup_results"]
        ui.print_success(f"Memory optimized: removed {cleanup['invalid_skills_removed']} invalid entries")
    
    # Report temporal updates
    if temporal_updates:
        ui.print_info(f"Timeline updated: {len(temporal_updates)} event transitions")
    
    # Display basic memory statistics
    total_skills = len(memory.get_current_skills())
    total_interactions = memory.memory_data["metadata"]["total_interactions"]
    if total_skills > 0 or total_interactions > 0:
        ui.print_info(f"Memory loaded: {total_skills} skills learned, {total_interactions} total interactions")
    
    ui.print_section_footer()
    
    # Clear the context to start fresh
    context = reset_conversation_context()  # Ensure a fresh context for each new session

    # Load the required data with visual feedback
    ui.print_section_header("Loading Application Data")
    ui.print_step(1, "Loading required files...")
    
    try:
        ui.start_loading("Loading job description")
        job_description = read_file(JOB_LISTING_FILE_PATH)
        ui.stop_loading()
        ui.print_data_loading_status("job_listing.txt", True)
        
        ui.start_loading("Loading skills database")
        skills = read_skills(SKILLS_FILE_PATH)
        ui.stop_loading()
        ui.print_data_loading_status("skillset.csv", True)
        
        ui.start_loading("Extracting resume content")
        resume_text = extract_pdf_text(RESUME_FILE_PATH)
        ui.stop_loading()
        ui.print_data_loading_status("ChristopherBurkeResume.pdf", True)
        
        ui.start_loading("Loading criteria")
        criteria = read_criteria(CRITERIA_FILE_PATH)
        ui.stop_loading()
        ui.print_data_loading_status("criteria.txt", True)
        
        ui.print_success("All data loaded successfully!")
        ui.print_section_footer()
        
    except Exception as e:
        ui.stop_loading()
        ui.print_error(f"Error loading data: {e}")
        ui.print_section_footer()
        return

    # Attempt to extract company name and job title using GPT
    ui.print_section_header("AI Processing")
    ui.print_step(2, "Extracting company information from job description...")
    
    ui.start_loading("Analyzing job description with AI")
    extracted_info, context = extract_company_and_title(job_description, context)
    ui.stop_loading()

    # Process extracted information
    company_name, job_title = process_extracted_info(extracted_info)
    ui.print_extracted_info(company_name, job_title)

    # Analyze job relevance and show relevant memories
    if total_skills > 0:
        ui.start_loading("Analyzing job requirements against learned skills")
        memory_analysis = memory.get_memory_analysis_for_job(job_description)
        ui.stop_loading()
        
        relevant_skills = memory_analysis.get("relevant_skills", [])
        if relevant_skills:
            ui.print_info(f"Found {len(relevant_skills)} relevant skills from memory:")
            for skill in relevant_skills[:3]:  # Show top 3
                score = memory_analysis["skill_scores"].get(skill["skill_name"], 0)
                ui.print_info(f"  • {skill['skill_name']} (relevance: {score:.1f})")

    # Get today's date
    current_date = get_todays_date()

    # Generate the initial cover letter with memory context
    ui.print_step(3, "Generating personalized cover letter...")
    ui.start_loading("Creating cover letter with AI (using job-relevant experience)")
    cover_letter, context = generate_cover_letter(job_description, skills, resume_text, criteria, context, current_date, memory)
    ui.stop_loading()
    
    ui.print_success("Cover letter generated successfully!")
    ui.print_cover_letter_preview(cover_letter)
    ui.print_section_footer()

    # User-driven iterative refinement loop
    approval = False
    refinement_count = 0
    
    while not approval:
        user_input = ui.get_user_approval()
        
        # Handle user input and update context accordingly
        if user_input == 'yes':
            approval = True  # Set approval to True to break the loop
        elif user_input == 'no':
            refinement_count += 1
            ui.print_warning("Cover letter completely rejected. Generating a new version...")
            
            # Analyze rejection for learning
            ui.start_loading("Learning from rejection")
            rejection_feedback = "Complete rejection - user found entire cover letter unsuitable"
            feedback_analyzer.analyze_feedback(rejection_feedback, cover_letter, "rejected")
            ui.stop_loading()
            
            ui.print_step(f"3.{refinement_count}", "Generating completely new cover letter...")
            
            # Regenerate the cover letter from scratch based on complete rejection
            ui.start_loading("Creating a completely new cover letter (applying lessons learned)")
            cover_letter, context = regenerate_cover_letter(cover_letter, job_description, skills, resume_text, criteria, context, current_date, memory)
            save_context_to_file(context, 'context.json')
            ui.stop_loading()
            
            ui.print_success("New cover letter generated successfully!")
            ui.print_cover_letter_preview(cover_letter)
        elif user_input == 'feedback':
            refinement_count += 1
            feedback = ui.get_user_feedback()
            
            # Analyze feedback for learning before refining (optimized for performance)
            ui.start_loading("Analyzing feedback for learning")
            insights = feedback_analyzer.analyze_feedback(feedback, cover_letter, "revision_requested")
            ui.stop_loading()
            
            # Only show learning message for meaningful insights
            if not insights.get("simple_approval") and (insights.get("skills_mentioned") or insights.get("phrases_to_avoid") or insights.get("temporal_information")):
                ui.print_info("Learning new preferences from your feedback...")
            
            ui.print_refinement_header()
            ui.print_step(f"3.{refinement_count}", "Refining cover letter based on your feedback...")

            # Refine the cover letter with feedback and memory context
            ui.start_loading("Applying your feedback (with learned context)")
            cover_letter, context = refine_cover_letter(cover_letter, feedback, criteria, context, memory, job_description)
            save_context_to_file(context, 'context.json')
            ui.stop_loading()

            ui.print_success("Cover letter refined successfully!")
            ui.print_cover_letter_preview(cover_letter)

    if approval:
        # Fast-track simple approval processing (optimized)
        ui.start_loading("Recording successful outcome")
        approval_feedback = "Cover letter approved and accepted by user"
        feedback_analyzer.analyze_feedback(approval_feedback, cover_letter, "accepted")
        ui.stop_loading()
        
        # Save the cover letter files
        ui.print_section_header("Saving Cover Letter")
        ui.print_step(4, "Saving cover letter files...")
        
        ui.start_loading("Saving text file")
        text_path = save_cover_letter_text(cover_letter, company_name, job_title)
        ui.stop_loading()
        ui.print_file_saved("Text file", text_path)

        ui.start_loading("Generating PDF")
        pdf_path = save_cover_letter_pdf(cover_letter, company_name, job_title)
        ui.stop_loading()
        ui.print_file_saved("PDF file", pdf_path)

        # Update the CSV record with the new cover letter and the file path
        ui.start_loading("Updating records")
        record_cover_letter(job_title, company_name, cover_letter, text_path)
        ui.stop_loading()

        # Create a log entry for the created text and PDF files
        file_log_entry = log_file_creation(text_path, "Cover letter text file.")
        pdf_log_entry = log_file_creation(pdf_path, "Cover letter PDF file.")

        # Log the session
        structured_log(user_request="Cover letter generation and refinement", gpt_response=cover_letter, created_files=[file_log_entry, pdf_log_entry])

        ui.print_success("Records updated successfully!")

        # Clear text within temporary files without deleting the files
        ui.print_step(5, "Cleaning up temporary files...")
        ui.start_loading("Clearing temporary files")
        clear_temporary_files([COVER_LETTER_TEMP_PATH, JOB_LISTING_FILE_PATH])
        clear_temporary_files(['context.json'])
        ui.stop_loading()
        ui.print_success("Temporary files cleared!")

        # Final session completion
        ui.print_session_complete()
        ui.print_section_footer()

    # Save or clear the final context for future sessions
    save_context_to_file(context, 'context.json')  # Save context if the session may be resumed
    context = reset_conversation_context()  # Clear context for new sessions

    ui.print_goodbye()

if __name__ == "__main__":
    main()