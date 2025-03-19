from enum import Enum
from typing import Dict


class Environment(str, Enum):
    LOCAL = "local"  # for docker-compose development
    CLOUD = "cloud"  # for kubernetes cloud deployment
    PYCHARM = "pycharm" # for local pycharm deployment
    QA = "qa"  # for QA environment
    IT = "it"  # for IT environment
    PROD = "prod"  # for production environment
    ONPREM = "onprem"  # for onprem environment

    @property
    def domain(self) -> str:
        """Get the domain for the current environment"""
        if self == Environment.LOCAL:
            return "app.kal-sense.kaleidoo-dev.com"
        elif self == Environment.QA:
            return "kal-sense.qa.kaleidoo-dev.com"
        elif self == Environment.IT:
            return "kal-sense.it.kaleidoo-dev.com"
        elif self == Environment.PROD:
            return "kal-sense.prod.kaleidoo-dev.com"
        elif self == Environment.CLOUD:
            return "kal-sense.cloud.kaleidoo-dev.com"  # Assuming cloud domain
        else:  # PYCHARM
            return "localhost"


# Service type prefixes
class ServiceType(str, Enum):
    KAL_SENSE = "kal-sense"
    SENSE_AI = "sense-ai-services"
    SENSE_AUDIO = "sense-audio"
    SENSE_CORE = "sense-core"


# List of all microservices in the system
class MicroService(str, Enum):
    # KAL-SENSE services
    API_GATEWAY = "api_gateway"
    FRONTEND = "frontend"
    ORGANIZATION_MANAGER = "organization_manager"
    PRODUCT_MANAGER = "product_manager"
    PROJECT_MANAGER = "project_manager"
    SERVICE_ACCOUNT_MANAGER = "service_account_manager"
    SYSTEM_SERVICE = "system_service"
    TAG_DESCRIPTION_MANAGER = "tag_description_manager"
    USER_CONVERSATION_MANAGER = "user_conversation_manager"
    USER_MANAGER = "user_manager"
    USER_PROJECT_MANAGER = "user_project_manager"
    
    # SENSE-AI services
    AI_DESCRIPTION = "ai_description"
    AI_TAGS = "ai_tags"
    BI = "bi"
    BUSINESS_RULES = "business_rules"
    CLOUD_NLP_SERVICES = "cloud_nlp_services"
    FACE_RECOGNITION = "face_recognition"
    INFO_EXTRACTOR = "info_extractor"
    LLM = "llm"
    NLP_MILVUS_SERVICE = "nlp_milvus_service"
    NLP_SERVICE = "nlp_service"
    OCR = "ocr"
    ORGANIZATIONAL_CHATBOT = "organizational_chatbot"
    SENTIMENT = "sentiment"
    SPEAKER_DIARIZATION = "speaker_diarization"
    THUMBNAIL = "thumbnail"
    TRANSCRIPTION = "transcription"
    TRANSLATION = "translation"
    VIDEO_CONVERTER = "video_converter"
    
    # SENSE-AUDIO services
    AUDIO_API_GATEWAY = "audio_api_gateway"
    AUDIO_PROJECT_MANAGER = "audio_project_manager"
    AUDIO_RULES_MANAGER = "audio_rules_manager"
    
    # SENSE-CORE services
    AUTOMATION_MANAGER = "automation_manager"
    CONNECTORS_SERVICE = "connectors_service"
    FILES_MANAGER = "files_manager"
    NOTIFICATIONS = "notifications"
    PROJECT_SOURCE_MANAGER = "project_source_manager"
    SCHEDULER_MANAGER = "scheduler_manager"
    SOCKET = "socket"
    TASK_MANAGER = "task_manager"
    USAGE_MANAGER = "usage_manager"
    
    # Other services
    RABBITMQ = "rabbitmq"
    ONPREM = "onprem"
    KEYCLOAK = "keycloak"
    MINIO = "minio"


