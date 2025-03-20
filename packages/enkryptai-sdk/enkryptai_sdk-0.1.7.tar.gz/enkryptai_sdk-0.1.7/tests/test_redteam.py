import os
import uuid
import pytest
from dotenv import load_dotenv
from enkryptai_sdk import RedTeamClient

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ENKRYPT_API_KEY = os.getenv("ENKRYPTAI_API_KEY")
ENKRYPT_BASE_URL = os.getenv("ENKRYPTAI_BASE_URL") or "https://api.enkryptai.com"

redteam_test_name = None
test_model_saved_name = "Test Model"

model_name = "gpt-4o-mini"
model_provider = "openai"
model_endpoint_url = "https://api.openai.com/v1/chat/completions"


@pytest.fixture
def redteam_client():
    return RedTeamClient(api_key=ENKRYPT_API_KEY, base_url=ENKRYPT_BASE_URL)


@pytest.fixture
def sample_redteam_model_health_config():
    return {
        "target_model_configuration": {
            "model_name": model_name,
            "testing_for": "LLM",
            "model_type": "text_2_text",
            "model_version": "v1",
            "model_source": "https://openai.com",
            "model_provider": model_provider,
            "model_endpoint_url": model_endpoint_url,
            "model_api_key": OPENAI_API_KEY,
            "system_prompt": "",
            "conversation_template": "",
            "rate_per_min": 20
        }
    }


@pytest.fixture
def sample_redteam_config():
    global redteam_test_name
    redteam_test_name = "Redteam Test " + str(uuid.uuid4())[:6]
    print("\nRedteam test name: ", redteam_test_name)
    return {
        "test_name": redteam_test_name,
        "model_saved_name": test_model_saved_name,
        "dataset_name": "standard",
        "redteam_test_configurations": {
            "bias_test": {
                "sample_percentage": 2,
                "attack_methods": {"basic": ["basic"]},
            },
            "cbrn_test": {
                "sample_percentage": 2,
                "attack_methods": {"basic": ["basic"]},
            },
            "insecure_code_test": {
                "sample_percentage": 2,
                "attack_methods": {"basic": ["basic"]},
            },
            "toxicity_test": {
                "sample_percentage": 2,
                "attack_methods": {"basic": ["basic"]},
            },
            "harmful_test": {
                "sample_percentage": 2,
                "attack_methods": {"basic": ["basic"]},
            },
        },
    }


def test_get_health(redteam_client):
    print("\n\nTesting get_health")
    response = redteam_client.get_health()
    print("\nResponse from get_health: ", response)
    assert response is not None
    assert hasattr(response, "status")
    assert response.status == "healthy"


def test_model_health(redteam_client, sample_redteam_model_health_config):
    print("\n\nTesting check_model_health")
    response = redteam_client.check_model_health(config=sample_redteam_model_health_config)
    print("\nResponse from check_model_health: ", response)
    assert response is not None
    assert hasattr(response, "status")
    assert response.status == "healthy"


def test_saved_model_health(redteam_client):
    print("\n\nTesting check_saved_model_health")
    response = redteam_client.check_saved_model_health(model_saved_name=test_model_saved_name)
    print("\nResponse from check_saved_model_health: ", response)
    assert response is not None
    assert hasattr(response, "status")
    assert response.status == "healthy"


def test_add_task_with_saved_model(redteam_client, sample_redteam_config):
    print("\n\nTesting adding a new redteam task with saved model")
    response = redteam_client.add_task(config=sample_redteam_config)
    print("\nResponse from adding a new redteam task with saved model: ", response)
    assert response is not None
    assert hasattr(response, "task_id")
    assert hasattr(response, "message")
    response.message == "Redteam task has been added successfully"
    # Sleep for a while to let the task complete
    import time
    print("\nSleeping for 60 seconds to let the task complete if possible ...")
    time.sleep(60)


def test_list_redteams(redteam_client):
    print("\n\nTesting list_redteam tasks")
    redteams = redteam_client.get_task_list()
    redteams_dict = redteams.to_dict()
    print("\nRedteam task list: ", redteams_dict)
    assert redteams_dict is not None
    assert isinstance(redteams_dict, dict)
    assert "tasks" in redteams_dict
    global redteam_test_name
    if redteam_test_name is None:
        print("\nRedteam test name is None, picking one from response")
        redteam_info = redteams_dict["tasks"][0]
        assert redteam_info is not None
        redteam_test_name = redteam_info["test_name"]
        assert redteam_test_name is not None
        print("\nPicked redteam task in list_redteams: ", redteam_test_name)


def test_get_task_status(redteam_client):
    print("\n\nTesting get_task_status")
    global redteam_test_name
    if redteam_test_name is None:
        print("\nRedteam test name is None, fetching it from list_redteams")
        list_response = redteam_client.get_task_list()
        redteams_dict = list_response.to_dict()
        redteam_info = redteams_dict.tasks[0]
        assert redteam_info is not None
        redteam_test_name = redteam_info.test_name
        assert redteam_test_name is not None
        print("\nPicked redteam task in get_task_status: ", redteam_test_name)

    response = redteam_client.status(test_name=redteam_test_name)
    print("\nRedteam task status: ", response)
    assert response is not None
    assert hasattr(response, "status")


def test_get_task(redteam_client):
    print("\n\nTesting get_task")
    global redteam_test_name
    if redteam_test_name is None:
        print("\nRedteam test name is None, fetching it from list_redteams")
        list_response = redteam_client.get_task_list()
        redteams_dict = list_response.to_dict()
        redteam_info = redteams_dict.tasks[0]
        assert redteam_info is not None
        redteam_test_name = redteam_info.test_name
        assert redteam_test_name is not None
        print("\nPicked redteam task in get_task: ", redteam_test_name)

    response = redteam_client.get_task(test_name=redteam_test_name)
    print("\nRedteam task: ", response)
    assert response is not None
    assert hasattr(response, "status")


def test_get_result_summary(redteam_client):
    print("\n\nTesting get_result_summary")
    global redteam_test_name
    if redteam_test_name is None:
        print("\nRedteam test name is None, fetching it from list_redteams")
        list_response = redteam_client.get_task_list()
        redteams_dict = list_response.to_dict()
        redteam_info = redteams_dict.tasks[0]
        assert redteam_info is not None
        redteam_test_name = redteam_info.test_name
        assert redteam_test_name is not None
        print("\nPicked redteam task in get_task_status: ", redteam_test_name)

    response = redteam_client.get_result_summary(test_name=redteam_test_name)
    print("\nRedteam task summary: ", response)
    assert response is not None
    # # Task might not be successful yet
    # # TODO: How to handle this?
    # assert hasattr(response, "summary")


def test_get_result_details(redteam_client):
    print("\n\nTesting get_result_details")
    global redteam_test_name
    if redteam_test_name is None:
        print("\nRedteam test name is None, fetching it from list_redteams")
        list_response = redteam_client.get_task_list()
        redteams_dict = list_response.to_dict()
        redteam_info = redteams_dict.tasks[0]
        assert redteam_info is not None
        redteam_test_name = redteam_info.test_name
        assert redteam_test_name is not None
        print("\nPicked redteam task in get_task_status: ", redteam_test_name)

    response = redteam_client.get_result_details(test_name=redteam_test_name)
    print("\nRedteam task details: ", response)
    assert response is not None
    # # Task might not be successful yet
    # # TODO: How to handle this?
    # assert hasattr(response, "details")
