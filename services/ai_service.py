import json
from typing import Any, Dict, Iterable, List

from orchestrator.graph import graph
from prompts.system_prompts import ASSESSMENT_PROMPT_TEMPLATE, EVALUATOR_PROMPT_TEMPLATE
from utils.logger import get_logger

logger = get_logger(__name__)


class AIService:
    def __init__(self) -> None:
        self._logger = logger

    @staticmethod
    def _build_prompt(template: str, payload: str) -> str:
        return template.format(payload=payload.strip())

    def invoke(self, user_input: str, learner_id: str) -> dict[str, Any]:
        state = {
            "user_input": user_input,
            "learner_id": learner_id,
            "execution_path": []
        }
        response = graph.invoke(state)
        self._logger.debug("Graph returned execution path: %s", response.get("execution_path"))
        return response or {}

    def run_assessment(self, user_input: str, learner_id: str) -> dict[str, Any]:
        prompt = self._build_prompt(ASSESSMENT_PROMPT_TEMPLATE, user_input)
        return self.invoke(prompt, learner_id)

    def evaluate_assessment(self, questions: Iterable[dict], learner_id: str) -> dict[str, Any]:
        payload = json.dumps(list(questions), indent=4)
        prompt = self._build_prompt(EVALUATOR_PROMPT_TEMPLATE, payload)
        return self.invoke(prompt, learner_id)

    def chat(self, user_input: str, learner_id: str) -> dict[str, Any]:
        return self.invoke(user_input, learner_id)