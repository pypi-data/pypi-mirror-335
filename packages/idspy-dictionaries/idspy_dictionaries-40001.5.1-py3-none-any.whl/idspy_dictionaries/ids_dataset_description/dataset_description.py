# __version__= "040001.5.1"
# __version_imas_dd__= "4.0.0-71-gf671395"
# __imas_dd_git_commit__= "f671395e0d3a530a942c6d332553acfa94de8d94"
# __imas_dd_git_branch__= "develop"
#
from ..dataclasses_idsschema import idspy_dataclass, IdsBaseClass, StructArray
from dataclasses import field
from typing import Optional


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
class CodeConstant(IdsBaseClass):
    """

    :ivar name : Name of software used
    :ivar description : Short description of the software (type, purpose)
    :ivar commit : Unique commit reference of software
    :ivar version : Unique version (tag) of software
    :ivar repository : URL of software repository
    :ivar parameters : List of the code specific parameters in XML format
    :ivar library : List of external libraries used by the code that has produced this IDS
    """

    class Meta:
        name = "code_constant"
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
class DatasetDescriptionSimulation(IdsBaseClass):
    """

    :ivar comment_before : Comment made when launching a simulation
    :ivar comment_after : Comment made at the end of a simulation
    :ivar time_begin : Start time
    :ivar time_step : Time interval between main steps, e.g. storage step (if relevant and constant)
    :ivar time_end : Stop time
    :ivar time_restart : Time of the last restart done during the simulation
    :ivar time_current : Current time of the simulation
    :ivar time_begun : Actual wall-clock time simulation started
    :ivar time_ended : Actual wall-clock time simulation finished
    :ivar workflow : Description of the workflow which has been used to produce this data entry (e.g. copy of the Kepler MOML if using Kepler)
    """

    class Meta:
        name = "dataset_description_simulation"
        is_root_ids = False

    comment_before: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    comment_after: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    time_begin: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    time_step: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    time_end: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    time_restart: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    time_current: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    time_begun: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    time_ended: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    workflow: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )


@idspy_dataclass(repr=False, slots=True)
class DatasetDescriptionEpochTime(IdsBaseClass):
    """

    :ivar seconds : Elapsed seconds since the Unix Epoch time (01/01/1970 00:00:00 UTC)
    :ivar nanoseconds : Elapsed nanoseconds since the time in seconds indicated above
    """

    class Meta:
        name = "dataset_description_epoch_time"
        is_root_ids = False

    seconds: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    nanoseconds: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )


@idspy_dataclass(repr=False, slots=True)
class DatasetDescription(IdsBaseClass):
    """

    :ivar ids_properties :
    :ivar uri : IMAS URI of the dataset
    :ivar machine : Name of the experimental device to which this data is related (if relevant)
    :ivar pulse : Pulse number to which this data is related (if relevant)
    :ivar pulse_time_begin : Date and time (UTC) at which the pulse started on the experiment (if relevant), expressed in a human readable form (ISO 8601) : the format of the string shall be : YYYY-MM-DDTHH:MM:SSZ. Example : 2020-07-24T14:19:00Z
    :ivar pulse_time_begin_epoch : Time at which the pulse started on the experiment (if relevant), expressed in Unix Epoch time. Temporarily represented as two integers, since for the moment IMAS is missing 64bits long integers to represent epoch time with nanoseconds resolution
    :ivar pulse_time_end_epoch : Time at which the pulse ended on the experiment (if relevant), expressed in Unix Epoch time. Temporarily represented as two integers, since for the moment IMAS is missing 64bits long integers to represent epoch time with nanoseconds resolution
    :ivar pulse_processing_time_begin : For experimental processed data, date and time (UTC) at which the pulse data processing started on the experiment (if relevant), expressed in a human readable form (ISO 8601) : the format of the string shall be : YYYY-MM-DDTHH:MM:SSZ. Example : 2020-07-24T14:19:00Z
    :ivar simulation : Description of the general simulation characteristics, if this dataset has been produced by a simulation. Several nodes describe typical time-dependent simulation with a time evolution as the main loop
    :ivar code : Decription of the code that has produced the dataset
    """

    class Meta:
        name = "dataset_description"
        is_root_ids = True

    ids_properties: Optional[IdsProperties] = field(
        default=None,
        metadata={"imas_type": "ids_properties", "field_type": IdsProperties},
    )
    uri: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    machine: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    pulse: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    pulse_time_begin: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    pulse_time_begin_epoch: Optional[DatasetDescriptionEpochTime] = field(
        default=None,
        metadata={
            "imas_type": "dataset_description_epoch_time",
            "field_type": DatasetDescriptionEpochTime,
        },
    )
    pulse_time_end_epoch: Optional[DatasetDescriptionEpochTime] = field(
        default=None,
        metadata={
            "imas_type": "dataset_description_epoch_time",
            "field_type": DatasetDescriptionEpochTime,
        },
    )
    pulse_processing_time_begin: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    simulation: Optional[DatasetDescriptionSimulation] = field(
        default=None,
        metadata={
            "imas_type": "dataset_description_simulation",
            "field_type": DatasetDescriptionSimulation,
        },
    )
    code: Optional[CodeConstant] = field(
        default=None,
        metadata={"imas_type": "code_constant", "field_type": CodeConstant},
    )
