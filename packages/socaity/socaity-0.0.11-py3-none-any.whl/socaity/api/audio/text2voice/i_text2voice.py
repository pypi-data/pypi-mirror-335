from abc import abstractmethod
from typing import Union, List

import media_toolkit as mt
from fastsdk.jobs.threaded.internal_job import InternalJob
from media_toolkit import AudioFile
from socaity.api.utils import get_model_instance


class _BaseText2Voice:

    @abstractmethod
    def text2voice(self, text: str, *args, **kwargs) -> Union[mt.AudioFile, List[mt.AudioFile], None]:
        """
        Converts text to an image
        :param text: The text to convert to an image
        :return: The image
        """
        raise NotImplementedError("Please implement this method")


def text2voice(
        text: str, model="speechcraft", service="socaity", wait_for_result: bool = False, *args, **kwargs
) -> Union[InternalJob, AudioFile, List[AudioFile], str, None]:
    """
    Converts a given text to an spoken audio file.
    :param text: The text to convert to audio.
    :param model: The model to use for the conversion.
    :param service: The service to use for the conversion.
    :param wait_for_result: Whether to wait for the result. If False (default), returns the job.
    """
    from .speechcraft import SpeechCraft
    names_cl = {"speechcraft": SpeechCraft}
    mdl = get_model_instance(names_cl, model_name=model, service=service, default_instance=SpeechCraft)
    job = mdl.text2voice(text=text, *args, **kwargs)
    if wait_for_result:
        return job.get_result()
    return job
