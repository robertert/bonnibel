class IntegrationException(Exception):
    """Базовое исключение для всех интеграций"""
    pass


class GitIntegrationException(IntegrationException):
    pass


class JiraIntegrationException(IntegrationException):
    pass


class ConfluenceIntegrationException(IntegrationException):
    pass