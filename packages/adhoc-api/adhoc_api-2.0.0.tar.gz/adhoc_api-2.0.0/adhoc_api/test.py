from .uaii import ClaudeAgent, OpenAIAgent, UAII, LLMConfig, claude_37_sonnet, gpt_4o, gemini_pro
from .tool import AdhocApi, APISpec
from .loader import load_yaml_api, load_yaml_examples
from pathlib import Path
from easyrepl import REPL

import pdb

here = Path(__file__).parent

test_api: APISpec = {
    'name': 'test',
    'description': 'test',
    'documentation': '',
}

def instantiate_apis():
    drafter_config: LLMConfig = {'provider': 'anthropic', 'model': 'claude-3-7-sonnet-latest'}
    drafter_config: LLMConfig = {'provider': 'openai', 'model': 'o3-mini'}
    drafter_config: LLMConfig = {'provider': 'openai', 'model': 'o1-mini'}
    drafter_config: LLMConfig = {'provider': 'openai', 'model': 'o1'}

    api = AdhocApi(apis=[test_api], drafter_config=drafter_config)


def test_claude_37():
    agent = ClaudeAgent(model='claude-3-7-sonnet-latest', system_prompt='You are a helpful assistant.')
    repl_loop(agent)


def test_openai():
    agent = OpenAIAgent(model='gpt-4o', system_prompt=None)
    repl_loop(agent)


def repl_loop(agent:UAII):
    for query in REPL(history_file='.chat'):
        res = agent.message(query, stream=True)
        for i in res:
            print(i, end='', flush=True)
        print()



def test_api_with_examples():
    examples = load_yaml_examples(here / '../examples/gdc/examples.yaml')
    gdc_api = load_yaml_api(here / '../examples/gdc/api.yaml')
    pdb.set_trace()
# 
    drafter_config: LLMConfig = {'provider': 'openai', 'model': 'gpt-4o'}
    api = AdhocApi(apis=[gdc_api], drafter_config=drafter_config)
    ...

def test_yaml_loading():
    from .loader import load_interpolated_yaml
    # examples_path = here / '../examples/gdc/examples.yaml'
    # gdc_api = here / '../examples/gdc/api.yaml'
    test_path = here / '../examples/gdc/test.yaml'
    # test_path = here / '../examples/gdc/infinite.yaml'
    apple = load_interpolated_yaml(test_path)
    # print(y)
    pdb.set_trace()
    ...


def test_example_curation():
    drafter_config: LLMConfig = {'provider': 'google', 'model': 'gemini-1.5-flash-001'}
    api = load_yaml_api(here / '../examples/gdc/api.yaml')
    adhoc = AdhocApi(apis=[api], drafter_config=drafter_config)
    for query in REPL(history_file='.chat'):
        res = adhoc.use_api('Genomics Data Commons', query)
        print(res)
        print()
    

def test_example_curation_2():
    api = load_yaml_api(here / '../examples/cbioportal/api.yaml')
    adhoc = AdhocApi(apis=[api], drafter_config=claude_37_sonnet)
    for query in REPL(history_file='.chat'):
        res = adhoc.use_api('cbioportal', query)
        print(res)
        print()
    


if __name__ == '__main__':
    # test_claude_37()
    # test_openai()
    # instantiate_apis()
    # test_api_with_examples()
    # test_yaml_loading()
    test_example_curation_2()