# Mapping microservices to their service types
SERVICE_TYPE_MAP = {
    # KAL-SENSE services
    MicroService.API_GATEWAY: ServiceType.KAL_SENSE,
    MicroService.FRONTEND: ServiceType.KAL_SENSE,
    MicroService.ORGANIZATION_MANAGER: ServiceType.KAL_SENSE,
    MicroService.PRODUCT_MANAGER: ServiceType.KAL_SENSE,
    MicroService.PROJECT_MANAGER: ServiceType.KAL_SENSE,
    MicroService.SERVICE_ACCOUNT_MANAGER: ServiceType.KAL_SENSE,
    MicroService.SYSTEM_SERVICE: ServiceType.KAL_SENSE,
    MicroService.TAG_DESCRIPTION_MANAGER: ServiceType.KAL_SENSE,
    MicroService.USER_CONVERSATION_MANAGER: ServiceType.KAL_SENSE,
    MicroService.USER_MANAGER: ServiceType.KAL_SENSE,
    MicroService.USER_PROJECT_MANAGER: ServiceType.KAL_SENSE,
    
    # SENSE-AI services
    MicroService.AI_DESCRIPTION: ServiceType.SENSE_AI,
    MicroService.AI_TAGS: ServiceType.SENSE_AI,
    MicroService.BI: ServiceType.SENSE_AI,
    MicroService.BUSINESS_RULES: ServiceType.SENSE_AI,
    MicroService.CLOUD_NLP_SERVICES: ServiceType.SENSE_AI,
    MicroService.FACE_RECOGNITION: ServiceType.SENSE_AI,
    MicroService.INFO_EXTRACTOR: ServiceType.SENSE_AI,
    MicroService.LLM: ServiceType.SENSE_AI,
    MicroService.NLP_MILVUS_SERVICE: ServiceType.SENSE_AI,
    MicroService.NLP_SERVICE: ServiceType.SENSE_AI,
    MicroService.OCR: ServiceType.SENSE_AI,
    MicroService.ORGANIZATIONAL_CHATBOT: ServiceType.SENSE_AI,
    MicroService.SENTIMENT: ServiceType.SENSE_AI,
    MicroService.SPEAKER_DIARIZATION: ServiceType.SENSE_AI,
    MicroService.THUMBNAIL: ServiceType.SENSE_AI,
    MicroService.TRANSCRIPTION: ServiceType.SENSE_AI,
    MicroService.TRANSLATION: ServiceType.SENSE_AI,
    MicroService.VIDEO_CONVERTER: ServiceType.SENSE_AI,
    
    # SENSE-AUDIO services
    MicroService.AUDIO_API_GATEWAY: ServiceType.SENSE_AUDIO,
    MicroService.AUDIO_PROJECT_MANAGER: ServiceType.SENSE_AUDIO,
    MicroService.AUDIO_RULES_MANAGER: ServiceType.SENSE_AUDIO,
    
    # SENSE-CORE services
    MicroService.AUTOMATION_MANAGER: ServiceType.SENSE_CORE,
    MicroService.CONNECTORS_SERVICE: ServiceType.SENSE_CORE,
    MicroService.FILES_MANAGER: ServiceType.SENSE_CORE,
    MicroService.NOTIFICATIONS: ServiceType.SENSE_CORE,
    MicroService.PROJECT_SOURCE_MANAGER: ServiceType.SENSE_CORE,
    MicroService.SCHEDULER_MANAGER: ServiceType.SENSE_CORE,
    MicroService.SOCKET: ServiceType.SENSE_CORE,
    MicroService.TASK_MANAGER: ServiceType.SENSE_CORE,
    MicroService.USAGE_MANAGER: ServiceType.SENSE_CORE,
    
    # Special cases
    MicroService.RABBITMQ: "",  # Special handling for RabbitMQ
    MicroService.ONPREM: "",    # Special handling for onprem
    MicroService.KEYCLOAK: "",  # Special handling for keycloak
    MicroService.MINIO: "",     # Special handling for minio
}


