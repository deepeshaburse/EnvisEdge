"""
Defines custom serializers and deserializers for different objects
"""

import pickle
import torch
from abc import ABC, abstractmethod

from fedrec.utilities import registry
from fedrec.utilities.serialization import load_tensor, save_tensor
from fedrec.utilities.saver_utilities import download_s3_file, is_s3_file



class AbstractSerializer(ABC):

    @abstractmethod
    @staticmethod
    def serialize(obj, file=None):
        threshold = int(1e7)
        # Override this method for custom implementation for a class.
        pkl_str = io.BytesIO()
        with open(file, "wb"):
            pickle.dump(obj, pkl_str)
        # The pkl string is too long to pass to the kafka message queue, write the string
        # to the file and upload it to the cloud.
        if file and len(list(pkl_str) > threshold:
            with open(file, "wb") as fd:
                fd.write(pkl_str.read())
            return file

        return pkl_str


    @abstractmethod
    @staticmethod
    def deserializer(obj):
        # Override this method for custom implementation for a class.
        pkl_str = io.BytesIO(obj)
        with open(file, "wb") as fd:
            deserialized_obj = pickle.load(pkl_str)
        return deserialized_obj


@registry.load("serializer", torch.Tensor.__name__)
class TensorSerializer(AbstractSerializer):

    @staticmethod
    def serialize(obj, file=None):
        if file:
            # if file is provided, save the tensor to the file and return the file path.
            save_tensor(obj, file)
            return file
        else:
            # create a buffer Bytes object, which can be used to write to the file.
            buffer = io.BytesIO()
            save_tensor(obj, buffer)
            return buffer

    @staticmethod
    def deserialize(obj):
        data_file = None
        if is_s3_file(obj):
            # This is most likely to be a link of s3 storage.
            # Copy the file locally and then deserialize it.
            data_file = download_s3_file(obj)
        if isinstance(obj, io.BytesIO):
            data_file = obj

        try:
            # This should be the path to the tensor object.
            tensor = load_tensor(obj, device=None)
        except Exception as e:
            raise ValueError("the filename specified to load the tensor from could not be accessed,Please make sure the path has correct permissions")
        else:
            return tensor
