from src.agent.planning.prompts.code_action_prompt import generate_tool_description


def test_generate_tool_description_basic():
    def sample_function(arg1: str, arg2: int) -> str:
        """This is a sample function."""
        pass

    result = generate_tool_description([sample_function])
    expected = (
        "[1] sample_function: This is a sample function.\n"
        "Arguments: arg1, arg2.\n"
        "Signature: sample_function(arg1, arg2) -> str"
    )
    assert result == expected


def test_generate_tool_description_no_args():
    def no_args_function() -> bool:
        """Function with no arguments."""
        pass

    result = generate_tool_description([no_args_function])
    expected = "[1] no_args_function: Function with no arguments.\n" "Signature: no_args_function(no arguments) -> bool"
    assert result == expected


def test_generate_tool_description_no_return_annotation():
    def no_return_type(arg1: str):
        """Function without return type annotation."""
        pass

    result = generate_tool_description([no_return_type])
    expected = (
        "[1] no_return_type: Function without return type annotation.\n"
        "Arguments: arg1.\n"
        "Signature: no_return_type(arg1) -> Any"
    )
    assert result == expected


def test_generate_tool_description_multiple_functions():
    def func1(x: int) -> int:
        """First function."""
        pass

    def func2(y: str) -> str:
        """Second function."""
        pass

    result = generate_tool_description([func1, func2])
    expected = (
        "[1] func1: First function.\n"
        "Arguments: x.\n"
        "Signature: func1(x) -> int\n\n"
        "[2] func2: Second function.\n"
        "Arguments: y.\n"
        "Signature: func2(y) -> str"
    )
    assert result == expected


def test_generate_tool_description_empty_list():
    result = generate_tool_description([])
    assert result == ""


def test_generate_tool_description_no_docstring():
    def no_doc(x: int) -> int:
        pass

    result = generate_tool_description([no_doc])
    expected = "[1] no_doc: None\n" "Arguments: x.\n" "Signature: no_doc(x) -> int"
    assert result == expected


def test_generate_tool_description_with_implementation():
    def implemented_function(x: int, y: int) -> int:
        """Adds two numbers together."""
        return x + y

    result = generate_tool_description([implemented_function])
    expected = (
        "[1] implemented_function: Adds two numbers together.\n"
        "Arguments: x, y.\n"
        "Signature: implemented_function(x, y) -> int"
    )
    assert result == expected
