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
class SignalFlt1DValidity(IdsBaseClass):
    """

    :ivar data : Data
    :ivar validity_timed : Indicator of the validity of the data for each time slice. 0: valid from automated processing, 1: valid and certified by the diagnostic RO; - 1 means problem identified in the data processing (request verification by the diagnostic RO), -2: invalid data, should not be used (values lower than -2 have a code-specific meaning detailing the origin of their invalidity)
    :ivar validity : Indicator of the validity of the data for the whole acquisition period. 0: valid from automated processing, 1: valid and certified by the diagnostic RO; - 1 means problem identified in the data processing (request verification by the diagnostic RO), -2: invalid data, should not be used (values lower than -2 have a code-specific meaning detailing the origin of their invalidity)
    :ivar time : Time
    """

    class Meta:
        name = "signal_flt_1d_validity"
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
    validity_timed: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=int),
        metadata={
            "imas_type": "INT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../time"},
            "field_type": np.ndarray,
        },
    )
    validity: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
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
class DataFlt0DConstantValidity(IdsBaseClass):
    """

    :ivar data : Data
    :ivar validity : Indicator of the validity of the data for the whole acquisition period. 0: valid from automated processing, 1: valid and certified by the diagnostic RO; - 1 means problem identified in the data processing (request verification by the diagnostic RO), -2: invalid data, should not be used (values lower than -2 have a code-specific meaning detailing the origin of their invalidity)
    """

    class Meta:
        name = "data_flt_0d_constant_validity"
        is_root_ids = False

    data: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    validity: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
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
class CalorimetryCoolingLoop(IdsBaseClass):
    """

    :ivar name : Short string identifier (unique for a given device)
    :ivar description : Description, e.g. “channel viewing the upper divertor”
    :ivar temperature_in : Temperature of the coolant when entering the loop
    :ivar temperature_out : Temperature of the coolant when exiting the loop
    :ivar mass_flow : Mass flow of the coolant going through the loop
    """

    class Meta:
        name = "calorimetry_cooling_loop"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    description: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    temperature_in: Optional[SignalFlt1DValidity] = field(
        default=None,
        metadata={
            "imas_type": "signal_flt_1d_validity",
            "field_type": SignalFlt1DValidity,
        },
    )
    temperature_out: Optional[SignalFlt1DValidity] = field(
        default=None,
        metadata={
            "imas_type": "signal_flt_1d_validity",
            "field_type": SignalFlt1DValidity,
        },
    )
    mass_flow: Optional[SignalFlt1DValidity] = field(
        default=None,
        metadata={
            "imas_type": "signal_flt_1d_validity",
            "field_type": SignalFlt1DValidity,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class CalorimetryGroupComponent(IdsBaseClass):
    """

    :ivar name : Short string identifier (unique for a given device)
    :ivar description : Description, e.g. “channel viewing the upper divertor”
    :ivar power : Power extracted from the component
    :ivar energy_cumulated : Energy extracted from the component since the start of the pulse
    :ivar energy_total : Energy extracted from the component on the whole plasma discharge, including the return to thermal equilibrium of the component in the post-pulse phase
    :ivar temperature_in : Temperature of the coolant when entering the component
    :ivar temperature_out : Temperature of the coolant when exiting the component
    :ivar mass_flow : Mass flow of the coolant going through the component
    :ivar transit_time : Transit time for the coolant to go from the input to the output of the component
    """

    class Meta:
        name = "calorimetry_group_component"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    description: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    power: Optional[SignalFlt1DValidity] = field(
        default=None,
        metadata={
            "imas_type": "signal_flt_1d_validity",
            "field_type": SignalFlt1DValidity,
        },
    )
    energy_cumulated: Optional[SignalFlt1DValidity] = field(
        default=None,
        metadata={
            "imas_type": "signal_flt_1d_validity",
            "field_type": SignalFlt1DValidity,
        },
    )
    energy_total: Optional[DataFlt0DConstantValidity] = field(
        default=None,
        metadata={
            "imas_type": "data_flt_0d_constant_validity",
            "field_type": DataFlt0DConstantValidity,
        },
    )
    temperature_in: Optional[SignalFlt1DValidity] = field(
        default=None,
        metadata={
            "imas_type": "signal_flt_1d_validity",
            "field_type": SignalFlt1DValidity,
        },
    )
    temperature_out: Optional[SignalFlt1DValidity] = field(
        default=None,
        metadata={
            "imas_type": "signal_flt_1d_validity",
            "field_type": SignalFlt1DValidity,
        },
    )
    mass_flow: Optional[SignalFlt1DValidity] = field(
        default=None,
        metadata={
            "imas_type": "signal_flt_1d_validity",
            "field_type": SignalFlt1DValidity,
        },
    )
    transit_time: Optional[SignalFlt1DValidity] = field(
        default=None,
        metadata={
            "imas_type": "signal_flt_1d_validity",
            "field_type": SignalFlt1DValidity,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class CalorimetryGroup(IdsBaseClass):
    """

    :ivar name : Short string identifier (unique for a given device)
    :ivar description : Description, e.g. “channel viewing the upper divertor”
    :ivar component : Set of components on which calorimetry measurements are carried out
    """

    class Meta:
        name = "calorimetry_group"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    description: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    component: Optional[CalorimetryGroupComponent] = field(
        default_factory=lambda: StructArray(
            type_input=CalorimetryGroupComponent
        ),
        metadata={
            "imas_type": "calorimetry_group_component",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": CalorimetryGroupComponent,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class Calorimetry(IdsBaseClass):
    """

    :ivar ids_properties :
    :ivar group : Set of groups of components on which calorimetry measurements are carried out (grouped by tokamak subsystems or localization on the machine)
    :ivar cooling_loop : Set of cooling loops
    :ivar latency : Upper bound of the delay between physical information received by the detector and data available on the real-time (RT) network.
    :ivar code :
    :ivar time : Generic time
    """

    class Meta:
        name = "calorimetry"
        is_root_ids = True

    ids_properties: Optional[IdsProperties] = field(
        default=None,
        metadata={"imas_type": "ids_properties", "field_type": IdsProperties},
    )
    group: Optional[CalorimetryGroup] = field(
        default_factory=lambda: StructArray(type_input=CalorimetryGroup),
        metadata={
            "imas_type": "calorimetry_group",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": CalorimetryGroup,
        },
    )
    cooling_loop: Optional[CalorimetryCoolingLoop] = field(
        default_factory=lambda: StructArray(type_input=CalorimetryCoolingLoop),
        metadata={
            "imas_type": "calorimetry_cooling_loop",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": CalorimetryCoolingLoop,
        },
    )
    latency: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
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
