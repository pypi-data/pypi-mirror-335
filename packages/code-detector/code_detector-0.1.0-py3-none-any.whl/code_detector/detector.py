"""
Main module for code detection functionality.
"""

import re
from .helpers import (
    _is_formal_letter, _is_command_line, _is_package_manager_command,
    _contains_code_in_backticks, _is_browser_notification, _is_common_phrase,
    _is_specific_command, _is_educational_example, _is_algorithm_complexity_discussion,
    _is_r_code, _is_mathematical_expression, _check_package_installation_patterns,
    _check_specific_command_patterns, _check_instructional_command_patterns,
    _check_natural_language_patterns, _check_explicit_code_markers,
    _is_imperative_tool_command, _matches_command_usage_patterns,
    _is_direct_command, _has_simple_code_patterns, _is_short_text_without_code_indicators,
    _has_code_in_backticks, _contains_pseudocode_patterns, _contains_installation_commands,
    _contains_general_tech_patterns, _is_descriptive_technology_text,
    _check_tool_mentions, _contains_command_line_patterns, _contains_code_syntax_patterns,
    _check_indentation_patterns, _has_code_ending_characters, _contains_regex_patterns,
    _check_special_character_density, _contains_comment_patterns,
    _is_instruction_not_code, _contains_embedded_code_patterns, _is_mathematical_equation,
    _is_about_useful_commands
)

