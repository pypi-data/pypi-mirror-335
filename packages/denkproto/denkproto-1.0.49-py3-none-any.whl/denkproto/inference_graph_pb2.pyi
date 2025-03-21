import modelfile_v2_pb2 as _modelfile_v2_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ModelSource(_message.Message):
    __slots__ = ("from_proto", "from_network_id", "from_network_experiment_id")
    FROM_PROTO_FIELD_NUMBER: _ClassVar[int]
    FROM_NETWORK_ID_FIELD_NUMBER: _ClassVar[int]
    FROM_NETWORK_EXPERIMENT_ID_FIELD_NUMBER: _ClassVar[int]
    from_proto: _modelfile_v2_pb2.ModelFile
    from_network_id: str
    from_network_experiment_id: str
    def __init__(self, from_proto: _Optional[_Union[_modelfile_v2_pb2.ModelFile, _Mapping]] = ..., from_network_id: _Optional[str] = ..., from_network_experiment_id: _Optional[str] = ...) -> None: ...

class ConstTensorNode(_message.Message):
    __slots__ = ("name", "output", "shape", "uint64_data", "int64_data", "float64_data")
    class Uint64Array(_message.Message):
        __slots__ = ("data",)
        DATA_FIELD_NUMBER: _ClassVar[int]
        data: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, data: _Optional[_Iterable[int]] = ...) -> None: ...
    class Int64Array(_message.Message):
        __slots__ = ("data",)
        DATA_FIELD_NUMBER: _ClassVar[int]
        data: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, data: _Optional[_Iterable[int]] = ...) -> None: ...
    class Float64Array(_message.Message):
        __slots__ = ("data",)
        DATA_FIELD_NUMBER: _ClassVar[int]
        data: _containers.RepeatedScalarFieldContainer[float]
        def __init__(self, data: _Optional[_Iterable[float]] = ...) -> None: ...
    NAME_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    SHAPE_FIELD_NUMBER: _ClassVar[int]
    UINT64_DATA_FIELD_NUMBER: _ClassVar[int]
    INT64_DATA_FIELD_NUMBER: _ClassVar[int]
    FLOAT64_DATA_FIELD_NUMBER: _ClassVar[int]
    name: str
    output: str
    shape: _containers.RepeatedScalarFieldContainer[int]
    uint64_data: ConstTensorNode.Uint64Array
    int64_data: ConstTensorNode.Int64Array
    float64_data: ConstTensorNode.Float64Array
    def __init__(self, name: _Optional[str] = ..., output: _Optional[str] = ..., shape: _Optional[_Iterable[int]] = ..., uint64_data: _Optional[_Union[ConstTensorNode.Uint64Array, _Mapping]] = ..., int64_data: _Optional[_Union[ConstTensorNode.Int64Array, _Mapping]] = ..., float64_data: _Optional[_Union[ConstTensorNode.Float64Array, _Mapping]] = ...) -> None: ...

class GenerateNumberNode(_message.Message):
    __slots__ = ("name", "output", "min", "max")
    NAME_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    MIN_FIELD_NUMBER: _ClassVar[int]
    MAX_FIELD_NUMBER: _ClassVar[int]
    name: str
    output: str
    min: int
    max: int
    def __init__(self, name: _Optional[str] = ..., output: _Optional[str] = ..., min: _Optional[int] = ..., max: _Optional[int] = ...) -> None: ...

class AddNumbersNode(_message.Message):
    __slots__ = ("name", "input_number_1", "input_number_2", "output")
    NAME_FIELD_NUMBER: _ClassVar[int]
    INPUT_NUMBER_1_FIELD_NUMBER: _ClassVar[int]
    INPUT_NUMBER_2_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    name: str
    input_number_1: str
    input_number_2: str
    output: str
    def __init__(self, name: _Optional[str] = ..., input_number_1: _Optional[str] = ..., input_number_2: _Optional[str] = ..., output: _Optional[str] = ...) -> None: ...

class ImageResizeNode(_message.Message):
    __slots__ = ("name", "input_size", "input_image", "output")
    NAME_FIELD_NUMBER: _ClassVar[int]
    INPUT_SIZE_FIELD_NUMBER: _ClassVar[int]
    INPUT_IMAGE_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    name: str
    input_size: str
    input_image: str
    output: str
    def __init__(self, name: _Optional[str] = ..., input_size: _Optional[str] = ..., input_image: _Optional[str] = ..., output: _Optional[str] = ...) -> None: ...

class ImagePatchesNode(_message.Message):
    __slots__ = ("name", "input_image", "input_boxes", "input_batch_map", "input_target_size", "input_maximum_iterations", "output")
    NAME_FIELD_NUMBER: _ClassVar[int]
    INPUT_IMAGE_FIELD_NUMBER: _ClassVar[int]
    INPUT_BOXES_FIELD_NUMBER: _ClassVar[int]
    INPUT_BATCH_MAP_FIELD_NUMBER: _ClassVar[int]
    INPUT_TARGET_SIZE_FIELD_NUMBER: _ClassVar[int]
    INPUT_MAXIMUM_ITERATIONS_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    name: str
    input_image: str
    input_boxes: str
    input_batch_map: str
    input_target_size: str
    input_maximum_iterations: str
    output: str
    def __init__(self, name: _Optional[str] = ..., input_image: _Optional[str] = ..., input_boxes: _Optional[str] = ..., input_batch_map: _Optional[str] = ..., input_target_size: _Optional[str] = ..., input_maximum_iterations: _Optional[str] = ..., output: _Optional[str] = ...) -> None: ...

class VirtualCameraNode(_message.Message):
    __slots__ = ("name", "output", "path")
    NAME_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    name: str
    output: str
    path: str
    def __init__(self, name: _Optional[str] = ..., output: _Optional[str] = ..., path: _Optional[str] = ...) -> None: ...

