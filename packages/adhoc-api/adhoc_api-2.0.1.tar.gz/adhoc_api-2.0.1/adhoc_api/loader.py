from pathlib import Path
import yaml
from yaml.nodes import ScalarNode
from yaml.loader import SafeLoader
from json import loads as json_loads

from .tool import APISpec
from .curation import Example, validate_example

import pdb

# type representing possible values that can be loaded from yaml/json files
SerialValue = dict|list|str|int|float|bool|None

class Interpolate(str):
    """Marker class for any string content in a yaml to indicate that it should be interpolated."""

class YAMLFileLoader(SafeLoader):
    """Custom YAML loader with support for various tags for conveniently loading file contents."""
    _loaded_yamls: dict[Path, SerialValue|None] = {}  # Track files being loaded to prevent circular references
    
    def __init__(self, stream):
        super().__init__(stream)
        # Store the yaml file's directory for relative paths
        self._yaml_dir = Path(stream.name).parent if hasattr(stream, 'name') else Path.cwd()
        self._yaml_file = Path(stream.name) if hasattr(stream, 'name') else None

    def load_file_content(self, node: ScalarNode) -> str:
        """Load content from a file specified in a !load tag."""
        path = Path(self.construct_scalar(node))
        full_path = self._yaml_dir / path
        
        if not full_path.exists():
            raise FileNotFoundError(f"!load_txt failed in {self._yaml_file.relative_to(self._yaml_dir)}  File not found: {full_path.relative_to(self._yaml_dir)}")
            
        return full_path.read_text(encoding='utf-8')
    
    def load_interp_string(self, node: ScalarNode) -> Interpolate:
        """Load a string with the !fill tag and mark it for interpolation"""
        return Interpolate(self.construct_scalar(node))

    def load_yaml_content(self, node: ScalarNode) -> SerialValue:
        """Load content from a file specified in a !load_yaml tag as parsed YAML."""
        path = Path(self.construct_scalar(node))
        full_path = self._yaml_dir / path

        # Check/mark for circular references
        if full_path in self._loaded_yamls and self._loaded_yamls[full_path] is None:
            raise RecursionError(f'Circular reference detected: Cannot load {full_path.relative_to(self._yaml_dir)} from {self._yaml_file.relative_to(self._yaml_dir)}')
        if full_path in self._loaded_yamls:
            return self._loaded_yamls[full_path]
        self._loaded_yamls[full_path] = None # indicates in the process of loading

        if not full_path.exists():
            raise FileNotFoundError(f"!load_yaml failed in {self._yaml_file.relative_to(self._yaml_dir)}. File not found: {full_path.relative_to(self._yaml_dir)}")
        
        # perform any interpolation of this sub file
        data = load_interpolated_yaml(full_path)

        # save the loaded data so it can be reused
        self._loaded_yamls[full_path] = data # indicates loaded successfully

        return data


    def load_json_content(self, node: ScalarNode) -> SerialValue:
        """Load content from a file specified in a !load_json tag as parsed JSON."""
        path = Path(self.construct_scalar(node))
        full_path = self._yaml_dir / path

        if not full_path.exists():
            raise FileNotFoundError(f"!load_json failed in {self._yaml_file.relative_to(self._yaml_dir)}. File not found: {full_path.relative_to(self._yaml_dir)}")
        
        return json_loads(full_path.read_text(encoding='utf-8'))

# Register the loading and interpolation tags
YAMLFileLoader.add_constructor('!load_txt', YAMLFileLoader.load_file_content)
YAMLFileLoader.add_constructor('!load_yaml', YAMLFileLoader.load_yaml_content)
YAMLFileLoader.add_constructor('!load_json', YAMLFileLoader.load_json_content)
YAMLFileLoader.add_constructor('!fill', YAMLFileLoader.load_interp_string)


def interpolate_strings(data: SerialValue|Interpolate, context: dict) -> SerialValue:
    """Recursively interpolate strings in the data structure using the context."""
    
    # recurse into dicts and lists
    if isinstance(data, dict):
        return {k: interpolate_strings(v, context) for k, v in data.items()}
    elif isinstance(data, list):
        return [interpolate_strings(item, context) for item in data]
    
    # strings that are marked Interpolate are interpolated
    elif isinstance(data, Interpolate):
        try:
            return data.format_map(context)
        except (KeyError, ValueError):
            # Return original string if interpolation fails. issue a warning.
            # TODO: integrate this into the logger
            print(f"Warning: Failed to interpolate string: {data}")
            return str(data)
    
    # everything else is returned as is
    return data



