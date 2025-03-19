import time
from typing import Union
import numpy as np
from fastsdk.jobs.threaded.internal_job import InternalJob
from fastsdk.fast_sdk import fastSDK, fastJob
from media_toolkit import ImageFile, VideoFile
from socaity.api.image.img2img.face2face.face2face_service_client import srvc_face2face


@fastSDK(api_client=srvc_face2face)
class Face2Face:
    def swap_img_to_img(
            self,
            source_img: Union[str, bytes, ImageFile],
            target_img: Union[str, bytes, ImageFile],
            enhance_face_model: Union[str, None] = 'gpen_bfr_512'
    ) -> InternalJob:
        """
        Swaps a face from source_img to target_img;
        in the manner that the face from source_img is placed on the face from target_img.
        :param source_img: Path to the image containing the face to be swapped.
            Or the image itself as bytes (with open(f): f.read()) .
        :param target_img: Path to the image containing the face to be swapped to.
            Or the image itself as bytes (with open(f): f.read()) .
        :param enhance_face_model: The face enhancement model_description to use. Use None for no enhancement.
        """
        return self._swap_img_to_img(
            source_img=source_img, target_img=target_img, enhance_face_model=enhance_face_model
        )

    def swap(
            self,
            faces: Union[str, dict, list],
            media: Union[str, bytes],
            enhance_face_model: Union[str, None] = 'gpen_bfr_512'
    ) -> InternalJob:
        return self._swap(faces=faces, media=media, enhance_face_model=enhance_face_model)

    def add_face(self, face_name: str, image: Union[str, bytes, ImageFile], save: bool = True) -> InternalJob:
        return self._add_face(face_name=face_name, image=image, save=save)

    def swap_video(
            self,
            face_name: str, target_video: Union[str, bytes, VideoFile], include_audio: bool = True,
            enhance_face_model: Union[str, None] = None #'gpen_bfr_512'
        ) -> InternalJob:
        return self._swap_video(face_name=face_name, target_video=target_video, include_audio=include_audio,
                                enhance_face_model=enhance_face_model)

    @fastJob
    def _swap_img_to_img(
            self,
            job: InternalJob,
            source_img: Union[np.array, bytes, str],
            target_img: Union[np.array, bytes, str],
            enhance_face_model: Union[str, None] = 'gpen_bfr_512'
    ) -> Union[ImageFile, None]:
        """
        Swaps a face from source_img to target_img;
        in the manner that the face from source_img is placed on the face from target_img.
        :param source_img: The image containing the face to be swapped. Read with open() -> f.read()
        :param target_img: The image containing the face to be swapped to. Read with open() -> f.read()
        """
        endpoint_request = job.request(
            endpoint_route="swap_img_to_img",
            source_img=source_img, target_img=target_img, enhance_face_model=enhance_face_model
        )
        result = endpoint_request.get_result()
        if endpoint_request.error is not None:
            raise Exception(f"Error in swap_one: {endpoint_request.error}")

        return result

    @fastJob
    def _swap(self, job, faces: Union[str, dict, list], media: bytes, enhance_face_model: str = 'gpen_bfr_512'):
        endpoint_request = job.request("swap", faces=faces, media=media, enhance_face_model=enhance_face_model)
        result = endpoint_request.get_result()
        if endpoint_request.error is not None:
            raise Exception(f"Error in swap: {endpoint_request.error}")

        return result

    @fastJob
    def _add_face(self, job, face_name: str, image: bytes, save: bool = True):
        endpoint_request = job.request("add_face", face_name=face_name, image=image, save=save)
        result = endpoint_request.get_result()
        if endpoint_request.error is not None:
            raise Exception(f"Error in add_reference_face: {endpoint_request.error}")

        return result

    @fastJob
    def _swap_video(
            self, job, face_name: str, target_video: str, include_audio: bool = True,
            enhance_face_model: str = 'gpen_bfr_512'
    ):
        request_result = job.request(
            "swap_video", face_name=face_name, target_video=target_video, include_audio=include_audio,
            enhance_face_model=enhance_face_model
        )

        # update progress bar
        while not request_result.is_finished():
            progress, message = request_result.progress
            job.set_progress(progress, message)
            time.sleep(0)

        if request_result.error is not None:
            raise Exception(f"Error in swap_video: {request_result.error}")

        return request_result.get_result()


if __name__ == "__main__":
    f2f = Face2Face(service="runpod")
    img_1 = "A:\\projects\\_face2face\\face2face\\test\\test_media\\test_face_1.jpg"
    img2 = "A:\\projects\\_face2face\\face2face\\test\\test_media\\test_face_2.jpg"

    job = f2f.swap_img_to_img(img_1, target_img=img2)
    job.run()
    result = job.get_result()
    print(result)
