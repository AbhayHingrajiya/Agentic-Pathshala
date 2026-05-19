import json
from typing import Optional, Literal
from pydantic import BaseModel, Field
from utils.prompt_loader import load_prompt
from utils.llm import llm
from mcp_server.mcp_client import call_mcp_tool

class AssignmentIntent(BaseModel):
    action: Literal[
        "assign", 
        "remove", 
        "list_assignments", 
        "list_learners", 
        "query_assignment_learners", 
        "query_learner_assignments"
    ] = Field(
        description="The action requested by the coach (assign, remove, list_assignments, list_learners, query_assignment_learners, or query_learner_assignments)."
    )
    resolved_assignment_id: Optional[str] = Field(
        None, 
        description="The exact assignment ID resolved from the catalog that matches the request. Required for assign, remove, and query_assignment_learners."
    )
    target_type: Optional[Literal["all", "cohort", "completed_assignment", "progress_below", "individual"]] = Field(
        None, 
        description="The target category of learners. Required for assign and remove actions."
    )
    cohort_name: Optional[str] = Field(None, description="Name of cohort group if target_type is cohort.")
    criteria_value: Optional[str] = Field(None, description="The assignment ID (for completed_assignment) or a number string like '50' (for progress_below).")
    learner_id: Optional[str] = Field(None, description="The exact learner_id of the individual learner. Required for individual targeting and query_learner_assignments.")
    status_filter: Optional[Literal["Pending", "In Progress", "Completed"]] = Field(
        None,
        description="Optional filter for assignment status (Pending, In Progress, Completed) when querying."
    )

def _resolve_assignment_id_programmatically(resolved_id: str, instruction: str, catalog: list) -> str:
    if not resolved_id:
        return resolved_id
        
    # 1. Exact match check
    for item in catalog:
        item_id = str(item.get("assignment_id", ""))
        if item_id.strip().lower() == resolved_id.strip().lower():
            return item_id
            
    # 2. Extract number from resolved_id or instruction
    import re
    numbers = re.findall(r'\d+', resolved_id)
    if not numbers:
        numbers = re.findall(r'\d+', instruction)
        
    if numbers:
        target_num = numbers[0]
        # Look for any assignment in catalog that starts with "Assignment {target_num}:" or contains "Assignment {target_num}"
        for item in catalog:
            item_id = str(item.get("assignment_id", ""))
            if f"Assignment {target_num}" in item_id or f"assignment {target_num}" in item_id.lower():
                return item_id
                
    # 3. Substring check
    for item in catalog:
        item_id = str(item.get("assignment_id", ""))
        if resolved_id.lower() in item_id.lower() or item_id.lower() in resolved_id.lower():
            return item_id
            
    return resolved_id

