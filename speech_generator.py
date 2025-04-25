import os
import re
import time
import markdown
from bs4 import BeautifulSoup

from speech_services import OpenAISpeechService, GoogleSpeechService, AzureSpeechService


def convert_markdown_chunk_to_ssml():
    pass

def check_chunk_size():
    """
    Check number of characters in chunk.
    If greater than 4096, we'll need to reduce the originating
    markdown chunk size by the delta (by calling rechunk).
    """
    pass

def rechunk():
    """
    Rechunk previously chunked markdown, with new max_size
    determined by delta produced via `check_ssml_chunk_size`. 
    
    Actually, this can just call `chunk_markdown_section` with
    an explicit `max_size` value passed.
    """
    pass



def generate_speech_from_markdown(
        markdown_content: str, 
        output_dir: str, 
        service: str, 
        voice: str, 
        split_at_subheadings: bool = False,
        instructions: str = "",
        use_ssml: bool = False
    ):
    """
    Convert markdown content to speech using a pluggable TTS service.

    Args:
        markdown_file: Markdown text content
        output_dir: Directory to save the audio files
        service: openai, google, or azure
        voice: Voice to use (OpenAI: alloy, echo, fable, onyx, nova, shimmer; 
          Google: en-US-Studio-O, en-US-Studio-Q;
          Azure: cora, adam, nancy, emma, jane, jason, davis, samuel)
        instructions: text string of instructions to include in call to OpenAI
        use_ssml: If True, convert chunks to SSML and send to service (currently available for Azure)

    Returns:
        List of lists of tuples:
        - Each nested list represents a section
        - Each tuple is as: (chunk_index, file_basename, output_filename)
    """
    sections = split_markdown_into_sections(markdown_content, split_at_subheadings)

    # Create the appropriate speech service
    if service == 'openai':
        speech_service = OpenAISpeechService(voice=voice, instructions=instructions)
    elif service == 'google':
        speech_service = GoogleSpeechService(voice_name=voice)
    elif service == 'azure':
        speech_service = AzureSpeechService(voice_name=voice)
    else:
        raise ValueError(f"Unsupported service '{service}'")

    output = []

    for section_ix, (title, content) in enumerate(sections):
        section_audio = []
        safe_title = re.sub(r'[^\w\s-]', '', title.lower())
        safe_title = re.sub(r'[\s]+', '_', safe_title)
        file_basename = f"{section_ix+1:02d}_{safe_title[:30]}"
        chunks = split_content_into_chunks(content)

        for chunk_ix, chunk in enumerate(chunks):
            print(f"Processing section {section_ix+1} (chunk {chunk_ix+1})...")
            filename = (
                f"{file_basename}.mp3" if len(chunks) == 1
                else f"{file_basename}_pt{chunk_ix:02d}.mp3"
            )
            output_path = os.path.join(output_dir, filename)

            if os.path.exists(output_path):
                print(f"Skipping existing file: {output_path}")
                continue

            audio_content = speech_service.synthesize_speech_from_text(chunk, output_path)

            with open(output_path, "wb") as f:
                f.write(audio_content)

            section_audio.append((chunk_ix, file_basename, output_path))

            time.sleep(1)

        output.append(section_audio)

    return output

def split_markdown_into_sections(markdown_content, split_at_subheadings=False):
    """
    Split markdown content into sections based on headings.

    Args:
        markdown_content: The markdown content

    Returns:
        list: List of tuples (section_title, section_content)
    """
    # Convert markdown to HTML
    html = markdown.markdown(markdown_content)
    soup = BeautifulSoup(html, 'html.parser')

    # Find heading elements
    if split_at_subheadings:
        headings = soup.find_all(['h1', 'h2'])
    else:
        headings = soup.find_all(['h1'])
    
    sections = []

    # If no headings, return the entire content as one section
    if not headings:
        return [("Content", markdown_content)]

    # Add content before the first heading as "Intro"
    intro_parts = []
    for element in soup.contents:
        if element == headings[0]:
            break
        if getattr(element, 'name', None) or isinstance(element, str):
            text = element.get_text() if hasattr(element, 'get_text') else str(element)
            if text.strip():
                intro_parts.append(text.strip() + "\n\n")
    if intro_parts:
        sections.append(("Intro", ''.join(intro_parts)))

    # Process each heading as a section
    for i, heading in enumerate(headings):
        title = heading.get_text()
        content_parts = []

        # Add the heading text first
        content_parts.append(f"{title}\n\n")

        # Get all content until the next heading
        element = heading.next_sibling
        while element and (i == len(headings) - 1 or element != headings[i + 1]):
            content_parts.append(element.get_text() + "\n\n")

            # Move to next element
            if hasattr(element, 'next_sibling'):
                element = element.next_sibling
            else:
                break

        content = ''.join(content_parts)
        sections.append((title, content))

    return sections


def split_content_into_chunks(content, max_chars=4096):
    """
    Chunk string of content to ensure we
    remain below character limit but retain all content.
    """
    sentences = content.split('. ')
    chunks = []
    current_chunk = ""

    for i, sentence in enumerate(sentences):
        # Reattach the ". " (unless it's the very last sentence)
        if i < len(sentences) - 1:
            sentence += ". "

        if len(current_chunk) + len(sentence) > max_chars:
            # Save the current chunk and start a new one
            chunks.append(current_chunk.strip())
            current_chunk = sentence
        else:
            current_chunk += sentence

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks