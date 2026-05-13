import yaml
# pyrefly: ignore [missing-import]
from langchain_core.prompts import ChatPromptTemplate

def load_prompt(prompt_name: str):
    with open(f"prompts/{prompt_name}.yaml", "r") as f:
        prompt_data = yaml.safe_load(f)

    system_template = prompt_data["system_template"]
    human_template = prompt_data["human_template"]

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_template),
        ("human", human_template)
    ])

    return prompt