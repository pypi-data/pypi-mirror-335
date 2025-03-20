import urllib3
from .base import BaseClient
from .dto import (
    RedteamHealthResponse,
    RedTeamModelHealthConfig,
    RedteamModelHealthResponse,
    RedTeamConfig,
    # RedTeamConfigWithSavedModel,
    RedTeamResponse,
    RedTeamResultSummary,
    RedTeamResultDetails,
    RedTeamTaskStatus,
    RedTeamTaskDetails,
    RedTeamTaskList,
)


class RedTeamClientError(Exception):
    """
    A custom exception for Red Team errors.
    """

    pass


class RedTeamClient(BaseClient):
    """
    A client for interacting with the Red Team API.
    """

    def __init__(self, api_key: str, base_url: str = "https://api.enkryptai.com"):
        super().__init__(api_key, base_url)

    # def get_model(self, model):
    #     models = self._request("GET", "/models/list-models")
    #     models = models["models"]
    #     for _model_data in models:
    #         if _model_data["model_saved_name"] == model:
    #             return _model_data["model_saved_name"]
    #     else:
    #         return None

    def get_health(self):
        """
        Get the health status of the service.
        """
        try:
            response = self._request("GET", "/redteam/health")
            if response.get("error"):
                raise RedTeamClientError(response["error"])
            return RedteamHealthResponse.from_dict(response)
        except Exception as e:
            raise RedTeamClientError(str(e))

    def check_model_health(self, config: RedTeamModelHealthConfig):
        """
        Get the health status of a model.
        """
        try:
            config = RedTeamModelHealthConfig.from_dict(config)
            response = self._request("POST", "/redteam/model-health", json=config.to_dict())
            # if response.get("error"):
            if response.get("error") not in [None, ""]:
                raise RedTeamClientError(response["error"])
            return RedteamModelHealthResponse.from_dict(response)
        except Exception as e:
            raise RedTeamClientError(str(e))
        
    def check_saved_model_health(self, model_saved_name: str):
        """
        Get the health status of a saved model.
        """
        try:
            headers = {
                "X-Enkrypt-Model": model_saved_name,
            }
            response = self._request("POST", "/redteam/model/model-health", headers=headers)
            # if response.get("error"):
            if response.get("error") not in [None, ""]:
                raise RedTeamClientError(response["error"])
            return RedteamModelHealthResponse.from_dict(response)
        except Exception as e:
            raise RedTeamClientError(str(e))

    def add_task(
        self,
        config: RedTeamConfig,
    ):
        """
        Add a new red teaming task.
        """
        config = RedTeamConfig.from_dict(config)
        test_configs = config.redteam_test_configurations.to_dict()
        # Remove None or empty test configurations
        test_configs = {k: v for k, v in test_configs.items() if v is not None}

        payload = {
            # "async": config.async_enabled,
            "dataset_name": config.dataset_name,
            "test_name": config.test_name,
            "redteam_test_configurations": {
                k: v.to_dict() for k, v in test_configs.items()
            },
        }

        saved_model = config.model_saved_name
        if saved_model:
            headers = {
                "X-Enkrypt-Model": saved_model,
                "Content-Type": "application/json",
            }
            response = self._request(
                "POST",
                "/redteam/v2/model/add-task",
                headers=headers,
                json=payload,
            )
            if response.get("error"):
                raise RedTeamClientError(response["error"])
            return RedTeamResponse.from_dict(response)
        elif config.target_model_configuration:
            payload["target_model_configuration"] = (
                config.target_model_configuration.to_dict()
            )
            # print(payload)
            response = self._request(
                "POST",
                "/redteam/v2/add-task",
                json=payload,
            )
            if response.get("error"):
                raise RedTeamClientError(response["error"])
            return RedTeamResponse.from_dict(response)
        else:
            raise RedTeamClientError(
                "Please use a saved model or provide a target model configuration"
            )

    def status(self, task_id: str = None, test_name: str = None):
        """
        Get the status of a specific red teaming task.

        Args:
            task_id (str, optional): The ID of the task to check status
            test_name (str, optional): The name of the test to check status

        Returns:
            dict: The task status information
            
        Raises:
            RedTeamClientError: If neither task_id nor test_name is provided, or if there's an error from the API
        """
        if not task_id and not test_name:
            raise RedTeamClientError("Either task_id or test_name must be provided")
        
        headers = {}
        if task_id:
            headers["X-Enkrypt-Task-ID"] = task_id
        if test_name:
            headers["X-Enkrypt-Test-Name"] = test_name

        response = self._request("GET", "/redteam/task-status", headers=headers)
        if response.get("error"):
            raise RedTeamClientError(response["error"])
        return RedTeamTaskStatus.from_dict(response)

    def cancel_task(self, task_id: str = None, test_name: str = None):
        """
        Cancel a specific red teaming task.

        Args:
            task_id (str, optional): The ID of the task to cancel
            test_name (str, optional): The name of the test to cancel

        Returns:
            dict: The cancellation response

        Raises:
            RedTeamClientError: If neither task_id nor test_name is provided, or if there's an error from the API
        """
        raise RedTeamClientError(
            "This feature is currently under development. Please check our documentation "
            "at https://docs.enkrypt.ai for updates or contact support@enkrypt.ai for assistance."
        )

        if not task_id and not test_name:
            raise RedTeamClientError("Either task_id or test_name must be provided")

        headers = {}
        if task_id:
            headers["X-Enkrypt-Task-ID"] = task_id
        if test_name:
            headers["X-Enkrypt-Test-Name"] = test_name

        response = self._request("POST", "/redteam/cancel-task", headers=headers)
        if response.get("error"):
            raise RedTeamClientError(response["error"])
        return response

    def get_task(self, task_id: str = None, test_name: str = None):
        """
        Get the status and details of a specific red teaming task.

        Args:
            task_id (str, optional): The ID of the task to retrieve
            test_name (str, optional): The name of the test to retrieve

        Returns:
            dict: The task details and status
            
        Raises:
            RedTeamClientError: If neither task_id nor test_name is provided, or if there's an error from the API
        """
        if not task_id and not test_name:
            raise RedTeamClientError("Either task_id or test_name must be provided")
        
        headers = {}
        if task_id:
            headers["X-Enkrypt-Task-ID"] = task_id
        if test_name:
            headers["X-Enkrypt-Test-Name"] = test_name

        response = self._request("GET", "/redteam/get-task", headers=headers)
        if response.get("error"):
            raise RedTeamClientError(response["error"])
        return RedTeamTaskDetails.from_dict(response["data"])

    def get_result_summary(self, task_id: str = None, test_name: str = None):
        """
        Get the summary of results for a specific red teaming task.

        Args:
            task_id (str, optional): The ID of the task to get results for
            test_name (str, optional): The name of the test to get results for

        Returns:
            dict: The summary of the task results
            
        Raises:
            RedTeamClientError: If neither task_id nor test_name is provided, or if there's an error from the API
        """
        if not task_id and not test_name:
            raise RedTeamClientError("Either task_id or test_name must be provided")
        
        headers = {}
        if task_id:
            headers["X-Enkrypt-Task-ID"] = task_id
        if test_name:
            headers["X-Enkrypt-Test-Name"] = test_name

        response = self._request("GET", "/redteam/results/summary", headers=headers)
        if response.get("error"):
            raise RedTeamClientError(response["error"])
        print(f"Response: {response}")
        return RedTeamResultSummary.from_dict(response)

    def get_result_details(self, task_id: str = None, test_name: str = None):
        """
        Get the detailed results for a specific red teaming task.

        Args:
            task_id (str, optional): The ID of the task to get detailed results for
            test_name (str, optional): The name of the test to get detailed results for

        Returns:
            dict: The detailed task results
            
        Raises:
            RedTeamClientError: If neither task_id nor test_name is provided, or if there's an error from the API
        """
        if not task_id and not test_name:
            raise RedTeamClientError("Either task_id or test_name must be provided")
        
        headers = {}
        if task_id:
            headers["X-Enkrypt-Task-ID"] = task_id
        if test_name:
            headers["X-Enkrypt-Test-Name"] = test_name
            
        response = self._request("GET", "/redteam/results/details", headers=headers)
        if response.get("error"):
            raise RedTeamClientError(response["error"])
        return RedTeamResultDetails.from_dict(response)

    def get_task_list(self):
        response = self._request("GET", "/redteam/list-tasks")
        if response.get("error"):
            raise RedTeamClientError(response["error"])
        return RedTeamTaskList.from_dict(response)
