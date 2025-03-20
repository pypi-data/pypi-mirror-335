from archytas.tool_utils import tool
from typing import Callable, Any, TypedDict
from typing_extensions import Annotated, NotRequired
from functools import cache

from .utils import Logger, SimpleLogger, get_code, strip_quotes
from .uaii import (
    UAII, GeminiAgent, OpenAIAgent, ClaudeAgent,
    LLMConfig, GeminiConfig, GPTConfig, ClaudeConfig,
    GEMINI_DEFAULTS, GPT_DEFAULTS, CLAUDE_DEFAULTS,
    set_api_key, validate_config,
    gpt_4o, o3_mini,
    OpenAIMessage, OpenAIRole
)
from .curation import Example, examples_to_str

import pdb




# configuration for agents that the user passes in




class APISpec(TypedDict):
    name: Annotated[str, 'The name of the API']
    cache_key: NotRequired[Annotated[str, 'The key used to retrieve the cached API chat. If not provided, caching will be disabled. Note: only Gemini supports caching at the moment.']]
    description: Annotated[str, 'A description of the API']
    documentation: Annotated[str, "The raw extracted text of the API's documentation"]
    model_override: NotRequired[Annotated[LLMConfig, 'Explicit AI model to use for this API. If not provided, uses the normal model specified when creating the AdhocApi instance.']]
    examples: NotRequired[Annotated[list[Example], 'A list of use cases for the API solving various tasks. These will be favored over having the drafter write a new solution if they match well with the problem']]


def validate_api_spec(spec: APISpec):
    """
    Validate an API specification by checking if it has any keys it shouldn't.

    Args:
        spec (APISpec): The API specification to validate
    """
    allowed_keys = set(APISpec.__annotations__.keys())
    spec_keys = set(spec.keys())
    if not spec_keys.issubset(allowed_keys):
        truncates_spec = {**spec, 'documentation': '<documentation omitted>'}
        raise ValueError(f'Invalid keys {spec_keys - allowed_keys} for API spec {truncates_spec}')


def count_api_tokens_for_model(spec: APISpec, config: LLMConfig) -> tuple[int,int]:
    """
    Count how many tokens the given API spec takes up in the context window of the given model.

    Args:
        spec (APISpec): The API specification
        config (LLMConfig): The configuration for the model
        threshold (float, optional): The fraction of the context window that the API documentation should be less than. Defaults to 0.7.

    Returns:
        tuple[int,int]: The number of tokens in the API documentation and the context window size
    """
    if config['provider'] == 'google':
        model = GeminiAgent(model=config['model'], cache_key=None, system_prompt='', cache_content='', ttl_seconds=0)
    elif config['provider'] == 'openai':
        model = OpenAIAgent(model=config['model'], system_prompt='')
    elif config['provider'] == 'anthropic':
        model = ClaudeAgent(model=config['model'], cache=False, system_prompt='')
    else:
        raise ValueError(f'Unknown provider "{config["provider"]}"')

    return model.count_tokens(DRAFTER_SYSTEM_PROMPT + spec['documentation']), model.get_context_window_size()



def select_best_model_for_api(spec: APISpec, configs: list[LLMConfig], threshold: float=0.7) -> LLMConfig:
    """
    Select the first suitable model for an API from a list of models.
    If a model_override is provided by the API spec, that will be used without checking.

    Args:
        spec (APISpec): The API specification
        configs (list[LLMConfig]): A list of configurations for possible models
    """
    # if the user has explicitly specified a model for this API, use that
    if 'model_override' in spec:
        return spec['model_override']

    # find the first model that has a long enough context window for this API
    tries: dict[str, tuple[int, int]] = {}
    for config in configs:
        token_count, window_size = count_api_tokens_for_model(spec, config)
        if token_count < threshold * window_size:
            return config
        tries[config['model']] = (token_count, window_size)

    # error
    avg_token_count = int(sum(token_count for (token_count, _) in tries.values()) / len(tries))
    model_window_sizes = {model: f'{window_size:,} tokens' for model, (_, window_size) in tries.items()}
    min_window_size = int(avg_token_count / threshold)
    raise ValueError(f'No suitable model found for API "{spec["name"]}". Api length: ~{avg_token_count:,} tokens, while provided models support: {model_window_sizes}. Minimum window size (with {1-threshold:.0%} margin) is ~{min_window_size:,} tokens')

