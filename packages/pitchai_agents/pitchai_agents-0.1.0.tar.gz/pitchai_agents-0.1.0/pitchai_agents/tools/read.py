
from markitdown import MarkItDown

md = MarkItDown() 

def read_file(file_path):
    '''Reads a file and returns the content'''
    with open(file_path, 'r') as file:
        content = file.read()

    print(content)
    return content
