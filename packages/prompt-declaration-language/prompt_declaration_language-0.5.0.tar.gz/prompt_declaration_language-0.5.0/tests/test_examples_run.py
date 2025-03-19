import io
import pathlib
import random
from dataclasses import dataclass
from typing import Optional

from pytest import CaptureFixture, MonkeyPatch

from pdl import pdl
from pdl.pdl_ast import ScopeType
from pdl.pdl_dumper import block_to_dict
from pdl.pdl_lazy import PdlDict
from pdl.pdl_parser import PDLParseError

# test_examples_run.py runs the examples and compares the results
# to the expected results in tests/results/examples

UPDATE_RESULTS = False
RESULTS_VERSION = 15

TO_SKIP = {
    str(name)
    for name in [
        pathlib.Path("examples")
        / "hello"
        / "hello-structured-decoding.pdl",  # TODO: check why
        pathlib.Path("examples") / "demo" / "2-teacher.pdl",  # TODO: check why
        pathlib.Path("examples") / "talk" / "8-tools.pdl",  # TODO: check why
        pathlib.Path("examples") / "talk" / "10-sdg.pdl",  # TODO: check why
        pathlib.Path("examples") / "teacher" / "teacher.pdl",  # TODO: check why
        pathlib.Path("examples") / "tools" / "calc.pdl",  # TODO: check why
        pathlib.Path("examples") / "tutorial" / "calling_apis.pdl",
        pathlib.Path("examples") / "cldk" / "cldk-assistant.pdl",
        pathlib.Path("examples") / "talk" / "10-multi-agent.pdl",
        pathlib.Path("examples") / "gsm8k" / "gsmhard-bugs.pdl",
        pathlib.Path("examples") / "gsm8k" / "math-base.pdl",
        pathlib.Path("examples") / "gsm8k" / "math-jinja.pdl",
        pathlib.Path("examples") / "gsm8k" / "math-python.pdl",
        pathlib.Path("examples") / "gsm8k" / "math.pdl",
        pathlib.Path("examples") / "gsm8k" / "gsm8.pdl",  # TODO: check why
        pathlib.Path("examples") / "tfidf_rag" / "rag.pdl",
        pathlib.Path("examples") / "react" / "react_call.pdl",
        pathlib.Path("examples") / "callback" / "repair_prompt.pdl",
        pathlib.Path("examples") / "gsm8k" / "math.pdl",
        pathlib.Path("examples") / "gsm8k" / "math_no_sd.pdl",
        pathlib.Path("examples") / "react" / "demo.pdl",  # TODO: check why
        pathlib.Path("examples") / "talk" / "9-react.pdl",  # TODO: check why
        pathlib.Path("examples") / "demo" / "4-translator.pdl",  # TODO check why
        pathlib.Path("examples")
        / "tutorial"
        / "calling_llm_with_input_messages.pdl",  # TODO check why
        pathlib.Path("examples")
        / "tutorial"
        / "muting_block_output.pdl",  # TODO check why
        pathlib.Path("examples") / "tutorial" / "calling_code.pdl",  # TODO check why
        pathlib.Path("examples") / "tutorial" / "calling_llm.pdl",  # TODO check why
        pathlib.Path("examples")
        / "tutorial"
        / "variable_def_use.pdl",  # TODO check why
        pathlib.Path("examples") / "tutorial" / "model_chaining.pdl",  # TODO check why
        pathlib.Path("examples")
        / "tutorial"
        / "function_definition.pdl",  # TODO check why
        pathlib.Path("examples")
        / "tutorial"
        / "calling_llm_with_input.pdl",  # TODO check why
        pathlib.Path("examples")
        / "tutorial"
        / "conditionals_loops.pdl",  # TODO check why
        pathlib.Path("examples")
        / "tutorial"
        / "grouping_definitions.pdl",  # TODO check why
        pathlib.Path("examples")
        / "granite"
        / "single_round_chat.pdl",  # TODO check why
        pathlib.Path("examples") / "chatbot" / "chatbot.pdl",  # TODO check why
        pathlib.Path("examples") / "fibonacci" / "fib.pdl",  # TODO check why
        pathlib.Path("examples")
        / "intrinsics"
        / "demo-hallucination.pdl",  # TODO check why
        pathlib.Path("examples")
        / "hello"
        / "hello-function-empty-context.pdl",  # TODO CREATE RESULTS FILE
        pathlib.Path("examples") / "hello" / "hello-roles-array.pdl",  # TODO check why
        pathlib.Path("examples") / "hello" / "hello-import.pdl",  # TODO check why
        pathlib.Path("examples")
        / "hello"
        / "hello-import-lib.pdl",  # (Produces no output)
        pathlib.Path("examples")
        / "hello"
        / "hello-model-chaining.pdl",  # TODO check why
        pathlib.Path("examples") / "talk" / "7-chatbot-roles.pdl",  # TODO check why
        pathlib.Path("examples")
        / "rag"
        / "pdf_index.pdl",  # TODO: check what the expected output is
        pathlib.Path("examples")
        / "rag"
        / "pdf_query.pdl",  # TODO: check what the expected output is
        pathlib.Path("examples")
        / "rag"
        / "rag_library1.pdl",  # (This is glue to Python, it doesn't "run" alone)
        pathlib.Path("examples")
        / "rag"
        / "tfidf_rag.pdl",  # TODO: check what the expected output is
        pathlib.Path("pdl-live-react") / "demos" / "error.pdl",
        pathlib.Path("pdl-live-react") / "demos" / "demo1.pdl",
        pathlib.Path("pdl-live-react") / "demos" / "demo2.pdl",
        # For now, skip the granite-io examples
        pathlib.Path("examples") / "granite-io" / "granite_io_hallucinations.pdl",
        pathlib.Path("examples") / "granite-io" / "granite_io_openai.pdl",
        pathlib.Path("examples") / "granite-io" / "granite_io_thinking.pdl",
        pathlib.Path("examples") / "granite-io" / "granite_io_transformers.pdl",
        pathlib.Path("examples") / "hello" / "hello-graniteio.pdl",
    ]
}