DRAFTER_SYSTEM_PROMPT = '''\
You are an assistant who is helping users to write code to interact with the {name} API.
You will be provided with the raw API documentation, and you have 2 jobs:
1. Answer questions about the API
2. Write code to perform specific tasks using the API

Each user query will include a keyword specifying which job to do: ASK_API for 1, and WRITE_CODE for 2.

When answering questions (ASK_API), please follow these rules:
- Answer in plain English
- Be concise and comprehensive
- Do not write large code blocks. If you need to provide code, keep it short and inline with the text of your response

When drafting code (WRITE_CODE), please follow these rules:
- Your output should be a single python code block. do not include any other comments or explanations in your response.
- Your code should directly solve the problem posed in the query and nothing more.
- The code should be ready to run directly as a python script.
- Assume `requests`, `numpy`, and `pandas` are installed, as well as any API specific libraries mentioned in the API documentation.
'''

from enum import Enum, auto
class QueryType(str, Enum):
    def _generate_next_value_(name, *_): return name # make enum use its name as the value
    ASK_API = auto()
    WRITE_CODE = auto()

def add_query_tag(query: str, type: QueryType) -> str:
    """
    Add the relevant tag to the start of a query so the drafter knows what type of action to take.
    
    Args:
        query (str): The query to make
        type (QueryType): The type of query to make. Currently support ASK_API and WRITE_CODE.
    """
    return f'{type}: {query}'

# def make_ask_api_query(query: str) -> str:
#     return f'ASK_API: {query}'

# def make_write_code_query(query: str) -> str:
#     return f'WRITE_CODE: {query}'

def add_examples_to_query(query: str, examples: list[Example]|None) -> str:
    if examples is None or len(examples) == 0:
        return query
    s = 's' if len(examples) > 1 else ''  # singular vs plural

    examples_str = examples_to_str(examples)

    return f'{query}\n\n(system note: The following example{s} were found that should relate strongly to the above task:\n\n{examples_str}\n)'

