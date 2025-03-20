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
class Rphiz0DStatic(IdsBaseClass):
    """

    :ivar r : Major radius
    :ivar phi : Toroidal angle (oriented counter-clockwise when viewing from above)
    :ivar z : Height
    """

    class Meta:
        name = "rphiz0d_static"
        is_root_ids = False

    r: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    phi: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    z: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class IdentifierStatic(IdsBaseClass):
    """

    :ivar name : Short string identifier
    :ivar index : Integer identifier (enumeration index within a list). Private identifier values must be indicated by a negative index.
    :ivar description : Verbose description
    """

    class Meta:
        name = "identifier_static"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    index: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    description: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )


@idspy_dataclass(repr=False, slots=True)
class PlasmaCompositionNeutralElementConstant(IdsBaseClass):
    """

    :ivar a : Mass of atom
    :ivar z_n : Nuclear charge
    :ivar atoms_n : Number of atoms of this element in the molecule
    """

    class Meta:
        name = "plasma_composition_neutral_element_constant"
        is_root_ids = False

    a: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    z_n: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    atoms_n: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )


@idspy_dataclass(repr=False, slots=True)
class GasMixtureConstant(IdsBaseClass):
    """

    :ivar element : List of elements forming the atom or molecule
    :ivar name : String identifying neutral (e.g. H, D, T, He, C, ...)
    :ivar fraction : Relative fraction of this species (in molecules) in the gas mixture
    """

    class Meta:
        name = "gas_mixture_constant"
        is_root_ids = False

    element: Optional[PlasmaCompositionNeutralElementConstant] = field(
        default_factory=lambda: StructArray(
            type_input=PlasmaCompositionNeutralElementConstant
        ),
        metadata={
            "imas_type": "plasma_composition_neutral_element_constant",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": PlasmaCompositionNeutralElementConstant,
        },
    )
    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    fraction: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class LineOfSight3Points(IdsBaseClass):
    """

    :ivar first_point : Position of the first point
    :ivar second_point : Position of the second point
    :ivar third_point : Position of the third point
    """

    class Meta:
        name = "line_of_sight_3points"
        is_root_ids = False

    first_point: Optional[Rphiz0DStatic] = field(
        default=None,
        metadata={"imas_type": "rphiz0d_static", "field_type": Rphiz0DStatic},
    )
    second_point: Optional[Rphiz0DStatic] = field(
        default=None,
        metadata={"imas_type": "rphiz0d_static", "field_type": Rphiz0DStatic},
    )
    third_point: Optional[Rphiz0DStatic] = field(
        default=None,
        metadata={"imas_type": "rphiz0d_static", "field_type": Rphiz0DStatic},
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
class PulseScheduleReferencePfActive(IdsBaseClass):
    """

    :ivar reference_name : Reference name (e.g. in the native pulse schedule system of the device)
    :ivar reference : Reference waveform. Caution : error bars of the reference/data node are not used in the usual sense, instead they are used to describe the control envelope, with a meaning depending on the chosen envelope_type option.
    :ivar reference_type : Reference type:  0:relative (don&#39;t use for the moment, to be defined later when segments are introduced in the IDS structure); 1: absolute: the reference time trace is provided in the reference/data node
    :ivar envelope_type : Envelope type:  0:relative: means that the envelope upper and lower bound values are defined respectively as reference.data * reference.data_error_upper and reference.data * reference.data_error_lower. 1: absolute: the envelope upper and lower bound values are given respectively by reference/data_error_upper and reference/data_error_lower. Lower and upper are taken in the strict mathematical sense, without considering absolute values of the data
    """

    class Meta:
        name = "pulse_schedule_reference_pf_active"
        is_root_ids = False

    reference_name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    reference: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "/pf_active/time"},
            "field_type": np.ndarray,
        },
    )
    reference_type: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    envelope_type: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )


@idspy_dataclass(repr=False, slots=True)
class PulseScheduleReferenceDensity(IdsBaseClass):
    """

    :ivar reference_name : Reference name (e.g. in the native pulse schedule system of the device)
    :ivar reference : Reference waveform. Caution : error bars of the reference/data node are not used in the usual sense, instead they are used to describe the control envelope, with a meaning depending on the chosen envelope_type option.
    :ivar reference_type : Reference type:  0:relative (don&#39;t use for the moment, to be defined later when segments are introduced in the IDS structure); 1: absolute: the reference time trace is provided in the reference/data node
    :ivar envelope_type : Envelope type:  0:relative: means that the envelope upper and lower bound values are defined respectively as reference.data * reference.data_error_upper and reference.data * reference.data_error_lower. 1: absolute: the envelope upper and lower bound values are given respectively by reference/data_error_upper and reference/data_error_lower. Lower and upper are taken in the strict mathematical sense, without considering absolute values of the data
    """

    class Meta:
        name = "pulse_schedule_reference_density"
        is_root_ids = False

    reference_name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    reference: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "/density_control/time"},
            "field_type": np.ndarray,
        },
    )
    reference_type: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    envelope_type: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )


