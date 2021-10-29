import asyncio
import os
from asyncio import CancelledError
from subprocess import CalledProcessError
from typing import Optional

from fastapi import APIRouter, Query, Depends, HTTPException, UploadFile, File
from sse_starlette.sse import EventSourceResponse
from starlette.responses import FileResponse, PlainTextResponse

from app.api.dependencies.authentication import get_current_user_authorizer
from app.api.schemas.box import BoxResponse, BoxStatusResponse
from app.api.schemas.common import ModelListResponse
from app.db.models.user import User
from app.domain.entities.box import BoxEntity
from app.domain.services import errors
from app.domain.services.box import BoxService, BoxOperation
from app.domain.services.factory import ServiceFactory
from app.resources import strings

router = APIRouter()


@router.get(
    "/projects/{project_id}/boxes",
    response_model=ModelListResponse[BoxEntity],
    name="box:get-box-list",
)
async def get_box_list(
        project_id: int,
        limit: int = Query(20, ge=1),
        offset: int = Query(0, ge=0),
        box_service: BoxService = Depends(ServiceFactory.dependency(BoxService))) -> ModelListResponse[BoxEntity]:
    boxes = box_service.get_boxes_by_project(project_id, offset, limit)
    return ModelListResponse(
        list=boxes,
        start=offset,
        perpage=limit,
        total=len(boxes)
    )


@router.put(
    '/projects/{project_id}/boxes/{box_id}',
    response_model=BoxResponse,
    name='box:update-box',
)
async def update_box(
        box_id: int,
        project_id: int,
        operation: BoxOperation,
        current_user: Optional[User] = Depends(get_current_user_authorizer()),
        box_service: BoxService = Depends(ServiceFactory.dependency(BoxService))) -> BoxResponse:
    box, error_msg = None, None
    try:
        box = box_service.operate_box(
            box_id=box_id, project_id=project_id, user_id=current_user.id, operation=operation)
    except errors.EntityDoesNotExist:
        error_msg = strings.BOX_NOT_EXIST
    except errors.BoxUnavailableException:
        error_msg = strings.BOX_UNAVAILABLE
    except errors.WrongBoxException:
        error_msg = strings.WRONG_BOX
    except errors.WrongProjectException:
        error_msg = strings.WRONG_PROJECT
    finally:
        if box:
            res = BoxResponse(box=box)
            return res
        else:
            raise HTTPException(
                status_code=400,
                detail=error_msg or '操作失败',
            )


@router.post(
    "/projects/{project_id}/boxes/{box_id}/upload",
    response_model=BoxStatusResponse,
    name="box:upload-in-box",
)
async def upload_in_box(
        box_id: int,
        project_id: int,
        bundle: Optional[UploadFile] = File(None),
        fe_bundle: Optional[UploadFile] = File(None),
        current_user: Optional[User] = Depends(get_current_user_authorizer()),
        box_service: BoxService = Depends(ServiceFactory.dependency(BoxService))) -> BoxStatusResponse:
    err_msg = None
    try:
        output = ''
        if bundle:
            output += box_service.deploy_in_box(
                box_id, project_id, current_user.id, bundle)
        if fe_bundle:
            output += box_service.deploy_in_box(
                box_id, project_id, current_user.id, fe_bundle)
        box = box_service.get_box(box_id)
        return BoxStatusResponse(status=output, box=box)
    except errors.EntityDoesNotExist:
        err_msg = strings.BOX_NOT_EXIST
    except errors.WrongProjectException:
        err_msg = strings.WRONG_PROJECT
    except errors.BoxUnavailableException:
        err_msg = strings.BOX_UNAVAILABLE
    finally:
        if err_msg:
            raise HTTPException(
                status_code=400,
                detail=err_msg or '操作失败',
            )


@router.get(
    "/projects/{project_id}/boxes/{box_id}/app_log",
    name="box:app-log-in-box",
)
async def get_logs(
        box_id: int,
        project_id: int,
        process_num: int = 0,
        box_service: BoxService = Depends(ServiceFactory.dependency(BoxService))):
    box = box_service.get_box(box_id)
    if not box:
        raise HTTPException(
            status_code=404,
            detail='日志不存在',
        )

    try:
        box_service.check_project(box.project.id, project_id)
    except errors.WrongProjectException:
        raise HTTPException(status_code=403, detail=strings.WRONG_PROJECT)

    file_path = box.log_file(process_num=process_num)

    async def log_generator():
        with open(file_path, 'rb') as file:
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(- min(1000, file_size), os.SEEK_END)
            while True:
                line = file.readline()
                try:
                    if line:
                        yield line.decode("utf-8")
                    else:
                        await asyncio.sleep(1)
                except CancelledError:
                    break

    event_generator = log_generator()
    return EventSourceResponse(event_generator)


@router.get(
    "/projects/{project_id}/boxes/{box_id}/files/list",
    name="box:list-files-in-box",
    response_class=PlainTextResponse,
)
async def list_files(
        box_id: int,
        path: str = '',
        box_service: BoxService = Depends(ServiceFactory.dependency(BoxService))):
    try:
        return box_service.list_files(box_id, path)
    except errors.EntityDoesNotExist:
        raise HTTPException(
            status_code=404,
            detail=f'box(id={box_id})不存在',
        )
    except CalledProcessError:
        return ''


@router.get(
    "/projects/{project_id}/boxes/{box_id}/files/content",
    name="box:show-file-content-in-box",
    response_class=FileResponse
)
async def show_file(
        box_id: int,
        filename: str,
        box_service: BoxService = Depends(ServiceFactory.dependency(BoxService))):
    box = box_service.get_box(box_id)
    if not box:
        raise HTTPException(
            status_code=404,
            detail=f'box(id={box_id})不存在',
        )

    return f'{box.box_dir}/{filename}'
