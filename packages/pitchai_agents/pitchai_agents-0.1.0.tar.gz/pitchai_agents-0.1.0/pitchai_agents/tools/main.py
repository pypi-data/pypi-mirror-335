from agent.tools.read import read_file
from agent.tools.communicate import ask_developer_question
from agent.tools.web import google_search, read_document
from agent.completion import complete_analysis

def write_all_tools_to_globals(current_globals):
    '''Writes all the tools to the globals'''
    current_globals['read_document'] = read_document
    current_globals['google_search'] = google_search
    current_globals['read_file'] = read_file
    current_globals['complete_analysis'] = complete_analysis

    return current_globals