@idspy_dataclass(repr=False, slots=True)
class PulseScheduleReferenceNbi(IdsBaseClass):
    """

    :ivar reference_name : Reference name (e.g. in the native pulse schedule system of the device)
    :ivar reference : Reference waveform. Caution : error bars of the reference/data node are not used in the usual sense, instead they are used to describe the control envelope, with a meaning depending on the chosen envelope_type option.
    :ivar reference_type : Reference type:  0:relative (don&#39;t use for the moment, to be defined later when segments are introduced in the IDS structure); 1: absolute: the reference time trace is provided in the reference/data node
    :ivar envelope_type : Envelope type:  0:relative: means that the envelope upper and lower bound values are defined respectively as reference.data * reference.data_error_upper and reference.data * reference.data_error_lower. 1: absolute: the envelope upper and lower bound values are given respectively by reference/data_error_upper and reference/data_error_lower. Lower and upper are taken in the strict mathematical sense, without considering absolute values of the data
    """

    class Meta:
        name = "pulse_schedule_reference_nbi"
        is_root_ids = False

    reference_name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    reference: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "/nbi/time"},
            "field_type": np.ndarray,
        },
    )
    reference_type: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    envelope_type: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )


@idspy_dataclass(repr=False, slots=True)
class PulseScheduleReferenceLh(IdsBaseClass):
    """

    :ivar reference_name : Reference name (e.g. in the native pulse schedule system of the device)
    :ivar reference : Reference waveform. Caution : error bars of the reference/data node are not used in the usual sense, instead they are used to describe the control envelope, with a meaning depending on the chosen envelope_type option.
    :ivar reference_type : Reference type:  0:relative (don&#39;t use for the moment, to be defined later when segments are introduced in the IDS structure); 1: absolute: the reference time trace is provided in the reference/data node
    :ivar envelope_type : Envelope type:  0:relative: means that the envelope upper and lower bound values are defined respectively as reference.data * reference.data_error_upper and reference.data * reference.data_error_lower. 1: absolute: the envelope upper and lower bound values are given respectively by reference/data_error_upper and reference/data_error_lower. Lower and upper are taken in the strict mathematical sense, without considering absolute values of the data
    """

    class Meta:
        name = "pulse_schedule_reference_lh"
        is_root_ids = False

    reference_name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    reference: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "/lh/time"},
            "field_type": np.ndarray,
        },
    )
    reference_type: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    envelope_type: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )


@idspy_dataclass(repr=False, slots=True)
class PulseScheduleReferenceEc(IdsBaseClass):
    """

    :ivar reference_name : Reference name (e.g. in the native pulse schedule system of the device)
    :ivar reference : Reference waveform. Caution : error bars of the reference/data node are not used in the usual sense, instead they are used to describe the control envelope, with a meaning depending on the chosen envelope_type option.
    :ivar reference_type : Reference type:  0:relative (don&#39;t use for the moment, to be defined later when segments are introduced in the IDS structure); 1: absolute: the reference time trace is provided in the reference/data node
    :ivar envelope_type : Envelope type:  0:relative: means that the envelope upper and lower bound values are defined respectively as reference.data * reference.data_error_upper and reference.data * reference.data_error_lower. 1: absolute: the envelope upper and lower bound values are given respectively by reference/data_error_upper and reference/data_error_lower. Lower and upper are taken in the strict mathematical sense, without considering absolute values of the data
    """

    class Meta:
        name = "pulse_schedule_reference_ec"
        is_root_ids = False

    reference_name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    reference: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "/ec/time"},
            "field_type": np.ndarray,
        },
    )
    reference_type: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    envelope_type: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )


@idspy_dataclass(repr=False, slots=True)
class PulseScheduleReferenceIc(IdsBaseClass):
    """

    :ivar reference_name : Reference name (e.g. in the native pulse schedule system of the device)
    :ivar reference : Reference waveform. Caution : error bars of the reference/data node are not used in the usual sense, instead they are used to describe the control envelope, with a meaning depending on the chosen envelope_type option.
    :ivar reference_type : Reference type:  0:relative (don&#39;t use for the moment, to be defined later when segments are introduced in the IDS structure); 1: absolute: the reference time trace is provided in the reference/data node
    :ivar envelope_type : Envelope type:  0:relative: means that the envelope upper and lower bound values are defined respectively as reference.data * reference.data_error_upper and reference.data * reference.data_error_lower. 1: absolute: the envelope upper and lower bound values are given respectively by reference/data_error_upper and reference/data_error_lower. Lower and upper are taken in the strict mathematical sense, without considering absolute values of the data
    """

    class Meta:
        name = "pulse_schedule_reference_ic"
        is_root_ids = False

    reference_name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    reference: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "/ic/time"},
            "field_type": np.ndarray,
        },
    )
    reference_type: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    envelope_type: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )


@idspy_dataclass(repr=False, slots=True)
class PulseScheduleReferencePosition(IdsBaseClass):
    """

    :ivar reference_name : Reference name (e.g. in the native pulse schedule system of the device)
    :ivar reference : Reference waveform. Caution : error bars of the reference/data node are not used in the usual sense, instead they are used to describe the control envelope, with a meaning depending on the chosen envelope_type option.
    :ivar reference_type : Reference type:  0:relative (don&#39;t use for the moment, to be defined later when segments are introduced in the IDS structure); 1: absolute: the reference time trace is provided in the reference/data node
    :ivar envelope_type : Envelope type:  0:relative: means that the envelope upper and lower bound values are defined respectively as reference.data * reference.data_error_upper and reference.data * reference.data_error_lower. 1: absolute: the envelope upper and lower bound values are given respectively by reference/data_error_upper and reference/data_error_lower. Lower are upper are taken in the strict mathematical sense, without considering absolute values of the data
    """

    class Meta:
        name = "pulse_schedule_reference_position"
        is_root_ids = False

    reference_name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    reference: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "/position_control/time"},
            "field_type": np.ndarray,
        },
    )
    reference_type: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    envelope_type: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )


@idspy_dataclass(repr=False, slots=True)
class PulseScheduleReferenceNoAos(IdsBaseClass):
    """

    :ivar reference_name : Reference name (e.g. in the native pulse schedule system of the device)
    :ivar reference : Reference waveform. Caution : error bars of the reference/data node are not used in the usual sense, instead they are used to describe the control envelope, with a meaning depending on the chosen envelope_type option.
    :ivar reference_type : Reference type:  0:relative (don&#39;t use for the moment, to be defined later when segments are introduced in the IDS structure); 1: absolute: the reference time trace is provided in the reference/data node
    :ivar envelope_type : Envelope type:  0:relative: means that the envelope upper and lower bound values are defined respectively as reference.data * reference.data_error_upper and reference.data * reference.data_error_lower. 1: absolute: the envelope upper and lower bound values are given respectively by reference/data_error_upper and reference/data_error_lower. Lower are upper are taken in the strict mathematical sense, without considering absolute values of the data
    """

    class Meta:
        name = "pulse_schedule_reference_no_aos"
        is_root_ids = False

    reference_name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    reference: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time"},
            "field_type": np.ndarray,
        },
    )
    reference_type: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    envelope_type: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )


@idspy_dataclass(repr=False, slots=True)
class PulseScheduleRz(IdsBaseClass):
    """

    :ivar r : Major radius
    :ivar z : Height
    """

    class Meta:
        name = "pulse_schedule_rz"
        is_root_ids = False

    r: Optional[PulseScheduleReferencePosition] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_position",
            "field_type": PulseScheduleReferencePosition,
        },
    )
    z: Optional[PulseScheduleReferencePosition] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_position",
            "field_type": PulseScheduleReferencePosition,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class PulseScheduleGap(IdsBaseClass):
    """

    :ivar name : Short string identifier (unique for a given device)
    :ivar description : Description, e.g. “channel viewing the upper divertor”
    :ivar r : Major radius of the reference point
    :ivar z : Height of the reference point
    :ivar angle : Angle between the direction in which the gap is measured (in the poloidal cross-section) and the horizontal axis.
    :ivar value : Value of the gap, i.e. distance between the reference point and the separatrix along the gap direction
    """

    class Meta:
        name = "pulse_schedule_gap"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    description: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    r: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    z: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    angle: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    value: Optional[PulseScheduleReferencePosition] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_position",
            "field_type": PulseScheduleReferencePosition,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class PulseScheduleOutline(IdsBaseClass):
    """

    :ivar r : Major radius
    :ivar z : Height
    """

    class Meta:
        name = "pulse_schedule_outline"
        is_root_ids = False

    r: Optional[PulseScheduleReferencePosition] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_position",
            "field_type": PulseScheduleReferencePosition,
        },
    )
    z: Optional[PulseScheduleReferencePosition] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_position",
            "field_type": PulseScheduleReferencePosition,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class PulseScheduleEvent(IdsBaseClass):
    """

    :ivar identifier : Unique identifier of this event provided by the scheduling / event handler
    :ivar time_stamp : Time stamp of this event
    :ivar duration : Duration of this event
    :ivar provider : System having generated this event
    :ivar listeners : Systems listening to this event
    """

    class Meta:
        name = "pulse_schedule_event"
        is_root_ids = False

    identifier: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    time_stamp: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    duration: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    provider: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    listeners: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=str),
        metadata={
            "imas_type": "STR_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class PulseScheduleIcAntenna(IdsBaseClass):
    """

    :ivar name : Short string identifier (unique for a given device)
    :ivar description : Description, e.g. “channel viewing the upper divertor”
    :ivar power_type : Type of power used in the sibling power node (defining which power is referred to in this pulse_schedule). Index = 1: power_launched, 2: power_forward (see definitions in the ic_antennas  IDS)
    :ivar power : Power
    :ivar phase : Phase
    :ivar frequency : Frequency
    """

    class Meta:
        name = "pulse_schedule_ic_antenna"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    description: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    power_type: Optional[IdentifierStatic] = field(
        default=None,
        metadata={
            "imas_type": "identifier_static",
            "field_type": IdentifierStatic,
        },
    )
    power: Optional[PulseScheduleReferenceIc] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_ic",
            "field_type": PulseScheduleReferenceIc,
        },
    )
    phase: Optional[PulseScheduleReferenceIc] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_ic",
            "field_type": PulseScheduleReferenceIc,
        },
    )
    frequency: Optional[PulseScheduleReferenceIc] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_ic",
            "field_type": PulseScheduleReferenceIc,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class PulseScheduleEcBeam(IdsBaseClass):
    """

    :ivar name : Short string identifier (unique for a given device)
    :ivar description : Description, e.g. “channel viewing the upper divertor”
    :ivar power_launched : Beam power launched into the vacuum vessel
    :ivar frequency : Frequency
    :ivar deposition_rho_tor_norm : Normalized toroidal flux coordinate at which the main deposition should occur
    :ivar steering_angle_pol : Steering angle of the EC beam in the R,Z plane (from the -R axis towards the -Z axis), angle_pol=atan2(-k_Z,-k_R), where k_Z and k_R are the Z and R components of the mean wave vector in the EC beam
    :ivar steering_angle_tor : Steering angle of the EC beam away from the poloidal plane that is increasing towards the positive phi axis, angle_tor=arcsin(k_phi/k), where k_phi is the component of the wave vector in the phi direction and k is the length of the wave vector. Here the term wave vector refers to the mean wave vector in the EC beam
    """

    class Meta:
        name = "pulse_schedule_ec_beam"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    description: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    power_launched: Optional[PulseScheduleReferenceEc] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_ec",
            "field_type": PulseScheduleReferenceEc,
        },
    )
    frequency: Optional[PulseScheduleReferenceEc] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_ec",
            "field_type": PulseScheduleReferenceEc,
        },
    )
    deposition_rho_tor_norm: Optional[PulseScheduleReferenceEc] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_ec",
            "field_type": PulseScheduleReferenceEc,
        },
    )
    steering_angle_pol: Optional[PulseScheduleReferenceEc] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_ec",
            "field_type": PulseScheduleReferenceEc,
        },
    )
    steering_angle_tor: Optional[PulseScheduleReferenceEc] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_ec",
            "field_type": PulseScheduleReferenceEc,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class PulseScheduleLhAntenna(IdsBaseClass):
    """

    :ivar name : Short string identifier (unique for a given device)
    :ivar power_type : Type of power used in the sibling power node (defining which power is referred to in this pulse_schedule). Index = 1: power_launched, 2: power_forward (see definitions in the lh_antennas  IDS)
    :ivar power : Power
    :ivar phase : Phasing between neighbour waveguides (in the toroidal direction)
    :ivar n_parallel : Main parallel refractive index of the injected wave power spectrum
    :ivar frequency : Frequency
    :ivar description : Description, e.g. “channel viewing the upper divertor”
    """

    class Meta:
        name = "pulse_schedule_lh_antenna"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    power_type: Optional[IdentifierStatic] = field(
        default=None,
        metadata={
            "imas_type": "identifier_static",
            "field_type": IdentifierStatic,
        },
    )
    power: Optional[PulseScheduleReferenceLh] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_lh",
            "field_type": PulseScheduleReferenceLh,
        },
    )
    phase: Optional[PulseScheduleReferenceLh] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_lh",
            "field_type": PulseScheduleReferenceLh,
        },
    )
    n_parallel: Optional[PulseScheduleReferenceLh] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_lh",
            "field_type": PulseScheduleReferenceLh,
        },
    )
    frequency: Optional[PulseScheduleReferenceLh] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_lh",
            "field_type": PulseScheduleReferenceLh,
        },
    )
    description: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )


