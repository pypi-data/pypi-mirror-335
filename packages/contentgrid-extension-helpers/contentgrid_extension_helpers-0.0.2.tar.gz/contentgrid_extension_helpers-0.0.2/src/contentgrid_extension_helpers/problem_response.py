from typing import Any, Dict, Mapping
from fastapi.responses import JSONResponse


def get_problem_dict(title: str | None, problem_type: str | None, status: int | None, detail: str | None, instance: str | None, **kwargs) -> Dict[str, Any]:
    result: Dict[str, Any] = dict()
    if title is not None:
        result["title"] = title
    if problem_type is not None:
        result["type"] = problem_type
    if status is not None:
        result["status"] = status
    if detail is not None:
        result["detail"] = detail
    if instance is not None:
        result["instance"] = instance

    for key, value in kwargs.items():
        if key == "type":
            raise ValueError(f"{key} is a reserved property name!")
        result[key] = value

    return result


class ProblemResponse(JSONResponse):
    def __init__(
            self,
            title: str | None = None,
            problem_type: str | None = "about:blank",  # not 'type' because it is a built-in function
            status: int = 400,
            detail: str | None = None,
            instance: str | None = None,
            headers: Mapping[str, str] | None = None,
            media_type: str | None = "application/problem+json",
            background: Any | None = None,
            **kwargs
    ):
        super().__init__(
            get_problem_dict(title, problem_type, status, detail, instance, **kwargs),
            status_code=status,
            headers=headers,
            media_type=media_type,
            background=background
        )