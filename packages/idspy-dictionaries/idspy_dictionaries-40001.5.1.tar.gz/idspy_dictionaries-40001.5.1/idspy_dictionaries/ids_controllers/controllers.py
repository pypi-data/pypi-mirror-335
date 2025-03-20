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
class ControllersStatespace(IdsBaseClass):
    """

    :ivar state_names : Names of the states
    :ivar a : A matrix
    :ivar b : B matrix
    :ivar c : C matrix
    :ivar d : D matrix, normally proper and D=0
    :ivar deltat : Discrete time sampling interval ; if less than 1e-10, the controller is considered to be expressed in continuous time
    """

    class Meta:
        name = "controllers_statespace"
        is_root_ids = False

    state_names: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=str),
        metadata={
            "imas_type": "STR_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    a: Optional[SignalFlt3D] = field(
        default_factory=lambda: StructArray(type_input=SignalFlt3D),
        metadata={
            "imas_type": "signal_flt_3d",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "../state_names",
                "coordinate2": "../state_names",
                "coordinate3": "time",
            },
            "field_type": SignalFlt3D,
        },
    )
    b: Optional[SignalFlt3D] = field(
        default_factory=lambda: StructArray(type_input=SignalFlt3D),
        metadata={
            "imas_type": "signal_flt_3d",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "../state_names",
                "coordinate2": "../../input_names",
                "coordinate3": "time",
            },
            "field_type": SignalFlt3D,
        },
    )
    c: Optional[SignalFlt3D] = field(
        default_factory=lambda: StructArray(type_input=SignalFlt3D),
        metadata={
            "imas_type": "signal_flt_3d",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "../state_names",
                "coordinate2": "../../output_names",
                "coordinate3": "time",
            },
            "field_type": SignalFlt3D,
        },
    )
    d: Optional[SignalFlt3D] = field(
        default_factory=lambda: StructArray(type_input=SignalFlt3D),
        metadata={
            "imas_type": "signal_flt_3d",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "../state_names",
                "coordinate2": "../../output_names",
                "coordinate3": "time",
            },
            "field_type": SignalFlt3D,
        },
    )
    deltat: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )


@idspy_dataclass(repr=False, slots=True)
class ControllersPid(IdsBaseClass):
    """

    :ivar p : Proportional term
    :ivar i : Integral term
    :ivar d : Derivative term
    :ivar tau : Filter time-constant for the D-term
    """

    class Meta:
        name = "controllers_pid"
        is_root_ids = False

    p: Optional[SignalFlt3D] = field(
        default_factory=lambda: StructArray(type_input=SignalFlt3D),
        metadata={
            "imas_type": "signal_flt_3d",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "../../output_names",
                "coordinate2": "../../input_names",
                "coordinate3": "time",
            },
            "field_type": SignalFlt3D,
        },
    )
    i: Optional[SignalFlt3D] = field(
        default_factory=lambda: StructArray(type_input=SignalFlt3D),
        metadata={
            "imas_type": "signal_flt_3d",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "../../output_names",
                "coordinate2": "../../input_names",
                "coordinate3": "time",
            },
            "field_type": SignalFlt3D,
        },
    )
    d: Optional[SignalFlt3D] = field(
        default_factory=lambda: StructArray(type_input=SignalFlt3D),
        metadata={
            "imas_type": "signal_flt_3d",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "../../output_names",
                "coordinate2": "../../input_names",
                "coordinate3": "time",
            },
            "field_type": SignalFlt3D,
        },
    )
    tau: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )


