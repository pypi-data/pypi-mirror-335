
# Programmatically get all h1, h2

# GPT: Get the relevant headers / subheaders for the current text

# GPT: Give text + headers to gpt -> first reason (which text should go to which header (1) ) 


# For header(+headerparagraph) + full text: please add write paragraph with everything that is NEW to header text in found text
# Initialize the analyzer with the markdown string
from markdown_it import MarkdownIt
from markdown_it.token import Token

# Initialize the parser
md = MarkdownIt()

def get_headers(markdown_string):
    '''Returns headers as a hierarchical list like "1.3.2 Header text"'''
    
    tokens = md.parse(markdown_string)
    headers = []
    
    level_stack = []  # Stack to keep track of header numbering

    for token in tokens:
        if token.type == 'heading_open':
            level = int(token.tag[1])
            content = tokens[tokens.index(token) + 1].content

            # Adjust stack size to match current level
            while len(level_stack) < level:
                level_stack.append(0)
            while len(level_stack) > level:
                level_stack.pop()

            # Increment the last level's counter
            level_stack[-1] += 1

            # Generate the hierarchical numbering
            header_number = ".".join(map(str, level_stack))
            headers.append(f"{header_number} {content}")

    return headers


def get_text_under_header(markdown_string, target_header_identifier):
    """
    Given the markdown string and a target header identifier (e.g., "1 Header 1" or "2.1.1 Deeper Subheader 1"),
    returns all text directly under that header until the next header appears.
    This does NOT include text under any subheaders.
    """
    buffer = ''
    text_after_header = markdown_string.split(target_header_identifier, 1)[-1]

    for line in text_after_header.split('\n'):
        if line.strip().startswith('#'):
            break
        buffer += line + '\n'
    
    # Remove the last newline character
    buffer = buffer[:-2]

    print('text undr heade ', buffer)

    return buffer



def header_identifier_to_markdown(header_identifier):
    """
    Translates a hierarchical header identifier (e.g., "1.3.4 Header text")
    into a Markdown header with the corresponding number of '#' characters (e.g., "### Header text").
    """
    # Split the identifier into its numerical part and the header text.
    parts = header_identifier.split(' ', 1)
    if len(parts) < 2:
        # If the format is unexpected, return the original string.
        return header_identifier
    numbering, header_text = parts
    # Determine the header level by counting the number of numbers separated by dots.
    level = len(numbering.split('.'))
    return f"{'#' * level} {header_text}"

def get_markdown_header_from_number(markdown_string, number_identifier):
    """
    Given a markdown string and a number identifier (e.g., "1.4.5"),
    finds the header in the markdown that starts with that number and returns the Markdown header version.
    If the header is found, it returns the header in markdown format (e.g., "### Header text").
    """
    headers = get_headers(markdown_string)
    print(headers)
    for header in headers:
        # Check if the header starts with the given number identifier followed by a space.
        if header.startswith(number_identifier + " "):
            return header_identifier_to_markdown(header)
    return None


# Example usage:
if __name__ == '__main__':
    markdown_string = """
# Header 1
Paragraph under header 1.

## Header 1.1
Paragraph under header 1.1.
More text under header 1.1.

## Header 1.2
Paragraph under header 1.2.

# Header 2
Paragraph under header 2.
    """

    print("Headers:")
    for header in get_headers(markdown_string):
        print(header)

    print("\nContent under '1 Header 1':")
    print(get_text_under_header(markdown_string, "1 Header 1"))

    print("\nContent under '1.1 Header 1.1':")
    print(get_text_under_header(markdown_string, "1.1 Header 1.1"))

    print(header_identifier_to_markdown("1.3.4 Header text"))  # Should return "### Header text"

    print(get_markdown_header_from_number(markdown_string, "1.1"))  # Should return "## Header 1.1"