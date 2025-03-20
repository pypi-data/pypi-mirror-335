# __version__= "040001.5.1"
# __version_imas_dd__= "4.0.0-71-gf671395"
# __imas_dd_git_commit__= "f671395e0d3a530a942c6d332553acfa94de8d94"
# __imas_dd_git_branch__= "develop"
#
from ..dataclasses_idsschema import idspy_dataclass, IdsBaseClass, StructArray
from dataclasses import field
import numpy as np
from typing import Optional


@idspy_dataclass(repr=False, slots=True)
class SignalFlt6D(IdsBaseClass):
    """

    :ivar data : Data
    :ivar time : Time
    """

    class Meta:
        name = "signal_flt_6d"
        is_root_ids = False

    data: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 6, dtype=float),
        metadata={
            "imas_type": "FLT_6D",
            "ndims": 6,
            "coordinates": {
                "coordinate1": "as_parent",
                "coordinate2": "as_parent",
                "coordinate3": "as_parent",
                "coordinate4": "as_parent",
                "coordinate5": "as_parent",
                "coordinate6": "../time",
            },
            "field_type": np.ndarray,
        },
    )
    time: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "flt_1d_type",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SignalFlt2D(IdsBaseClass):
    """

    :ivar data : Data
    :ivar time : Time
    """

    class Meta:
        name = "signal_flt_2d"
        is_root_ids = False

    data: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "as_parent",
                "coordinate2": "../time",
            },
            "field_type": np.ndarray,
        },
    )
    time: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "flt_1d_type",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SignalInt3D(IdsBaseClass):
    """

    :ivar data : Data
    :ivar time : Time
    """

    class Meta:
        name = "signal_int_3d"
        is_root_ids = False

    data: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=int),
        metadata={
            "imas_type": "INT_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "as_parent",
                "coordinate2": "as_parent",
                "coordinate3": "../time",
            },
            "field_type": np.ndarray,
        },
    )
    time: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "flt_1d_type",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SignalFlt5D(IdsBaseClass):
    """

    :ivar data : Data
    :ivar time : Time
    """

    class Meta:
        name = "signal_flt_5d"
        is_root_ids = False

    data: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 5, dtype=float),
        metadata={
            "imas_type": "FLT_5D",
            "ndims": 5,
            "coordinates": {
                "coordinate1": "as_parent",
                "coordinate2": "as_parent",
                "coordinate3": "as_parent",
                "coordinate4": "as_parent",
                "coordinate5": "../time",
            },
            "field_type": np.ndarray,
        },
    )
    time: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "flt_1d_type",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SignalFlt1D(IdsBaseClass):
    """

    :ivar data : Data
    :ivar time : Time
    """

    class Meta:
        name = "signal_flt_1d"
        is_root_ids = False

    data: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../time"},
            "field_type": np.ndarray,
        },
    )
    time: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "flt_1d_type",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SignalFlt3D(IdsBaseClass):
    """

    :ivar data : Data
    :ivar time : Time
    """

    class Meta:
        name = "signal_flt_3d"
        is_root_ids = False

    data: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "as_parent",
                "coordinate2": "as_parent",
                "coordinate3": "../time",
            },
            "field_type": np.ndarray,
        },
    )
    time: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "flt_1d_type",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SignalFlt4D(IdsBaseClass):
    """

    :ivar data : Data
    :ivar time : Time
    """

    class Meta:
        name = "signal_flt_4d"
        is_root_ids = False

    data: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 4, dtype=float),
        metadata={
            "imas_type": "FLT_4D",
            "ndims": 4,
            "coordinates": {
                "coordinate1": "as_parent",
                "coordinate2": "as_parent",
                "coordinate3": "as_parent",
                "coordinate4": "../time",
            },
            "field_type": np.ndarray,
        },
    )
    time: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "flt_1d_type",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SignalInt2D(IdsBaseClass):
    """

    :ivar data : Data
    :ivar time : Time
    """

    class Meta:
        name = "signal_int_2d"
        is_root_ids = False

    data: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=int),
        metadata={
            "imas_type": "INT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "as_parent",
                "coordinate2": "../time",
            },
            "field_type": np.ndarray,
        },
    )
    time: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "flt_1d_type",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SignalInt1D(IdsBaseClass):
    """

    :ivar data : Data
    :ivar time : Time
    """

    class Meta:
        name = "signal_int_1d"
        is_root_ids = False

    data: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=int),
        metadata={
            "imas_type": "INT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../time"},
            "field_type": np.ndarray,
        },
    )
    time: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "flt_1d_type",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class IdsProvenanceNodeReference(IdsBaseClass):
    """

    :ivar name : Reference name
    :ivar timestamp : Date and time (UTC) at which the reference was created, expressed in a human readable form (ISO 8601) : the format of the string shall be : YYYY-MM-DDTHH:MM:SSZ. Example : 2020-07-24T14:19:00Z
    """

    class Meta:
        name = "ids_provenance_node_reference"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    timestamp: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )


