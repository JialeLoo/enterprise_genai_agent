from app.tools.deployments import get_deployment
from app.tools.incidents import get_incidents
from app.tools.knowledge import search_knowledge
from app.tools.logs import get_service_logs


ENTERPRISE_TOOLS = [
    get_deployment,
    get_incidents,
    get_service_logs,
    search_knowledge,
]