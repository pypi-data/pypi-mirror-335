import pandas as pd
from .base import BaseDTO
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict


@dataclass
class RedteamHealthResponse(BaseDTO):
    status: str
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RedteamHealthResponse":
        return cls(
            status=data.get("status", "")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status
        }


@dataclass
class RedTeamResponse(BaseDTO):
    task_id: Optional[str] = None
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    _extra_fields: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict) -> "RedTeamResponse":
        return cls(
            task_id=data.get("task_id"),
            message=data.get("message"),
            data=data.get("data"),
        )
    
    def to_dict(self) -> Dict:
        return super().to_dict()


@dataclass
class RedTeamTaskStatus(BaseDTO):
    status: Optional[str] = None


@dataclass
class RedTeamTaskDetails(BaseDTO):
    created_at: Optional[str] = None
    model_name: Optional[str] = None
    status: Optional[str] = None
    test_name: Optional[str] = None
    task_id: Optional[str] = None


@dataclass
class StatisticItem(BaseDTO):
    success_percentage: float
    total: int
    _extra_fields: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict) -> "StatisticItem":
        return cls(
            success_percentage=data.get("success(%)", 0.0), total=data.get("total", 0)
        )

    def to_dict(self) -> Dict:
        d = super().to_dict()
        # Special handling for success percentage key
        d["success(%)"] = d.pop("success_percentage")
        return d


@dataclass
class ResultSummary(BaseDTO):
    test_date: str
    test_name: str
    dataset_name: str
    model_name: str
    model_endpoint_url: str
    model_source: str
    model_provider: str
    risk_score: float
    test_type: Dict[str, StatisticItem]
    nist_category: Dict[str, StatisticItem]
    scenario: Dict[str, StatisticItem]
    category: Dict[str, StatisticItem]
    attack_method: Dict[str, StatisticItem]
    _extra_fields: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict) -> "ResultSummary":
        def convert_stat_list(stat_list: List[Dict]) -> Dict[str, StatisticItem]:
            result = {}
            for item in stat_list:
                for key, value in item.items():
                    result[key] = StatisticItem.from_dict(value)
            return result

        return cls(
            test_date=data.get("test_date", ""),
            test_name=data.get("test_name", ""),
            dataset_name=data.get("dataset_name", ""),
            model_name=data.get("model_name", ""),
            model_endpoint_url=data.get("model_endpoint_url", ""),
            model_source=data.get("model_source", ""),
            model_provider=data.get("model_provider", ""),
            risk_score=data.get("risk_score", 0.0),
            test_type=convert_stat_list(data.get("test_type", [])),
            nist_category=convert_stat_list(data.get("nist_category", [])),
            scenario=convert_stat_list(data.get("scenario", [])),
            category=convert_stat_list(data.get("category", [])),
            attack_method=convert_stat_list(data.get("attack_method", [])),
        )

    def to_dict(self) -> Dict:
        def convert_stat_dict(stat_dict: Dict[str, StatisticItem]) -> List[Dict]:
            return [{key: value.to_dict()} for key, value in stat_dict.items()]

        d = super().to_dict()
        # Convert stat dictionaries to lists of dictionaries
        d["test_type"] = convert_stat_dict(self.test_type)
        d["nist_category"] = convert_stat_dict(self.nist_category)
        d["scenario"] = convert_stat_dict(self.scenario)
        d["category"] = convert_stat_dict(self.category)
        d["attack_method"] = convert_stat_dict(self.attack_method)
        return d


@dataclass
class RedTeamResultSummary(BaseDTO):
    summary: ResultSummary
    _extra_fields: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict) -> "RedTeamResultSummary":
        if not data or "summary" not in data:
            return cls(summary=ResultSummary.from_dict({}))
        return cls(summary=ResultSummary.from_dict(data["summary"]))

    def to_dict(self) -> Dict:
        return {"summary": self.summary.to_dict()}


@dataclass
class TestEvalTokens(BaseDTO):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    _extra_fields: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestResult(BaseDTO):
    prompt: str
    category: str
    test_type: str
    nist_category: str
    source: str
    attack_method: str
    jailbreak_prompt: str
    response: str
    success: str
    reasoning: str
    detected_language: str
    eval_latency: float
    eval_tokens: TestEvalTokens
    test_name: str
    _extra_fields: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RedTeamResultDetails(BaseDTO):
    details: List[TestResult]
    _extra_fields: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict) -> "RedTeamResultDetails":
        if not data or "details" not in data:
            return cls(details=[])

        details = []
        for result in data["details"]:
            # Convert eval_tokens dict to TestEvalTokens object
            eval_tokens = TestEvalTokens(**result["eval_tokens"])

            # Create a copy of the result dict and replace eval_tokens
            result_copy = dict(result)
            result_copy["eval_tokens"] = eval_tokens

            # Create TestResult object
            test_result = TestResult(**result_copy)
            details.append(test_result)

        return cls(details=details)

    def to_dict(self) -> Dict:
        return {
            "details": [
                {**result.to_dict(), "eval_tokens": result.eval_tokens.to_dict()}
                for result in self.details
            ]
        }

    def to_dataframe(self) -> pd.DataFrame:
        data = [
            {**result.to_dict(), "eval_tokens": result.eval_tokens.to_dict()}
            for result in self.details
        ]
        return pd.DataFrame(data)


