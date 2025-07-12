"""
Professional Visual Interface Module for Cover Letter GPT
Provides sophisticated visual elements using colorama for a professional user experience
"""

import time
import sys
from colorama import Fore, Back, Style, init
from threading import Thread
import itertools

# Initialize colorama for cross-platform color support
init(autoreset=True)

class VisualInterface:
    """Professional visual interface with sophisticated styling and minimal decoration"""
    
    def __init__(self):
        self.loading_animation = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        self.is_loading = False
        self.loading_thread = None
        
    def print_banner(self):
        """Display a professional banner for the application"""
        banner = f"""
{Fore.CYAN}{Style.BRIGHT}
┌────────────────────────────────────────────────────────────────────────────────┐
│                                                                                │
│                         COVER LETTER GENERATOR                                 │
│                                                                                │
│                    AI-Powered Professional Writing Assistant                   │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
{Style.RESET_ALL}
        """
        print(banner)
        
    def print_section_header(self, title):
        """Print a professional section header"""
        print(f"\n{Fore.BLUE}{Style.BRIGHT}┌─ {title.upper()} ─{'─' * (60 - len(title))}")
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL}")
        
    def print_section_footer(self):
        """Print a section footer"""
        print(f"{Fore.BLUE}{Style.BRIGHT}└─{'─' * 78}{Style.RESET_ALL}")
        
    def print_step(self, step_number, step_description):
        """Print a numbered step with professional styling"""
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL} {Fore.CYAN}[{step_number}]{Style.RESET_ALL} {step_description}")
    
    def print_data_preview(self, data):
        """Print a data preview with professional styling"""
        # Handle multi-line data and bullet points properly
        lines = str(data).split('\n')
        for line in lines:
            # Clean up bullet points and dashes to stay within the pipe structure
            if line.strip().startswith('- '):
                formatted_line = line.replace('- ', '  • ', 1)
            elif line.strip().startswith('•'):
                formatted_line = f"  {line.strip()}"
            else:
                formatted_line = line
            print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL} {Fore.YELLOW}{formatted_line}{Style.RESET_ALL}")
        
    def print_success(self, message):
        """Print a success message with professional styling"""
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL} {Fore.GREEN}[✓]{Style.RESET_ALL} {message}")
        
    def print_error(self, message):
        """Print an error message with professional styling"""
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL} {Fore.RED}[✗]{Style.RESET_ALL} ERROR: {message}")
        
    def print_warning(self, message):
        """Print a warning message with professional styling"""
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL} {Fore.YELLOW}[!]{Style.RESET_ALL} WARNING: {message}")
        
    def print_info(self, message):
        """Print an info message with professional styling"""
        # Handle multi-line messages and bullet points
        lines = str(message).split('\n')
        for line in lines:
            # Clean up bullet points and dashes to stay within the pipe structure
            if line.strip().startswith('- '):
                formatted_line = f"    • {line.strip()[2:]}"
            elif line.strip().startswith('•'):
                formatted_line = f"    {line.strip()}"
            else:
                formatted_line = line
            print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL} {Fore.CYAN}[i]{Style.RESET_ALL} {formatted_line}")
        
    def print_highlight(self, message):
        """Print a highlighted message with professional styling"""
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL} {Back.BLUE}{Fore.WHITE}{Style.BRIGHT} {message} {Style.RESET_ALL}")
        
    def print_extracted_info(self, company_name, job_title):
        """Display extracted company and job information in a professional format"""
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL} {Fore.CYAN}[EXTRACTED INFORMATION]{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL} ├─ Company: {Fore.WHITE}{Style.BRIGHT}{company_name}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL} └─ Position: {Fore.WHITE}{Style.BRIGHT}{job_title}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL}")
        
    def print_cover_letter_preview(self, cover_letter):
        """Display the cover letter with professional styling"""
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL} {Fore.MAGENTA}[COVER LETTER PREVIEW]{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL} {'─' * 76}")
        
        # Add subtle styling to the cover letter content with proper wrapping
        lines = cover_letter.split('\n')
        for i, line in enumerate(lines):
            if line.strip():
                # Wrap long lines to fit within the border (72 characters max to account for border)
                wrapped_lines = self._wrap_text(line, 72)
                for j, wrapped_line in enumerate(wrapped_lines):
                    # All text should be white for consistent professional appearance
                    print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL} {Fore.WHITE}{wrapped_line}{Style.RESET_ALL}")
            else:
                print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL}")
        
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL} {'─' * 76}")
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL}")
        
    def _wrap_text(self, text, width):
        """Wrap text to specified width, preserving words"""
        if len(text) <= width:
            return [text]
        
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            # Check if adding this word would exceed the width
            test_line = current_line + (" " if current_line else "") + word
            if len(test_line) <= width:
                current_line = test_line
            else:
                # If we have a current line, add it to lines
                if current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    # Single word is longer than width, just add it
                    lines.append(word)
                    current_line = ""
        
        # Add the last line if it exists
        if current_line:
            lines.append(current_line)
            
        return lines
        
    def get_user_approval(self):
        """Get user approval with professional prompt"""
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL} {Fore.CYAN}[REVIEW REQUIRED]{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL} Please review the cover letter above and select an option:")
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL} {Fore.GREEN}[1] yes{Style.RESET_ALL}      - Approve and save the cover letter")
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL} {Fore.RED}[2] no{Style.RESET_ALL}       - Reject completely, generate new version")
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL} {Fore.YELLOW}[3] feedback{Style.RESET_ALL} - Provide specific feedback for refinement")
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL}")
        
        while True:
            user_input = input(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL} {Fore.CYAN}Your selection:{Style.RESET_ALL} ").strip().lower()
            if user_input in ['yes', 'no', 'feedback', '1', '2', '3']:
                # Convert numbered options to text
                if user_input == '1':
                    return 'yes'
                elif user_input == '2':
                    return 'no'
                elif user_input == '3':
                    return 'feedback'
                else:
                    return user_input
            else:
                print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL} {Fore.RED}[✗]{Style.RESET_ALL} Invalid selection. Please choose 'yes', 'no', 'feedback', or 1-3.")
                
    def get_user_feedback(self):
        """Get detailed feedback from user with professional prompt"""
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL} {Fore.YELLOW}[FEEDBACK REQUEST]{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL} Please provide specific feedback on how to improve the cover letter:")
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL}")
        feedback = input(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL} {Fore.CYAN}Your feedback:{Style.RESET_ALL} ")
        return feedback.strip()
        
    def start_loading(self, message):
        """Start a loading animation with message"""
        self.is_loading = True
        self.loading_thread = Thread(target=self._loading_animation, args=(message,))
        self.loading_thread.start()
        
    def stop_loading(self):
        """Stop the loading animation"""
        self.is_loading = False
        if self.loading_thread:
            self.loading_thread.join()
        # Clear the loading line
        print(f"\r{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL} {' ' * 74}\r", end="")
        
    def _loading_animation(self, message):
        """Internal method for loading animation"""
        while self.is_loading:
            for frame in self.loading_animation:
                if not self.is_loading:
                    break
                print(f"\r{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL} {Fore.CYAN}{frame}{Style.RESET_ALL} {message}...", end="", flush=True)
                time.sleep(0.1)
                
    def print_file_saved(self, file_type, file_path):
        """Print file saved confirmation with professional styling"""
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL} {Fore.GREEN}[✓]{Style.RESET_ALL} {file_type} saved successfully")
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL}   └─ Location: {Fore.WHITE}{file_path}{Style.RESET_ALL}")
        
    def print_session_complete(self):
        """Print session completion message with professional styling"""
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL} {Fore.GREEN}[✓]{Style.RESET_ALL} {Style.BRIGHT}SESSION COMPLETED SUCCESSFULLY{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL} Your cover letter has been generated and saved.")
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL} The application is ready for your next job application.")
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL}")
        
    def print_progress_bar(self, current, total, description="Progress"):
        """Print a professional progress bar"""
        percent = int((current / total) * 100)
        filled_length = int(40 * current // total)
        bar = '█' * filled_length + '░' * (40 - filled_length)
        print(f"\r{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL} {description}: {Fore.CYAN}[{bar}]{Style.RESET_ALL} {percent}%", end="", flush=True)
        if current == total:
            print()  # New line when complete
            
    def print_data_loading_status(self, file_name, success=True):
        """Print file loading status with professional styling"""
        if success:
            print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL} {Fore.GREEN}[✓]{Style.RESET_ALL} Loaded: {file_name}")
        else:
            print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL} {Fore.RED}[✗]{Style.RESET_ALL} Failed to load: {file_name}")
            
    def print_refinement_header(self):
        """Print header for refinement process"""
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL} {Fore.YELLOW}[REFINEMENT PROCESS]{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL}")
        
    def print_goodbye(self):
        """Print professional goodbye message"""
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL} {Fore.CYAN}Thank you for using Cover Letter Generator.{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL} {Fore.WHITE}Best of luck with your job application.{Style.RESET_ALL}")
        self.print_section_footer()
        
    def pause_for_effect(self, seconds=1):
        """Add a pause for dramatic effect"""
        time.sleep(seconds)
        
    def clear_screen(self):
        """Clear the screen (cross-platform)"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def print_parameter_info(self, param_type, temperature, freq_penalty, presence_penalty):
        """Print parameter information for debugging/info purposes"""
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL} {Fore.CYAN}[PARAMETERS]{Style.RESET_ALL} {param_type}")
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL}   ├─ Temperature: {temperature}")
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL}   ├─ Frequency Penalty: {freq_penalty}")
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL}   └─ Presence Penalty: {presence_penalty}")
        
    def print_operation_summary(self, operation, details):
        """Print a summary of an operation"""
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL} {Fore.MAGENTA}[{operation.upper()}]{Style.RESET_ALL}")
        for detail in details:
            print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL}   • {detail}")
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL}")
        
    def print_blank_line(self):
        """Print a blank line within the section"""
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL}")
        
    def print_divider(self):
        """Print a horizontal divider within the section"""
        print(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL} {'─' * 76}")