@idspy_dataclass(repr=False, slots=True)
class IdsProvenanceNode(IdsBaseClass):
    """

    :ivar path : Path of the node within the IDS, following the syntax given in the link below. If empty, means the provenance information applies to the whole IDS.
    :ivar reference : List of references used to populate or calculate this node, identified as explained below. In case the node is the result of of a calculation / data processing, the reference is an input to the process described in the &#34;code&#34; structure at the root of the IDS. The reference can be an IDS (identified by a URI or a persitent identifier, see syntax in the link below) or non-IDS data imported directly from an non-IMAS database (identified by the command used to import the reference, or the persistent identifier of the data reference). Often data are obtained by a chain of processes, however only the last process input are recorded here. The full chain of provenance has then to be reconstructed recursively from the provenance information contained in the data references.
    """

    class Meta:
        name = "ids_provenance_node"
        is_root_ids = False

    path: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    reference: Optional[IdsProvenanceNodeReference] = field(
        default_factory=lambda: StructArray(
            type_input=IdsProvenanceNodeReference
        ),
        metadata={
            "imas_type": "ids_provenance_node_reference",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": IdsProvenanceNodeReference,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class IdsProvenance(IdsBaseClass):
    """

    :ivar node : Set of IDS nodes for which the provenance is given. The provenance information applies to the whole structure below the IDS node. For documenting provenance information for the whole IDS, set the size of this array of structure to 1 and leave the child &#34;path&#34; node empty
    """

    class Meta:
        name = "ids_provenance"
        is_root_ids = False

    node: Optional[IdsProvenanceNode] = field(
        default_factory=lambda: StructArray(type_input=IdsProvenanceNode),
        metadata={
            "imas_type": "ids_provenance_node",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": IdsProvenanceNode,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class Library(IdsBaseClass):
    """

    :ivar name : Name of software
    :ivar description : Short description of the software (type, purpose)
    :ivar commit : Unique commit reference of software
    :ivar version : Unique version (tag) of software
    :ivar repository : URL of software repository
    :ivar parameters : List of the code specific parameters in XML format
    """

    class Meta:
        name = "library"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    description: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    commit: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    version: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    repository: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    parameters: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )


@idspy_dataclass(repr=False, slots=True)
class IdsProperties(IdsBaseClass):
    """

    :ivar comment : Any comment describing the content of this IDS
    :ivar name : User-defined name for this IDS occurrence
    :ivar homogeneous_time : This node must be filled (with 0, 1, or 2) for the IDS to be valid. If 1, the time of this IDS is homogeneous, i.e. the time values for this IDS are stored in the time node just below the root of this IDS. If 0, the time values are stored in the various time fields at lower levels in the tree. In the case only constant or static nodes are filled within the IDS, homogeneous_time must be set to 2
    :ivar provider : Name of the person in charge of producing this data
    :ivar creation_date : Date at which this data has been produced
    :ivar provenance : Provenance information about this IDS
    """

    class Meta:
        name = "ids_properties"
        is_root_ids = False

    comment: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    homogeneous_time: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    provider: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    creation_date: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    provenance: Optional[IdsProvenance] = field(
        default=None,
        metadata={"imas_type": "ids_provenance", "field_type": IdsProvenance},
    )


@idspy_dataclass(repr=False, slots=True)
class Code(IdsBaseClass):
    """

    :ivar name : Name of software generating IDS
    :ivar description : Short description of the software (type, purpose)
    :ivar commit : Unique commit reference of software
    :ivar version : Unique version (tag) of software
    :ivar repository : URL of software repository
    :ivar parameters : List of the code specific parameters in XML format
    :ivar output_flag : Output flag : 0 means the run is successful, other values mean some difficulty has been encountered, the exact meaning is then code specific. Negative values mean the result shall not be used.
    :ivar library : List of external libraries used by the code that has produced this IDS
    """

    class Meta:
        name = "code"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    description: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    commit: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    version: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    repository: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    parameters: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    output_flag: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=int),
        metadata={
            "imas_type": "INT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "/time"},
            "field_type": np.ndarray,
        },
    )
    library: Optional[Library] = field(
        default_factory=lambda: StructArray(type_input=Library),
        metadata={
            "imas_type": "library",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": Library,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class TemporaryConstantQuantitiesFloat0D(IdsBaseClass):
    """

    :ivar value : Value
    """

    class Meta:
        name = "temporary_constant_quantities_float_0d"
        is_root_ids = False

    value: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class TemporaryConstantQuantitiesInt0D(IdsBaseClass):
    """

    :ivar value : Value
    """

    class Meta:
        name = "temporary_constant_quantities_int_0d"
        is_root_ids = False

    value: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )


@idspy_dataclass(repr=False, slots=True)
class TemporaryConstantQuantitiesString0D(IdsBaseClass):
    """

    :ivar value : Value
    """

    class Meta:
        name = "temporary_constant_quantities_string_0d"
        is_root_ids = False

    value: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )


@idspy_dataclass(repr=False, slots=True)
class TemporaryConstantQuantitiesFloat1D(IdsBaseClass):
    """

    :ivar value : Value
    """

    class Meta:
        name = "temporary_constant_quantities_float_1d"
        is_root_ids = False

    value: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class TemporaryConstantQuantitiesInt1D(IdsBaseClass):
    """

    :ivar value : Value
    """

    class Meta:
        name = "temporary_constant_quantities_int_1d"
        is_root_ids = False

    value: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=int),
        metadata={
            "imas_type": "INT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class TemporaryConstantQuantitiesString1D(IdsBaseClass):
    """

    :ivar value : Value
    """

    class Meta:
        name = "temporary_constant_quantities_string_1d"
        is_root_ids = False

    value: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=str),
        metadata={
            "imas_type": "STR_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class TemporaryDynamicQuantitiesFloat1D(IdsBaseClass):
    """

    :ivar value : Value
    """

    class Meta:
        name = "temporary_dynamic_quantities_float_1d"
        is_root_ids = False

    value: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )


