from typing import TypedDict
from langgraph.graph import StateGraph

# Import Image-specific prompts (Make sure these files exist)
from prompts.image.classification_prompt import classification_prompt_image
from prompts.image.refine_prompt import image_refine_prompt

# Import Models
from models.llm import LLM_Model
from models.image_gen import generate_image_data

class AgentState(TypedDict, total=False):
    original: str
    classified: str
    refined: str
    image_b64: str   # Stores Base64 string instead of bytes/url
    previous: str
    size_choice: int # Specific to images

class ImageAgent():
    def __init__(self) -> None:
        # Initialize LLM (we create new instances in nodes, but good for setup)
        self.llm = LLM_Model(0.1).get_model()
        return None

    def classifier_node(self, state: AgentState) -> AgentState:
        # 1. Generate Prompt
        prompt = classification_prompt_image(str(state.get("original")), str(state.get("previous")))
        
        print("@@Img Classifier@@\n")
        print(prompt)
        print("@@Img Classifier@@\n")
        
        # 2. Invoke LLM
        llm = LLM_Model(0.2).get_model()
        response = llm.invoke(prompt)
        
        print("@@Img Classifier_response@@\n")
        print(response.content)
        print("@@Img Classifier_response@@\n")

        # 3. Update State
        state["classified"] = str(response.content)
        return state

    def refiner_node(self, state: AgentState) -> AgentState:
        # 1. Generate Prompt
        prompt = image_refine_prompt(str(state.get("original")), str(state.get("previous")))
        
        print("@@Img Refiner@@\n")
        print(prompt)
        print("@@Img Refiner@@\n")
        
        # 2. Invoke LLM
        llm = LLM_Model(0.5).get_model() # Higher temp for creativity
        response = llm.invoke(prompt)
        
        print("@@Img Refiner_response@@\n")
        print(response.content)
        print("@@Img Refiner_response@@\n")

        # 3. Update State
        state["refined"] = str(response.content)
        return state
    
    def generate_image_node(self, state: AgentState) -> AgentState:
        # Get inputs
        prompt = str(state.get("refined"))
        choice = state.get("size_choice", 3) # Default to 3 if missing
        
        # Call the Image Generator
        # Returns Base64 string
        image_data = generate_image_data(prompt, choice)
        
        # Update State
        state["image_b64"] = image_data
        return state
    
    def get_app(self):
        workflow = StateGraph(AgentState)
        
        # Add Nodes
        workflow.add_node("classifier", self.classifier_node)
        workflow.add_node("refiner", self.refiner_node)
        workflow.add_node("generator", self.generate_image_node)
        
        # Logic Check Function
        def check_image_classification(state):
            decision = state.get("classified").strip().upper().replace(".", "")
            # Logic: If it IS "IMAGE" and NOT "NOT_IMAGE"
            if "NOT" in decision:
                return "__end__"
            if "IMAGE" in decision:
                return "refiner"
            return "__end__"

        # Add Edges
        workflow.add_conditional_edges(
            "classifier",
            check_image_classification,
            {
                "refiner": "refiner",
                "__end__": "__end__",
            }
        )
        
        workflow.add_edge("refiner", "generator")
        
        workflow.set_entry_point("classifier")
        workflow.set_finish_point("generator")
        
        app = workflow.compile()
        
        return app