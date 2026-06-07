from fastapi import APIRouter

from models.rule_models import (
	CreateSeverityRuleRequest,
	CreateComponentRuleRequest,
	CreateTriageRuleRequest,
	AddKeywordRequest,
)
from repositories.rule_repository import (
	get_severity_rules,
	get_component_rules,
	get_triage_rules,
	add_severity_rule,
	add_severity_keyword,
	add_component_rule,
	add_component_keyword,
	add_triage_rule,
)


router = APIRouter(prefix="/rules", tags=["rules"])


@router.get("/severity")
def list_severity_rules():
	return {
		"rules": get_severity_rules()
	}


@router.post("/severity")
def create_severity_rule(request: CreateSeverityRuleRequest):
	return add_severity_rule(request)


@router.post("/severity/{severity_id}/keywords")
def create_severity_keyword(severity_id: int, request: AddKeywordRequest):
	return add_severity_keyword(severity_id, request.keyword)


@router.get("/components")
def list_component_rules():
	return {
		"rules": get_component_rules()
	}


@router.post("/components")
def create_component_rule(request: CreateComponentRuleRequest):
	return add_component_rule(request)


@router.post("/components/{component_rule_id}/keywords")
def create_component_keyword(component_rule_id: int, request: AddKeywordRequest):
	return add_component_keyword(component_rule_id, request.keyword)


@router.get("/triage")
def list_triage_rules():
	return {
		"rules": get_triage_rules()
	}


@router.post("/triage")
def create_triage_rule(request: CreateTriageRuleRequest):
	return add_triage_rule(request)