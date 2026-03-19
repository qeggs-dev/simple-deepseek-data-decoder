from pydantic import BaseModel

class FormatPackage(BaseModel):
    session: str = ""
    node: str = ""
    message: str = ""
    file: str = ""
    user_input: str = ""
    read_link: str = ""
    search: str = ""
    search_unit: str = ""
    thinking: str = ""
    ai_answer: str = ""