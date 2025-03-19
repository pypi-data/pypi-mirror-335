from code_ops.aexec import async_execute_catch_logs_errors
from code_ops.splitoff import try_splitoff_code_w_fallbacks
from code_ops.modify_string import check_for_forbidden_definitions
from utils.string_shortening import cutoff_str, shorten_all_strings_in_dict
from agent.history import summarize_history
from agent.tools.web import read_document, google_search
from agent.completion import complete_analysis
from agent.max_step import time_almost_up_warning
from agent.report.update_report import update_report
from chat.ui_msg_actions import UIMsgActions
from utils.string_shortening import cutoff_str
from uuid import uuid4
import asyncio
import logging
from rich.console import Console

logger = logging.getLogger(__name__)


console = Console()


async def run_agent(global_goal: str, max_steps: int = 6, min_steps=6,  conversation_id: str = '', msg_actions: UIMsgActions = None, agent_id:str = '', headless=True, communication_callback=None):
    current_history = []
    # Initialize empty globals, but provide the request_user_input function
    current_globals = {}

    if not msg_actions:
        msg_actions = await UIMsgActions.create(conversation_id=conversation_id, headless=headless)


    step_idx = 0
    while True:
        # Make sure that the functions are not overwritten in the globals (or that they are set)
        current_globals['complete_analysis'] = complete_analysis
        current_globals['read_document'] = read_document
        current_globals['google_search'] = google_search

        summarized_history: str = await summarize_history(global_goal, current_history, num_medium_summarized=7, num_unsummarized_final=3, agent_id=agent_id)

        # TIME UP 
        global_goal += time_almost_up_warning(step_idx, max_steps)
        if step_idx > max_steps + 1:
            return response

        # ACTION
        response = await msg_actions.run_action(action_id=f'agent_{uuid4().hex}', prompt_path='webstep', prompt_format_kwargs={'goal': global_goal, 'history': summarized_history, 'globals': shorten_all_strings_in_dict(current_globals)}, model='gemini-2.0-flash')
        
        # CODE STR PREPROCESSING
        code_str = try_splitoff_code_w_fallbacks(response, ['```python', '```tool_code'], '```')
        non_code_response = response.replace(code_str, '')

        if communication_callback:
            await communication_callback(f"-# Agent: {agent_id}\n## Step: {step_idx}\n\n **Thought:** {non_code_response}")

        
        
        # EXECUTION
        # if ('await read_document' in code_str or 'google' in code_str) and not 'print' in code_str:
        #     logs  = 'Warning: You are not printing the reading of the document, that makes no sense because then you ar enot actually reading and integrating the information'
        else:
            current_globals, logs = await async_execute_catch_logs_errors(code_str, current_globals)
            current_globals.pop('__builtins__', None)

            logs = cutoff_str(logs, max_words=20000)

            # if logs:
            #     await update_report(f"{non_code_response}\n\n\n{logs}", global_goal)

        # LOGS
        console.log(cutoff_str(logs, max_words=200), style='blue')
        
        # SAVE
        current_step_result_dict = {'thought': non_code_response, 'code': code_str, 'logs': logs, 'result': shorten_all_strings_in_dict(current_globals)}
        current_history.append(current_step_result_dict)

        # Check if the process should be stopped
        if 'complete_analysis(' in response:
            if step_idx < min_steps:
                logs += f"Minimum number of steps not reached. You need to take at least {min_steps} steps. You have taken {step_idx}. You need to research much deeper and much less superficially. You need to take more steps and go deeper into the analysis."
            else:
                response = f"Last step before completing analysis was:\n{current_history[-1]}\n\n\nFinal result of the analysis was:\n{current_step_result_dict}"
                return response
      

        step_idx += 1

        


