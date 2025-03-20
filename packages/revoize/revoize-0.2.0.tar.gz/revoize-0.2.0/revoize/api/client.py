import os
from time import sleep
from typing import Dict, List, Optional, Type, TypeVar, overload

import pydantic
import requests

from ..defaults import DEFAULT_REVOIZE_URL
from ..schema import (
    DownloadLink,
    Enhancement,
    EnhancementId,
    EnhancementParameters,
    EnhancementProcessStatus,
    EnhancementStatus,
    File,
    UploadDetails,
    UploadedFileMetadata,
    UserInfo,
)
from .exceptions import EnhancementTimeoutError, RequestError
from .utils import raise_if_response_not_ok, try_parse_response

ExtendsBaseModel = TypeVar("ExtendsBaseModel", bound=pydantic.BaseModel)


class RevoizeClient:

    default_ehnacement_timeout = 120
    batch_request_limit = 10

    def __init__(
        self,
        api_key: str,
        revoize_url: Optional[str] = None,
    ):
        # Signature of this method is using None instead of DEFAULT_* parameters
        # so that we can pass here None values from tests and CLI scripts. Otherwise,
        # we'd need to set those defaults in all those other places as well.
        self.revoize_url = revoize_url or DEFAULT_REVOIZE_URL
        self.api_key = api_key

    def get_user_info(self) -> UserInfo:
        return self._get_revoize(
            "/internal-api/users/me",
            error_message="Failed to retrieve user info from Revoize.",
            response_schema=UserInfo,
        )

    def enhance_file(
        self,
        input_file_path: str,
        output_file_path: str,
        enhancement_parameters: Optional[EnhancementParameters] = None,
        timeout: int = default_ehnacement_timeout,
    ):
        if enhancement_parameters is None:
            enhancement_parameters = EnhancementParameters()
        file = self.upload_file(input_file_path)
        enhancement = self.start_enhance(file, enhancement_parameters)
        self.await_enhancement(enhancement, timeout=timeout)
        self.download_enhanced_file(enhancement, output_file_path)

    def upload_file(self, input_file_path: str) -> File:
        file_name = os.path.basename(input_file_path)
        # TODO: make this support a multi-part upload when needed
        upload_details = self._initiate_upload(file_name, 1)
        file = File(id=upload_details.file_id, name=file_name)

        uploaded_file_data = self._upload_file(upload_details, input_file_path)
        self._complete_file_upload(file, uploaded_file_data)
        return file

    def _initiate_upload(self, filename: str, number_of_parts: int) -> UploadDetails:
        initiate_upload_body = {
            "fileName": filename,
            "numberOfParts": number_of_parts,
        }
        return self._post_revoize(
            "/internal-api/uploads",
            json=initiate_upload_body,
            error_message="Failed to initiate upload",
            response_schema=UploadDetails,
        )

    def _upload_file(
        self, upload_details: UploadDetails, file_path: str
    ) -> UploadedFileMetadata:
        with open(file_path, "rb") as uploaded_file:
            file_contents = uploaded_file.read()
        upload_url = upload_details.presigned_urls["1"]
        upload_url = self._replace_s3_url(upload_url)
        response = self._put_raw(
            upload_url,
            data=file_contents,
            error_message="Error uploading file",
        )

        return UploadedFileMetadata(
            upload_id=upload_details.upload_id, etag=response.headers["etag"]
        )

    def _replace_s3_url(self, source_url: str) -> str:
        return f"{self.revoize_url}/s3/{source_url.split('/', 3)[3]}"

    def _complete_file_upload(
        self,
        file: File,
        uploaded_file_metadata: UploadedFileMetadata,
    ):
        complete_file_upload_body = {
            "fileId": file.id,
            "fileName": file.name,
            "uploadedParts": [
                {
                    "partNumber": 1,
                    "etag": uploaded_file_metadata.etag,
                }
            ],
        }
        self._post_revoize(
            (f"/internal-api/uploads/{uploaded_file_metadata.upload_id}/complete"),
            json=complete_file_upload_body,
            error_message="Could not complete file upload",
        )
        return

    def start_enhance(
        self,
        uploaded_file: File,
        enhancement_parameters: Optional[EnhancementParameters] = None,
    ) -> EnhancementId:
        if enhancement_parameters is None:
            enhancement_parameters = EnhancementParameters()
        start_enhance_body = {
            "soundIntensity": 100,
            "voiceVolume": enhancement_parameters.loudness,
        }
        enhancement_id = self._post_revoize(
            f"/internal-api/files/{uploaded_file.id}/enhance",
            json=start_enhance_body,
            error_message="Error, could not trigger file enhancement",
            response_schema=EnhancementId,
        )
        return enhancement_id

    def get_all_enhancements(self) -> List[Enhancement]:
        enhancements = []
        for i in range(1, 1000):
            response = self._get_revoize(
                "/internal-api/enhancements",
                params={"page": i, "limit": self.batch_request_limit},
                error_message="Error when retrieving enhancement list",
            )
            response_json = response.json()
            enhancements += [Enhancement(**value) for value in response_json["results"]]
            if not response_json["hasNext"]:
                break
        else:
            raise RequestError(
                "Error when retrieving enhancement list. The loop reached a safety "
                "limit, there's more results than we can handle"
            )
        return enhancements

    def get_enhancement(self, enhancement: EnhancementId) -> EnhancementProcessStatus:
        return self._get_revoize(
            f"/internal-api/enhancements/{enhancement.id}",
            error_message="Error when retrieving enhancement",
            response_schema=EnhancementProcessStatus,
        )

    def await_enhancement(
        self,
        enhancement: EnhancementId,
        timeout: int = default_ehnacement_timeout,
    ) -> None:
        for _ in range(timeout):
            _enhancement = self.get_enhancement(enhancement)
            if _enhancement.status == EnhancementStatus.FINISHED:
                return
            sleep(1)
        # TODO: Improve description to indicate that enhancement might still succeed,
        # just the function checking the status timed out.
        raise EnhancementTimeoutError("Await for enhancement timed out.")

    def download_enhanced_file(
        self, enhancement: EnhancementId, output_file_path
    ) -> None:
        download_link_response = self._get_download_link(enhancement)
        download_url = self._replace_s3_url(download_link_response.link)
        response = self._get_raw(
            download_url, error_message="Error when trying to download enhanced file"
        )

        with open(output_file_path, "wb") as target_file:
            target_file.write(response.content)

    def _get_download_link(self, enhancement: EnhancementId) -> DownloadLink:
        return self._post_revoize(
            f"/internal-api/enhancements/{enhancement.id}/output-file-link",
            error_message="Error when trying to generate file download link",
            response_schema=DownloadLink,
        )

    @overload
    def _get_revoize(
        self,
        path,
        *args,
        error_message: str,
        response_schema: Type[ExtendsBaseModel],
        **kwargs,
    ) -> ExtendsBaseModel: ...

    @overload
    def _get_revoize(
        self,
        path,
        *args,
        error_message: str,
        **kwargs,
    ) -> requests.Response: ...

    def _get_revoize(
        self,
        path,
        *args,
        error_message: str,
        response_schema: Optional[Type[ExtendsBaseModel]] = None,
        **kwargs,
    ) -> requests.Response | ExtendsBaseModel:
        auth_header = self._get_auth_header()
        kwargs["headers"] = kwargs.get("headers", {}) | auth_header
        url = f"{self.revoize_url}{path}"
        response = self._get_raw(url, *args, error_message=error_message, **kwargs)
        if response_schema is not None:
            return try_parse_response(response, response_schema)
        return response

    @overload
    def _post_revoize(
        self,
        path,
        *args,
        error_message: str,
        response_schema: Type[ExtendsBaseModel],
        **kwargs,
    ) -> ExtendsBaseModel: ...

    @overload
    def _post_revoize(
        self,
        path,
        *args,
        error_message: str,
        **kwargs,
    ) -> requests.Response: ...

    def _post_revoize(
        self,
        path,
        *args,
        error_message: str,
        response_schema: Optional[Type[ExtendsBaseModel]] = None,
        **kwargs,
    ) -> requests.Response | ExtendsBaseModel:
        auth_header = self._get_auth_header()
        kwargs["headers"] = kwargs.get("headers", {}) | auth_header
        url = f"{self.revoize_url}{path}"
        response = self._post_raw(url, *args, error_message=error_message, **kwargs)
        if response_schema is not None:
            return try_parse_response(response, response_schema)
        return response

    def _get_auth_header(self) -> Dict[str, str]:
        return {"X-API-KEY": self.api_key}

    def _get_raw(self, *args, error_message: str, **kwargs) -> requests.Response:
        response = requests.get(*args, **kwargs)
        raise_if_response_not_ok(response, error_message)
        return response

    def _post_raw(self, *args, error_message: str, **kwargs) -> requests.Response:
        response = requests.post(*args, **kwargs)
        raise_if_response_not_ok(response, error_message)
        return response

    def _put_raw(self, *args, error_message: str, **kwargs) -> requests.Response:
        response = requests.put(*args, **kwargs)
        raise_if_response_not_ok(response, error_message)
        return response