@idspy_dataclass(repr=False, slots=True)
class PulseScheduleNbiUnit(IdsBaseClass):
    """

    :ivar name : Short string identifier (unique for a given device)
    :ivar description : Description, e.g. “channel viewing the upper divertor”
    :ivar species : Species injected by the NBI unit (may be more than one in case the unit injects a gas mixture)
    :ivar power : Power launched from this unit into the vacuum vessel
    :ivar energy : Full energy of the injected species (acceleration of a single atom)
    """

    class Meta:
        name = "pulse_schedule_nbi_unit"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    description: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    species: Optional[GasMixtureConstant] = field(
        default_factory=lambda: StructArray(type_input=GasMixtureConstant),
        metadata={
            "imas_type": "gas_mixture_constant",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GasMixtureConstant,
        },
    )
    power: Optional[PulseScheduleReferenceNbi] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_nbi",
            "field_type": PulseScheduleReferenceNbi,
        },
    )
    energy: Optional[PulseScheduleReferenceNbi] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_nbi",
            "field_type": PulseScheduleReferenceNbi,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class PulseScheduleNbi(IdsBaseClass):
    """

    :ivar unit : Set of NBI units
    :ivar power : Total NBI power (sum over the units)
    :ivar mode : Control mode (operation mode and/or settings used by the controller)
    :ivar time : Timebase for the dynamic nodes located at this level of the IDS structure and below
    """

    class Meta:
        name = "pulse_schedule_nbi"
        is_root_ids = False

    unit: Optional[PulseScheduleNbiUnit] = field(
        default_factory=lambda: StructArray(type_input=PulseScheduleNbiUnit),
        metadata={
            "imas_type": "pulse_schedule_nbi_unit",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": PulseScheduleNbiUnit,
        },
    )
    power: Optional[PulseScheduleReferenceNbi] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_nbi",
            "field_type": PulseScheduleReferenceNbi,
        },
    )
    mode: Optional[np.ndarray] = field(
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
class PulseScheduleIc(IdsBaseClass):
    """

    :ivar antenna : Set of ICRH antennas
    :ivar power : Total IC power (sum over the antennas)
    :ivar mode : Control mode (operation mode and/or settings used by the controller)
    :ivar time : Timebase for the dynamic nodes located at this level of the IDS structure and below
    """

    class Meta:
        name = "pulse_schedule_ic"
        is_root_ids = False

    antenna: Optional[PulseScheduleIcAntenna] = field(
        default_factory=lambda: StructArray(type_input=PulseScheduleIcAntenna),
        metadata={
            "imas_type": "pulse_schedule_ic_antenna",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": PulseScheduleIcAntenna,
        },
    )
    power: Optional[PulseScheduleReferenceIc] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_ic",
            "field_type": PulseScheduleReferenceIc,
        },
    )
    mode: Optional[np.ndarray] = field(
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
class PulseScheduleLh(IdsBaseClass):
    """

    :ivar antenna : Set of LH antennas
    :ivar power : Total LH power (sum over the antennas)
    :ivar mode : Control mode (operation mode and/or settings used by the controller)
    :ivar time : Timebase for the dynamic nodes located at this level of the IDS structure and below
    """

    class Meta:
        name = "pulse_schedule_lh"
        is_root_ids = False

    antenna: Optional[PulseScheduleLhAntenna] = field(
        default_factory=lambda: StructArray(type_input=PulseScheduleLhAntenna),
        metadata={
            "imas_type": "pulse_schedule_lh_antenna",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": PulseScheduleLhAntenna,
        },
    )
    power: Optional[PulseScheduleReferenceLh] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_lh",
            "field_type": PulseScheduleReferenceLh,
        },
    )
    mode: Optional[np.ndarray] = field(
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
class PulseScheduleEc(IdsBaseClass):
    """

    :ivar beam : Set of Electron Cyclotron beams
    :ivar power_launched : Total EC power launched in the plasma (sum over the beams)
    :ivar mode : Control mode (operation mode and/or settings used by the controller)
    :ivar time : Timebase for the dynamic nodes located at this level of the IDS structure and below
    """

    class Meta:
        name = "pulse_schedule_ec"
        is_root_ids = False

    beam: Optional[PulseScheduleEcBeam] = field(
        default_factory=lambda: StructArray(type_input=PulseScheduleEcBeam),
        metadata={
            "imas_type": "pulse_schedule_ec_beam",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": PulseScheduleEcBeam,
        },
    )
    power_launched: Optional[PulseScheduleReferenceEc] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_ec",
            "field_type": PulseScheduleReferenceEc,
        },
    )
    mode: Optional[np.ndarray] = field(
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
class PulseScheduleDensityControlIon(IdsBaseClass):
    """

    :ivar element : List of elements forming the atom or molecule
    :ivar z_ion : Ion charge
    :ivar name : String identifying ion (e.g. H, D, T, He, C, D2, ...)
    :ivar n_i_volume_average : Volume averaged ion density (average over the plasma volume up to the LCFS)
    """

    class Meta:
        name = "pulse_schedule_density_control_ion"
        is_root_ids = False

    element: Optional[PlasmaCompositionNeutralElementConstant] = field(
        default_factory=lambda: StructArray(
            type_input=PlasmaCompositionNeutralElementConstant
        ),
        metadata={
            "imas_type": "plasma_composition_neutral_element_constant",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": PlasmaCompositionNeutralElementConstant,
        },
    )
    z_ion: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    n_i_volume_average: Optional[PulseScheduleReferenceDensity] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_density",
            "field_type": PulseScheduleReferenceDensity,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class PulseScheduleDensityControlValve(IdsBaseClass):
    """

    :ivar name : Short string identifier (unique for a given device)
    :ivar description : Description, e.g. “channel viewing the upper divertor”
    :ivar flow_rate : Flow rate of the valve
    :ivar species : Species injected by the valve (may be more than one in case the valve injects a gas mixture)
    """

    class Meta:
        name = "pulse_schedule_density_control_valve"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    description: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    flow_rate: Optional[PulseScheduleReferenceDensity] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_density",
            "field_type": PulseScheduleReferenceDensity,
        },
    )
    species: Optional[GasMixtureConstant] = field(
        default_factory=lambda: StructArray(type_input=GasMixtureConstant),
        metadata={
            "imas_type": "gas_mixture_constant",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GasMixtureConstant,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class PulseScheduleDensityControl(IdsBaseClass):
    """

    :ivar valve : Set of injection valves. Time-dependent
    :ivar n_e_line : Line integrated electron density over a line of sight in the whole vacuum chamber
    :ivar n_e_line_lcfs : Line integrated electron density over a line of sight within the LCFS
    :ivar n_e_profile_average : Integral of a 1D core profile over rho_tor_norm up to the LCFS
    :ivar n_e_line_of_sight : Description of the line of sight for calculating n_e, defined by two points when the beam is not reflected, a third point is added to define the reflected beam path
    :ivar n_e_volume_average : Volume averaged electron density (average over the plasma volume up to the LCFS)
    :ivar zeff : Line averaged effective charge
    :ivar zeff_method : Method for zeff calculation : Index = 1: average over a line of sight in the whole vacuum chamber, 2 : average over a line of sight within the LCFS, 3 : average of a 1D core profile over rho_tor_norm up to the LCFS
    :ivar zeff_line_of_sight : Description of the line of sight for calculating zeff, defined by two points when the beam is not reflected, a third point is added to define the reflected beam path
    :ivar n_t_over_n_d : Average ratio of tritium over deuterium density
    :ivar n_h_over_n_d : Average ratio of hydrogen over deuterium density
    :ivar ion : Quantities related to the different ion species, in the sense of isonuclear or isomolecular sequences
    :ivar mode : Control mode (operation mode and/or settings used by the controller)
    :ivar time : Timebase for the dynamic nodes located at this level of the IDS structure and below
    """

    class Meta:
        name = "pulse_schedule_density_control"
        is_root_ids = False

    valve: Optional[PulseScheduleDensityControlValve] = field(
        default_factory=lambda: StructArray(
            type_input=PulseScheduleDensityControlValve
        ),
        metadata={
            "imas_type": "pulse_schedule_density_control_valve",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": PulseScheduleDensityControlValve,
        },
    )
    n_e_line: Optional[PulseScheduleReferenceDensity] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_density",
            "field_type": PulseScheduleReferenceDensity,
        },
    )
    n_e_line_lcfs: Optional[PulseScheduleReferenceDensity] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_density",
            "field_type": PulseScheduleReferenceDensity,
        },
    )
    n_e_profile_average: Optional[PulseScheduleReferenceDensity] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_density",
            "field_type": PulseScheduleReferenceDensity,
        },
    )
    n_e_line_of_sight: Optional[LineOfSight3Points] = field(
        default=None,
        metadata={
            "imas_type": "line_of_sight_3points",
            "field_type": LineOfSight3Points,
        },
    )
    n_e_volume_average: Optional[PulseScheduleReferenceDensity] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_density",
            "field_type": PulseScheduleReferenceDensity,
        },
    )
    zeff: Optional[PulseScheduleReferenceDensity] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_density",
            "field_type": PulseScheduleReferenceDensity,
        },
    )
    zeff_method: Optional[IdentifierStatic] = field(
        default=None,
        metadata={
            "imas_type": "identifier_static",
            "field_type": IdentifierStatic,
        },
    )
    zeff_line_of_sight: Optional[LineOfSight3Points] = field(
        default=None,
        metadata={
            "imas_type": "line_of_sight_3points",
            "field_type": LineOfSight3Points,
        },
    )
    n_t_over_n_d: Optional[PulseScheduleReferenceDensity] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_density",
            "field_type": PulseScheduleReferenceDensity,
        },
    )
    n_h_over_n_d: Optional[PulseScheduleReferenceDensity] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_density",
            "field_type": PulseScheduleReferenceDensity,
        },
    )
    ion: Optional[PulseScheduleDensityControlIon] = field(
        default_factory=lambda: StructArray(
            type_input=PulseScheduleDensityControlIon
        ),
        metadata={
            "imas_type": "pulse_schedule_density_control_ion",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": PulseScheduleDensityControlIon,
        },
    )
    mode: Optional[np.ndarray] = field(
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
class PulseScheduleFluxControl(IdsBaseClass):
    """

    :ivar ip : Plasma current
    :ivar v_loop : Loop voltage
    :ivar li_3 : Internal inductance
    :ivar beta_tor_norm : Normalized toroidal beta, defined as 100 * beta_tor * a[m] * B0 [T] / ip [MA]
    :ivar mode : Control mode (operation mode and/or settings used by the controller)
    :ivar time : Timebase for the dynamic nodes located at this level of the IDS structure and below
    """

    class Meta:
        name = "pulse_schedule_flux_control"
        is_root_ids = False

    ip: Optional[PulseScheduleReferenceNoAos] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_no_aos",
            "field_type": PulseScheduleReferenceNoAos,
        },
    )
    v_loop: Optional[PulseScheduleReferenceNoAos] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_no_aos",
            "field_type": PulseScheduleReferenceNoAos,
        },
    )
    li_3: Optional[PulseScheduleReferenceNoAos] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_no_aos",
            "field_type": PulseScheduleReferenceNoAos,
        },
    )
    beta_tor_norm: Optional[PulseScheduleReferenceNoAos] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_no_aos",
            "field_type": PulseScheduleReferenceNoAos,
        },
    )
    mode: Optional[np.ndarray] = field(
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
class PulseSchedulePfActiveSupply(IdsBaseClass):
    """

    :ivar name : Short string identifier (unique for a given device)
    :ivar description : Description, e.g. “channel viewing the upper divertor”
    :ivar voltage : Voltage at the supply output (Vside1-Vside2)
    :ivar current : Current fed into one turn of the coil. (Multiply by number of turns to obtain generated magnetic field). Positive when flowing from side 1 to side 2 of the coil, this numbering being made consistently with the convention that the current flows counter-clockwise when viewed from above.
    """

    class Meta:
        name = "pulse_schedule_pf_active_supply"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    description: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    voltage: Optional[PulseScheduleReferencePfActive] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_pf_active",
            "field_type": PulseScheduleReferencePfActive,
        },
    )
    current: Optional[PulseScheduleReferencePfActive] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_pf_active",
            "field_type": PulseScheduleReferencePfActive,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class PulseSchedulePfActiveCoil(IdsBaseClass):
    """

    :ivar name : Short string identifier (unique for a given device)
    :ivar description : Description, e.g. “channel viewing the upper divertor”
    :ivar current : Current fed in the coil (for 1 turn, to be multiplied by the number of turns to obtain the generated magnetic field), positive when flowing from side 1 to side 2 of the coil (inside the coil), this numbering being made consistently with the convention that the current is counter-clockwise when seen from above.
    :ivar resistance_additional : Additional resistance due to e.g. dynamically switchable resistors
    """

    class Meta:
        name = "pulse_schedule_pf_active_coil"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    description: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    current: Optional[PulseScheduleReferencePfActive] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_pf_active",
            "field_type": PulseScheduleReferencePfActive,
        },
    )
    resistance_additional: Optional[PulseScheduleReferencePfActive] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_pf_active",
            "field_type": PulseScheduleReferencePfActive,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class PulseSchedulePfActive(IdsBaseClass):
    """

    :ivar coil : Set of poloidal field coils
    :ivar supply : Set of PF power supplies
    :ivar mode : Control mode (operation mode and/or settings used by the controller)
    :ivar time : Timebase for the dynamic nodes located at this level of the IDS structure and below
    """

    class Meta:
        name = "pulse_schedule_pf_active"
        is_root_ids = False

    coil: Optional[PulseSchedulePfActiveCoil] = field(
        default_factory=lambda: StructArray(
            type_input=PulseSchedulePfActiveCoil
        ),
        metadata={
            "imas_type": "pulse_schedule_pf_active_coil",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": PulseSchedulePfActiveCoil,
        },
    )
    supply: Optional[PulseSchedulePfActiveSupply] = field(
        default_factory=lambda: StructArray(
            type_input=PulseSchedulePfActiveSupply
        ),
        metadata={
            "imas_type": "pulse_schedule_pf_active_supply",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": PulseSchedulePfActiveSupply,
        },
    )
    mode: Optional[np.ndarray] = field(
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
class PulseSchedulePosition(IdsBaseClass):
    """

    :ivar magnetic_axis : Magnetic axis position
    :ivar geometric_axis : RZ position of the geometric axis (defined as (Rmin+Rmax) / 2 and (Zmin+Zmax) / 2 of the boundary)
    :ivar minor_radius : Minor radius of the plasma boundary (defined as (Rmax-Rmin) / 2 of the boundary)
    :ivar elongation : Elongation of the plasma boundary
    :ivar elongation_upper : Elongation (upper half w.r.t. geometric axis) of the plasma boundary
    :ivar elongation_lower : Elongation (lower half w.r.t. geometric axis) of the plasma boundary
    :ivar triangularity : Triangularity of the plasma boundary
    :ivar triangularity_upper : Upper triangularity of the plasma boundary
    :ivar triangularity_lower : Lower triangularity of the plasma boundary
    :ivar triangularity_inner : Inner triangularity of the plasma boundary
    :ivar triangularity_outer : Outer triangularity of the plasma boundary
    :ivar triangularity_minor : Minor triangularity of the plasma boundary
    :ivar squareness_upper_outer : Upper outer squareness of the plasma boundary (definition from T. Luce, Plasma Phys. Control. Fusion 55 (2013) 095009)
    :ivar squareness_upper_inner : Upper inner squareness of the plasma boundary (definition from T. Luce, Plasma Phys. Control. Fusion 55 (2013) 095009)
    :ivar squareness_lower_outer : Lower outer squareness of the plasma boundary (definition from T. Luce, Plasma Phys. Control. Fusion 55 (2013) 095009)
    :ivar squareness_lower_inner : Lower inner squareness of the plasma boundary (definition from T. Luce, Plasma Phys. Control. Fusion 55 (2013) 095009)
    :ivar x_point : Array of X-points, for each of them the RZ position is given
    :ivar strike_point : Array of strike points, for each of them the RZ position is given
    :ivar active_limiter_point : RZ position of the active limiter point (point of the plasma boundary in contact with the limiter)
    :ivar boundary_outline : Set of (R,Z) points defining the outline of the plasma boundary
    :ivar z_r_max : Height of the separatrix point of maximum major radius
    :ivar z_r_min : Height of the separatrix point of minimum major radius
    :ivar gap : Set of gaps, defined by a reference point and a direction.
    :ivar current_centroid : RZ position of the current centroid
    :ivar mode : Control mode (operation mode and/or settings used by the controller)
    :ivar time : Timebase for the dynamic nodes located at this level of the IDS structure and below
    """

    class Meta:
        name = "pulse_schedule_position"
        is_root_ids = False

    magnetic_axis: Optional[PulseScheduleRz] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_rz",
            "field_type": PulseScheduleRz,
        },
    )
    geometric_axis: Optional[PulseScheduleRz] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_rz",
            "field_type": PulseScheduleRz,
        },
    )
    minor_radius: Optional[PulseScheduleReferencePosition] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_position",
            "field_type": PulseScheduleReferencePosition,
        },
    )
    elongation: Optional[PulseScheduleReferencePosition] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_position",
            "field_type": PulseScheduleReferencePosition,
        },
    )
    elongation_upper: Optional[PulseScheduleReferencePosition] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_position",
            "field_type": PulseScheduleReferencePosition,
        },
    )
    elongation_lower: Optional[PulseScheduleReferencePosition] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_position",
            "field_type": PulseScheduleReferencePosition,
        },
    )
    triangularity: Optional[PulseScheduleReferencePosition] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_position",
            "field_type": PulseScheduleReferencePosition,
        },
    )
    triangularity_upper: Optional[PulseScheduleReferencePosition] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_position",
            "field_type": PulseScheduleReferencePosition,
        },
    )
    triangularity_lower: Optional[PulseScheduleReferencePosition] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_position",
            "field_type": PulseScheduleReferencePosition,
        },
    )
    triangularity_inner: Optional[PulseScheduleReferencePosition] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_position",
            "field_type": PulseScheduleReferencePosition,
        },
    )
    triangularity_outer: Optional[PulseScheduleReferencePosition] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_position",
            "field_type": PulseScheduleReferencePosition,
        },
    )
    triangularity_minor: Optional[PulseScheduleReferencePosition] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_position",
            "field_type": PulseScheduleReferencePosition,
        },
    )
    squareness_upper_outer: Optional[PulseScheduleReferencePosition] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_position",
            "field_type": PulseScheduleReferencePosition,
        },
    )
    squareness_upper_inner: Optional[PulseScheduleReferencePosition] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_position",
            "field_type": PulseScheduleReferencePosition,
        },
    )
    squareness_lower_outer: Optional[PulseScheduleReferencePosition] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_position",
            "field_type": PulseScheduleReferencePosition,
        },
    )
    squareness_lower_inner: Optional[PulseScheduleReferencePosition] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_position",
            "field_type": PulseScheduleReferencePosition,
        },
    )
    x_point: Optional[PulseScheduleRz] = field(
        default_factory=lambda: StructArray(type_input=PulseScheduleRz),
        metadata={
            "imas_type": "pulse_schedule_rz",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": PulseScheduleRz,
        },
    )
    strike_point: Optional[PulseScheduleRz] = field(
        default_factory=lambda: StructArray(type_input=PulseScheduleRz),
        metadata={
            "imas_type": "pulse_schedule_rz",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": PulseScheduleRz,
        },
    )
    active_limiter_point: Optional[PulseScheduleRz] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_rz",
            "field_type": PulseScheduleRz,
        },
    )
    boundary_outline: Optional[PulseScheduleOutline] = field(
        default_factory=lambda: StructArray(type_input=PulseScheduleOutline),
        metadata={
            "imas_type": "pulse_schedule_outline",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": PulseScheduleOutline,
        },
    )
    z_r_max: Optional[PulseScheduleReferencePosition] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_position",
            "field_type": PulseScheduleReferencePosition,
        },
    )
    z_r_min: Optional[PulseScheduleReferencePosition] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_position",
            "field_type": PulseScheduleReferencePosition,
        },
    )
    gap: Optional[PulseScheduleGap] = field(
        default_factory=lambda: StructArray(type_input=PulseScheduleGap),
        metadata={
            "imas_type": "pulse_schedule_gap",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": PulseScheduleGap,
        },
    )
    current_centroid: Optional[PulseScheduleRz] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_rz",
            "field_type": PulseScheduleRz,
        },
    )
    mode: Optional[np.ndarray] = field(
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
class PulseScheduleTf(IdsBaseClass):
    """

    :ivar b_field_tor_vacuum_r : Vacuum field times major radius in the toroidal field magnet. Positive sign means anti-clockwise when viewed from above
    :ivar mode : Control mode (operation mode and/or settings used by the controller)
    :ivar time : Timebase for the dynamic nodes located at this level of the IDS structure and below
    """

    class Meta:
        name = "pulse_schedule_tf"
        is_root_ids = False

    b_field_tor_vacuum_r: Optional[PulseScheduleReferenceNoAos] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_reference_no_aos",
            "field_type": PulseScheduleReferenceNoAos,
        },
    )
    mode: Optional[np.ndarray] = field(
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
class PulseSchedule(IdsBaseClass):
    """

    :ivar ids_properties :
    :ivar ic : Ion cyclotron heating and current drive system
    :ivar ec : Electron cyclotron heating and current drive system
    :ivar lh : Lower Hybrid heating and current drive system
    :ivar nbi : Neutral beam heating and current drive system
    :ivar density_control : Gas injection system and density control references
    :ivar event : List of events, either predefined triggers  or events recorded during the pulse
    :ivar flux_control : Magnetic flux control references
    :ivar pf_active : Poloidal field coil references
    :ivar position_control : Plasma position and shape control references
    :ivar tf : Toroidal field references
    :ivar code :
    :ivar time : Generic time
    """

    class Meta:
        name = "pulse_schedule"
        is_root_ids = True

    ids_properties: Optional[IdsProperties] = field(
        default=None,
        metadata={"imas_type": "ids_properties", "field_type": IdsProperties},
    )
    ic: Optional[PulseScheduleIc] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_ic",
            "field_type": PulseScheduleIc,
        },
    )
    ec: Optional[PulseScheduleEc] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_ec",
            "field_type": PulseScheduleEc,
        },
    )
    lh: Optional[PulseScheduleLh] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_lh",
            "field_type": PulseScheduleLh,
        },
    )
    nbi: Optional[PulseScheduleNbi] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_nbi",
            "field_type": PulseScheduleNbi,
        },
    )
    density_control: Optional[PulseScheduleDensityControl] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_density_control",
            "field_type": PulseScheduleDensityControl,
        },
    )
    event: Optional[PulseScheduleEvent] = field(
        default_factory=lambda: StructArray(type_input=PulseScheduleEvent),
        metadata={
            "imas_type": "pulse_schedule_event",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": PulseScheduleEvent,
        },
    )
    flux_control: Optional[PulseScheduleFluxControl] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_flux_control",
            "field_type": PulseScheduleFluxControl,
        },
    )
    pf_active: Optional[PulseSchedulePfActive] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_pf_active",
            "field_type": PulseSchedulePfActive,
        },
    )
    position_control: Optional[PulseSchedulePosition] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_position",
            "field_type": PulseSchedulePosition,
        },
    )
    tf: Optional[PulseScheduleTf] = field(
        default=None,
        metadata={
            "imas_type": "pulse_schedule_tf",
            "field_type": PulseScheduleTf,
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