NOT_DETERMINISTIC = {
    str(name)
    for name in [
        pathlib.Path("examples") / "weather" / "weather.pdl",
        pathlib.Path("examples") / "demo" / "3-weather.pdl",
        pathlib.Path("examples") / "granite" / "multi_round_chat.pdl",
        pathlib.Path("examples") / "react" / "demo.pdl",
        pathlib.Path("examples") / "react" / "wikipedia.pdl",
        pathlib.Path("examples") / "code" / "code.pdl",
        pathlib.Path("examples") / "code" / "code-eval.pdl",
        pathlib.Path("examples") / "code" / "code-json.pdl",
        pathlib.Path("examples") / "talk" / "1-hello.pdl",
        pathlib.Path("examples") / "talk" / "2-model-chaining.pdl",
        pathlib.Path("examples") / "talk" / "3-def-use.pdl",
        pathlib.Path("examples") / "talk" / "5-code-eval.pdl",
        pathlib.Path("examples") / "talk" / "6-code-json.pdl",
        pathlib.Path("examples") / "talk" / "9-react.pdl",
        pathlib.Path("examples") / "tutorial" / "include.pdl",
        pathlib.Path("examples") / "tutorial" / "data_block.pdl",
        pathlib.Path("examples") / "sdk" / "hello.pdl",
        pathlib.Path("examples") / "hello" / "hello.pdl",
        pathlib.Path("examples") / "hello" / "hello-model-input.pdl",
        pathlib.Path("examples") / "hello" / "hello-parser-regex.pdl",
        pathlib.Path("examples") / "hello" / "hello-def-use.pdl",
    ]
}


@dataclass
class InputsType:
    stdin: Optional[str] = None
    scope: Optional[ScopeType] = None


