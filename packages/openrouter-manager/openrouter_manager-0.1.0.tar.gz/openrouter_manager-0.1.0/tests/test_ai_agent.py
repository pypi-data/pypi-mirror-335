import pytest
import os

from unittest.mock import ANY, patch
from openrouter_manager.adapter.ai_agent import AiAgent

__author__ = "Lenin Lozano"
__copyright__ = "Lenin Lozano"
__license__ = "MIT"


def test_when_no_api_key_then_throw_error():
    """Main Function Tests"""
    with pytest.raises(ValueError) as e_info:
        AiAgent()
    assert str(e_info.value) == "AIAGENT_API_KEY is missing in environment variables"


def test_when_prompt_file_doesnot_exists_in_environment_then_throw_error():
    os.environ["AIAGENT_API_KEY"] = "12123123123"
    os.environ["AIAGENT_PROMPT_FILE"] = "test_prompt_file"
    with pytest.raises(ValueError) as e_info:
        AiAgent()
    assert str(e_info.value) == "Prompt file not found: test_prompt_file"


def test_when_prompt_file_doesnot_exists_as_argument_then_throw_error():
    os.environ["AIAGENT_API_KEY"] = "12123123123"
    with pytest.raises(ValueError) as e_info:
        AiAgent(prompt_file="test_prompt_file")
    assert str(e_info.value) == "Prompt file not found: test_prompt_file"


def test_creation_when_ok():
    os.environ["AIAGENT_API_KEY"] = "12123123123"
    os.environ["AIAGENT_PROMPT_FILE"] = "tests/data/test_prompt.prompt"
    AiAgent()


def test_creation_with_prompt_file_as_argument():
    os.environ["AIAGENT_API_KEY"] = "121231"
    AiAgent(prompt_file="tests/data/test_prompt.prompt")


def test_set_prompt():
    os.environ["AIAGENT_API_KEY"] = "12123123123"
    os.environ["AIAGENT_PROMPT_FILE"] = "tests/data/test_prompt.prompt"
    ai_agent = AiAgent()
    ai_agent.set_prompt("tests/data/test_prompt_2.prompt")
    assert str(ai_agent.prompt) == '''Eres un asistente que resume incidencias.
Título: 
Descripción: 
Genera un resumen breve.'''


@patch('openrouter_manager.adapter.ai_agent.requests')
def test_resolve_ok(mock_requests):
    mock_response = mock_requests.post.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {'choices': [{
        'message': {
            'content': "Te doy la respuesta papá"
        }
    }]}
    os.environ["AIAGENT_API_KEY"] = "12123123123"
    os.environ["AIAGENT_PROMPT_FILE"] = "tests/data/test_prompt.prompt"
    ai_agent = AiAgent()
    result = ai_agent.resolve({"titulo": "Este es el titulo",
                               "descripcion": "Descripcion"})
    print(result)
    mock_requests.post.assert_called_once_with(
        'https://openrouter.ai/api/v1/chat/completions', data=ANY, headers=ANY)
    assert result == "Te doy la respuesta papá"
