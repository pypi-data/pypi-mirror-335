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
class Rphiz1DDynamicRootTime(IdsBaseClass):
    """

    :ivar r : Major radius
    :ivar phi : Toroidal angle
    :ivar z : Height
    """

    class Meta:
        name = "rphiz1d_dynamic_root_time"
        is_root_ids = False

    r: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "/time"},
            "field_type": np.ndarray,
        },
    )
    phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "/time"},
            "field_type": np.ndarray,
        },
    )
    z: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "/time"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class Xyz0DConstant(IdsBaseClass):
    """

    :ivar x : Component along X axis
    :ivar y : Component along Y axis
    :ivar z : Component along Z axis
    """

    class Meta:
        name = "xyz0d_constant"
        is_root_ids = False

    x: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    y: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    z: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class Xyz0DStatic(IdsBaseClass):
    """

    :ivar x : Component along X axis
    :ivar y : Component along Y axis
    :ivar z : Component along Z axis
    """

    class Meta:
        name = "xyz0d_static"
        is_root_ids = False

    x: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    y: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    z: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
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
class SpiSpeciesDensity(IdsBaseClass):
    """

    :ivar a : Mass of atom
    :ivar z_n : Nuclear charge
    :ivar name : String identifying the species (e.g. H, D, T, ...)
    :ivar density : Density of the species
    """

    class Meta:
        name = "spi_species_density"
        is_root_ids = False

    a: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    z_n: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    density: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class SpiSpeciesFraction(IdsBaseClass):
    """

    :ivar a : Mass of atom
    :ivar z_n : Nuclear charge
    :ivar name : String identifying the species (e.g. H, D, T, ...)
    :ivar fraction : Atomic fraction of the species
    """

    class Meta:
        name = "spi_species_fraction"
        is_root_ids = False

    a: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    z_n: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    fraction: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class SpiFragment(IdsBaseClass):
    """

    :ivar position : Position of the centre of mass of the pellet
    :ivar velocity_r : Major radius component of the fragment velocity
    :ivar velocity_z : Vertical component of the fragment velocity
    :ivar velocity_phi : Toroidal component of the fragment velocity
    :ivar volume : Volume of the fragment
    :ivar species : Atomic species in the fragment composition
    """

    class Meta:
        name = "spi_fragment"
        is_root_ids = False

    position: Optional[Rphiz1DDynamicRootTime] = field(
        default=None,
        metadata={
            "imas_type": "rphiz1d_dynamic_root_time",
            "field_type": Rphiz1DDynamicRootTime,
        },
    )
    velocity_r: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "/time"},
            "field_type": np.ndarray,
        },
    )
    velocity_z: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "/time"},
            "field_type": np.ndarray,
        },
    )
    velocity_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "/time"},
            "field_type": np.ndarray,
        },
    )
    volume: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "/time"},
            "field_type": np.ndarray,
        },
    )
    species: Optional[SpiSpeciesDensity] = field(
        default_factory=lambda: StructArray(type_input=SpiSpeciesDensity),
        metadata={
            "imas_type": "spi_species_density",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": SpiSpeciesDensity,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SpiShatterCone(IdsBaseClass):
    """

    :ivar direction : Unit vector of the cone direction
    :ivar origin : Coordinates of the origin of the shatter cone
    :ivar unit_vector_major : Major unit vector describing the geometry of the elliptic shatter cone
    :ivar unit_vector_minor : Minor unit vector describing the geometry of the elliptic shatter cone
    :ivar angle_major : Angle between the cone direction and unit_vector_major
    :ivar angle_minor : Angle between the cone direction and unit_vector_minor
    """

    class Meta:
        name = "spi_shatter_cone"
        is_root_ids = False

    direction: Optional[Xyz0DConstant] = field(
        default=None,
        metadata={"imas_type": "xyz0d_constant", "field_type": Xyz0DConstant},
    )
    origin: Optional[Rphiz0DStatic] = field(
        default=None,
        metadata={"imas_type": "rphiz0d_static", "field_type": Rphiz0DStatic},
    )
    unit_vector_major: Optional[Xyz0DStatic] = field(
        default=None,
        metadata={"imas_type": "xyz0d_static", "field_type": Xyz0DStatic},
    )
    unit_vector_minor: Optional[Xyz0DStatic] = field(
        default=None,
        metadata={"imas_type": "xyz0d_static", "field_type": Xyz0DStatic},
    )
    angle_major: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    angle_minor: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class SpiShell(IdsBaseClass):
    """

    :ivar species : Atomic species in the shell composition
    :ivar atoms_n : Total number of atoms of desublimated gas
    """

    class Meta:
        name = "spi_shell"
        is_root_ids = False

    species: Optional[SpiSpeciesDensity] = field(
        default_factory=lambda: StructArray(type_input=SpiSpeciesDensity),
        metadata={
            "imas_type": "spi_species_density",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": SpiSpeciesDensity,
        },
    )
    atoms_n: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class SpiGas(IdsBaseClass):
    """

    :ivar flow_rate : Flow rate of the gas at the injector exit
    :ivar species : Atomic species in the gas composition
    :ivar atoms_n : Total number of atoms of the gas
    :ivar temperature : Gas temperature
    """

    class Meta:
        name = "spi_gas"
        is_root_ids = False

    flow_rate: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "/time"},
            "field_type": np.ndarray,
        },
    )
    species: Optional[SpiSpeciesFraction] = field(
        default_factory=lambda: StructArray(type_input=SpiSpeciesFraction),
        metadata={
            "imas_type": "spi_species_fraction",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": SpiSpeciesFraction,
        },
    )
    atoms_n: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    temperature: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class SpiPellet(IdsBaseClass):
    """

    :ivar position : Position of the centre of mass of the pellet
    :ivar velocity_r : Major radius component of the velocity of the centre of mass of the pellet
    :ivar velocity_z : Vertical component of the velocity of the centre of mass of the pellet
    :ivar velocity_phi : Toroidal component of the velocity of the centre of mass of the pellet
    :ivar velocity_shatter : Norm of the velocity of the centre of mass of the pellet right before shattering
    :ivar diameter : Pellet diameter
    :ivar length : Pellet length (cylindrical pellet)
    :ivar shell : Shell-layer around of the unshattered pellet
    :ivar core : Core of the unshattered pellet
    """

    class Meta:
        name = "spi_pellet"
        is_root_ids = False

    position: Optional[Rphiz1DDynamicRootTime] = field(
        default=None,
        metadata={
            "imas_type": "rphiz1d_dynamic_root_time",
            "field_type": Rphiz1DDynamicRootTime,
        },
    )
    velocity_r: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "/time"},
            "field_type": np.ndarray,
        },
    )
    velocity_z: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "/time"},
            "field_type": np.ndarray,
        },
    )
    velocity_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "/time"},
            "field_type": np.ndarray,
        },
    )
    velocity_shatter: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    diameter: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    length: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    shell: Optional[SpiShell] = field(
        default=None,
        metadata={"imas_type": "spi_shell", "field_type": SpiShell},
    )
    core: Optional[SpiShell] = field(
        default=None,
        metadata={"imas_type": "spi_shell", "field_type": SpiShell},
    )