def is_code(text):
    """
    Advanced regex-based function to detect if text is likely code.
    Returns True if input appears to be code, False otherwise.
    Improved to better detect commands, imports, and simple code statements.
    Better handling of mathematical equations, R code, and general technology text.
    """
    import re
    
    # Handle empty inputs
    if not text or text.isspace():
        return False
    
    # Clean the text and get a lowercase version for some checks
    text = text.strip()
    text_lower = text.lower()
    
    # Direct check for JavaScript function syntax
    if re.search(r'function\s+\w+\s*\(\s*.*?\s*\)\s*{', text) or re.search(r'function\s*\(\s*.*?\s*\)\s*{.*?}', text):
        return True
        
    # Check if text is describing commands being useful
    if _is_about_useful_commands(text_lower):
        return False
    
    # Check if input is a formal letter/email - should not be classified as code
    if _is_formal_letter(text, text_lower):
        return False
    
    # Check if text is a command-line instruction
    if _is_command_line(text):
        return True
    
    # Check if text is a package manager command
    if _is_package_manager_command(text_lower):
        return True
    
    # Check for code in backticks
    if _contains_code_in_backticks(text):
        return True
    
    # Early return for common browser/system notifications
    if _is_browser_notification(text_lower):
        return False
    
    # Check for common natural language phrases
    if _is_common_phrase(text_lower):
        return False
    
    # Check for specific command patterns
    if _is_specific_command(text):
        return True
    
    # Check if text is an educational example that shouldn't be classified as code
    if _is_educational_example(text, text_lower):
        return False
    
    # Check for algorithm complexity discussion
    if _is_algorithm_complexity_discussion(text, text_lower):
        return False
        
    # Check for R code patterns
    if _is_r_code(text, text_lower):
        return True
    
    # Check for mathematical expressions (not code)
    if _is_mathematical_expression(text, text_lower):
        return False
    
    # Check first for specific package installation commands or common CLI patterns
    if _check_package_installation_patterns(text_lower):
        return True
    
    # Check for common package installation or command line instructions
    if _check_specific_command_patterns(text, text_lower):
        return True
    
    # Check if instructional text contains command-like pattern
    if _check_instructional_command_patterns(text, text_lower):
        return True
    
    # If we have natural language patterns but no explicit code, it's description (return False)
    has_natural_language = _check_natural_language_patterns(text_lower)
    has_explicit_code = _check_explicit_code_markers(text)
    
    if has_natural_language and not has_explicit_code:
        # Check if we have a command within instructional text
        if re.search(r'(use|run|type)\s+(\w+)\s+(\w+)\s+([\w\-\.]+)', text_lower):
            match = re.search(r'(use|run|type)\s+(\w+)\s+(\w+)\s+([\w\-\.]+)', text_lower)
            cmd = match.group(2)
            action = match.group(3)
            target = match.group(4)
            
            # Common CLI commands and their actions
            cli_commands = {
                'pip': ['install', 'uninstall', 'freeze', 'list'],
                'npm': ['install', 'uninstall', 'update', 'init'],
                'git': ['clone', 'pull', 'push', 'commit', 'add'],
                'docker': ['run', 'build', 'pull', 'push', 'exec'],
                'apt': ['install', 'remove', 'update', 'upgrade'],
                'brew': ['install', 'uninstall', 'update'],
                'yum': ['install', 'remove', 'update'],
                'conda': ['install', 'create', 'activate']
            }
            
            # If the command and action pair is valid, check for descriptive context before classifying as code
            if cmd in cli_commands and action in cli_commands[cmd]:
                # Check for descriptive language indicating this is text about commands, not actual code
                descriptive_phrases = [
                    r'is\s+used\s+to',
                    r'can\s+be\s+used\s+to',
                    r'helps?\s+to',
                    r'allows?\s+you\s+to',
                    r'you\s+can\s+use',
                    r'important\s+for',
                    r'useful\s+for',
                    r'example\s+of',
                    r'helps?\s+in',
                    r'are\s+useful',
                    r'is\s+useful',
                    r'are\s+helpful',
                    r'is\s+helpful',
                    r'is\s+a',
                    r'are\s+great',
                    r'framework',
                    r'step\s+to'
                ]
                
                for phrase in descriptive_phrases:
                    if re.search(phrase, text_lower):
                        return False
                        
                return True
        return False
    
    # If we have explicit code markers, it's code
    if has_explicit_code:
        return True
    
    # SECTION 1: IMPERATIVE TOOL COMMANDS
    if _is_imperative_tool_command(text, text_lower):
        return True
    
    # SECTION 2: COMMAND PATTERNS AND USAGE
    if _matches_command_usage_patterns(text, text_lower):
        return True
        
    # SECTION 3: DIRECT COMMAND DETECTION
    if _is_direct_command(text, text_lower):
        return True
    
    # SECTION 4: SIMPLE CODE PATTERNS
    if _has_simple_code_patterns(text):
        return True
       
    # SECTION 5: SHORT TEXT WITHOUT CODE INDICATORS
    if _is_short_text_without_code_indicators(text):
        return False
    
    # SECTION 6: BACKTICK CONTENT
    if _has_code_in_backticks(text, text_lower):
        return True
    
    # Check for pseudocode patterns
    if _contains_pseudocode_patterns(text, text_lower):
        return True
        
    # Check for installation command patterns
    if _contains_installation_commands(text_lower):
        return True
        
    # Check for general technology patterns
    if _contains_general_tech_patterns(text_lower):
        # Additional check for descriptive language about technology
        if _is_descriptive_technology_text(text_lower):
            return False
            
        # Only return True if it also contains specific commands
        if re.search(r'(pip|npm|apt|gem|yum|brew)\s+install\s+\w+', text_lower):
            return True
            
        # Check for other specific command patterns with clear syntax
        if re.search(r'(git\s+clone|docker\s+run|kubectl\s+apply|ssh\s+user@)\s+\w+', text_lower):
            return True
            
        return False
    
    # Check for tool mentions
    tool_mention_result = _check_tool_mentions(text, text_lower)
    if tool_mention_result is not None:
        return tool_mention_result
    
    # Check for command line patterns
    if _contains_command_line_patterns(text, text_lower):
        return True

    # Check for strong code syntax patterns
    if _contains_code_syntax_patterns(text, text_lower):
        return True
    
    # Check for code-like indentation patterns
    indentation_result = _check_indentation_patterns(text, text_lower)
    if indentation_result is not None:
        return indentation_result
    
    # Check for code-specific line endings
    if _has_code_ending_characters(text):
        return True
    
    # Check for code blocks and markdown code syntax
    if "```" in text or "~~~" in text:
        return True
    
    # Check for regex patterns
    if _contains_regex_patterns(text):
        return True
    
    # Check for high density of special characters
    special_chars_result = _check_special_character_density(text, text_lower)
    if special_chars_result is not None:
        return special_chars_result
    
    # Check for code comments
    if _contains_comment_patterns(text):
        return True
    
    # Check for instructional language vs. actual code
    if _is_instruction_not_code(text, text_lower):
        return False
    
    # Check for code patterns embedded in text
    if _contains_embedded_code_patterns(text, text_lower):
        return True
    
    # Check for CSS patterns
    if re.search(r'[.#]?[\w-]+\s*{\s*[\w-]+:', text):
        return True
    
    # Catch-all to prevent mathematical equations from being classified as code
    if _is_mathematical_equation(text_lower):
        return False
        
    # Add specific check for mentions of function names without code
    if re.search(r'the\s+\w+\s+function\s+from', text_lower):
        return False
        
    # Default return value if no conditions are met
    # This is crucial to avoid returning None
    return False