@idspy_dataclass(repr=False, slots=True)
class ControllersLinearController(IdsBaseClass):
    """

    :ivar name : Name of this controller
    :ivar description : Description of this controller
    :ivar controller_class : One of a known class of controllers
    :ivar input_names : Names of the input signals, following the SDN convention
    :ivar output_names : Names of the output signals following the SDN convention
    :ivar statespace : Statespace controller in discrete or continuous time
    :ivar pid : Filtered PID controller
    :ivar inputs : Input signals; the timebase is common to inputs and outputs for any particular controller
    :ivar outputs : Output signals; the timebase is common to inputs and outputs for any particular controller
    """

    class Meta:
        name = "controllers_linear_controller"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    description: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    controller_class: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    input_names: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=str),
        metadata={
            "imas_type": "STR_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    output_names: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=str),
        metadata={
            "imas_type": "STR_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    statespace: Optional[ControllersStatespace] = field(
        default=None,
        metadata={
            "imas_type": "controllers_statespace",
            "field_type": ControllersStatespace,
        },
    )
    pid: Optional[ControllersPid] = field(
        default=None,
        metadata={"imas_type": "controllers_pid", "field_type": ControllersPid},
    )
    inputs: Optional[SignalFlt2D] = field(
        default_factory=lambda: StructArray(type_input=SignalFlt2D),
        metadata={
            "imas_type": "signal_flt_2d",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../input_names",
                "coordinate2": "time",
            },
            "field_type": SignalFlt2D,
        },
    )
    outputs: Optional[SignalFlt2D] = field(
        default_factory=lambda: StructArray(type_input=SignalFlt2D),
        metadata={
            "imas_type": "signal_flt_2d",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../output_names",
                "coordinate2": "time",
            },
            "field_type": SignalFlt2D,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class ControllersNonlinearController(IdsBaseClass):
    """

    :ivar name : Name of this controller
    :ivar description : Description of this controller
    :ivar controller_class : One of a known class of controllers
    :ivar input_names : Names of the input signals, following the SDN convention
    :ivar output_names : Output signal names following the SDN convention
    :ivar function : Method to be defined
    :ivar inputs : Input signals; the timebase is common  to inputs and outputs for any particular controller
    :ivar outputs : Output signals; the timebase is common  to inputs and outputs for any particular controller
    """

    class Meta:
        name = "controllers_nonlinear_controller"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    description: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    controller_class: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    input_names: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=str),
        metadata={
            "imas_type": "STR_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    output_names: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=str),
        metadata={
            "imas_type": "STR_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    function: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    inputs: Optional[SignalFlt2D] = field(
        default_factory=lambda: StructArray(type_input=SignalFlt2D),
        metadata={
            "imas_type": "signal_flt_2d",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../input_names",
                "coordinate2": "time",
            },
            "field_type": SignalFlt2D,
        },
    )
    outputs: Optional[SignalFlt2D] = field(
        default_factory=lambda: StructArray(type_input=SignalFlt2D),
        metadata={
            "imas_type": "signal_flt_2d",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../output_names",
                "coordinate2": "time",
            },
            "field_type": SignalFlt2D,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class Controllers(IdsBaseClass):
    """

    :ivar ids_properties :
    :ivar linear_controller : A linear controller, this is rather conventional
    :ivar nonlinear_controller : A non-linear controller, this is less conventional and will have to be developed
    :ivar time : Generic time
    :ivar code :
    """

    class Meta:
        name = "controllers"
        is_root_ids = True

    ids_properties: Optional[IdsProperties] = field(
        default=None,
        metadata={"imas_type": "ids_properties", "field_type": IdsProperties},
    )
    linear_controller: Optional[ControllersLinearController] = field(
        default_factory=lambda: StructArray(
            type_input=ControllersLinearController
        ),
        metadata={
            "imas_type": "controllers_linear_controller",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": ControllersLinearController,
        },
    )
    nonlinear_controller: Optional[ControllersNonlinearController] = field(
        default_factory=lambda: StructArray(
            type_input=ControllersNonlinearController
        ),
        metadata={
            "imas_type": "controllers_nonlinear_controller",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": ControllersNonlinearController,
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
    code: Optional[Code] = field(
        default=None, metadata={"imas_type": "code", "field_type": Code}
    )
