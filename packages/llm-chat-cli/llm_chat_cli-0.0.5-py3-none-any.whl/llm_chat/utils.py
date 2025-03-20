"""
Utility functions for LLM Chat
"""

import tiktoken
import textwrap
import time
import sys
from rich.console import Console
from rich.markdown import Markdown
from termcolor import colored


def count_tokens(text, model):
    """
    Count tokens in the given text.

    Args:
        text (str): The text to count tokens for
        model (str): The model name (currently unused, but kept for future model-specific counting)

    Returns:
        int: Number of tokens in the text
    """
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


def print_wrapped_text(text, width=80, indent="  "):
    """
    Print text with proper wrapping.

    Args:
        text (str): The text to wrap and print
        width (int): Maximum line width
        indent (str): Indentation string to prepend to each line
    """
    wrapped_lines = textwrap.wrap(text, width=width)
    for line in wrapped_lines:
        print(f"{indent}{line}")


def render_markdown(text, stream_mode=False, last_chunk=""):
    """
    Render text as markdown.

    Args:
        text (str): The markdown text to render
        stream_mode (bool): Whether to render in stream mode
        last_chunk (str): The last chunk that was rendered (used in stream mode)
    """
    console = Console()
    md = Markdown(text)
    
    if stream_mode:
        # Only render the new addition to the text
        new_text = text[len(last_chunk):]
        if new_text:
            # Print without the markdown formatting for streaming
            sys.stdout.write(new_text)
            sys.stdout.flush()
    else:
        # Full render with markdown formatting
        console.print(md)
        
def stream_with_markdown_chunks(chunks, code_blocks=True):
    """
    Stream text with special handling for code blocks and other Markdown formatting.
    
    Args:
        chunks (iterable): Iterator of text chunks to stream
        code_blocks (bool): Whether to preserve code block formatting while streaming
    
    Returns:
        str: The full accumulated response
    """
    full_response = ""
    in_code_block = False
    code_block_buffer = ""
    showed_generating_message = False
    console = Console()
    
    # Accumulate a buffer for paragraphs to apply markdown formatting
    text_buffer = ""
    special_markers = ["```", "##", "**", "*", "_", ">", "- ", "1. ", "![", "["]
    needs_formatting = False
    
    # Helper function to render text with markdown formatting
    def render_text(text):
        # Skip if empty
        if not text.strip():
            return
            
        # Detect if text has markdown elements that need formatting
        has_md = any(marker in text for marker in special_markers)
        # Detect if text ends with a complete paragraph
        ends_with_paragraph = text.endswith("\n\n") or text.endswith("\n")
        
        # If we have markdown and a complete thought/paragraph, render it
        if has_md and ends_with_paragraph:
            console.print(Markdown(text))
            return True
        # If it's just plain text, output directly
        elif not has_md:
            sys.stdout.write(text)
            sys.stdout.flush()
            return True
        # Otherwise, it needs more context to be formatted properly
        return False
    
    try:
        for chunk in chunks:
            if chunk is None:
                continue
                
            full_response += chunk
            
            # If we see a code block marker
            if "```" in chunk:
                # We need to find all occurrences and handle them in order
                remaining_chunk = chunk
                while "```" in remaining_chunk:
                    # Find the position of the next code block marker
                    marker_pos = remaining_chunk.find("```")
                    
                    if in_code_block:
                        # We're in a code block, this is a closing marker
                        code_block_buffer += remaining_chunk[:marker_pos+3]
                        
                        # Clear the "generating code" message
                        if showed_generating_message:
                            sys.stdout.write("\r" + " " * 30 + "\r")
                            sys.stdout.flush()
                            showed_generating_message = False
                        
                        # Display the formatted code block
                        console.print(Markdown(code_block_buffer))
                        code_block_buffer = ""
                        
                        # Process remainder of chunk after this marker
                        remaining_chunk = remaining_chunk[marker_pos+3:]
                        in_code_block = False
                    else:
                        # We're not in a code block, this is an opening marker
                        # First render any text before the marker with markdown
                        if marker_pos > 0:
                            text_to_render = remaining_chunk[:marker_pos]
                            if text_buffer:
                                text_to_render = text_buffer + text_to_render
                                text_buffer = ""
                            render_text(text_to_render)
                        
                        # Show "generating code" message
                        sys.stdout.write(colored("\n> Generating code... ", "cyan"))
                        sys.stdout.flush()
                        showed_generating_message = True
                        
                        # Start the code block buffer with this marker
                        code_block_buffer = remaining_chunk[marker_pos:]
                        
                        # Update remaining chunk to be empty since we've captured it all
                        remaining_chunk = ""
                        in_code_block = True
                
                # If we've processed all markers but still have text and we're not in a code block
                if remaining_chunk and not in_code_block:
                    # Check if remaining chunk has markdown that needs formatting
                    if any(marker in remaining_chunk for marker in special_markers):
                        text_buffer += remaining_chunk
                        # Try to render if it's a complete paragraph
                        if "\n\n" in text_buffer or text_buffer.endswith("\n"):
                            if render_text(text_buffer):
                                text_buffer = ""
                    else:
                        # Just plain text, output directly
                        sys.stdout.write(remaining_chunk)
                        sys.stdout.flush()
                
            else:
                # No code block markers in this chunk
                if in_code_block:
                    # Add to the code block buffer
                    code_block_buffer += chunk
                else:
                    # Check if chunk contains other markdown formatting
                    if any(marker in chunk for marker in special_markers):
                        text_buffer += chunk
                        # Try to render if it looks like a complete paragraph or line
                        if "\n\n" in text_buffer or text_buffer.endswith("\n"):
                            if render_text(text_buffer):
                                text_buffer = ""
                    else:
                        # Just plain text, output directly
                        if text_buffer:
                            # First try to render any buffered text
                            if render_text(text_buffer):
                                text_buffer = ""
                            else:
                                text_buffer += chunk
                        else:
                            sys.stdout.write(chunk)
                            sys.stdout.flush()
        
        # Handle any remaining text at the end
        if text_buffer:
            console.print(Markdown(text_buffer))
            
        # Handle any incomplete code block at the end
        if code_block_buffer:
            if showed_generating_message:
                sys.stdout.write("\r" + " " * 30 + "\r")
                sys.stdout.flush()
                showed_generating_message = False
            
            console.print(Markdown(code_block_buffer))
    
    except Exception as e:
        # If something goes wrong, try to recover
        if showed_generating_message:
            sys.stdout.write("\r" + " " * 30 + "\r")
            sys.stdout.flush()
        sys.stdout.write(f"\nError in streaming: {str(e)}\n")
        sys.stdout.flush()
    
    return full_response


def print_available_models(models):
    print(colored("\nAvailable models:", "cyan"))
    for p, m_list in models.items():
        print(colored(f"{p.capitalize()}:", "yellow"))
        for m in m_list:
            print(colored(f"  - {m}", "green"))


def create_typing_animation(text="Thinking", color="cyan"):
    """
    Create a typing animation effect.

    Args:
        text (str): The text to display before the animation
        color (str): The color to use for the animation
    """
    animations = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
    i = 0
    start_time = time.time()
    sys.stdout.write(colored(f"{text} ", color))
    sys.stdout.flush()

    while time.time() - start_time < 0.5:  # Reduced animation time to 0.5 seconds
        sys.stdout.write(colored(f"\r{text} {animations[i % len(animations)]}", color))
        sys.stdout.flush()
        time.sleep(0.05)  # Faster animation updates
        i += 1

    sys.stdout.write(colored(f"\r{text}   \n", color))
    sys.stdout.flush()