class AdhocApi:
    """
    Toolset for interacting with external APIs in an flexible manner. 
    These tools can be used to draft code that perform requests to APIs given some goal in plain English.
    Common usage is to first list APIs to determine which to use, then draft code to perform a specific task, then run the code.
    Note that each API maintains a separate chat history, so treat each API as a separate conversation.
    """
    def __init__(self, *,
        apis: list[APISpec],
        drafter_config: LLMConfig | list[LLMConfig],
        curator_config: LLMConfig | None = o3_mini,
        contextualizer_config: LLMConfig | None = gpt_4o,
        logger: Logger=SimpleLogger()
    ):
        """
        Create a new AdhocApi instance.

        Args:
            apis (list[APISpec]): A list of APIs available to the tool
            drafter_config (LLMConfig | list[LLMConfig]): The base configuration for the drafter agent.
                If a list is provided, for each API we will automatically pick the first model from the list
                that has a long enough context window for that API.
            curator_config (LLMConfig, optional): Optional configuration for the curator agent. If None, 
                will not include a curator step. Defaults to OpenAI's o3-mini.
            contextualizer_config (LLMConfig, optional): Optional configuration for a helper agent during the example
                curation step. Must be defined if a curator_config is provided. Defaults to OpenAI's gpt-4o.
            logger (Logger, optional): A logger to use for logging. Defaults to SimpleLogger.
        """
        # keep a list of all messages in/out of the tool (independent of possibly multiple drafter agents)
        self.all_messages: list[OpenAIMessage] = []
        
        self.apis: dict[str, tuple[APISpec, LLMConfig]] = {}
        self.logger = logger

        # validate the drafter configs and set the API keys
        if not isinstance(drafter_config, list): drafter_config = [drafter_config]
        for config in drafter_config:
            validate_config(config)
            set_api_key(config)
        
        # save the curator config if provided
        if curator_config is not None:
            validate_config(curator_config)
            set_api_key(curator_config)
        self.curator_config = curator_config

        # save the contextualizer config if provided
        if contextualizer_config is None and curator_config is not None:
            raise ValueError(f'contextualizer_config must be provided if curator_config is provided. Got {curator_config=} and {contextualizer_config=}')
        if contextualizer_config is not None:
            validate_config(contextualizer_config)
            set_api_key(contextualizer_config)
        self.contextualizer_config = contextualizer_config

        # validate the API specs and select the best model for each API
        for api in apis:
            validate_api_spec(api)
            config = select_best_model_for_api(api, drafter_config)
            self.apis[api['name']] = (api, config)
            self.logger.info({'api': api['name'], 'selected model': config['model']})
        
        # print warning if any APIs include examples, but no curator config is provided
        for api in apis:
            if 'examples' in api and len(api['examples']) > 0 and curator_config is None:
                self.logger.error(f'API {api["name"]} includes examples, but no curator config was provided. Examples will not be used.')


    def _get_api(self, api: str) -> tuple[APISpec, LLMConfig]:
        """
        Get the API and model specs for the given API.

        Args:
            api (str): The name of the API to get the specs for

        Returns:
            tuple[APISpec, LLMConfig]: The API and model specs
        """
        specs = self.apis.get(api)
        if specs is None:
            raise ValueError(f'API {api} not found. Please consult the list of available APIs: {[*self.apis.keys()]}')
        return specs

    @cache
    def _get_agent(self, api: str) -> UAII:
        """
        get the agent instance for the given API (make a new one if it doesn't exist)

        Args:
            api (str): The name of the API to get the agent for

        Returns:
            UAII: The agent instance
        """
        # @cache handles the case where the agent already exists

        # create a new agent if it doesn't exist
        api_spec, drafter_config = self._get_api(api)
        api_docs = api_spec['documentation']
        provider = drafter_config['provider']

        if provider == 'google':
            config: GeminiConfig = {**GEMINI_DEFAULTS, **drafter_config}
            return GeminiAgent(
                model=config['model'],
                cache_key=api_spec.get('cache_key', None),
                system_prompt=DRAFTER_SYSTEM_PROMPT.format(name=api),
                cache_content=api_docs,
                ttl_seconds=config['ttl_seconds'],
                logger=self.logger,
            )

        elif provider == 'openai':
            config: GPTConfig = {**GPT_DEFAULTS, **drafter_config}
            return OpenAIAgent(
                model=config['model'],
                system_prompt=DRAFTER_SYSTEM_PROMPT.format(name=api) + f'\n\n# API Documentation:\n{api_docs}',
            )

        elif provider == 'anthropic':
            config: ClaudeConfig = {**CLAUDE_DEFAULTS, **drafter_config}
            return ClaudeAgent(
                model=config['model'],
                cache=bool(api_spec.get('cache_key', None)),
                system_prompt=DRAFTER_SYSTEM_PROMPT + f'\n\n# API Documentation:\n{api_docs}',
            )

        else:
            raise ValueError(f'Unknown provider {provider}')

    def _get_oneshot_agent(self, config: LLMConfig) -> UAII:
        """
        get the agent instance for the given API (make a new one if it doesn't exist)

        Args:
            api (str): The name of the API to get the agent for

        Returns:
            UAII: The agent instance
        """
        # @cache handles the case where the agent already exists

        # create a new agent if it doesn't exist
        provider = config['provider']

        if provider == 'google':
            config: GeminiConfig = {**GEMINI_DEFAULTS, **config}
            return GeminiAgent(model=config['model'], cache_key=None, system_prompt='', cache_content='', ttl_seconds=0, logger=self.logger)
        elif provider == 'openai':
            config: GPTConfig = {**GPT_DEFAULTS, **config}
            return OpenAIAgent(model=config['model'])
        elif provider == 'anthropic':
            config: ClaudeConfig = {**CLAUDE_DEFAULTS, **config}
            return ClaudeAgent(model=config['model'])
        else:
            raise ValueError(f'Unknown provider {provider}')


    def _api_draft_helper(self, api: str, query: str, type: QueryType) -> str:
        """
        Helper method for sending requests to the drafter agent. Properly handles example curation

        Args:
            api (str): The name of the API this query is for
            query (str): The query to send to the drafter
            type (QueryType): The type of query to send
        """
        # get the agent
        drafter = self._get_agent(api)

        # look for examples that solve this task or are relevant to it
        examples = None
        if self.curator_config is not None:
            # collect any relevant context from the previous messages
            context_free_query = self._make_query_context_free(query)
            
            # filter 1000s of examples to smaller subset

            # short-circuit return early if an exact match is found
            perfect = self._find_perfect_example(api, context_free_query)
            if perfect is not None:
                # save this forced conversation chunk back into the drafter
                drafter.push_user_message(query)
                drafter.push_assistant_message(perfect)

                self.logger.info(f'Found perfect matching example for query "{query}":\n{perfect}')
                return perfect

            self.logger.info(f'No perfect matching example found for query "{query}".')

            # check if there are any good matches worth including as context for the drafter
            examples = self._find_relevant_examples(api, context_free_query)
            if examples is None or len(examples) == 0:
                self.logger.info(f'No relevant examples found for query "{query}".')
            else:
                self.logger.info(f'Found {len(examples)} relevant examples for query "{query}":\n{examples}' )

        # send the query to the drafter agent (for this API) and return the response
        query = add_query_tag(query, type)
        query = add_examples_to_query(query, examples)
        print(f'query being passed to drafter: "{query}"')
        res = drafter.message(query)

        return res
    


    def _make_query_context_free(self, query: str) -> str:
        """
        Make a user query completely self-contained, i.e. requiring no context from the surrounding conversation
        
        Args:
            query (str): The query to make context-free
        Returns:
            str: The context-free query
        """
        # get the agent
        if self.contextualizer_config is None:
            self.logger.error('No contextualizer config provided, so cannot make query context-free. Returning original query.')
            return query
        agent = self._get_oneshot_agent(self.contextualizer_config)

        # Make the query context free
        context_free_query = query
        if len(self.all_messages) > 0:
            system_query = f'Based on any relevant context from the prior conversation (particularly the user\'s messages), please convert the user\'s following query to one that is context free (i.e. it can be understood by itself without needing to reference the rest of the conversation). If no extra context is present in the prior conversation, then repeat the query verbatim. Do your best to phrase the context-free query the same way the user might have phrased it. Output only the original query verbatim or an updated context-free query, with no other comments or questions. The query is: "{query}"'
            context_free_query = agent.multishot([*self.all_messages, OpenAIMessage(role=OpenAIRole.system, content=system_query)])
            context_free_query = strip_quotes(context_free_query)
        
            self.logger.info(f'Made query context-free: "{query=}" -> "{context_free_query=}"')

        return context_free_query
    
    def _find_perfect_example(self, api: str, query: str) -> str | None:
        """
        Identify if the provided examples list for the given API contains a perfect match for the query.
        This step is skipped if self.curator_config is None.

        Args:
            api (str): The name of the API to check
            query (str): The query to check for a perfect match
        Returns:
            str | None: Either a response containing the perfect example that was found or None if no perfect match is found
        """
        # skip if no curator config is provided
        if self.curator_config is None:
            return None
        
        # Get the list of examples for the API (skip if none)
        api_spec, _ = self._get_api(api)
        examples = api_spec.get('examples', None)
        if examples is None or len(examples) == 0:
            return None
        

        # Have an agent check if any of the examples are a perfect match for the query
        curator = self._get_oneshot_agent(self.curator_config)
        examples_str = examples_to_str(examples, title_header='Solutions', example_header='Solution')
        prompt = f'''\
A user using the {api} API has asked the following question: "{query}".
The system might have some existing saved code solutions to this exact problem.
Please identify if any of the following existing solutions are a perfect match for the user's question.
"Perfect" in this context means the solution will return exactly what the user requested without ANY modifications.
Please ignore any solutions that are close, but not a perfect match. E.g. if any parameters are not exactly as requested, the solution is not perfect.
If a solution contains parameters the user doesn't mention, those may be ignored when determining if the solution is a perfect match.
If there are multiple perfect matches, please select an overall best one.
Your answer should be either the solution name (e.g. 'Solution 5') or 'None' if no perfect match is found.
Please do not output any other comments or text other than your answer.
Here are the existing solutions:

{examples_str}
'''
        response = curator.oneshot(prompt)
        response = response.strip().lower() 

        if response == 'none':
            return None
        
        if not response.startswith('solution'):
            self.logger.error(f'Unexpected response from curator identifying any perfect examples. expected either "None" or "Example X", but got "{response=}"')
            return None
        
        index_str = response.split('solution', 1)[1].strip()

        try:
            example_index = int(index_str) - 1
        except Exception as e:
            self.logger.error(f'Failed to parse solution index from curator response. Expected "Solution X", but got "{response=}"')
            return None

        if example_index < 0 or example_index >= len(examples):
            self.logger.error(f'Solution index {example_index} out of range for examples list of length {len(examples)}')
            return None

        # collect the perfect example and return it
        perfect = examples[example_index]

        if 'notes' not in perfect:
            return perfect['code'] 

        return f"# Solution\n## Notes\n{perfect['notes']}\n\n## Code\n```python\n{perfect['code']}\n```"

    
    def _find_relevant_examples(self, api: str, query: str) -> list[Example] | None:
        """
        Identify if the provided examples list for the given API contains any relevant examples for the query.
        This step is skipped if self.curator_config is None.

        Args:
            api (str): The name of the API to check
            query (str): The query to check for relevant examples
        Returns:
            list[Example] | None: Either a list of relevant examples or None
        """

        # skip if no curator config is provided
        if self.curator_config is None:
            return None

        # Get the list of examples for the API (skip if none)
        api_spec, _ = self._get_api(api)
        examples = api_spec.get('examples', None)
        if examples is None or len(examples) == 0:
            return None


        # Have an agent check if any of the examples are relevant to the query
        curator = self._get_oneshot_agent(self.curator_config)
        examples_str = examples_to_str(examples, title_header='Solutions', example_header='Solution')
        prompt = f'''\
A user using the {api} API has asked the following question: "{query}".
The system might have some existing saved code solutions that are relevant to this problem.
Please identify which if any of the following existing solutions are relevant to the user's question.
Your answer should be a comma-separated list of solution names (e.g. 'Solution 5, Solution 7'). 
If no examples are relevant, please output an empty string.
Please do not output any other comments or text other than your answer.
Here are the existing solutions:

{examples_str}
'''
        # get the agent response and parse it's answer
        response = curator.oneshot(prompt)
        response = response.strip().lower()
        if response == '':
            return None
        selections = response.split(',')
        selections = [selection.strip() for selection in selections]
        relevant_examples = []
        for selection in selections:
            if not selection.startswith('solution'):
                self.logger.error(f'Unexpected response from curator identifying relevant solutions. expected "Solution X", but got "{selection=}". Whole response: "{response=}"')
                return None
            index_str = selection.split('solution', 1)[1].strip()
            try:
                example_index = int(index_str) - 1
            except Exception as e:
                self.logger.error(f'Failed to parse solution index from curator response. Expected "Solution X", but got "{selection=}"')
                return None
            if example_index < 0 or example_index >= len(examples):
                self.logger.error(f'Solution index {example_index} out of range for examples list of length {len(examples)}')
                return None
            relevant_examples.append(examples[example_index])

        return relevant_examples
    
    
    
    @tool
    def list_apis(self) -> dict:
        """
        This tool lists all the APIs available to you.

        Returns:
            dict: A dict mapping from API names to their descriptions
        """
        return {
            name: {'description': api['description']}
            for name, (api, _) in self.apis.items()
        }

    @tool
    def ask_api(self, api: str, query: str) -> str:
        """
        Ask a question about the API to get more information.

        Args:
            api (str): The name of the API to ask about
            query (str): The question to ask

        Returns:
            str: The response to the query
        """
        # log the request
        self.logger.info({'api': api, 'ASK_API': query})
        
        # make the actual request
        res = self._api_draft_helper(api, query, QueryType.ASK_API)

        # update all messages with this transaction
        self.all_messages.append({'role': 'user', 'content': query})
        self.all_messages.append({'role': 'assistant', 'content': res})
        
        return res
        
    
    @tool
    def use_api(self, api: str, goal: str) -> str:
        """
        Draft python code for an API request given some goal in plain English.

        Args:
            api (str): The name of the API to use
            goal (str): The task to be performed by the API request (in plain English)

        Returns:
            str: The raw generated code to perform the task
        """
        # log the request
        self.logger.info({'api': api, 'WRITE_CODE': goal})

        # make the actual request
        res = self._api_draft_helper(api, goal, QueryType.WRITE_CODE)
        
        # strip off any markdown syntax
        code = get_code(res)

        # update all messages with this transaction
        self.all_messages.append({'role': 'user', 'content': goal})
        self.all_messages.append({'role': 'assistant', 'content': res})

        return code



