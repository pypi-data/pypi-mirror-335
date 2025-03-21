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
redteam_model_test_name = None
redteam_picked_test_name = None
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
        },
    }


@pytest.fixture
def sample_redteam_target_config():
    global redteam_test_name
    redteam_test_name = f"Redteam Test {str(uuid.uuid4())[:6]}"
    print("\nRedteam target model test name: ", redteam_test_name)
    return {
        "test_name": redteam_test_name,
        "dataset_name": "standard",
        "redteam_test_configurations": {
            # # Commenting to have only 1 for faster testing
            # "bias_test": {
            #     "sample_percentage": 2,
            #     "attack_methods": {"basic": ["basic"]},
            # },
            # "cbrn_test": {
            #     "sample_percentage": 2,
            #     "attack_methods": {"basic": ["basic"]},
            # },
            # "insecure_code_test": {
            #     "sample_percentage": 2,
            #     "attack_methods": {"basic": ["basic"]},
            # },
            # "toxicity_test": {
            #     "sample_percentage": 2,
            #     "attack_methods": {"basic": ["basic"]},
            # },
            "harmful_test": {
                "sample_percentage": 2,
                "attack_methods": {"basic": ["basic"]},
            },
        },
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
        },
    }


@pytest.fixture
def sample_redteam_model_config():
    global redteam_model_test_name
    redteam_model_test_name = f"Redteam Test {str(uuid.uuid4())[:6]}"
    print("\nRedteam saved model test name: ", redteam_model_test_name)
    return {
        "test_name": redteam_model_test_name,
        "dataset_name": "standard",
        "redteam_test_configurations": {
            # # Commenting to have only 1 for faster testing
            # "bias_test": {
            #     "sample_percentage": 2,
            #     "attack_methods": {"basic": ["basic"]},
            # },
            # "cbrn_test": {
            #     "sample_percentage": 2,
            #     "attack_methods": {"basic": ["basic"]},
            # },
            # "insecure_code_test": {
            #     "sample_percentage": 2,
            #     "attack_methods": {"basic": ["basic"]},
            # },
            # "toxicity_test": {
            #     "sample_percentage": 2,
            #     "attack_methods": {"basic": ["basic"]},
            # },
            "harmful_test": {
                "sample_percentage": 2,
                "attack_methods": {"basic": ["basic"]},
            },
        },
    }


def get_task_name_from_list(redteam_client, status=None):
    """Helper function to get a redteam task name from the task list.
    
    Args:
        redteam_client: The RedTeamClient instance
        status: Optional status filter (e.g., "Finished", "Running")
    
    Returns:
        str: A test name from the task list
    """
    print(f"\nFetching redteam task with status: {status if status else 'Finished'}")
    redteams = redteam_client.get_task_list(status=status)
    redteams_dict = redteams.to_dict()
    print(f"\nRedteam task list retrieved with {len(redteams_dict.get('tasks', []))} tasks")
    
    if not redteams_dict.get("tasks"):
        # If no tasks with specified status, try without status filter
        if status:
            print(f"\nNo tasks with status '{status}', fetching any task")
            redteams = redteam_client.get_task_list()
            redteams_dict = redteams.to_dict()
    
    if not redteams_dict.get("tasks"):
        return None
    
    task_info = redteams_dict["tasks"][0]
    test_name = task_info["test_name"]
    print(f"\nSelected redteam task: {test_name} (Status: {task_info.get('status', 'unknown')})")
    return test_name


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


def test_add_task_with_target_model(redteam_client, sample_redteam_target_config):
    print("\n\nTesting adding a new redteam task with target model")
    # Debug sample_redteam_target_config
    # print("\nSample redteam target config: ", sample_redteam_target_config)
    response = redteam_client.add_task(config=sample_redteam_target_config)
    print("\nResponse from adding a new redteam task with target model: ", response)
    assert response is not None
    assert hasattr(response, "task_id")
    assert hasattr(response, "message")
    response.message == "Redteam task has been added successfully"
    # Sleep for a while to let the task complete
    import time
    print("\nSleeping for 60 seconds to let the task complete if possible ...")
    time.sleep(60)


