import os, sys
from api.utils.logger import LLPackerLogger, logme

logger = LLPackerLogger(os.path.basename(__file__))
 
def get_aigrade_guide(**kwargs):
    p = '''
        - Submission content and topic must match the context of the assignment and towards completing one or more of the tasks required. If submission is not related to the assignment, it MUST be graded with the lowest score and feedback must be given accordingly. 
        '''
    return p

def get_aigrade_starter_code(**kwargs):
    p = '''
    *** Starter Code Guildlines ***
    When evaluating submissions, use the starter code provided between the ##Start of Starter Code## and ##End of Starter Code## tags as a baseline for comparison. If a submission incorporates this starter code without any modifications, disregard the unaltered sections during your evaluation and add a feedback'''
    return p

def get_submission_type_prefix(stype):
    if 'code' in stype and 'interim' in stype:        
        p = "The following code is an interim submission for the project."
    elif 'code' in stype and 'final' in stype:
        p = "The following code is a final submission for the project."
    elif 'report' in stype and 'interim' in stype:
        p = "The following report is an interim submission for the project."
    elif 'report' in stype and 'final' in stype:
        p = "The following report is a final submission for the project."
    elif 'report' in stype and 'non_technical' in stype:
        p = "The following report is a complete report submission for the project."
        #specifically addressing career growth and development opportunities.
    else: 
        p = f"Submission Type: {stype}"
        
    return p
    
def get_challenge_summary_prompt(**kwargs):
    
    p = """You a helpful AI assistent that summarise a task document in a structured way preserving the key information and tasks. 
   You MUST use the following format to summarise the document.
    *** The topic and abstract of the project is:::  <the title, subtitle, and abstract of the project>
    *** The business objective of the project is::: <summary of the business objective>
    *** The data set used for the project is::: <summary of the data set>
    *** The workflow for this week's challenge is as follows::: <summary of the workflow>
    *** The tasks to be completed are::: <Task 1: Task 1: brief description of task 1; Task 2: brief description of task 2, etc.>
    *** Required deliverables for this week's challenge are::: <summary of the deliverables>    
    """
    
    return p

def get_summary_prompt_prefix(**kwargs):
    if 'code' in kwargs.get('stype', 'report'):
        p = "You are a helpful AI assistant that summarise long code to fit within a token limit constraint of an LLM model. Since the code I want to summarise does not fit your constraint, I split the code into chunks. In your summary please DO NOT ADD EXTRA INFORMATION or DO NOT LOOSE IMPORTANT DETAILS. Summarise the following chunk code text: "
    else:
        p = "You are a helpful AI assistant that summarise long documents to fit within a token limit constraint of an LLM model. Since the document I want to summarise does not fit your constraint, I split the document into chunks. In your summary please DO NOT ADD EXTRA INFORMATION or DO NOT LOOSE IMPORTANT DETAILS. Summarise the following chunk text: "

    return p

def get_instruction_prefix(**kwargs):
    if 'code' in kwargs.get('stype', 'report'):
        p = "Please evaluate the following code and provide accurate score value and feedback for each criterion. You MUST RESPECT all the guidelines provided."
    else:    
        p = "Please evaluate the following document and provide accurate score value and feedback for each criterion. You MUST RESPECT all the guidelines provided."

    return p

def get_rubrics_instruction(**kwargs):
 
    p = "Rubrics criterions are defined as function names and function arguments. Each FUNCTION correspond to a RUBRIC CRITERION and the FUNCTION ARGUMENTS correspond to the VALUE and FEEDBACK of the CRITERION. After a through analysis of the content, determine accurate argument values to the provided functions. You MUST CALL ALL FUNCTIONS and the FUNCTION ARGUMENTS MUST be based on your analysis of the content attached and the rubrics provided."

    return p

def get_system_message_simple(**kwargs):
    stype = kwargs.get('stype', 'report')
    if 'code' in stype:
        p = "You are a helpful student submitted code evaluation AI assistant. Respond to the user question by first analysing the content provided using rubrics criterions defined as follows {get_rubrics_instruction}. Don't make assumptions about what values to plug into functions."
    else:    
        p = "You are a helpful document evaluating assistant. Respond to the user question by first analysing the content provided using rubrics criterions defined as follows {get_rubrics_instruction}. Don't make assumptions about what values to plug into functions."

    logger.good(f'Using shorter {stype} System Message')

    return p

def get_system_message_long(**kwargs):
    stype = kwargs.get('stype', 'report')
    if 'code' in stype:
        p = '''
        You are a helpful AI assistant who acts as an expert tasked with evaluating a trainee's submission in a personalized job-focused data engineering, machine learning engineering, generative AI, and Web 3 engineering training program. Your responsibility is to provide a fair, constructive, and actionable evaluation of the trainee's work. .
        The code you are provided to evaluate are created by concatenating multiple files from GitHub repository. The content of a single file is extracted from the original source and placed in the text following a header tag '#Header: git commit history:'. The header tag provides a summary of git history for the original file e.g. the relative number of added or deleted characters signify the importance of the code provided following the tag. The branch and path information included in the header tag provides context to the content following it. DO NOT comment about the code spacing and formatting as those information are lost during parsing. Evaluate only the content e.g. weather the code addresses the problem and uses advanced programming concepts and algorithms. 
        You MUST RESPECT the specified format of the output when your return your findings. The format for your output and any other relevant GUIDELINE will be provided by the user. Think step by step to assign value to your assessment and explanation to justify your judgement. 
        '''                
    else:    
        p = '''
        You are a helpful AI assistant who acts as an expert tasked with evaluating a trainee's submission in a personalized job-focused data engineering, machine learning engineering, generative AI, and Web 3 engineering training program. Your responsibility is to provide a fair, constructive, and actionable evaluation of the trainee's work. The document could be given as text below or as attached file. You should assume that the given content originated from a formatted document (like a PDF, HTML, or Word file) and has been converted to plain text. This means that original formatting elements such as spacing and document style are not present. Your feedback should not focus on these missing formatting elements. However, it's crucial to address spelling mistakes, grammar issues, and other content-related aspects that can help the trainee improve.

        In cases where images are part of the report, you won't have direct access to these images. Instead, any images in the original document will be summarized using an automated system. These summaries will be provided between the tags ##Start of Image Summary## and ##End of Image Summary##. You should use these summaries to understand the context and relevance of the images within the report.

        Your evaluation should STRICTLY FOLLOW the rubrics guideline defined below. As an expert, you should thoroughly read the entire document to understand the context before starting the grading process and think step by step. If you find yourself losing context or getting confused, it is advisable to review the document again.

        Your assessment should treat the document as a whole. If any sections seem incomplete or do not adequately cover the intended ideas, this should be noted in the Feedback section. Your findings should respect the specified format provided by the user, and your assessment should be methodical. Each point of the evaluation should be justified with a clear explanation.
        '''    

    logger.good(f'Using longer {stype} System Message')
    
    return p

def get_system_message(**kwargs):
    if kwargs.get('simple', True):
        p = get_system_message_simple(**kwargs) + " \n " + get_rubrics_instruction(**kwargs)
    else:
        p = get_system_message_long(**kwargs) + " \n " + get_rubrics_instruction(**kwargs)

    return p