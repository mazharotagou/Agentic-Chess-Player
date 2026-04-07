from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from pydantic import BaseModel, Field
from typing import List


class Move(BaseModel):
    """Stores one legal candidate move."""
    move_code: str = Field(description="Universal Chess Interface notation of the move")
    reason: str = Field(description="Reason why this move was selected")


class MoveList(BaseModel):
    """Contains a list of best candidate moves."""
    move_list: List[Move] = Field(description="List of best legal moves")


class BestMove(BaseModel):
    """Contains the single best legal move in UCI notation."""
    best_move: str = Field(description="Best legal move in Universal Chess Interface notation")
    reason: str = Field(description="Reason why this move was selected as best")


@CrewBase
class ChessAgent:
    """ChessAgent crew"""

    agents_config = "agents.yaml"
    tasks_config = "tasks.yaml"

    @agent
    def chess_strategist(self) -> Agent:
        return Agent(
            config=self.agents_config["chess_strategist"],
            verbose=True,
            allow_code_execution=True,
        )

    @agent
    def chess_player(self) -> Agent:
        return Agent(
            config=self.agents_config["chess_player"],
            verbose=True,
        )

    @task
    def analyze_position(self) -> Task:
        return Task(
            config=self.tasks_config["analyze_position"],
            output_pydantic=MoveList,
        )

    @task
    def select_best_move(self) -> Task:
        return Task(
            config=self.tasks_config["select_best_move"],
            output_pydantic=BestMove,
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
