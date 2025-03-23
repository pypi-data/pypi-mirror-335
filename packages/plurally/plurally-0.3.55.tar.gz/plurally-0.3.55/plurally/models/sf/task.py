import enum

DEFAULT_PROPERTIES = "Subject,Status,Priority,Description,ActivityDate"
REQUIRED_PROPERTIES = ("Subject", "Status", "ActivityDate")


def query_statuses(service):
    return service.query("SELECT MasterLabel FROM TaskStatus")


def get_TaskStatuses(service):
    return enum.Enum(
        "TaskStatus",
        [status["MasterLabel"] for status in query_statuses(service)["records"]],
    )