@idspy_dataclass(repr=False, slots=True)
class TemporaryDynamicQuantitiesInt1D(IdsBaseClass):
    """

    :ivar value : Value
    """

    class Meta:
        name = "temporary_dynamic_quantities_int_1d"
        is_root_ids = False

    value: Optional[SignalInt1D] = field(
        default=None,
        metadata={"imas_type": "signal_int_1d", "field_type": SignalInt1D},
    )


@idspy_dataclass(repr=False, slots=True)
class TemporaryConstantQuantitiesFloat2D(IdsBaseClass):
    """

    :ivar value : Value
    """

    class Meta:
        name = "temporary_constant_quantities_float_2d"
        is_root_ids = False

    value: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {"coordinate1": "1...N", "coordinate2": "1...N"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class TemporaryConstantQuantitiesInt2D(IdsBaseClass):
    """

    :ivar value : Value
    """

    class Meta:
        name = "temporary_constant_quantities_int_2d"
        is_root_ids = False

    value: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=int),
        metadata={
            "imas_type": "INT_2D",
            "ndims": 2,
            "coordinates": {"coordinate1": "1...N", "coordinate2": "1...N"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class TemporaryDynamicQuantitiesFloat2D(IdsBaseClass):
    """

    :ivar value : Value
    """

    class Meta:
        name = "temporary_dynamic_quantities_float_2d"
        is_root_ids = False

    value: Optional[SignalFlt2D] = field(
        default_factory=lambda: StructArray(type_input=SignalFlt2D),
        metadata={
            "imas_type": "signal_flt_2d",
            "ndims": 2,
            "coordinates": {"coordinate1": "1...N", "coordinate2": "time"},
            "field_type": SignalFlt2D,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class TemporaryDynamicQuantitiesInt2D(IdsBaseClass):
    """

    :ivar value : Value
    """

    class Meta:
        name = "temporary_dynamic_quantities_int_2d"
        is_root_ids = False

    value: Optional[SignalInt2D] = field(
        default_factory=lambda: StructArray(type_input=SignalInt2D),
        metadata={
            "imas_type": "signal_int_2d",
            "ndims": 2,
            "coordinates": {"coordinate1": "1...N", "coordinate2": "time"},
            "field_type": SignalInt2D,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class TemporaryConstantQuantitiesFloat3D(IdsBaseClass):
    """

    :ivar value : Value
    """

    class Meta:
        name = "temporary_constant_quantities_float_3d"
        is_root_ids = False

    value: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate2": "1...N",
                "coordinate3": "1...N",
            },
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class TemporaryConstantQuantitiesInt3D(IdsBaseClass):
    """

    :ivar value : Value
    """

    class Meta:
        name = "temporary_constant_quantities_int_3d"
        is_root_ids = False

    value: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=int),
        metadata={
            "imas_type": "INT_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate2": "1...N",
                "coordinate3": "1...N",
            },
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class TemporaryDynamicQuantitiesFloat3D(IdsBaseClass):
    """

    :ivar value : Value
    """

    class Meta:
        name = "temporary_dynamic_quantities_float_3d"
        is_root_ids = False

    value: Optional[SignalFlt3D] = field(
        default_factory=lambda: StructArray(type_input=SignalFlt3D),
        metadata={
            "imas_type": "signal_flt_3d",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate2": "1...N",
                "coordinate3": "time",
            },
            "field_type": SignalFlt3D,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class TemporaryDynamicQuantitiesInt3D(IdsBaseClass):
    """

    :ivar value : Value
    """

    class Meta:
        name = "temporary_dynamic_quantities_int_3d"
        is_root_ids = False

    value: Optional[SignalInt3D] = field(
        default_factory=lambda: StructArray(type_input=SignalInt3D),
        metadata={
            "imas_type": "signal_int_3d",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate2": "1...N",
                "coordinate3": "time",
            },
            "field_type": SignalInt3D,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class TemporaryDynamicQuantitiesFloat4D(IdsBaseClass):
    """

    :ivar value : Value
    """

    class Meta:
        name = "temporary_dynamic_quantities_float_4d"
        is_root_ids = False

    value: Optional[SignalFlt4D] = field(
        default_factory=lambda: StructArray(type_input=SignalFlt4D),
        metadata={
            "imas_type": "signal_flt_4d",
            "ndims": 4,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate2": "1...N",
                "coordinate3": "1...N",
                "coordinate4": "time",
            },
            "field_type": SignalFlt4D,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class TemporaryConstantQuantitiesFloat4D(IdsBaseClass):
    """

    :ivar value : Value
    """

    class Meta:
        name = "temporary_constant_quantities_float_4d"
        is_root_ids = False

    value: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 4, dtype=float),
        metadata={
            "imas_type": "FLT_4D",
            "ndims": 4,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate2": "1...N",
                "coordinate3": "1...N",
                "coordinate4": "1...N",
            },
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class TemporaryDynamicQuantitiesFloat5D(IdsBaseClass):
    """

    :ivar value : Value
    """

    class Meta:
        name = "temporary_dynamic_quantities_float_5d"
        is_root_ids = False

    value: Optional[SignalFlt5D] = field(
        default_factory=lambda: StructArray(type_input=SignalFlt5D),
        metadata={
            "imas_type": "signal_flt_5d",
            "ndims": 5,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate2": "1...N",
                "coordinate3": "1...N",
                "coordinate4": "1...N",
                "coordinate5": "time",
            },
            "field_type": SignalFlt5D,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class TemporaryConstantQuantitiesFloat5D(IdsBaseClass):
    """

    :ivar value : Value
    """

    class Meta:
        name = "temporary_constant_quantities_float_5d"
        is_root_ids = False

    value: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 5, dtype=float),
        metadata={
            "imas_type": "FLT_5D",
            "ndims": 5,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate2": "1...N",
                "coordinate3": "1...N",
                "coordinate4": "1...N",
                "coordinate5": "1...N",
            },
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class TemporaryDynamicQuantitiesFloat6D(IdsBaseClass):
    """

    :ivar value : Value
    """

    class Meta:
        name = "temporary_dynamic_quantities_float_6d"
        is_root_ids = False

    value: Optional[SignalFlt6D] = field(
        default_factory=lambda: StructArray(type_input=SignalFlt6D),
        metadata={
            "imas_type": "signal_flt_6d",
            "ndims": 6,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate2": "1...N",
                "coordinate3": "1...N",
                "coordinate4": "1...N",
                "coordinate5": "1...N",
                "coordinate6": "time",
            },
            "field_type": SignalFlt6D,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class TemporaryConstantQuantitiesFloat6D(IdsBaseClass):
    """

    :ivar value : Value
    """

    class Meta:
        name = "temporary_constant_quantities_float_6d"
        is_root_ids = False

    value: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 6, dtype=float),
        metadata={
            "imas_type": "FLT_6D",
            "ndims": 6,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate2": "1...N",
                "coordinate3": "1...N",
                "coordinate4": "1...N",
                "coordinate5": "1...N",
                "coordinate6": "1...N",
            },
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class Temporary(IdsBaseClass):
    """

    :ivar ids_properties :
    :ivar constant_float0d : Constant 0D float
    :ivar constant_integer0d : Constant 0D integer
    :ivar constant_string0d : Constant 0D string
    :ivar constant_integer1d : Constant 1D integer
    :ivar constant_string1d : Constant 1D string
    :ivar constant_float1d : Constant 1D float
    :ivar dynamic_float1d : Dynamic 1D float
    :ivar dynamic_integer1d : Dynamic 1D integer
    :ivar constant_float2d : Constant 2D float
    :ivar constant_integer2d : Constant 2D integer
    :ivar dynamic_float2d : Dynamic 2D float
    :ivar dynamic_integer2d : Dynamic 2D integer
    :ivar constant_float3d : Constant 3D float
    :ivar constant_integer3d : Constant 3D integer
    :ivar dynamic_float3d : Dynamic 3D float
    :ivar dynamic_integer3d : Dynamic 3D integer
    :ivar constant_float4d : Constant 4D float
    :ivar dynamic_float4d : Dynamic 4D float
    :ivar constant_float5d : Constant 5D float
    :ivar dynamic_float5d : Dynamic 5D float
    :ivar constant_float6d : Constant 6D float
    :ivar dynamic_float6d : Dynamic 6D float
    :ivar code :
    :ivar time : Generic time
    """

    class Meta:
        name = "temporary"
        is_root_ids = True

    ids_properties: Optional[IdsProperties] = field(
        default=None,
        metadata={"imas_type": "ids_properties", "field_type": IdsProperties},
    )
    constant_float0d: Optional[TemporaryConstantQuantitiesFloat0D] = field(
        default_factory=lambda: StructArray(
            type_input=TemporaryConstantQuantitiesFloat0D
        ),
        metadata={
            "imas_type": "temporary_constant_quantities_float_0d",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": TemporaryConstantQuantitiesFloat0D,
        },
    )
    constant_integer0d: Optional[TemporaryConstantQuantitiesInt0D] = field(
        default_factory=lambda: StructArray(
            type_input=TemporaryConstantQuantitiesInt0D
        ),
        metadata={
            "imas_type": "temporary_constant_quantities_int_0d",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": TemporaryConstantQuantitiesInt0D,
        },
    )
    constant_string0d: Optional[TemporaryConstantQuantitiesString0D] = field(
        default_factory=lambda: StructArray(
            type_input=TemporaryConstantQuantitiesString0D
        ),
        metadata={
            "imas_type": "temporary_constant_quantities_string_0d",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": TemporaryConstantQuantitiesString0D,
        },
    )
    constant_integer1d: Optional[TemporaryConstantQuantitiesInt1D] = field(
        default_factory=lambda: StructArray(
            type_input=TemporaryConstantQuantitiesInt1D
        ),
        metadata={
            "imas_type": "temporary_constant_quantities_int_1d",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": TemporaryConstantQuantitiesInt1D,
        },
    )
    constant_string1d: Optional[TemporaryConstantQuantitiesString1D] = field(
        default_factory=lambda: StructArray(
            type_input=TemporaryConstantQuantitiesString1D
        ),
        metadata={
            "imas_type": "temporary_constant_quantities_string_1d",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": TemporaryConstantQuantitiesString1D,
        },
    )
    constant_float1d: Optional[TemporaryConstantQuantitiesFloat1D] = field(
        default_factory=lambda: StructArray(
            type_input=TemporaryConstantQuantitiesFloat1D
        ),
        metadata={
            "imas_type": "temporary_constant_quantities_float_1d",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": TemporaryConstantQuantitiesFloat1D,
        },
    )
    dynamic_float1d: Optional[TemporaryDynamicQuantitiesFloat1D] = field(
        default_factory=lambda: StructArray(
            type_input=TemporaryDynamicQuantitiesFloat1D
        ),
        metadata={
            "imas_type": "temporary_dynamic_quantities_float_1d",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": TemporaryDynamicQuantitiesFloat1D,
        },
    )
    dynamic_integer1d: Optional[TemporaryDynamicQuantitiesInt1D] = field(
        default_factory=lambda: StructArray(
            type_input=TemporaryDynamicQuantitiesInt1D
        ),
        metadata={
            "imas_type": "temporary_dynamic_quantities_int_1d",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": TemporaryDynamicQuantitiesInt1D,
        },
    )
    constant_float2d: Optional[TemporaryConstantQuantitiesFloat2D] = field(
        default_factory=lambda: StructArray(
            type_input=TemporaryConstantQuantitiesFloat2D
        ),
        metadata={
            "imas_type": "temporary_constant_quantities_float_2d",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": TemporaryConstantQuantitiesFloat2D,
        },
    )
    constant_integer2d: Optional[TemporaryConstantQuantitiesInt2D] = field(
        default_factory=lambda: StructArray(
            type_input=TemporaryConstantQuantitiesInt2D
        ),
        metadata={
            "imas_type": "temporary_constant_quantities_int_2d",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": TemporaryConstantQuantitiesInt2D,
        },
    )
    dynamic_float2d: Optional[TemporaryDynamicQuantitiesFloat2D] = field(
        default_factory=lambda: StructArray(
            type_input=TemporaryDynamicQuantitiesFloat2D
        ),
        metadata={
            "imas_type": "temporary_dynamic_quantities_float_2d",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": TemporaryDynamicQuantitiesFloat2D,
        },
    )
    dynamic_integer2d: Optional[TemporaryDynamicQuantitiesInt2D] = field(
        default_factory=lambda: StructArray(
            type_input=TemporaryDynamicQuantitiesInt2D
        ),
        metadata={
            "imas_type": "temporary_dynamic_quantities_int_2d",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": TemporaryDynamicQuantitiesInt2D,
        },
    )
    constant_float3d: Optional[TemporaryConstantQuantitiesFloat3D] = field(
        default_factory=lambda: StructArray(
            type_input=TemporaryConstantQuantitiesFloat3D
        ),
        metadata={
            "imas_type": "temporary_constant_quantities_float_3d",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": TemporaryConstantQuantitiesFloat3D,
        },
    )
    constant_integer3d: Optional[TemporaryConstantQuantitiesInt3D] = field(
        default_factory=lambda: StructArray(
            type_input=TemporaryConstantQuantitiesInt3D
        ),
        metadata={
            "imas_type": "temporary_constant_quantities_int_3d",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": TemporaryConstantQuantitiesInt3D,
        },
    )
    dynamic_float3d: Optional[TemporaryDynamicQuantitiesFloat3D] = field(
        default_factory=lambda: StructArray(
            type_input=TemporaryDynamicQuantitiesFloat3D
        ),
        metadata={
            "imas_type": "temporary_dynamic_quantities_float_3d",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": TemporaryDynamicQuantitiesFloat3D,
        },
    )
    dynamic_integer3d: Optional[TemporaryDynamicQuantitiesInt3D] = field(
        default_factory=lambda: StructArray(
            type_input=TemporaryDynamicQuantitiesInt3D
        ),
        metadata={
            "imas_type": "temporary_dynamic_quantities_int_3d",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": TemporaryDynamicQuantitiesInt3D,
        },
    )
    constant_float4d: Optional[TemporaryConstantQuantitiesFloat4D] = field(
        default_factory=lambda: StructArray(
            type_input=TemporaryConstantQuantitiesFloat4D
        ),
        metadata={
            "imas_type": "temporary_constant_quantities_float_4d",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": TemporaryConstantQuantitiesFloat4D,
        },
    )
    dynamic_float4d: Optional[TemporaryDynamicQuantitiesFloat4D] = field(
        default_factory=lambda: StructArray(
            type_input=TemporaryDynamicQuantitiesFloat4D
        ),
        metadata={
            "imas_type": "temporary_dynamic_quantities_float_4d",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": TemporaryDynamicQuantitiesFloat4D,
        },
    )
    constant_float5d: Optional[TemporaryConstantQuantitiesFloat5D] = field(
        default_factory=lambda: StructArray(
            type_input=TemporaryConstantQuantitiesFloat5D
        ),
        metadata={
            "imas_type": "temporary_constant_quantities_float_5d",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": TemporaryConstantQuantitiesFloat5D,
        },
    )
    dynamic_float5d: Optional[TemporaryDynamicQuantitiesFloat5D] = field(
        default_factory=lambda: StructArray(
            type_input=TemporaryDynamicQuantitiesFloat5D
        ),
        metadata={
            "imas_type": "temporary_dynamic_quantities_float_5d",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": TemporaryDynamicQuantitiesFloat5D,
        },
    )
    constant_float6d: Optional[TemporaryConstantQuantitiesFloat6D] = field(
        default_factory=lambda: StructArray(
            type_input=TemporaryConstantQuantitiesFloat6D
        ),
        metadata={
            "imas_type": "temporary_constant_quantities_float_6d",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": TemporaryConstantQuantitiesFloat6D,
        },
    )
    dynamic_float6d: Optional[TemporaryDynamicQuantitiesFloat6D] = field(
        default_factory=lambda: StructArray(
            type_input=TemporaryDynamicQuantitiesFloat6D
        ),
        metadata={
            "imas_type": "temporary_dynamic_quantities_float_6d",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": TemporaryDynamicQuantitiesFloat6D,
        },
    )
    code: Optional[Code] = field(
        default=None, metadata={"imas_type": "code", "field_type": Code}
    )
    time: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "flt_1d_type",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
