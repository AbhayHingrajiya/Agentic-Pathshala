import sys
from typing import Optional

from rich.align import Align
from rich import box, json
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

from config.settings import settings
from handlers.login_handler import LoginHandler
from rag.ingestion import ingest_documents
from repositories.assignment_repository import AssignmentRepository
from repositories.learner_repository import LearnerRepository
from repositories.coach_repository import CoachRepository
from services.ai_service import AIService
from services.assignment_service import AssignmentService
from services.auth_service import AuthService
from utils.logger import get_logger
from utils.validator import is_non_empty_string


import json
from utils.chat_history_manager import ChatHistoryManager



import logging
logger = logging.getLogger(__name__)

console = Console()
#logger = get_logger(__name__)


class MainApp:
    def __init__(self) -> None:
        learner_repository = LearnerRepository()
        assignment_repository = AssignmentRepository()
        coach_repository = CoachRepository()

        auth_service = AuthService(learner_repository, coach_repository)
        assignment_service = AssignmentService(assignment_repository)
        self.ai_service = AIService()

        self.login_handler = LoginHandler(auth_service, console)
        ingest_documents()

        logger.info("Configuration loaded from %s", settings.MCP_SERVER_URL)

    def show_banner(self):
        """Display application banner"""

        banner = Text(
            "Agentic Pathshala - AI Learning Coach",
        )

        console.print(
            Panel(
                Align.center(banner),
                border_style="bright_blue",
                padding=(1, 2),
                box=box.DOUBLE,
            )
        )

    def login(self) -> Optional[object]:
        self.show_banner()
        console.print("\n[bold yellow]🔐 Login Required[/bold yellow]\n")

        session = self.login_handler.login()
        if session is None:
            console.print("\n[bold red]❌ Login failed![/bold red]")
            self.login()
            return None

        # Display is handled in LoginHandler, so we just run
        self._handle_chat(session)
        session = None
        self.login()
        return session

    def _request_user_prompt(self) -> Optional[str]:
        user_prompt = Prompt.ask("\n[bold yellow]Enter your prompt[/bold yellow]").strip()
        if not is_non_empty_string(user_prompt):
            console.print("[bold red]❌ Prompt cannot be empty![/bold red]\n")
            return None
        return user_prompt

    def _handle_chat(self, session: object) -> None:
        """
        Runs a persistent multi-turn chat session.
        User stays in chat until they type /exit or /quit.
        Why a while loop here instead of in run()?
        Because this is the only place that knows we're in "chat mode".
        The run() loop handles menu navigation — it shouldn't know about
        chat-specific concepts like /exit commands.
        """
        console.print(
            Panel(
                "[bold green]💬 Chat Session Started[/bold green]\n"
                "[dim]Type [bold]/exit[/bold] or [bold]/quit[/bold] to return to the main menu.[/dim]",
                border_style="green",
                padding=(1, 2),
            )
        )
        # This loop IS the chat session
        awaiting_assessment_assignment = False
        while True:
            # Ask user for input using rich prompt
            user_prompt = Prompt.ask("\n[bold yellow]You[/bold yellow]").strip()
            # --- Exit commands ---
            if user_prompt.lower() in ("/exit", "/quit"):
                console.print(
                    Panel(
                        "[bold yellow]👋 Leaving chat session...[/bold yellow]",
                        border_style="yellow",
                        padding=(1, 1),
                    )
                )
                # Clear chat history for this user session
                ChatHistoryManager.reset()
                break   # ← exits the while loop, returns to run() main menu
            # --- Skip empty input ---
            if not user_prompt:
                console.print("[dim]Please type a message.[/dim]")
                continue   # ← loops back to ask again
            # --- Run the graph for this turn ---
            with console.status(
                "[bold magenta]🧠 AI Coach is thinking...[/bold magenta]",
                spinner="dots"
            ):
                extra_state = {}
                if awaiting_assessment_assignment:
                    extra_state["current_intent"] = "assessment_query"
                    awaiting_assessment_assignment = False

                response = self.ai_service.invoke(user_prompt, session.user_id, session, **extra_state)

            agent_response_str = response.get("agent_response", "")
            execution_path = response.get("execution_path", [])
            
            if "assessment_agent:ask_assignment" in execution_path:
                awaiting_assessment_assignment = True

            # --- Agentic assessment detection ---
            # If the graph returned a questions JSON payload, hand off to the assessment loop.
            # We try to parse agent_response as JSON and check for a 'questions' key.
            cleaned_response_str = agent_response_str.strip()
            if cleaned_response_str.startswith("```"):
                lines = cleaned_response_str.split("\n")
                if lines[0].startswith("```"): lines = lines[1:]
                if lines and lines[-1].startswith("```"): lines = lines[:-1]
                cleaned_response_str = "\n".join(lines).strip()

            try:
                parsed = json.loads(cleaned_response_str) if cleaned_response_str else {}
                if isinstance(parsed, dict) and ("questions" in parsed or "error" in parsed):
                    if "error" in parsed:
                        console.print(f"\n[bold red]❌ {parsed['error']}[/bold red]")
                    elif parsed.get("questions"):
                        assignment_id = parsed.get("assignment_id", "Unknown Assignment")
                        rag_context = response.get("retrieved_context", "")
                        self._run_conversational_assessment(
                            session,
                            parsed["questions"],
                            rag_context,
                            assignment_id
                        )
                    else:
                        console.print("[yellow]No questions found for this assignment.[/yellow]")
                    console.print(f"\n[dim italic]Path taken: {' ➡️ '.join(execution_path)}[/dim italic]\n")
                    continue   # back to chat prompt
            except (json.JSONDecodeError, TypeError):
                pass  # not JSON → treat as normal chat response

            # --- Normal chat response display ---
            console.print("\n[bold cyan]🤖 AI Coach:[/bold cyan]")
            if agent_response_str:
                console.print(agent_response_str)
            else:
                console.print("[red]Something went wrong with the graph![/red]")
            console.print(f"\n[dim italic]Path taken: {' ➡️ '.join(execution_path)}[/dim italic]\n")
            # Loop continues → user sees "You:" prompt again

    def _exit_application(self) -> None:
        console.print(
            Panel(
                "[bold green]🙏 Thank you for using Agentic Pathshala![/bold green]",
                border_style="green",
                padding=(1, 2),
            )
        )
        sys.exit(0)

    def _run_conversational_assessment(
        self,
        session: object,
        questions: list,
        rag_context: str,
        assignment_id: str
    ) -> None:
        """
        Drives the multi-turn conversational assessment loop.
        Called from _handle_chat when agent_response contains a 'questions' payload.
        """
        console.print(Panel(
            f"[bold green]📋 Assessment Started: {assignment_id}[/bold green]\n"
            f"[dim]{len(questions)} question(s). Answer each carefully.[/dim]",
            border_style="green",
            padding=(1, 2)
        ))
        scores = []
        for idx, q_data in enumerate(questions, start=1):
            question_text = q_data.get("question", "")
            correct_answer = q_data.get("correct_answer", "")
            # Show question
            console.print(Panel(
                question_text,
                title=f"[bold yellow]Question {idx} of {len(questions)}[/bold yellow]",
                border_style="yellow",
                padding=(1, 2)
            ))
            user_answer = Prompt.ask("[bold cyan]Your Answer[/bold cyan]").strip()
            if not user_answer:
                user_answer = "(no answer provided)"
            # Build evaluation payload
            eval_payload = json.dumps({
                "question": question_text,
                "correct_answer": correct_answer,
                "user_answer": user_answer
            })
            # Call graph in evaluate_answer mode
            with console.status("[bold magenta]Evaluating...[/bold magenta]", spinner="dots"):
                eval_response = self.ai_service.invoke(
                    user_input=eval_payload,
                    learner_id=session.user_id,
                    session=session,
                    assessment_mode="evaluate_answer",
                    assessment_assignment_id=assignment_id
                )
            eval_raw = eval_response.get("agent_response", "{}").strip()
            
            # Strip markdown fences if present
            if eval_raw.startswith("```"):
                lines = eval_raw.split("\n")
                if lines[0].startswith("```"): lines = lines[1:]
                if lines and lines[-1].startswith("```"): lines = lines[:-1]
                eval_raw = "\n".join(lines).strip()
                
            try:
                eval_data = json.loads(eval_raw)
            except json.JSONDecodeError:
                eval_data = {"score": 0, "max_score": 5, "reason": f"Evaluation parse error: {eval_raw}"}
            score = eval_data.get("score", 0)
            max_score = eval_data.get("max_score", 5)
            reason = eval_data.get("reason", "")
            scores.append({"question": question_text, "score": score, "max_score": max_score})
            console.print(Panel(
                f"[bold]Score:[/bold] {score}/{max_score}\n"
                f"[bold]Reason:[/bold] {reason}",
                title="[bold magenta]📊 Evaluation[/bold magenta]",
                border_style="magenta",
                padding=(1, 2)
            ))
        # --- Final Summary ---
        total = sum(s["score"] for s in scores)
        max_total = sum(s["max_score"] for s in scores)
        percentage = round((total / max_total) * 100) if max_total > 0 else 0
        score_lines = "\n".join(
            f"  Q{i+1}: {s['score']}/{s['max_score']}"
            for i, s in enumerate(scores)
        )
        console.print(Panel(
            f"[bold green]🎉 Assessment Complete![/bold green]\n\n"
            f"[bold]Question-wise Scores:[/bold]\n{score_lines}\n\n"
            f"[bold]Total:[/bold] {total}/{max_total}\n"
            f"[bold]Final Score:[/bold] {percentage}%",
            title="[bold cyan]📊 Results[/bold cyan]",
            border_style="cyan",
            padding=(1, 2)
        ))
        # --- Write progress via MCP ---
        try:
            from mcp_server.mcp_client import call_mcp_tool
            result = call_mcp_tool("update_learner_assignment_progress", {
                "learner_id": session.user_id,
                "assignment_id": assignment_id,
                "progress_percentage": percentage,
                "status": "completed"
            })
            if result.get("success"):
                console.print(f"[green]✅ Progress saved: {assignment_id} → {percentage}% (completed)[/green]\n")
            else:
                console.print(f"[yellow]⚠️ Could not save progress: {result.get('error')}[/yellow]\n")
        except Exception as e:
            console.print(f"[yellow]⚠️ Progress update failed: {e}[/yellow]\n")

if __name__ == "__main__":
    app = MainApp()
    app.login()