"""File Schemas."""
from pydantic import BaseModel


class File(BaseModel):
    """File.

    Attributes:
        id (str): The id of the file.
        file_name (str): The name of the file.
        file_for (str): The file for.
        file_type (str): The type of the file.
        file_size (str): The size of the file.
        organization_id (str): The id of the organization.
        user_id (str): The id of the user.
        request_type (str): The type of request.
        is_deleted (bool): The status of the file.
        date_created (str): The date the file was created.
        last_updated (str): The last date the file was updated.
    """

    file_for: str
    file_size: str
    organization_id: str
    user_id: str
    request_type: str
    is_deleted: bool


class FileResponse(File):
    """File Response.

    Attributes:
        url (str): The url of the file.
    """

    id: str
    file_name: str
    file_type: str