def coach_assignment_agent(state: dict) -> dict:
    instruction = state.get("user_input", "")
    session = state.get("session", {})
    coach_id = session.get("user_id", "unknown")

    # 1. Fetch catalog data via MCP
    try:
        learners_res = call_mcp_tool("get_learners", {})
        learners = learners_res.get("learners", [])
        
        assignments_res = call_mcp_tool("get_assignments", {})
        assignments = assignments_res.get("assignments", [])
    except Exception as e:
        state["agent_response"] = f"❌ Failed to communicate with MCP data services: {str(e)}"
        state["execution_path"].append("coach_assignment_agent_error")
        return state

    # 2. Let the LLM parse intent and resolve assignment ID
    try:
        structured_llm = llm.with_structured_output(AssignmentIntent)
        parser_prompt = load_prompt("coach_assignment_parser")
        chain = parser_prompt | structured_llm
        parsed_intent = chain.invoke({
            "assignments_data": json.dumps(assignments),
            "learners_data": json.dumps(learners),
            "instruction": instruction
        })
        if parsed_intent.resolved_assignment_id:
            parsed_intent.resolved_assignment_id = _resolve_assignment_id_programmatically(
                parsed_intent.resolved_assignment_id,
                instruction,
                assignments
            )
    except Exception as e:
        state["agent_response"] = f"❌ Failed to parse assignment instructions: {str(e)}"
        state["execution_path"].append("coach_assignment_agent_error")
        return state

    # 3. Resolve matched learners or informational queries
    action = parsed_intent.action

    if action == "list_assignments":
        execution_status = "🎓 **Available Assignments Catalog** 🎓\n"
        execution_status += "=====================================\n\n"
        for a in assignments:
            execution_status += f"- 📝 **{a.get('assignment_id')}**\n"
        state["agent_response"] = execution_status
        state["execution_path"].append("coach_assignment_agent")
        return state

    elif action == "list_learners":
        execution_status = "🎓 **Registered Learners Catalog** 🎓\n"
        execution_status += "=====================================\n\n"
        for l in learners:
            execution_status += f"- 👤 **{l.get('name')}** ({l.get('learner_id')}) | Email: {l.get('email')} | Cohort: {l.get('cohort_group', 'None')}\n"
        state["agent_response"] = execution_status
        state["execution_path"].append("coach_assignment_agent")
        return state

    elif action == "query_assignment_learners":
        assignment_id = parsed_intent.resolved_assignment_id
        status_filter = parsed_intent.status_filter

        if not assignment_id:
            state["agent_response"] = "❌ Failed to query: Please specify a valid assignment ID or title."
            state["execution_path"].append("coach_assignment_agent_error")
            return state

        valid_assignment = call_mcp_tool("validate_assignment_exists", {"assignment_id": assignment_id})
        if not valid_assignment.get("exists"):
            state["agent_response"] = f"❌ Failed to query: Assignment `{assignment_id}` does not exist in master catalog."
            state["execution_path"].append("coach_assignment_agent_invalid_assignment")
            return state

        filter_text = f" (Status: {status_filter})" if status_filter else ""
        execution_status = f"🎓 **Learners Assigned to: {assignment_id}{filter_text}** 🎓\n"
        execution_status += "=====================================\n\n"
        found_any = False
        for l in learners:
            l_id = l.get("learner_id")
            l_tasks = call_mcp_tool("get_assignments_for_learner", {"learner_id": l_id}).get("assignments", [])
            for t in l_tasks:
                if str(t.get("assignment_id")).strip() == str(assignment_id).strip():
                    t_status = t.get("status", "Pending")
                    if status_filter and t_status.lower().strip() != status_filter.lower().strip():
                        continue
                    execution_status += f"- ✅ **{l.get('name')}** ({l_id}) | Status: {t_status} | Progress: {t.get('progress_percentage', 0)}%\n"
                    found_any = True
                    break
        if not found_any:
            execution_status += "No learners matched the query criteria."

        state["agent_response"] = execution_status
        state["execution_path"].append("coach_assignment_agent")
        return state

    elif action == "query_learner_assignments":
        target_id = parsed_intent.learner_id
        status_filter = parsed_intent.status_filter

        if not target_id:
            state["agent_response"] = "❌ Failed to query: Please specify a valid learner name or ID."
            state["execution_path"].append("coach_assignment_agent_error")
            return state

        learner_profile = next((l for l in learners if l.get("learner_id") == target_id), None)
        if not learner_profile:
            state["agent_response"] = f"❌ Failed to query: Learner `{target_id}` not found."
            state["execution_path"].append("coach_assignment_agent_error")
            return state

        l_name = learner_profile.get("name")
        filter_text = f" (Status: {status_filter})" if status_filter else ""
        execution_status = f"🎓 **Assignments for: {l_name} ({target_id}){filter_text}** 🎓\n"
        execution_status += "=====================================\n\n"

        l_tasks = call_mcp_tool("get_assignments_for_learner", {"learner_id": target_id}).get("assignments", [])
        found_any = False
        for t in l_tasks:
            t_status = t.get("status", "Pending")
            if status_filter and t_status.lower().strip() != status_filter.lower().strip():
                continue
            execution_status += f"- 📝 **{t.get('assignment_id')}** | Status: {t_status} | Progress: {t.get('progress_percentage', 0)}%\n"
            found_any = True

        if not found_any:
            execution_status += "No assignments found matching the criteria."

        state["agent_response"] = execution_status
        state["execution_path"].append("coach_assignment_agent")
        return state

    # For assign and remove actions, proceed with target learners resolve
    target_learners = []
    assignment_id = parsed_intent.resolved_assignment_id
    if not assignment_id:
        state["agent_response"] = f"❌ Execution failed: Missing assignment ID for {action} action."
        state["execution_path"].append("coach_assignment_agent_error")
        return state

    # Validate assignment existence first
    valid_assignment = call_mcp_tool("validate_assignment_exists", {"assignment_id": assignment_id})
    if not valid_assignment.get("exists"):
        state["agent_response"] = f"❌ Execution failed: Assignment `{assignment_id}` does not exist in master catalog."
        state["execution_path"].append("coach_assignment_agent_invalid_assignment")
        return state

    if parsed_intent.target_type == "all":
        target_learners = learners
        
    elif parsed_intent.target_type == "individual":
        target_id = parsed_intent.learner_id
        target_learners = [
            l for l in learners 
            if l.get("learner_id") == target_id
        ]
        
    elif parsed_intent.target_type == "cohort":
        cohort = (parsed_intent.cohort_name or "").lower().strip()
        target_learners = [
            l for l in learners 
            if l.get("cohort_group") and l.get("cohort_group").lower().strip() == cohort
        ]
        
    elif parsed_intent.target_type == "completed_assignment":
        comp_id = parsed_intent.criteria_value
        for l in learners:
            l_id = l.get("learner_id")
            l_tasks = call_mcp_tool("get_assignments_for_learner", {"learner_id": l_id}).get("assignments", [])
            is_completed = any(
                str(t.get("assignment_id")).strip() == str(comp_id).strip() and t.get("status") == "Completed"
                for t in l_tasks
            )
            if is_completed:
                target_learners.append(l)
                
    elif parsed_intent.target_type == "progress_below":
        try:
            threshold = int(parsed_intent.criteria_value or 50)
        except ValueError:
            threshold = 50
            
        for l in learners:
            l_id = l.get("learner_id")
            l_tasks = call_mcp_tool("get_assignments_for_learner", {"learner_id": l_id}).get("assignments", [])
            for t in l_tasks:
                if int(t.get("progress_percentage", 0)) < threshold:
                    target_learners.append(l)
                    break

    # 4. Execute assignments via MCP
    results = []
    success_count = 0
    fail_count = 0
    already_assigned = 0

    if not target_learners:
        execution_status = "No learners matched the criteria."
    else:
        for learner in target_learners:
            l_id = learner.get("learner_id")
            l_name = learner.get("name")
            try:
                if parsed_intent.action == "remove":
                    res = call_mcp_tool(
                        "remove_task_from_learner",
                        {"learner_id": l_id, "assignment_id": assignment_id}
                    )
                    if res.get("success"):
                        success_count += 1
                        results.append(f"✅ {l_name} ({l_id}): Removed successfully.")
                    else:
                        fail_count += 1
                        results.append(f"❌ {l_name} ({l_id}): {res.get('error', '')}")
                else:
                    res = call_mcp_tool(
                        "assign_task_to_learner",
                        {"learner_id": l_id, "assignment_id": assignment_id, "coach_id": coach_id}
                    )
                    if res.get("success"):
                        success_count += 1
                        results.append(f"✅ {l_name} ({l_id}): Assigned successfully.")
                    else:
                        err = res.get("error", "")
                        if "already assigned" in err.lower():
                            already_assigned += 1
                            results.append(f"⏳ {l_name} ({l_id}): Already assigned.")
                        else:
                            fail_count += 1
                            results.append(f"❌ {l_name} ({l_id}): {err}")
            except Exception as e:
                fail_count += 1
                results.append(f"❌ {l_name} ({l_id}): {str(e)}")

        action_verb = "Removed" if parsed_intent.action == "remove" else "Assigned"
        execution_status = (
            f"Action: {parsed_intent.action.upper()}\n"
            f"Target Category: {parsed_intent.target_type.upper()}\n"
            f"Learners Matched: {len(target_learners)}\n"
            f"- {action_verb} Successfully: {success_count}\n"
            f"- Skipped / Already {action_verb}: {already_assigned}\n"
            f"- Failed: {fail_count}\n\n"
            "Execution Log:\n" + "\n".join(results)
        )

    # 5. Format response using system prompt
    prompt = load_prompt("coach_assignment_agent")
    chain = prompt | llm
    response = chain.invoke({
        "coach_id": coach_id,
        "instruction": instruction,
        "learners_data": json.dumps(learners, indent=2),
        "assignments_data": json.dumps(assignments, indent=2),
        "execution_status": execution_status
    })

    state["agent_response"] = response.content.strip()
    state["execution_path"].append("coach_assignment_agent")
    return state