TESTS_WITH_INPUT: dict[str, InputsType] = {
    str(name): inputs
    for name, inputs in {
        pathlib.Path("examples")
        / "demo"
        / "4-translator.pdl": InputsType(stdin="french\nstop\n"),
        pathlib.Path("examples")
        / "tutorial"
        / "input_stdin.pdl": InputsType(stdin="Hello\n"),
        pathlib.Path("examples")
        / "tutorial"
        / "input_stdin_multiline.pdl": InputsType(stdin="Hello\nBye\n"),
        pathlib.Path("examples")
        / "input"
        / "input_test1.pdl": InputsType(stdin="Hello\n"),
        pathlib.Path("examples")
        / "input"
        / "input_test2.pdl": InputsType(stdin="Hello\n"),
        pathlib.Path("examples")
        / "chatbot"
        / "chatbot.pdl": InputsType(stdin="What is APR?\nyes\n"),
        pathlib.Path("examples")
        / "talk"
        / "7-chatbot-roles.pdl": InputsType(stdin="What is APR?\nquit\n"),
        pathlib.Path("examples")
        / "granite"
        / "single_round_chat.pdl": InputsType(
            scope=PdlDict({"PROMPT": "What is APR?\nyes\n"})
        ),
        pathlib.Path("examples")
        / "hello"
        / "hello-data.pdl": InputsType(scope=PdlDict({"something": "ABC"})),
        pathlib.Path("examples")
        / "tutorial"
        / "conditionals_loops.pdl": InputsType(
            stdin="What is APR?\nno\nSay it as a poem\nyes\n"
        ),
    }.items()
}


EXPECTED_PARSE_ERROR = [
    pathlib.Path("tests") / "data" / "line" / "hello.pdl",
    pathlib.Path("tests") / "data" / "line" / "hello1.pdl",
    pathlib.Path("tests") / "data" / "line" / "hello4.pdl",
    pathlib.Path("tests") / "data" / "line" / "hello7.pdl",
    pathlib.Path("tests") / "data" / "line" / "hello8.pdl",
    pathlib.Path("tests") / "data" / "line" / "hello10.pdl",
    pathlib.Path("tests") / "data" / "line" / "hello11.pdl",
    pathlib.Path("tests") / "data" / "line" / "hello31.pdl",
]

EXPECTED_RUNTIME_ERROR = [
    pathlib.Path("examples") / "demo" / "1-gen-data.pdl",
    pathlib.Path("examples") / "tutorial" / "gen-data.pdl",
    pathlib.Path("examples") / "hello" / "hello-type-code.pdl",
    pathlib.Path("examples") / "hello" / "hello-type-list.pdl",
    pathlib.Path("examples") / "hello" / "hello-type.pdl",
    pathlib.Path("examples") / "hello" / "hello-parser-json.pdl",
    pathlib.Path("tests") / "data" / "line" / "hello12.pdl",
    pathlib.Path("tests") / "data" / "line" / "hello13.pdl",
    pathlib.Path("tests") / "data" / "line" / "hello14.pdl",
    pathlib.Path("tests") / "data" / "line" / "hello15.pdl",
    pathlib.Path("tests") / "data" / "line" / "hello16.pdl",
    pathlib.Path("tests") / "data" / "line" / "hello17.pdl",
    pathlib.Path("tests") / "data" / "line" / "hello18.pdl",
    pathlib.Path("tests") / "data" / "line" / "hello19.pdl",
    pathlib.Path("tests") / "data" / "line" / "hello20.pdl",
    pathlib.Path("tests") / "data" / "line" / "hello21.pdl",
    pathlib.Path("tests") / "data" / "line" / "hello22.pdl",
    pathlib.Path("tests") / "data" / "line" / "hello23.pdl",
    pathlib.Path("tests") / "data" / "line" / "hello24.pdl",
    pathlib.Path("tests") / "data" / "line" / "hello25.pdl",
    pathlib.Path("tests") / "data" / "line" / "hello26.pdl",
    pathlib.Path("tests") / "data" / "line" / "hello27.pdl",
    pathlib.Path("tests") / "data" / "line" / "hello28.pdl",
    pathlib.Path("tests") / "data" / "line" / "hello29.pdl",
    pathlib.Path("tests") / "data" / "line" / "hello3.pdl",
    pathlib.Path("tests") / "data" / "line" / "hello30.pdl",
    pathlib.Path("tests") / "data" / "line" / "hello9.pdl",
]


