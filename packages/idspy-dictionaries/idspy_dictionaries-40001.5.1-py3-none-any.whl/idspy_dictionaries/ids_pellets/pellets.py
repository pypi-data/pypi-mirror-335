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
class Rphiz0DDynamicAos3(IdsBaseClass):
    """

    :ivar r : Major radius
    :ivar phi : Toroidal angle (oriented counter-clockwise when viewing from above)
    :ivar z : Height
    """

    class Meta:
        name = "rphiz0d_dynamic_aos3"
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
class IdentifierDynamicAos3(IdsBaseClass):
    """

    :ivar name : Short string identifier
    :ivar index : Integer identifier (enumeration index within a list). Private identifier values must be indicated by a negative index.
    :ivar description : Verbose description
    """

    class Meta:
        name = "identifier_dynamic_aos3"
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
class PlasmaCompositionNeutralElement(IdsBaseClass):
    """

    :ivar a : Mass of atom
    :ivar z_n : Nuclear charge
    :ivar atoms_n : Number of atoms of this element in the molecule
    """

    class Meta:
        name = "plasma_composition_neutral_element"
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
class LineOfSight2PointsDynamicAos3(IdsBaseClass):
    """

    :ivar first_point : Position of the first point
    :ivar second_point : Position of the second point
    """

    class Meta:
        name = "line_of_sight_2points_dynamic_aos3"
        is_root_ids = False

    first_point: Optional[Rphiz0DDynamicAos3] = field(
        default=None,
        metadata={
            "imas_type": "rphiz0d_dynamic_aos3",
            "field_type": Rphiz0DDynamicAos3,
        },
    )
    second_point: Optional[Rphiz0DDynamicAos3] = field(
        default=None,
        metadata={
            "imas_type": "rphiz0d_dynamic_aos3",
            "field_type": Rphiz0DDynamicAos3,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class Rphiz1DDynamicAos3(IdsBaseClass):
    """

    :ivar r : Major radius
    :ivar phi : Toroidal angle (oriented counter-clockwise when viewing from above)
    :ivar z : Height
    """

    class Meta:
        name = "rphiz1d_dynamic_aos3"
        is_root_ids = False

    r: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../r"},
            "field_type": np.ndarray,
        },
    )
    z: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../r"},
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
class PelletsPropellantGas(IdsBaseClass):
    """

    :ivar element : List of elements forming the gas molecule
    :ivar name : String identifying the neutral molecule (e.g. H2, D2, T2, N2, ...)
    :ivar molecules_n : Number of molecules of the propellant gas injected in the vacuum vessel when launching the pellet
    """

    class Meta:
        name = "pellets_propellant_gas"
        is_root_ids = False

    element: Optional[PlasmaCompositionNeutralElement] = field(
        default_factory=lambda: StructArray(
            type_input=PlasmaCompositionNeutralElement
        ),
        metadata={
            "imas_type": "plasma_composition_neutral_element",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": PlasmaCompositionNeutralElement,
        },
    )
    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    molecules_n: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class PelletsTimeSlicePelletShape(IdsBaseClass):
    """

    :ivar type : Identifier structure for the shape type: 1-spherical; 2-cylindrical; 3-rectangular
    :ivar size : Size of the pellet in the various dimensions, depending on the shape type. Spherical pellets: size(1) is the radius of the pellet. Cylindrical pellets: size(1) is the radius and size(2) is the height of the cylinder. Rectangular pellets: size(1) is the height, size(2) is the width and size(3) is the length
    """

    class Meta:
        name = "pellets_time_slice_pellet_shape"
        is_root_ids = False

    type: Optional[IdentifierDynamicAos3] = field(
        default=None,
        metadata={
            "imas_type": "identifier_dynamic_aos3",
            "field_type": IdentifierDynamicAos3,
        },
    )
    size: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class PelletsTimeSlicePelletSpecies(IdsBaseClass):
    """

    :ivar a : Mass of atom
    :ivar z_n : Nuclear charge
    :ivar name : String identifying the species (e.g. H, D, T, ...)
    :ivar density : Material density of the species in the pellet
    :ivar fraction : Atomic fraction of the species in the pellet
    :ivar sublimation_energy : Sublimation energy per atom
    """

    class Meta:
        name = "pellets_time_slice_pellet_species"
        is_root_ids = False

    a: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    z_n: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    density: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    fraction: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    sublimation_energy: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class PelletsTimeSlicePelletPathProfiles(IdsBaseClass):
    """

    :ivar distance : Distance along the pellet path, with the origin taken at path_geometry/first_point. Used as the main coordinate for the path_profiles structure
    :ivar rho_tor_norm : Normalized toroidal coordinate along the pellet path
    :ivar psi : Poloidal flux along the pellet path
    :ivar velocity : Pellet velocity along the pellet path
    :ivar n_e : Electron density along the pellet path
    :ivar t_e : Electron temperature along the pellet path
    :ivar ablation_rate : Ablation rate (electrons) along the pellet path
    :ivar ablated_particles : Number of ablated particles (electrons) along the pellet path
    :ivar rho_tor_norm_drift : Difference to due ExB drifts between the ablation and the final deposition locations, in terms of the normalized toroidal flux coordinate
    :ivar position : Position along the pellet path
    """

    class Meta:
        name = "pellets_time_slice_pellet_path_profiles"
        is_root_ids = False

    distance: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    rho_tor_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../distance"},
            "field_type": np.ndarray,
        },
    )
    psi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../distance"},
            "field_type": np.ndarray,
        },
    )
    velocity: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../distance"},
            "field_type": np.ndarray,
        },
    )
    n_e: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../distance"},
            "field_type": np.ndarray,
        },
    )
    t_e: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../distance"},
            "field_type": np.ndarray,
        },
    )
    ablation_rate: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../distance"},
            "field_type": np.ndarray,
        },
    )
    ablated_particles: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../distance"},
            "field_type": np.ndarray,
        },
    )
    rho_tor_norm_drift: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../distance"},
            "field_type": np.ndarray,
        },
    )
    position: Optional[Rphiz1DDynamicAos3] = field(
        default=None,
        metadata={
            "imas_type": "rphiz1d_dynamic_aos3",
            "field_type": Rphiz1DDynamicAos3,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class PelletsTimeSlicePellet(IdsBaseClass):
    """

    :ivar shape : Initial shape of a pellet at launch
    :ivar species : Set of atomic species included in the pellet composition
    :ivar velocity_initial : Initial velocity of the pellet as it enters the vaccum chamber
    :ivar path_geometry : Geometry of the pellet path in the vaccuum chamber
    :ivar path_profiles : 1-D profiles of plasma and pellet along the pellet path
    :ivar propellant_gas : Propellant gas
    """

    class Meta:
        name = "pellets_time_slice_pellet"
        is_root_ids = False

    shape: Optional[PelletsTimeSlicePelletShape] = field(
        default=None,
        metadata={
            "imas_type": "pellets_time_slice_pellet_shape",
            "field_type": PelletsTimeSlicePelletShape,
        },
    )
    species: Optional[PelletsTimeSlicePelletSpecies] = field(
        default_factory=lambda: StructArray(
            type_input=PelletsTimeSlicePelletSpecies
        ),
        metadata={
            "imas_type": "pellets_time_slice_pellet_species",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": PelletsTimeSlicePelletSpecies,
        },
    )
    velocity_initial: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    path_geometry: Optional[LineOfSight2PointsDynamicAos3] = field(
        default=None,
        metadata={
            "imas_type": "line_of_sight_2points_dynamic_aos3",
            "field_type": LineOfSight2PointsDynamicAos3,
        },
    )
    path_profiles: Optional[PelletsTimeSlicePelletPathProfiles] = field(
        default=None,
        metadata={
            "imas_type": "pellets_time_slice_pellet_path_profiles",
            "field_type": PelletsTimeSlicePelletPathProfiles,
        },
    )
    propellant_gas: Optional[PelletsPropellantGas] = field(
        default=None,
        metadata={
            "imas_type": "pellets_propellant_gas",
            "field_type": PelletsPropellantGas,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class PelletsTimeSlice(IdsBaseClass):
    """

    :ivar pellet : Set of pellets ablated in the plasma at a given time
    :ivar time : Time
    """

    class Meta:
        name = "pellets_time_slice"
        is_root_ids = False

    pellet: Optional[PelletsTimeSlicePellet] = field(
        default_factory=lambda: StructArray(type_input=PelletsTimeSlicePellet),
        metadata={
            "imas_type": "pellets_time_slice_pellet",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": PelletsTimeSlicePellet,
        },
    )
    time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class Pellets(IdsBaseClass):
    """

    :ivar ids_properties :
    :ivar time_slice : Description of the pellets launched at various time slices. The time of this structure corresponds to the full ablation of the pellet inside the plasma.
    :ivar latency : Upper bound of the delay between input command received from the RT network and actuator starting to react. Applies globally to the system described by this IDS unless specific latencies (e.g. channel-specific or antenna-specific) are provided at a deeper level in the IDS structure.
    :ivar code :
    :ivar time : Generic time
    """

    class Meta:
        name = "pellets"
        is_root_ids = True

    ids_properties: Optional[IdsProperties] = field(
        default=None,
        metadata={"imas_type": "ids_properties", "field_type": IdsProperties},
    )
    time_slice: Optional[PelletsTimeSlice] = field(
        default_factory=lambda: StructArray(type_input=PelletsTimeSlice),
        metadata={
            "imas_type": "pellets_time_slice",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": PelletsTimeSlice,
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