# Mapping microservices to their default ports for LOCAL environment
DEFAULT_PORTS = {
    # Frontend (3000s)
    MicroService.FRONTEND: 3000,
    
    # KAL-SENSE services (8080-8089)
    MicroService.API_GATEWAY: 8080,
    MicroService.USER_MANAGER: 8081,
    MicroService.ORGANIZATION_MANAGER: 8082,
    MicroService.SYSTEM_SERVICE: 8083,
    MicroService.TAG_DESCRIPTION_MANAGER: 8084,
    MicroService.PROJECT_MANAGER: 8085,
    MicroService.SERVICE_ACCOUNT_MANAGER: 8086,
    MicroService.USER_PROJECT_MANAGER: 8087,
    MicroService.PRODUCT_MANAGER: 8088,
    MicroService.USER_CONVERSATION_MANAGER: 8089,
    
    # SENSE-CORE services (8090-8099)
    MicroService.FILES_MANAGER: 8090,
    MicroService.TASK_MANAGER: 8091,
    MicroService.AUDIO_RULES_MANAGER: 8093,
    MicroService.PROJECT_SOURCE_MANAGER: 8094,
    MicroService.SCHEDULER_MANAGER: 8095,
    MicroService.AUTOMATION_MANAGER: 8096,
    
    # SENSE-AUDIO services
    MicroService.AUDIO_PROJECT_MANAGER: 8089,
    MicroService.AUDIO_API_GATEWAY: 8080,
    
    # SENSE-AI services (8000-8050)
    MicroService.AI_DESCRIPTION: 8000,
    MicroService.LLM: 8000,
    MicroService.INFO_EXTRACTOR: 8000,
    MicroService.OCR: 8000,
    MicroService.THUMBNAIL: 8000,
    MicroService.VIDEO_CONVERTER: 8000,
    MicroService.NLP_SERVICE: 8002,
    MicroService.BUSINESS_RULES: 8003,
    MicroService.SENTIMENT: 8081,
    MicroService.AI_TAGS: 8084,
    MicroService.BI: 8084,
    MicroService.CLOUD_NLP_SERVICES: 8019,
    MicroService.FACE_RECOGNITION: 8009,
    MicroService.ORGANIZATIONAL_CHATBOT: 8044,
    MicroService.SPEAKER_DIARIZATION: 8043,
    MicroService.TRANSCRIPTION: 8412,
    MicroService.TRANSLATION: 8015,
    MicroService.NLP_MILVUS_SERVICE: 9991,
    
    # SPECIAL services (9000+)
    MicroService.KEYCLOAK: 9002,
    MicroService.MINIO: 9000,
    
    # Other services
    MicroService.RABBITMQ: 5672,
    MicroService.SOCKET: 8080,
    MicroService.USAGE_MANAGER: 8027,
    MicroService.NOTIFICATIONS: 8012,
}


def get_service_url(service_name: str, environment: Environment, port: int = 8080, 
                   service_type: str = "kal-sense") -> str:
    """
    Get service URL based on environment
    
    Parameters:
        service_name: Name of the microservice
        environment: Environment where the service is running
        port: Port number (default: 8080)
        service_type: Service type prefix for cloud deployment (default: "kal-sense")
        
    Returns:
        URL string for the service based on environment
    """
    if environment == Environment.CLOUD:
        normalized_name = service_name.replace("_", "-")  # Convert to hyphen for k8s
        # Get the string value of the service_type enum if it's an enum
        service_type_str = service_type.value if hasattr(service_type, 'value') else service_type
        return f"http://{service_type_str}-{normalized_name}-service:80"
    elif environment == Environment.PYCHARM:
        return f"http://0.0.0.0:{port}"  # Use localhost for PyCharm
    else:  # LOCAL, QA, IT, PROD
        domain = environment.domain
        if environment == Environment.LOCAL:
            normalized_name = service_name.replace("-", "_")  # Convert to underscore for docker
            return f"http://{normalized_name}:{port}"
        else:
            normalized_name = service_name.replace("_", "-")  # Convert to hyphen for web URLs
            return f"https://{normalized_name}.{domain}"


def get_microservice_url(service: MicroService, environment: Environment) -> str:
    """
    Get URL for a specific microservice based on environment
    
    Parameters:
        service: MicroService enum value
        environment: Current environment
        
    Returns:
        URL for the requested microservice
    """
    service_name = service.value
    service_type = SERVICE_TYPE_MAP.get(service, ServiceType.KAL_SENSE)
    
    # Handle special cases
    if service == MicroService.RABBITMQ:
        if environment == Environment.CLOUD:
            return "amqp://rabbitmq-service:5672"
        else:
            return "amqp://rabbitmq:5672"
    
    if service == MicroService.ONPREM:
        if environment == Environment.CLOUD:
            return "http://onprem-service"
        else:
            return "http://onprem:8080"
    
    if service == MicroService.KEYCLOAK:
        if environment == Environment.CLOUD:
            return "http://keycloak-service:9002"
        else:
            return "http://keycloak:9002"
    
    if service == MicroService.MINIO:
        if environment == Environment.CLOUD:
            return "http://minio-service:9000"
        else:
            return "http://minio:9000"
    
    # Get default port for local environment
    port = DEFAULT_PORTS.get(service, 8080)
    
    return get_service_url(service_name, environment, port, service_type)
