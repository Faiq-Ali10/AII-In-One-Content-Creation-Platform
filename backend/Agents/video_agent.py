from typing import TypedDict
from langgraph.graph import StateGraph

# 1. Import your specific Video Prompts 
from prompts.video.classification_prompt import classification_prompt_video
from prompts.video.refine_prompt1 import refine_prompt_image_for_video
from prompts.video.refine_prompt2 import refine_prompt_video

# 2. Import Models
from models.llm import LLM_Model
from models.image_gen import generate_image_data
from models.video_gen import generate_video_from_image_base64 

# 3. Define State
class VideoAgentState(TypedDict, total=False):
    original: str          # User's raw input
    previous: str          # Context
    classified: str        # VIDEO / NOT_VIDEO
    
    # Image Generation Data
    refined_image_prompt: str  # The "16:9 Cinematic" prompt
    image_b64: str             # The "First Frame" (Base64)
    
    # Video Generation Data
    refined_video_prompt: str  # The "Motion" prompt
    video_b64: str             # Final video result (Base64)
    
    size_choice: int       # Optional (Default to Landscape)

class VideoAgent():
    def __init__(self) -> None:
        pass

    # --- NODE 1: CLASSIFIER ---
    def classifier_node(self, state: VideoAgentState) -> VideoAgentState:
        prompt = classification_prompt_video(state.get("original", ""), state.get("previous", ""))
        
        print("@@Video Classifier@@\n")
        print(prompt)
        
        llm = LLM_Model(0.1).get_model()
        response = llm.invoke(prompt)
        
        state["classified"] = str(response.content)
        print(f"Decision: {state['classified']}\n@@Video Classifier@@")
        return state

    # --- NODE 2: IMAGE REFINER (First Frame) ---
    def image_refiner_node(self, state: VideoAgentState) -> VideoAgentState:
        # Uses the "16:9 / Wide Shot" prompt we designed
        prompt = refine_prompt_image_for_video(state.get("original", ""), state.get("previous", ""))
        
        llm = LLM_Model(0.7).get_model()
        response = llm.invoke(prompt)
        
        state["refined_image_prompt"] = str(response.content)
        print(f"@@Refined Image Prompt@@:\n{state['refined_image_prompt']}")
        return state

    # --- NODE 3: IMAGE GENERATOR ---
    def image_generator_node(self, state: VideoAgentState) -> VideoAgentState:
        prompt = state.get("refined_image_prompt")
        
        image_data = generate_image_data(prompt, 3) 
        
        state["image_b64"] = image_data
        print("@@Base Image Generated@@")
        return state

    # --- NODE 4: VIDEO MOTION REFINER ---
    def video_refiner_node(self, state: VideoAgentState) -> VideoAgentState:
        # Combines User Intent + The Image we just made
        user_input = state.get("original")
        image_context = state.get("refined_image_prompt")
        
        prompt = refine_prompt_video(user_input, image_context)
        
        llm = LLM_Model(0.5).get_model()
        response = llm.invoke(prompt)
        
        state["refined_video_prompt"] = str(response.content)
        print(f"@@Refined Video Prompt@@:\n{state['refined_video_prompt']}")
        return state

    # --- NODE 5: VIDEO GENERATOR ---
    def video_generator_node(self, state: VideoAgentState) -> VideoAgentState:
        image_b64 = state.get("image_b64")
        motion_prompt = state.get("refined_video_prompt")
        
        # Calls the function that uses Hugging Face / Fal.ai
        video_data = generate_video_from_image_base64(image_b64, motion_prompt)
        
        state["video_b64"] = video_data
        print("@@Video Generated@@")
        return state

    # --- GRAPH CONSTRUCTION ---
    def get_app(self):
        workflow = StateGraph(VideoAgentState)
        
        # Add Nodes
        workflow.add_node("classifier", self.classifier_node)
        workflow.add_node("image_refiner", self.image_refiner_node)
        workflow.add_node("image_generator", self.image_generator_node)
        workflow.add_node("video_refiner", self.video_refiner_node)
        workflow.add_node("video_generator", self.video_generator_node)
        
        # Conditional Edge Logic
        def check_video_intent(state):
            decision = state.get("classified", "").upper().strip()
            if "NOT" in decision:
                return "__end__"
            return "image_refiner"

        # Define Edges
        workflow.add_conditional_edges(
            "classifier",
            check_video_intent,
            {
                "image_refiner": "image_refiner",
                "__end__": "__end__"
            }
        )
        
        # Linear Chain: Image Refiner -> Gen Image -> Video Refiner -> Gen Video
        workflow.add_edge("image_refiner", "image_generator")
        workflow.add_edge("image_generator", "video_refiner")
        workflow.add_edge("video_refiner", "video_generator")
        workflow.add_edge("video_generator", "__end__")
        
        workflow.set_entry_point("classifier")
        
        return workflow.compile()