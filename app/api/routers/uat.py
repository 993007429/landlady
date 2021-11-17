from typing import Optional

from fastapi import UploadFile, File, Depends, HTTPException, APIRouter

from app.api.dependencies.authentication import get_current_user_authorizer
from app.api.schemas.uat import UATStatusResponse
from app.db.models import User
from app.domain.services import errors
from app.domain.services.factory import ServiceFactory
from app.domain.services.project import ProjectService
from app.resources import strings

router = APIRouter()


@router.post(
    "/projects/{project_id}/uat/upload",
    response_model=UATStatusResponse,
    name="box:upload-in-uat",
)
async def upload_in_uat(
        project_id: int,
        bundle: Optional[UploadFile] = File(None),
        current_user: User = Depends(get_current_user_authorizer()),
        project_service: ProjectService = Depends(ServiceFactory.dependency(ProjectService))) -> UATStatusResponse:
    err_msg = None
    try:
        output = ''
        if bundle:
            output += project_service.deploy_uat(
                project_id, current_user.id, bundle)
        return UATStatusResponse(status=output)
    except errors.AdminOnlyOperationException:
        err_msg = strings.ADMIN_ONLY_OPERATION
    finally:
        if err_msg:
            raise HTTPException(
                status_code=400,
                detail=err_msg or '操作失败',
            )