def test_add_task_with_saved_model(redteam_client, sample_redteam_model_config):
    print("\n\nTesting adding a new redteam task with saved model")
    response = redteam_client.add_task_with_saved_model(config=sample_redteam_model_config,model_saved_name=test_model_saved_name)
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
    redteams = redteam_client.get_task_list(status="Finished")
    redteams_dict = redteams.to_dict()
    print("\nRedteam task list: ", redteams_dict)
    assert redteams_dict is not None
    assert isinstance(redteams_dict, dict)
    assert "tasks" in redteams_dict
    
    global redteam_picked_test_name
    if redteam_picked_test_name is None:
        redteam_picked_test_name = get_task_name_from_list(redteam_client, status="Finished")
        assert redteam_picked_test_name is not None
        print("\nPicked redteam finished task in list_redteams: ", redteam_picked_test_name)


def test_get_task_status(redteam_client):
    print("\n\nTesting get_task_status")
    global redteam_picked_test_name
    if redteam_picked_test_name is None:
        redteam_picked_test_name = get_task_name_from_list(redteam_client, status="Finished")
        assert redteam_picked_test_name is not None

    response = redteam_client.status(test_name=redteam_picked_test_name)
    print("\nRedteam task status: ", response)
    assert response is not None
    assert hasattr(response, "status")


def test_get_task(redteam_client):
    print("\n\nTesting get_task")
    global redteam_picked_test_name
    if redteam_picked_test_name is None:
        redteam_picked_test_name = get_task_name_from_list(redteam_client, status="Finished")
        assert redteam_picked_test_name is not None

    response = redteam_client.get_task(test_name=redteam_picked_test_name)
    print("\nRedteam task: ", response)
    assert response is not None
    assert hasattr(response, "status")


def test_get_result_summary(redteam_client):
    print("\n\nTesting get_result_summary")
    global redteam_picked_test_name
    if redteam_picked_test_name is None:
        redteam_picked_test_name = get_task_name_from_list(redteam_client, status="Finished")
        assert redteam_picked_test_name is not None

    response = redteam_client.get_result_summary(test_name=redteam_picked_test_name)
    print("\nRedteam task result summary: ", response)
    assert response is not None
    # # Task might not be successful yet
    # # TODO: How to handle this?
    # assert hasattr(response, "summary")


def test_get_result_summary_test_type(redteam_client):
    print("\n\nTesting get_result_summary_test_type")
    global redteam_picked_test_name
    if redteam_picked_test_name is None:
        redteam_picked_test_name = get_task_name_from_list(redteam_client, status="Finished")
        assert redteam_picked_test_name is not None

    response = redteam_client.get_result_summary_test_type(test_name=redteam_picked_test_name, test_type="harmful_test")
    print("\nRedteam task result summary of test type: ", response)
    assert response is not None
    # # Task might not be successful yet
    # # TODO: How to handle this?
    # assert hasattr(response, "summary")


def test_get_result_details(redteam_client):
    print("\n\nTesting get_result_details")
    global redteam_picked_test_name
    if redteam_picked_test_name is None:
        redteam_picked_test_name = get_task_name_from_list(redteam_client, status="Finished")
        assert redteam_picked_test_name is not None

    response = redteam_client.get_result_details(test_name=redteam_picked_test_name)
    print("\nRedteam task result details: ", response)
    assert response is not None
    # # Task might not be successful yet
    # # TODO: How to handle this?
    # assert hasattr(response, "details")


def test_get_result_details_test_type(redteam_client):
    print("\n\nTesting get_result_details_test_type")
    global redteam_picked_test_name
    if redteam_picked_test_name is None:
        redteam_picked_test_name = get_task_name_from_list(redteam_client, status="Finished")
        assert redteam_picked_test_name is not None

    response = redteam_client.get_result_details_test_type(test_name=redteam_picked_test_name, test_type="harmful_test")
    print("\nRedteam task result details of test type: ", response)
    assert response is not None
    # # Task might not be successful yet
    # # TODO: How to handle this?
    # assert hasattr(response, "details")