if __name__ == '__main__':
    from rich.logging import RichHandler

    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )

    logging.getLogger('prompt_loader').setLevel(logging.ERROR)
    logging.getLogger('afasask.gpt.prompt_loader').setLevel(logging.ERROR)
    logging.getLogger('ui_msg_actions').setLevel(logging.ERROR)
    logging.getLogger('afasask.chat.ui_msg_actions').setLevel(logging.ERROR)
    logging.getLogger('msg_manager').setLevel(logging.ERROR)
    logging.getLogger('afasask.chat.msg_manager').setLevel(logging.ERROR)
    logging.getLogger('_client').setLevel(logging.ERROR)
    logging.getLogger('openai').setLevel(logging.ERROR)
    logging.getLogger('httpx').setLevel(logging.ERROR)
    
    # goal ="I am wondering what is the best way for a Belgian company owner to buy a car. Most tax optimal. My budget is 15.000 euro's. Within 2 years we'll move to the Netherlands so we probably can't take the car then. We'll private use it at least 60% of the time. Do some deep research, investigating some subfacts and making some calculations. This means that we either have to sell or import the car to the Netherlands in 2 years. What is the cheapest option? What about buying vs leasing? Also considering what we would get when we sell it. As you can see many possible configuratins and options. Electric seems most dedictable but new or second hand? New has higher depreciation. What is tax optimal? Research deeply."
    # goal = "What is the scientifically proven (cite many papers) best way to prioritize things and focus and time manage when you have your own AI service consultancy business building custom solutions. Really go in eep research, not easily being content"
    # goal = "Compare the prices of many many image search solutions (we have about 1000000 titles for which we need images) and list the cheapest. Deeply research. This may be unoffical serp apis, check the pricing of many providers to find the cheapest for this amount of titles. We can limit ourselves to 10000 a day, that would be acceptable. Quality does not matter. We just have 100000 queries and want to find the first iamge search result for them. This is image search, not image reverse search."

    # goal = '''There MUST be some way to get structured output data by specifying command line options for pytest. Deeply search for it. Specifically we want the names of the failed tests and the stacktraces/errors that they gave.'''

    # goal = '''We are building an AI as data-analyst solution for AFAS, allowing company wide strategic decisions based on natural language questions to your AI data-analyst who makes an analysis based on your AFAS database. Of course if we can get into contact with the AFAS mother organization they can offer the data-analyst to their clients and make profit and it will be  areal growth engine. Deeply research and find out how we can get in contact. Is the CEO at certain locations, places, or the executives? At which 'beurzen' are they? We already know this: "This page contains direct contact information for  
    #                 Martijn Delahaye (Directeur Marketing & Communicatie AFAS Nederland, martijn.delahaye@afas.nl, 06 51 84 91 10) and Esmee Bryon (Marketing medewerker AFAS België,                               
    #                 esmee.bryon@afas.be, +32 15 28 19 10). It also mentions Herman Zondag (Directeur Customer Experience, 06-51849356) for interview requests, questions about events or AFAS Theater               
    #                 and redirects to AFAS.nl/contact for general inquiries. Finally, it mentions that AFAS works with persbureau Hibou.   
    #                 including an address (Inspiratielaan 3, 3833 AV Leusden), phone number (033-434 3884), a WhatsApp number (+31 6 1332084157), and email addresses (events@afas.nl for               
    #                 business inquiries, klacht@afastheater.nl for complaints). It also links to the AFAS.nl/pers page for media inquiries and provides a contact form.                                              
                                                                                                                                                                                                                    
    #                 I've also gathered information on key executives (Bas van der Veldt, Rico Hein, Willem van den Born, and Melanie Blom), AFAS-sponsored locations, and events. I tried exploring                 
    #                 the "Bas bij jou" page, but it timed out.                                                                                                                                                       
                                                                                                                                                                                                                    
    #                 Based on the information gathered, it appears we have enough information to contact AFAS and identify key personnel. The next logical step is to investigate the AFAS.nl/pers                   
    #                 page for media contacts, as that might provide direct email addresses for communication. I'll also use the general contact form for inquiries, as it has been identified.                                                                            
                                                                                                                                                                                                                    
    #                 We have successfully gathered contact information for key people in marketing, communications and customer experience. We also have a general contact number and email available.               
    #                 We also know the names of other executives like Rico Hein, Willem van den Born, Melanie Blom, and Britt Breure. The CEO, Bas van der Veldt, can be reached through a request                    
    #                 form."
                    
    #                 So now the goal is to see where you can normally find and meet these people, hobbies, etc. To which beurzen might they go? What are smart ways to get into natural contact with them? Do some depe research.'''

    goal = """We are an AI consultancy/service company specializing in GenAI such as agents, chatbots, reports writers, AI as data-analyst, deep research AI, report readers. We'll have a call with encon.eu a sustainability consultant. They know us already and it will be a short exploratory call to explore their needs. What are their needs? What questions should be asked? What are their services and how do AI-workers/genAI/AI agents speed this up? They were busy deivsing a digitalizaiton strategy a few months ago. How to engage with that? We want to go towards a personal demo and then a business demo but what might a sustainibility consultant need when they advise on buildings, subsidies certifications and anything sustainability? Make sure ot do some deep research on their websites, collecting information and studying their case studies, target, group, value propositions, etc."""

    goal = '''What is all current news about the Dutch and NW EU fry potato market in terms of contracttteelt. Normally contractteelt contracts are published around the start of the year. What were the contract prices this year?'''
    asyncio.run(run_agent(max_steps=50, min_steps=6, global_goal=goal))
