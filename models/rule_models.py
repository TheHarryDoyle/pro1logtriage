from pydantic import BaseModel


class CreateSeverityRuleRequest(BaseModel):
	name: str
	keywords: list[str]
	priority: int | None = None
	enabled: bool = True


class AddKeywordRequest(BaseModel):
	keyword: str


class CreateComponentRuleRequest(BaseModel):
	component: str
	keywords: list[str]
	priority: int | None = None
	enabled: bool = True


class CreateTriageRuleRequest(BaseModel):
	category: str
	keywords: list[str]
	confidence: float
	suggested_actions: str
	commands_to_check: list[str]
	priority: int | None = None
	enabled: bool = True