def test_valid_programs(capsys: CaptureFixture[str], monkeypatch: MonkeyPatch) -> None:
    actual_parse_error: set[str] = set()
    actual_runtime_error: set[str] = set()
    wrong_results = {}
    for pdl_file_name in pathlib.Path(".").glob("**/*.pdl"):
        scope: ScopeType = PdlDict({})
        if str(pdl_file_name) in TO_SKIP:
            continue
        if str(pdl_file_name) in TESTS_WITH_INPUT:
            inputs = TESTS_WITH_INPUT[str(pdl_file_name)]
            if inputs.stdin is not None:
                monkeypatch.setattr(
                    "sys.stdin",
                    io.StringIO(inputs.stdin),
                )
            if inputs.scope is not None:
                scope = inputs.scope
        try:
            random.seed(11)
            output = pdl.exec_file(
                pdl_file_name,
                scope=scope,
                output="all",
                config=pdl.InterpreterConfig(batch=0),
            )
            result = output["result"]
            block_to_dict(output["trace"], json_compatible=True)
            result_dir_name = (
                pathlib.Path(".") / "tests" / "results" / pdl_file_name.parent
            )
            if str(pdl_file_name) in NOT_DETERMINISTIC:
                continue
            wrong_result = True
            for result_file_name in result_dir_name.glob(
                pdl_file_name.stem + ".*.result"
            ):
                with open(result_file_name, "r", encoding="utf-8") as result_file:
                    expected_result = str(result_file.read())
                if str(result).strip() == expected_result.strip():
                    wrong_result = False
                    break
            if wrong_result:
                if UPDATE_RESULTS:
                    result_file_name_0 = (
                        pdl_file_name.stem + "." + str(RESULTS_VERSION) + ".result"
                    )
                    result_dir_name.mkdir(parents=True, exist_ok=True)
                    with open(
                        result_dir_name / result_file_name_0, "w", encoding="utf-8"
                    ) as result_file:
                        print(str(result), file=result_file)
                wrong_results[str(pdl_file_name)] = {
                    "actual": str(result),
                }
        except PDLParseError:
            actual_parse_error |= {str(pdl_file_name)}
        except Exception as exc:
            if str(pdl_file_name) not in set(str(p) for p in EXPECTED_RUNTIME_ERROR):
                print(f"{pdl_file_name}: {exc}")  # unexpected error: breakpoint
            actual_runtime_error |= {str(pdl_file_name)}
            print(exc)

    # Parse errors
    expected_parse_error = set(str(p) for p in EXPECTED_PARSE_ERROR)
    unexpected_parse_error = sorted(list(actual_parse_error - expected_parse_error))
    assert (
        len(unexpected_parse_error) == 0
    ), f"Unexpected parse error: {unexpected_parse_error}"

    # Runtime errors
    expected_runtime_error = set(str(p) for p in EXPECTED_RUNTIME_ERROR)
    unexpected_runtime_error = sorted(
        list(actual_runtime_error - expected_runtime_error)
    )
    assert (
        len(unexpected_runtime_error) == 0
    ), f"Unexpected runtime error: {unexpected_runtime_error}"

    # Unexpected valid
    unexpected_valid = sorted(
        list(
            (expected_parse_error - actual_parse_error).union(
                expected_runtime_error - actual_runtime_error
            )
        )
    )
    assert len(unexpected_valid) == 0, f"Unexpected valid: {unexpected_valid}"
    # Unexpected results
    assert len(wrong_results) == 0, f"Wrong results: {wrong_results}"
