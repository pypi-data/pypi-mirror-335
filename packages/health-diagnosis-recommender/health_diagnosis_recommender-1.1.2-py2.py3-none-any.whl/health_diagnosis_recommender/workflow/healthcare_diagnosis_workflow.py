from phi.workflow.workflow import Workflow
from ..agents.cv_agent import CVAgent
from ..agents.nlp_agent import NLPAgent 
from ..agents.diagnosis_generator import DiagnosisGenerator
from ..utils.logger import LoggerManager
from ..utils.cache import CacheManager

class HealthcareDiagnosisWorkflow(Workflow):
    
    workflow_name: str = "Healthcare_Diagnosis_Workflow"
    session_state: dict
    cv_agent: CVAgent
    nlp_agent: NLPAgent
    gen_ai_agent: DiagnosisGenerator
    cache_manager: CacheManager
    logger: LoggerManager
    model_config = {
        "arbitrary_types_allowed": True  
    }

    def __init__(self, cv_agent: CVAgent, nlp_agent: NLPAgent, gen_ai_agent: DiagnosisGenerator):
        
        super().__init__(
            cv_agent=cv_agent,
            nlp_agent=nlp_agent,
            gen_ai_agent=gen_ai_agent,
            cache_manager=CacheManager({}),
            session_state={},
            logger = LoggerManager()
        )