@idspy_dataclass(repr=False, slots=True)
class SpiOpd(IdsBaseClass):
    """

    :ivar position : Position of the measurement
    :ivar time_arrival : Arrival time at the optical pellet diagnostic, for each object
    """

    class Meta:
        name = "spi_opd"
        is_root_ids = False

    position: Optional[Rphiz0DStatic] = field(
        default=None,
        metadata={"imas_type": "rphiz0d_static", "field_type": Rphiz0DStatic},
    )
    time_arrival: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SpiSingle(IdsBaseClass):
    """

    :ivar name : Short string identifier (unique for a given device)
    :ivar description : Description, e.g. “channel viewing the upper divertor”
    :ivar optical_pellet_diagnostic : Information related to the embedded optical pellet diagnostic
    :ivar time_trigger : Time of trigger request to the power supply according to the DMS sequence
    :ivar time_shatter : Arrival time at the shattering unit
    :ivar pellet : Information related to the pellet
    :ivar fragmentation_gas : Description of the gas produced during fragmentation
    :ivar propellant_gas : Description of the propellant gas
    :ivar injection_direction : Unit vector of the unshattered pellet velocity direction right before shattering
    :ivar shattering_position : Position where the pellet is shattered. It is defined as the intersection of the trayectory of the pellet center of mass with the shattering element
    :ivar shattering_angle : Impact (or grazing) angle of the pellet with the shattering element. It is the complementary of the incidence angle with the element surface at the shattering location
    :ivar shatter_cone : Description of the elliptic shatter cone
    :ivar velocity_mass_centre_fragments_r : Major radius component of the velocity of the centre of mass of the fragments at the shattering cone origin
    :ivar velocity_mass_centre_fragments_z : Vertical component of the velocity velocity of the centre of mass of the fragments at the shattering cone origin
    :ivar velocity_mass_centre_fragments_phi : Toroidal component of the velocity of the centre of mass of the fragments at the shattering cone origin
    :ivar fragment : Set of shattered pellet fragments
    """

    class Meta:
        name = "spi_single"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    description: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    optical_pellet_diagnostic: Optional[SpiOpd] = field(
        default=None, metadata={"imas_type": "spi_opd", "field_type": SpiOpd}
    )
    time_trigger: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    time_shatter: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    pellet: Optional[SpiPellet] = field(
        default=None,
        metadata={"imas_type": "spi_pellet", "field_type": SpiPellet},
    )
    fragmentation_gas: Optional[SpiGas] = field(
        default=None, metadata={"imas_type": "spi_gas", "field_type": SpiGas}
    )
    propellant_gas: Optional[SpiGas] = field(
        default=None, metadata={"imas_type": "spi_gas", "field_type": SpiGas}
    )
    injection_direction: Optional[Xyz0DConstant] = field(
        default=None,
        metadata={"imas_type": "xyz0d_constant", "field_type": Xyz0DConstant},
    )
    shattering_position: Optional[Rphiz0DStatic] = field(
        default=None,
        metadata={"imas_type": "rphiz0d_static", "field_type": Rphiz0DStatic},
    )
    shattering_angle: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    shatter_cone: Optional[SpiShatterCone] = field(
        default=None,
        metadata={
            "imas_type": "spi_shatter_cone",
            "field_type": SpiShatterCone,
        },
    )
    velocity_mass_centre_fragments_r: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    velocity_mass_centre_fragments_z: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    velocity_mass_centre_fragments_phi: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    fragment: Optional[SpiFragment] = field(
        default_factory=lambda: StructArray(type_input=SpiFragment),
        metadata={
            "imas_type": "spi_fragment",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": SpiFragment,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class Spi(IdsBaseClass):
    """

    :ivar ids_properties :
    :ivar injector : Set of shattered pellet injectors
    :ivar latency : Upper bound of the delay between input command received from the RT network and actuator starting to react. Applies globally to the system described by this IDS unless specific latencies (e.g. channel-specific or antenna-specific) are provided at a deeper level in the IDS structure.
    :ivar code :
    :ivar time : Generic time
    """

    class Meta:
        name = "spi"
        is_root_ids = True

    ids_properties: Optional[IdsProperties] = field(
        default=None,
        metadata={"imas_type": "ids_properties", "field_type": IdsProperties},
    )
    injector: Optional[SpiSingle] = field(
        default_factory=lambda: StructArray(type_input=SpiSingle),
        metadata={
            "imas_type": "spi_single",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": SpiSingle,
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