class ImageClassificationNode(_message.Message):
    __slots__ = ("name", "input", "output", "model_source")
    NAME_FIELD_NUMBER: _ClassVar[int]
    INPUT_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    MODEL_SOURCE_FIELD_NUMBER: _ClassVar[int]
    name: str
    input: str
    output: str
    model_source: ModelSource
    def __init__(self, name: _Optional[str] = ..., input: _Optional[str] = ..., output: _Optional[str] = ..., model_source: _Optional[_Union[ModelSource, _Mapping]] = ...) -> None: ...

class ImageObjectDetectionNode(_message.Message):
    __slots__ = ("name", "input", "output", "model_source")
    NAME_FIELD_NUMBER: _ClassVar[int]
    INPUT_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    MODEL_SOURCE_FIELD_NUMBER: _ClassVar[int]
    name: str
    input: str
    output: str
    model_source: ModelSource
    def __init__(self, name: _Optional[str] = ..., input: _Optional[str] = ..., output: _Optional[str] = ..., model_source: _Optional[_Union[ModelSource, _Mapping]] = ...) -> None: ...

class ImageOcrNode(_message.Message):
    __slots__ = ("name", "input", "output", "model_source")
    NAME_FIELD_NUMBER: _ClassVar[int]
    INPUT_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    MODEL_SOURCE_FIELD_NUMBER: _ClassVar[int]
    name: str
    input: str
    output: str
    model_source: ModelSource
    def __init__(self, name: _Optional[str] = ..., input: _Optional[str] = ..., output: _Optional[str] = ..., model_source: _Optional[_Union[ModelSource, _Mapping]] = ...) -> None: ...

class BoundingBoxFilterNode(_message.Message):
    __slots__ = ("name", "input_threshold", "input_boxes", "output_boxes", "output_batch_map")
    NAME_FIELD_NUMBER: _ClassVar[int]
    INPUT_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    INPUT_BOXES_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_BOXES_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_BATCH_MAP_FIELD_NUMBER: _ClassVar[int]
    name: str
    input_threshold: str
    input_boxes: str
    output_boxes: str
    output_batch_map: str
    def __init__(self, name: _Optional[str] = ..., input_threshold: _Optional[str] = ..., input_boxes: _Optional[str] = ..., output_boxes: _Optional[str] = ..., output_batch_map: _Optional[str] = ...) -> None: ...

class Node(_message.Message):
    __slots__ = ("const_tensor_node", "generate_number_node", "add_numbers_node", "image_resize_node", "image_patches_node", "virtual_camera_node", "image_classification_node", "image_object_detection_node", "image_ocr_node", "bounding_box_filter_node")
    CONST_TENSOR_NODE_FIELD_NUMBER: _ClassVar[int]
    GENERATE_NUMBER_NODE_FIELD_NUMBER: _ClassVar[int]
    ADD_NUMBERS_NODE_FIELD_NUMBER: _ClassVar[int]
    IMAGE_RESIZE_NODE_FIELD_NUMBER: _ClassVar[int]
    IMAGE_PATCHES_NODE_FIELD_NUMBER: _ClassVar[int]
    VIRTUAL_CAMERA_NODE_FIELD_NUMBER: _ClassVar[int]
    IMAGE_CLASSIFICATION_NODE_FIELD_NUMBER: _ClassVar[int]
    IMAGE_OBJECT_DETECTION_NODE_FIELD_NUMBER: _ClassVar[int]
    IMAGE_OCR_NODE_FIELD_NUMBER: _ClassVar[int]
    BOUNDING_BOX_FILTER_NODE_FIELD_NUMBER: _ClassVar[int]
    const_tensor_node: ConstTensorNode
    generate_number_node: GenerateNumberNode
    add_numbers_node: AddNumbersNode
    image_resize_node: ImageResizeNode
    image_patches_node: ImagePatchesNode
    virtual_camera_node: VirtualCameraNode
    image_classification_node: ImageClassificationNode
    image_object_detection_node: ImageObjectDetectionNode
    image_ocr_node: ImageOcrNode
    bounding_box_filter_node: BoundingBoxFilterNode
    def __init__(self, const_tensor_node: _Optional[_Union[ConstTensorNode, _Mapping]] = ..., generate_number_node: _Optional[_Union[GenerateNumberNode, _Mapping]] = ..., add_numbers_node: _Optional[_Union[AddNumbersNode, _Mapping]] = ..., image_resize_node: _Optional[_Union[ImageResizeNode, _Mapping]] = ..., image_patches_node: _Optional[_Union[ImagePatchesNode, _Mapping]] = ..., virtual_camera_node: _Optional[_Union[VirtualCameraNode, _Mapping]] = ..., image_classification_node: _Optional[_Union[ImageClassificationNode, _Mapping]] = ..., image_object_detection_node: _Optional[_Union[ImageObjectDetectionNode, _Mapping]] = ..., image_ocr_node: _Optional[_Union[ImageOcrNode, _Mapping]] = ..., bounding_box_filter_node: _Optional[_Union[BoundingBoxFilterNode, _Mapping]] = ...) -> None: ...

class Graph(_message.Message):
    __slots__ = ("nodes", "created_at", "license_id")
    NODES_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    LICENSE_ID_FIELD_NUMBER: _ClassVar[int]
    nodes: _containers.RepeatedCompositeFieldContainer[Node]
    created_at: int
    license_id: str
    def __init__(self, nodes: _Optional[_Iterable[_Union[Node, _Mapping]]] = ..., created_at: _Optional[int] = ..., license_id: _Optional[str] = ...) -> None: ...