@dataclass
class AttackMethods(BaseDTO):
    basic: List[str] = field(default_factory=lambda: ["basic"])
    advanced: Dict[str, List[str]] = field(
        default_factory=lambda: {"static": ["single_shot"], "dynamic": ["iterative"]}
    )

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


@dataclass
class TestConfig(BaseDTO):
    sample_percentage: int = 100
    attack_methods: AttackMethods = field(default_factory=AttackMethods)

    def to_dict(self) -> dict:
        return {
            "sample_percentage": self.sample_percentage,
            "attack_methods": self.attack_methods.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict):
        attack_methods = AttackMethods.from_dict(data.pop("attack_methods", {}))
        return cls(**data, attack_methods=attack_methods)


@dataclass
class RedTeamTestConfigurations(BaseDTO):
    # Basic tests
    bias_test: TestConfig = field(default=None)
    cbrn_test: TestConfig = field(default=None)
    insecure_code_test: TestConfig = field(default=None)
    toxicity_test: TestConfig = field(default=None)
    harmful_test: TestConfig = field(default=None)
    # Advanced tests
    adv_info_test: TestConfig = field(default=None)
    adv_bias_test: TestConfig = field(default=None)
    adv_command_test: TestConfig = field(default=None)
    _extra_fields: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**{k: TestConfig.from_dict(v) for k, v in data.items()})


@dataclass
class TargetModelConfiguration(BaseDTO):
    testing_for: str = "LLM"
    model_name: str = "gpt-4o-mini"
    model_type: str = "text_2_text"
    model_version: Optional[str] = None
    system_prompt: str = ""
    conversation_template: str = ""
    model_source: str = ""
    model_provider: str = "openai"
    model_endpoint_url: str = "https://api.openai.com/v1/chat/completions"
    model_api_key: Optional[str] = None
    rate_per_min: int = 20
    _extra_fields: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


@dataclass
class RedTeamModelHealthConfig(BaseDTO):
    target_model_configuration: TargetModelConfiguration = field(
        default_factory=TargetModelConfiguration
    )

    def to_dict(self) -> dict:
        d = asdict(self)
        d["target_model_configuration"] = self.target_model_configuration.to_dict()
        return d

    @classmethod
    def from_dict(cls, data: dict):
        data = data.copy()
        target_config = TargetModelConfiguration.from_dict(
            data.pop("target_model_configuration", {})
        )
        return cls(
            # **data,
            target_model_configuration=target_config,
        )


@dataclass
class RedteamModelHealthResponse(BaseDTO):
    status: str
    error: str
    _extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RedteamModelHealthResponse":
        return cls(
            status=data.get("status", ""),
            error=data.get("error", "")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "error": self.error
        }


@dataclass
class RedTeamConfig(BaseDTO):
    test_name: str = "Test Name"
    dataset_name: str = "standard"
    model_saved_name: str = "gpt-4o-mini"

    redteam_test_configurations: RedTeamTestConfigurations = field(
        default_factory=RedTeamTestConfigurations
    )
    target_model_configuration: TargetModelConfiguration = field(
        default_factory=TargetModelConfiguration
    )

    _extra_fields: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["redteam_test_configurations"] = self.redteam_test_configurations.to_dict()
        d["target_model_configuration"] = self.target_model_configuration.to_dict()
        return d

    @classmethod
    def from_dict(cls, data: dict):
        data = data.copy()
        test_configs = RedTeamTestConfigurations.from_dict(
            data.pop("redteam_test_configurations", {})
        )
        target_config = TargetModelConfiguration.from_dict(
            data.pop("target_model_configuration", {})
        )
        return cls(
            **data,
            redteam_test_configurations=test_configs,
            target_model_configuration=target_config,
        )


# @dataclass
# class RedTeamConfigWithSavedModel(BaseDTO):
#     test_name: str = "Test Name"
#     dataset_name: str = "standard"
#     model_saved_name: str = "gpt-4o-mini"

#     redteam_test_configurations: RedTeamTestConfigurations = field(
#         default_factory=RedTeamTestConfigurations
#     )
#     target_model_configuration: TargetModelConfiguration = field(
#         default_factory=TargetModelConfiguration
#     )

#     _extra_fields: Dict[str, Any] = field(default_factory=dict)

#     def to_dict(self) -> dict:
#         d = asdict(self)
#         d["redteam_test_configurations"] = self.redteam_test_configurations.to_dict()
#         d["target_model_configuration"] = self.target_model_configuration.to_dict()
#         return d

#     @classmethod
#     def from_dict(cls, data: dict):
#         data = data.copy()
#         test_configs = RedTeamTestConfigurations.from_dict(
#             data.pop("redteam_test_configurations", {})
#         )
#         target_config = TargetModelConfiguration.from_dict(
#             data.pop("target_model_configuration", {})
#         )
#         return cls(
#             **data,
#             redteam_test_configurations=test_configs,
#             target_model_configuration=target_config,
#         )


@dataclass
class RedTeamTaskList(BaseDTO):
    tasks: List[RedTeamTaskDetails] = field(default_factory=list)

    def to_dataframe(self) -> pd.DataFrame:
        data = [task for task in self.tasks]
        return pd.DataFrame(data)


# Default configurations
DEFAULT_REDTEAM_CONFIG = RedTeamConfig()