# factory for making individual tools per API
# class AdhocApiFactory:
#     def __init__(self, api: APISpec, drafter_config: GeminiConfig | GPTConfig | ClaudeConfig):
#         self.api = api
#         self.drafter_config = drafter_config
#         self._set_api_key()




import subprocess
import tempfile
import os

class PythonTool:
    """Tool for running python code. If the user asks you to write code, you can run it here."""
    def __init__(self, sideeffect:Callable[[str, str, str, int], Any]=lambda x: None):
        """
        Set up a PythonTool instance.

        Args:
            sideeffect (Callable[[str], Any], optional): A side effect function to run when the tool is used. Defaults to do nothing.
        """
        self.sideeffect = sideeffect

    @tool
    def run(self, code: str) -> tuple[str, str, int]:
        """
        Runs python code in a python subprocess.

        The environment is not persistent between runs, so any variables created will not be available in subsequent runs.
        The only visible effects of this tool are from output to stdout/stderr. If you want to view a result, you MUST print it.

        Args:
            code (str): The code to run

        Returns:
            tuple: The stdout, stderr, and returncode from executing the code
        """

        # make a temporary file to run the code
        with tempfile.NamedTemporaryFile(suffix='.py', mode='w+') as f:
            f.write(code)
            f.flush()
            f.seek(0)

            # run the file in a separate Python process and capture the output
            try:
                result = subprocess.run(['python', f.name], capture_output=True, text=True, cwd=os.getcwd())
                stdout = result.stdout
                stderr = result.stderr or (f'No error output available. Process returned non-zero error code {result.returncode}' if result.returncode != 0 else '')
                returncode = result.returncode
            except Exception as e:
                stdout, stderr, returncode = "", str(e), 1
        
        # perform side effect
        self.sideeffect(code, stdout, stderr, returncode)


        return stdout, stderr, returncode


from .files import tree
from pathlib import Path

@tool
def view_filesystem(max_depth:int=-1, max_similar: int=25, ignore: list[str] = []) -> str:
    """
    View files and directories in the current working directory, displayed in a tree structure.

    Args:
        max_depth (int, optional): The maximum depth to traverse. Set to negative for infinite depth.
        max_similar (int, optional): The maximum number of similar files to display. When too many similar files are found, further matches will be elided. Defaults to 25.
        ignore (list, optional): List of unix filename pattern strings (e.g. '*.py', 'file?.txt', 'file[!a-c]*.txt', etc.) to skip including in output. Defaults to [].

    Returns:
        str: A string representation of the tree structure of the current working directory.
    """
    return tree(Path('.'), ignore=ignore, max_depth=max_depth, max_similar=max_similar)