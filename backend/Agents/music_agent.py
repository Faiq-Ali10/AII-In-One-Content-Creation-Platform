from typing import TypedDict
from prompts.music.classification_prompt import classification_prompt
from prompts.music.refine_prompt import refine_prompt
from models.llm import LLM_Model
from models.music import generate_music
from langgraph.graph import StateGraph

class AgentState(TypedDict, total=False):
    original: str
    classified: str
    refined: str
    music : bytes
    previous : str

class MusicAgent():
    def __init__(self) -> None:
        self.llm = LLM_Model(0.1).get_model()
        return None

    def classifier_node(self, state: AgentState) -> AgentState:
        prompt = classification_prompt(str(state.get("original")), str(state.get("previous")))
        print("@@Classifier@@\n")
        print(prompt)
        print("@@Classifier@@\n")
        llm = LLM_Model(0.2).get_model()
        response = llm.invoke(prompt)
        print("@@Classifier_response@@\n")
        print(response.content)
        print("@@Classifier_response@@\n")

        state["classified"] = str(response.content)
        return state

    def refiner_node(self, state: AgentState) -> AgentState:
        prompt = refine_prompt(str(state.get("original")), str(state.get("previous")))
        print("@@refiner@@\n")
        print(prompt)
        print("@@refiner@@\n")
        llm = LLM_Model(0.5).get_model()
        response = llm.invoke(prompt)
        print("@@refiner_response@@\n")
        print(response.content)
        print("@@refiner_response@@\n")

        state["refined"] = str(response.content)
        return state
    
    def generate_music_node(self, state: AgentState) -> AgentState:
        music = generate_music(str(state.get("refined")))
        
        state["music"] = music
        return state
    
    def get_app(self):
        workflow = StateGraph(AgentState)
        
        workflow.add_node("classifier", self.classifier_node)
        workflow.add_node("refiner", self.refiner_node)
        workflow.add_node("generator", self.generate_music_node)
        
        workflow.add_conditional_edges(
            "classifier",
            lambda state : "refiner" if state.get("classified").strip().upper().replace(".", "") == "MUSIC" else "__end__",
            {
                "refiner" : "refiner",
                "__end__" : "__end__",
            }
        )
        
        workflow.add_edge("refiner", "generator")
        
        workflow.set_entry_point("classifier")
        workflow.set_finish_point("generator")
        
        app = workflow.compile()
        
        # with open("graph.png", "wb") as file:
        #     file.write(app.get_graph().draw_mermaid_png())
            
        return app
