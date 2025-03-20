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
class BTorVacuum1(IdsBaseClass):
    """

    :ivar r0 : Reference major radius where the vacuum toroidal magnetic field is given (usually a fixed position such as the middle of the vessel at the equatorial midplane)
    :ivar b0 : Vacuum toroidal field at R0 [T]; Positive sign means anti-clockwise when viewing from above. The product R0B0 must be consistent with the b_tor_vacuum_r field of the tf IDS.
    """

    class Meta:
        name = "b_tor_vacuum_1"
        is_root_ids = False

    r0: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    b0: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "/time"},
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
class NtmTimeSliceModeDetailedEvolutionDeltaw(IdsBaseClass):
    """

    :ivar value : Value of the contribution
    :ivar name : Name of the contribution
    """

    class Meta:
        name = "ntm_time_slice_mode_detailed_evolution_deltaw"
        is_root_ids = False

    value: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time_detailed"},
            "field_type": np.ndarray,
        },
    )
    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )


@idspy_dataclass(repr=False, slots=True)
class NtmTimeSliceModeDetailedEvolutionTorque(IdsBaseClass):
    """

    :ivar value : Value of the contribution
    :ivar name : Name of the contribution
    """

    class Meta:
        name = "ntm_time_slice_mode_detailed_evolution_torque"
        is_root_ids = False

    value: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time_detailed"},
            "field_type": np.ndarray,
        },
    )
    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )


@idspy_dataclass(repr=False, slots=True)
class NtmTimeSliceModeDetailedEvolution(IdsBaseClass):
    """

    :ivar time_detailed : Time array used to describe the detailed evolution of the NTM
    :ivar width : Full width of the mode
    :ivar dwidth_dt : Time derivative of the full width of the mode
    :ivar phase : Phase of the mode
    :ivar dphase_dt : Time derivative of the phase of the mode
    :ivar frequency : Frequency of the mode
    :ivar dfrequency_dt : Time derivative of the frequency of the mode
    :ivar n_phi : Toroidal mode number
    :ivar m_pol : Poloidal mode number
    :ivar deltaw : deltaw contributions to the Rutherford equation
    :ivar torque : torque contributions to the Rutherford equation
    :ivar calculation_method : Description of how the mode evolution is calculated
    :ivar delta_diff : Extra diffusion coefficient for the transport equations of Te, ne, Ti
    :ivar rho_tor_norm : Normalized flux coordinate on which the mode is centred
    :ivar rho_tor : Flux coordinate on which the mode is centred
    """

    class Meta:
        name = "ntm_time_slice_mode_detailed_evolution"
        is_root_ids = False

    time_detailed: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    width: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../time_detailed"},
            "field_type": np.ndarray,
        },
    )
    dwidth_dt: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../time_detailed"},
            "field_type": np.ndarray,
        },
    )
    phase: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../time_detailed"},
            "field_type": np.ndarray,
        },
    )
    dphase_dt: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../time_detailed"},
            "field_type": np.ndarray,
        },
    )
    frequency: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../time_detailed"},
            "field_type": np.ndarray,
        },
    )
    dfrequency_dt: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../time_detailed"},
            "field_type": np.ndarray,
        },
    )
    n_phi: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    m_pol: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    deltaw: Optional[NtmTimeSliceModeDetailedEvolutionDeltaw] = field(
        default_factory=lambda: StructArray(
            type_input=NtmTimeSliceModeDetailedEvolutionDeltaw
        ),
        metadata={
            "imas_type": "ntm_time_slice_mode_detailed_evolution_deltaw",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": NtmTimeSliceModeDetailedEvolutionDeltaw,
        },
    )
    torque: Optional[NtmTimeSliceModeDetailedEvolutionTorque] = field(
        default_factory=lambda: StructArray(
            type_input=NtmTimeSliceModeDetailedEvolutionTorque
        ),
        metadata={
            "imas_type": "ntm_time_slice_mode_detailed_evolution_torque",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": NtmTimeSliceModeDetailedEvolutionTorque,
        },
    )
    calculation_method: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    delta_diff: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "1...3",
                "coordinate2": "../time_detailed",
            },
            "field_type": np.ndarray,
        },
    )
    rho_tor_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../time_detailed"},
            "field_type": np.ndarray,
        },
    )
    rho_tor: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../time_detailed"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class NtmTimeSliceModeEvolutionDeltaw(IdsBaseClass):
    """

    :ivar value : Value of the contribution
    :ivar name : Name of the contribution
    """

    class Meta:
        name = "ntm_time_slice_mode_evolution_deltaw"
        is_root_ids = False

    value: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )


@idspy_dataclass(repr=False, slots=True)
class NtmTimeSliceModeEvolutionTorque(IdsBaseClass):
    """

    :ivar value : Value of the contribution
    :ivar name : Name of the contribution
    """

    class Meta:
        name = "ntm_time_slice_mode_evolution_torque"
        is_root_ids = False

    value: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )


@idspy_dataclass(repr=False, slots=True)
class NtmTimeSliceModeOnset(IdsBaseClass):
    """

    :ivar width : Seed island full width at onset time
    :ivar time_onset : Onset time
    :ivar time_offset : Offset time (when a mode disappears). If the mode reappears later in the simulation, use another index of the mode array of structure
    :ivar phase : Phase of the mode at onset
    :ivar n_phi : Toroidal mode number
    :ivar m_pol : Poloidal mode number
    :ivar cause : Cause of the mode onset
    """

    class Meta:
        name = "ntm_time_slice_mode_onset"
        is_root_ids = False

    width: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    time_onset: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    time_offset: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    phase: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    n_phi: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    m_pol: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    cause: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )


@idspy_dataclass(repr=False, slots=True)
class NtmTimeSliceMode(IdsBaseClass):
    """

    :ivar onset : NTM onset characteristics
    :ivar width : Full width of the mode
    :ivar dwidth_dt : Time derivative of the full width of the mode
    :ivar phase : Phase of the mode
    :ivar dphase_dt : Time derivative of the phase of the mode
    :ivar frequency : Frequency of the mode
    :ivar dfrequency_dt : Time derivative of the frequency of the mode
    :ivar n_phi : Toroidal mode number
    :ivar m_pol : Poloidal mode number
    :ivar deltaw : deltaw contributions to the Rutherford equation
    :ivar torque : torque contributions to the Rutherford equation
    :ivar calculation_method : Description of how the mode evolution is calculated
    :ivar delta_diff : Extra diffusion coefficient for the transport equations of Te, ne, Ti
    :ivar rho_tor_norm : Normalized flux coordinate on which the mode is centred
    :ivar rho_tor : Flux coordinate on which the mode is centred
    :ivar detailed_evolution : Detailed NTM evolution on a finer timebase than the time_slice array of structure
    """

    class Meta:
        name = "ntm_time_slice_mode"
        is_root_ids = False

    onset: Optional[NtmTimeSliceModeOnset] = field(
        default=None,
        metadata={
            "imas_type": "ntm_time_slice_mode_onset",
            "field_type": NtmTimeSliceModeOnset,
        },
    )
    width: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    dwidth_dt: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    phase: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    dphase_dt: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    frequency: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    dfrequency_dt: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    n_phi: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    m_pol: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    deltaw: Optional[NtmTimeSliceModeEvolutionDeltaw] = field(
        default_factory=lambda: StructArray(
            type_input=NtmTimeSliceModeEvolutionDeltaw
        ),
        metadata={
            "imas_type": "ntm_time_slice_mode_evolution_deltaw",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": NtmTimeSliceModeEvolutionDeltaw,
        },
    )
    torque: Optional[NtmTimeSliceModeEvolutionTorque] = field(
        default_factory=lambda: StructArray(
            type_input=NtmTimeSliceModeEvolutionTorque
        ),
        metadata={
            "imas_type": "ntm_time_slice_mode_evolution_torque",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": NtmTimeSliceModeEvolutionTorque,
        },
    )
    calculation_method: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    delta_diff: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...3"},
            "field_type": np.ndarray,
        },
    )
    rho_tor_norm: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    rho_tor: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    detailed_evolution: Optional[NtmTimeSliceModeDetailedEvolution] = field(
        default=None,
        metadata={
            "imas_type": "ntm_time_slice_mode_detailed_evolution",
            "field_type": NtmTimeSliceModeDetailedEvolution,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class NtmTimeSlice(IdsBaseClass):
    """

    :ivar mode : List of the various NTM modes appearing during the simulation. If a mode appears several times, use several indices in this array of structure with the same m,n values.
    :ivar time : Time
    """

    class Meta:
        name = "ntm_time_slice"
        is_root_ids = False

    mode: Optional[NtmTimeSliceMode] = field(
        default_factory=lambda: StructArray(type_input=NtmTimeSliceMode),
        metadata={
            "imas_type": "ntm_time_slice_mode",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": NtmTimeSliceMode,
        },
    )
    time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class Ntms(IdsBaseClass):
    """

    :ivar ids_properties :
    :ivar vacuum_toroidal_field : Characteristics of the vacuum toroidal field (used in rho_tor definition)
    :ivar time_slice : Description of neoclassical tearing modes for various time slices
    :ivar code :
    :ivar time : Generic time
    """

    class Meta:
        name = "ntms"
        is_root_ids = True

    ids_properties: Optional[IdsProperties] = field(
        default=None,
        metadata={"imas_type": "ids_properties", "field_type": IdsProperties},
    )
    vacuum_toroidal_field: Optional[BTorVacuum1] = field(
        default=None,
        metadata={"imas_type": "b_tor_vacuum_1", "field_type": BTorVacuum1},
    )
    time_slice: Optional[NtmTimeSlice] = field(
        default_factory=lambda: StructArray(type_input=NtmTimeSlice),
        metadata={
            "imas_type": "ntm_time_slice",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": NtmTimeSlice,
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