def load_interpolated_yaml(path: Path) -> dict:
    """
    Load a YAML file, replace !load tags, and perform string interpolation.
    For example, say I have the following text file:
    
    ```text
    This is the content of template.txt
    ```
    
    And the following yaml file:
    ```yaml
    name: my_api
    description: This is {name}
    template: !load template.txt
    message: | 
      This uses loaded content: {template}
    ```

    Loading this yaml file will result in the following dictionary:
    ```python
    {
        'name': 'my_api',
        'description': 'This is my_api',
        'template': 'This is the content of template.txt',
        'message': 'This uses loaded content: This is the content of template.txt'
    }
    ```
    """    
    with path.open(encoding='utf-8') as f:
        data = yaml.load(f, YAMLFileLoader)
    
    return interpolate_strings(data, data)




def load_yaml_api(path: Path) -> APISpec:
    """
    Load an API definition from a YAML file.
    API files should have the following structure:
        ```yaml
        name: <name>
        cache_key: <cache_key> # Optional - if not provided, caching will be disabled
        description: <description>
        documentation: <documentation>
        model_override: # Optional - if not provided, uses the model specified when creating the AdhocApi instance.
            provider: <provider>
            model: <model>
        ```
    
    Additionally, content from a file can be automatically loaded via the !load tag:
    ```yaml
    name: some_api
    description: some description of the API
    documentation: !load documentation.md
    ```
    This will load the contents of `documentation.md` and insert is under the `documentation` field.

    Lastly, you can interpolate values from the yaml in the string. For example:
    ```yaml
    name: some_api
    description: some description of the API
    documentation: |
        This API is called '{name}'
        Also, we can interpolate content from files.
        for example, {loaded_from_a_file}
    loaded_from_a_file: !load some_file.txt
    ```
    The `{name}` field in documentation will be replaced with the value of `name` in the yaml file.
    The `{some_extra_field}` field will be replaced with the contents of `some_file.txt`,
    which is then interpolated into the `documentation` field.

    Note: extra fields in the yaml file will not be included in the APISpec.
    This may be useful for collecting content from files or interoperating with other sources.

    Args:
        path (Path): The path to the YAML file containing the API definition.

    Returns:
        APISpec: The API definition.
    """
    raw_spec = load_interpolated_yaml(path)
    # collect only the fields that are relevant for APISpec
    spec = {k: v for k, v in raw_spec.items() if k in APISpec.__annotations__}
    
    # validate that the required fields are present
    # TODO: would be nice if validation could be more automated based on the APISpec class
    required_fields = {'name', 'description', 'documentation'}
    missing_fields = required_fields - set(spec.keys())
    if missing_fields:
        raise ValueError(f"API definition is missing required fields: {missing_fields}")
    
    # create the APISpec
    return APISpec(**spec)



def load_multiple_apis(path: Path) -> list[APISpec]:
    """TBD what format would be best for multiple APIs"""
    raise NotImplementedError("Loading multiple APIs from a single yaml is not implemented yet.")


def load_yaml_examples(path: Path) -> list[Example]:
    """
    Load examples from a YAML file.
    Example files should have the following structure:
    ```yaml
    - query: <query>
      code: <code>
      notes: <notes> # Optional
    - query: <query>
      code: <code>
      notes: <notes> # Optional
    ```

    Args:
        path (Path): The path to the YAML file containing the examples.

    Returns:
        list[Example]: A list of Example objects.
    """
    with path.open(encoding='utf-8') as f:
        data = yaml.load(f, SafeLoader)

    # type validation
    if not isinstance(data, list):
        raise ValueError(f"Expected a list of examples in {path}, but got {type(data)}")
    for example in data:
        validate_example(example)

    return data


if __name__ == '__main__':
    here = Path(__file__).parent
    # path = here / '../examples/gdc/api.yaml'
    # # res = load_interpolated_yaml(path)
    # api = load_yaml_api(path)
    # pdb.set_trace()
    ...
    path = here / '../examples/gdc/examples.yaml'
    examples = load_yaml_examples(path)
    pdb.set_trace()
    ...