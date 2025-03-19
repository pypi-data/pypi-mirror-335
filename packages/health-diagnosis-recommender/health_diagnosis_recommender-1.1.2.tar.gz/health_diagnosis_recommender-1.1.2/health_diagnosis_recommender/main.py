from rich.prompt import Prompt
import os
from phi.utils.pprint import pprint_run_response
from phi.run.response import RunResponse, RunEvent
from phi.storage.workflow.sqlite import SqlWorkflowStorage
from health_diagnosis_recommender.workflow.healthcare_diagnosis_workflow import HealthcareDiagnosisWorkflow
from health_diagnosis_recommender.agents.cv_agent import CVAgent
from health_diagnosis_recommender.agents.nlp_agent import NLPAgent
from health_diagnosis_recommender.agents.diagnosis_generator import DiagnosisGenerator
from health_diagnosis_recommender.utils.logger import LoggerManager
from health_diagnosis_recommender.utils.cache import CacheManager


class HealthcareDiagnosisAgent:
    def __init__(self, session_id: str, storage: SqlWorkflowStorage):
        self.cv_agent = CVAgent()
        self.nlp_agent = NLPAgent()
        self.gen_ai_agent = DiagnosisGenerator()
        self.workflow = HealthcareDiagnosisWorkflow(self.cv_agent, self.nlp_agent, self.gen_ai_agent)
        self.session_id = session_id
        self.storage = storage
        self.logger = LoggerManager()
        self.cache_manager = CacheManager({})
    
    def run(self, image_path: str, use_cache: bool = True) -> RunResponse:
        self.logger.get_logger().info(f"Processing image: {image_path}")
        
        if use_cache:
            cached_response = self.cache_manager.cached(image_path)
            if cached_response:
                self.logger.get_logger().info("Found a cached diagnosis result")
                return RunResponse(content=cached_response, event=RunEvent.workflow_completed)
        
        results = self.workflow.cv_agent.get_disease_label(image_path)
        if results is None:
            return RunResponse(event=RunEvent.workflow_completed, response="No CV data found")
        
        symptoms = self.workflow.nlp_agent.extract_symptoms(image_path, results)
        if symptoms is None:
            return RunResponse(event=RunEvent.workflow_completed, response="No symptoms found")
        
        diagnosis = self.workflow.gen_ai_agent.generate_diagnosis(image_path, results, symptoms)
        if diagnosis is None:
            return RunResponse(event=RunEvent.workflow_completed, response="No diagnosis generated")
        
        return RunResponse(content=diagnosis, event=RunEvent.workflow_completed)

if __name__ == "__main__":
    file_path = Prompt.ask("[bold]Enter the path to your local file[/bold]\n📂")

    if not os.path.exists(file_path):
        print("❌ Error: The file path does not exist. Please enter a valid path.")
        exit()

    summarizer = HealthcareDiagnosisAgent(
        session_id=f"Image Diagnosis - {file_path.replace(':', '').replace('\\', '_').replace('\\', '_')}",
        storage=SqlWorkflowStorage(
            table_name="Image Diagnosis Results",
            db_file="tmp/workflows.db",
        ),
    )

    # Run the summarizer with the local file
    summary = summarizer.run(image_path=file_path, use_cache=True)
    pprint_run_response(summary, markdown=True)
