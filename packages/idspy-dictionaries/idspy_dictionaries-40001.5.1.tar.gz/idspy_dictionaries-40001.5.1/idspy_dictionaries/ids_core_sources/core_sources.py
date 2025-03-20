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
class PlasmaCompositionNeutralStateConstant(IdsBaseClass):
    """

    :ivar name : String identifying neutral state
    :ivar electron_configuration : Configuration of atomic orbitals of this state, e.g. 1s2-2s1
    :ivar vibrational_level : Vibrational level (can be bundled)
    :ivar vibrational_mode : Vibrational mode of this state, e.g. &#34;A_g&#34;. Need to define, or adopt a standard nomenclature.
    """

    class Meta:
        name = "plasma_composition_neutral_state_constant"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    electron_configuration: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    vibrational_level: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    vibrational_mode: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )


@idspy_dataclass(repr=False, slots=True)
class PlasmaCompositionIonStateConstant(IdsBaseClass):
    """

    :ivar z_min : Minimum Z of the charge state bundle (z_min = z_max = 0 for a neutral)
    :ivar z_max : Maximum Z of the charge state bundle (equal to z_min if no bundle)
    :ivar name : String identifying ion state (e.g. C+, C+2 , C+3, C+4, C+5, C+6, ...)
    :ivar electron_configuration : Configuration of atomic orbitals of this state, e.g. 1s2-2s1
    :ivar vibrational_level : Vibrational level (can be bundled)
    :ivar vibrational_mode : Vibrational mode of this state, e.g. &#34;A_g&#34;. Need to define, or adopt a standard nomenclature.
    """

    class Meta:
        name = "plasma_composition_ion_state_constant"
        is_root_ids = False

    z_min: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    z_max: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    electron_configuration: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    vibrational_level: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    vibrational_mode: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )


@idspy_dataclass(repr=False, slots=True)
class PlasmaCompositionNeutralConstant(IdsBaseClass):
    """

    :ivar element : List of elements forming the atom or molecule
    :ivar name : String identifying neutral (e.g. H, D, T, He, C, ...)
    :ivar state : State of the species (energy, excitation, ...)
    """

    class Meta:
        name = "plasma_composition_neutral_constant"
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
    state: Optional[PlasmaCompositionNeutralStateConstant] = field(
        default=None,
        metadata={
            "imas_type": "plasma_composition_neutral_state_constant",
            "field_type": PlasmaCompositionNeutralStateConstant,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class PlasmaCompositionIonsConstant(IdsBaseClass):
    """

    :ivar element : List of elements forming the atom or molecule
    :ivar z_ion : Ion charge (of the dominant ionization state; lumped ions are allowed)
    :ivar name : String identifying ion (e.g. H+, D+, T+, He+2, C+, ...)
    :ivar state : Quantities related to the different states of the species (ionization, energy, excitation, ...)
    """

    class Meta:
        name = "plasma_composition_ions_constant"
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
    state: Optional[PlasmaCompositionIonStateConstant] = field(
        default=None,
        metadata={
            "imas_type": "plasma_composition_ion_state_constant",
            "field_type": PlasmaCompositionIonStateConstant,
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
class CodeWithTimebase(IdsBaseClass):
    """

    :ivar name : Name of software used
    :ivar description : Short description of the software (type, purpose)
    :ivar commit : Unique commit reference of software
    :ivar version : Unique version (tag) of software
    :ivar repository : URL of software repository
    :ivar parameters : List of the code specific parameters in XML format
    :ivar output_flag : Output flag : 0 means the run is successful, other values mean some difficulty has been encountered, the exact meaning is then code specific. Negative values mean the result shall not be used.
    """

    class Meta:
        name = "code_with_timebase"
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
    output_flag: Optional[SignalInt1D] = field(
        default=None,
        metadata={"imas_type": "signal_int_1d", "field_type": SignalInt1D},
    )


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
class DistributionSpecies(IdsBaseClass):
    """

    :ivar ion : Description of the ion or neutral species, used if type/index = 2 or 3
    :ivar neutral : Description of the neutral species, used if type/index = 4 or 5
    """

    class Meta:
        name = "distribution_species"
        is_root_ids = False

    ion: Optional[PlasmaCompositionIonsConstant] = field(
        default=None,
        metadata={
            "imas_type": "plasma_composition_ions_constant",
            "field_type": PlasmaCompositionIonsConstant,
        },
    )
    neutral: Optional[PlasmaCompositionNeutralConstant] = field(
        default=None,
        metadata={
            "imas_type": "plasma_composition_neutral_constant",
            "field_type": PlasmaCompositionNeutralConstant,
        },
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
class CoreRadialGrid(IdsBaseClass):
    """

    :ivar rho_tor_norm : Normalized toroidal flux coordinate. The normalizing value for rho_tor_norm, is the toroidal flux coordinate at the equilibrium boundary (LCFS or 99.x % of the LCFS in case of a fixed boundary equilibium calculation, see time_slice/boundary/b_flux_pol_norm in the equilibrium IDS)
    :ivar rho_tor : Toroidal flux coordinate = sqrt(phi/(pi*b0)), where the toroidal magnetic field, b0, corresponds to that stored in vacuum_toroidal_field/b0 and pi can be found in the IMAS constants
    :ivar rho_pol_norm : Normalized poloidal flux coordinate = sqrt((psi(rho)-psi(magnetic_axis)) / (psi(LCFS)-psi(magnetic_axis)))
    :ivar psi : Poloidal magnetic flux. Integral of magnetic field passing through a contour defined by the intersection of a flux surface passing through the point of interest and a Z=constant plane. If the integration surface is flat, the surface normal vector is in the increasing vertical coordinate direction, Z, namely upwards.
    :ivar volume : Volume enclosed inside the magnetic surface
    :ivar area : Cross-sectional area of the flux surface
    :ivar surface : Surface area of the toroidal flux surface
    :ivar psi_magnetic_axis : Value of the poloidal magnetic flux at the magnetic axis (useful to normalize the psi array values when the radial grid doesn&#39;t go from the magnetic axis to the plasma boundary)
    :ivar psi_boundary : Value of the poloidal magnetic flux at the plasma boundary (useful to normalize the psi array values when the radial grid doesn&#39;t go from the magnetic axis to the plasma boundary)
    """

    class Meta:
        name = "core_radial_grid"
        is_root_ids = False

    rho_tor_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    rho_tor: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    rho_pol_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    psi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    volume: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    area: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    surface: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    psi_magnetic_axis: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    psi_boundary: Optional[float] = field(
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
class CoreSourcesSourceProfiles1DParticlesDecomposed2(IdsBaseClass):
    """

    :ivar implicit_part : Implicit part of the source term, i.e. to be multiplied by the equation&#39;s primary quantity
    :ivar explicit_part : Explicit part of the source term
    """

    class Meta:
        name = "core_sources_source_profiles_1d_particles_decomposed_2"
        is_root_ids = False

    implicit_part: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    explicit_part: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class CoreSourcesSourceProfiles1DParticlesDecomposed3(IdsBaseClass):
    """

    :ivar implicit_part : Implicit part of the source term, i.e. to be multiplied by the equation&#39;s primary quantity
    :ivar explicit_part : Explicit part of the source term
    """

    class Meta:
        name = "core_sources_source_profiles_1d_particles_decomposed_3"
        is_root_ids = False

    implicit_part: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    explicit_part: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class CoreSourcesSourceProfiles1DParticlesDecomposed4(IdsBaseClass):
    """

    :ivar implicit_part : Implicit part of the source term, i.e. to be multiplied by the equation&#39;s primary quantity
    :ivar explicit_part : Explicit part of the source term
    """

    class Meta:
        name = "core_sources_source_profiles_1d_particles_decomposed_4"
        is_root_ids = False

    implicit_part: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    explicit_part: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class CoreSourcesSourceProfiles1DMomentumDecomposed4(IdsBaseClass):
    """

    :ivar implicit_part : Implicit part of the source term, i.e. to be multiplied by the equation&#39;s primary quantity
    :ivar explicit_part : Explicit part of the source term
    """

    class Meta:
        name = "core_sources_source_profiles_1d_momentum_decomposed_4"
        is_root_ids = False

    implicit_part: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    explicit_part: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class CoreSourcesSourceProfiles1DEnergyDecomposed4(IdsBaseClass):
    """

    :ivar implicit_part : Implicit part of the source term, i.e. to be multiplied by the equation&#39;s primary quantity
    :ivar explicit_part : Explicit part of the source term
    """

    class Meta:
        name = "core_sources_source_profiles_1d_energy_decomposed_4"
        is_root_ids = False

    implicit_part: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    explicit_part: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class CoreSourcesSourceProfiles1DEnergyDecomposed3(IdsBaseClass):
    """

    :ivar implicit_part : Implicit part of the source term, i.e. to be multiplied by the equation&#39;s primary quantity
    :ivar explicit_part : Explicit part of the source term
    """

    class Meta:
        name = "core_sources_source_profiles_1d_energy_decomposed_3"
        is_root_ids = False

    implicit_part: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    explicit_part: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class CoreSourcesSourceProfiles1DEnergyDecomposed2(IdsBaseClass):
    """

    :ivar implicit_part : Implicit part of the source term, i.e. to be multiplied by the equation&#39;s primary quantity
    :ivar explicit_part : Explicit part of the source term
    """

    class Meta:
        name = "core_sources_source_profiles_1d_energy_decomposed_2"
        is_root_ids = False

    implicit_part: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    explicit_part: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class CoreSourcesSourceProfiles1DNeutralState(IdsBaseClass):
    """

    :ivar name : String identifying state
    :ivar vibrational_level : Vibrational level (can be bundled)
    :ivar vibrational_mode : Vibrational mode of this state, e.g. &#34;A_g&#34;. Need to define, or adopt a standard nomenclature.
    :ivar neutral_type : Neutral type (if the considered state is a neutral), in terms of energy. ID =1: cold; 2: thermal; 3: fast; 4: NBI
    :ivar electron_configuration : Configuration of atomic orbitals of this state, e.g. 1s2-2s1
    :ivar particles : Source term for the state density transport equation
    :ivar energy : Source terms for the state energy transport equation
    """

    class Meta:
        name = "core_sources_source_profiles_1d_neutral_state"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    vibrational_level: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    vibrational_mode: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    neutral_type: Optional[IdentifierDynamicAos3] = field(
        default=None,
        metadata={
            "imas_type": "identifier_dynamic_aos3",
            "field_type": IdentifierDynamicAos3,
        },
    )
    electron_configuration: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    particles: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    energy: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class CoreSourcesSourceProfiles1DNeutral(IdsBaseClass):
    """

    :ivar element : List of elements forming the atom or molecule
    :ivar name : String identifying the neutral species (e.g. H, D, T, He, C, ...)
    :ivar ion_index : Index of the corresponding ion species in the ../../ion array
    :ivar particles : Source term for neutral density equation
    :ivar energy : Source term for the neutral energy transport equation.
    :ivar multiple_states_flag : Multiple states calculation flag : 0-Only one state is considered; 1-Multiple states are considered and are described in the state structure
    :ivar state : Source terms related to the different charge states of the species (energy, excitation, ...)
    """

    class Meta:
        name = "core_sources_source_profiles_1d_neutral"
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
    ion_index: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    particles: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    energy: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    multiple_states_flag: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    state: Optional[CoreSourcesSourceProfiles1DNeutralState] = field(
        default_factory=lambda: StructArray(
            type_input=CoreSourcesSourceProfiles1DNeutralState
        ),
        metadata={
            "imas_type": "core_sources_source_profiles_1d_neutral_state",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": CoreSourcesSourceProfiles1DNeutralState,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class CoreSourcesSourceProfiles1DComponents2(IdsBaseClass):
    """

    :ivar radial : Radial component
    :ivar diamagnetic : Diamagnetic component
    :ivar parallel : Parallel component
    :ivar poloidal : Poloidal component
    :ivar toroidal : Toroidal component
    :ivar toroidal_decomposed : Decomposition of the source term for ion toroidal momentum equation into implicit and explicit parts
    """

    class Meta:
        name = "core_sources_source_profiles_1d_components_2"
        is_root_ids = False

    radial: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    diamagnetic: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    poloidal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    toroidal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    toroidal_decomposed: Optional[
        CoreSourcesSourceProfiles1DMomentumDecomposed4
    ] = field(
        default=None,
        metadata={
            "imas_type": "core_sources_source_profiles_1d_momentum_decomposed_4",
            "field_type": CoreSourcesSourceProfiles1DMomentumDecomposed4,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class CoreSourcesSourceProfiles1DIonsChargeStates(IdsBaseClass):
    """

    :ivar z_min : Minimum Z of the charge state bundle
    :ivar z_max : Maximum Z of the charge state bundle
    :ivar name : String identifying charge state (e.g. C+, C+2 , C+3, C+4, C+5, C+6, ...)
    :ivar vibrational_level : Vibrational level (can be bundled)
    :ivar vibrational_mode : Vibrational mode of this state, e.g. &#34;A_g&#34;. Need to define, or adopt a standard nomenclature.
    :ivar electron_configuration : Configuration of atomic orbitals of this state, e.g. 1s2-2s1
    :ivar particles : Source term for the charge state density transport equation
    :ivar particles_inside : State source inside the flux surface. Cumulative volume integral of the source term for the electron density equation.
    :ivar particles_decomposed : Decomposition of the source term for state density equation into implicit and explicit parts
    :ivar energy : Source terms for the charge state energy transport equation
    :ivar power_inside : Power coupled to the state inside the flux surface. Cumulative volume integral of the source term for the electron energy equation
    :ivar energy_decomposed : Decomposition of the source term for state energy equation into implicit and explicit parts
    """

    class Meta:
        name = "core_sources_source_profiles_1d_ions_charge_states"
        is_root_ids = False

    z_min: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    z_max: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    vibrational_level: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    vibrational_mode: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    electron_configuration: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    particles: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    particles_inside: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    particles_decomposed: Optional[
        CoreSourcesSourceProfiles1DParticlesDecomposed4
    ] = field(
        default=None,
        metadata={
            "imas_type": "core_sources_source_profiles_1d_particles_decomposed_4",
            "field_type": CoreSourcesSourceProfiles1DParticlesDecomposed4,
        },
    )
    energy: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    power_inside: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    energy_decomposed: Optional[
        CoreSourcesSourceProfiles1DEnergyDecomposed4
    ] = field(
        default=None,
        metadata={
            "imas_type": "core_sources_source_profiles_1d_energy_decomposed_4",
            "field_type": CoreSourcesSourceProfiles1DEnergyDecomposed4,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class CoreSourcesSourceProfiles1DIons(IdsBaseClass):
    """

    :ivar element : List of elements forming the atom or molecule
    :ivar z_ion : Ion charge (of the dominant ionization state; lumped ions are allowed)
    :ivar name : String identifying ion (e.g. H, D, T, He, C, D2, ...)
    :ivar neutral_index : Index of the corresponding neutral species in the ../../neutral array
    :ivar particles : Source term for ion density equation
    :ivar particles_inside : Ion source inside the flux surface. Cumulative volume integral of the source term for the electron density equation.
    :ivar particles_decomposed : Decomposition of the source term for ion density equation into implicit and explicit parts
    :ivar energy : Source term for the ion energy transport equation.
    :ivar power_inside : Power coupled to the ion species inside the flux surface. Cumulative volume integral of the source term for the electron energy equation
    :ivar energy_decomposed : Decomposition of the source term for ion energy equation into implicit and explicit parts
    :ivar momentum : Source term for the ion momentum transport equations along various components (directions)
    :ivar multiple_states_flag : Multiple states calculation flag : 0-Only the &#39;ion&#39; level is considered and the &#39;state&#39; array of structure is empty; 1-Ion states are considered and are described in the &#39;state&#39; array of structure
    :ivar state : Source terms related to the different charge states of the species (ionization, energy, excitation, ...)
    """

    class Meta:
        name = "core_sources_source_profiles_1d_ions"
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
    z_ion: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    neutral_index: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    particles: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    particles_inside: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    particles_decomposed: Optional[
        CoreSourcesSourceProfiles1DParticlesDecomposed3
    ] = field(
        default=None,
        metadata={
            "imas_type": "core_sources_source_profiles_1d_particles_decomposed_3",
            "field_type": CoreSourcesSourceProfiles1DParticlesDecomposed3,
        },
    )
    energy: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    power_inside: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    energy_decomposed: Optional[
        CoreSourcesSourceProfiles1DEnergyDecomposed3
    ] = field(
        default=None,
        metadata={
            "imas_type": "core_sources_source_profiles_1d_energy_decomposed_3",
            "field_type": CoreSourcesSourceProfiles1DEnergyDecomposed3,
        },
    )
    momentum: Optional[CoreSourcesSourceProfiles1DComponents2] = field(
        default=None,
        metadata={
            "imas_type": "core_sources_source_profiles_1d_components_2",
            "field_type": CoreSourcesSourceProfiles1DComponents2,
        },
    )
    multiple_states_flag: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    state: Optional[CoreSourcesSourceProfiles1DIonsChargeStates] = field(
        default_factory=lambda: StructArray(
            type_input=CoreSourcesSourceProfiles1DIonsChargeStates
        ),
        metadata={
            "imas_type": "core_sources_source_profiles_1d_ions_charge_states",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": CoreSourcesSourceProfiles1DIonsChargeStates,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class CoreSourcesSourceProfiles1DElectrons(IdsBaseClass):
    """

    :ivar particles : Source term for electron density equation
    :ivar particles_decomposed : Decomposition of the source term for electron density equation into implicit and explicit parts
    :ivar particles_inside : Electron source inside the flux surface. Cumulative volume integral of the source term for the electron density equation.
    :ivar energy : Source term for the electron energy equation
    :ivar energy_decomposed : Decomposition of the source term for electron energy equation into implicit and explicit parts
    :ivar power_inside : Power coupled to electrons inside the flux surface. Cumulative volume integral of the source term for the electron energy equation
    """

    class Meta:
        name = "core_sources_source_profiles_1d_electrons"
        is_root_ids = False

    particles: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    particles_decomposed: Optional[
        CoreSourcesSourceProfiles1DParticlesDecomposed3
    ] = field(
        default=None,
        metadata={
            "imas_type": "core_sources_source_profiles_1d_particles_decomposed_3",
            "field_type": CoreSourcesSourceProfiles1DParticlesDecomposed3,
        },
    )
    particles_inside: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    energy: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    energy_decomposed: Optional[
        CoreSourcesSourceProfiles1DEnergyDecomposed3
    ] = field(
        default=None,
        metadata={
            "imas_type": "core_sources_source_profiles_1d_energy_decomposed_3",
            "field_type": CoreSourcesSourceProfiles1DEnergyDecomposed3,
        },
    )
    power_inside: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class CoreSourcesSourceProfiles1D(IdsBaseClass):
    """

    :ivar grid : Radial grid
    :ivar electrons : Sources for electrons
    :ivar total_ion_energy : Source term for the total (summed over ion  species) energy equation
    :ivar total_ion_energy_decomposed : Decomposition of the source term for total ion energy equation into implicit and explicit parts
    :ivar total_ion_power_inside : Total power coupled to ion species (summed over ion  species) inside the flux surface. Cumulative volume integral of the source term for the total ion energy equation
    :ivar total_ion_particles : Source term for the total (summed over ion species) ion density equation
    :ivar total_ion_particles_decomposed : Decomposition of the source term for total ion density equation into implicit and explicit parts
    :ivar total_ion_particles_inside : Total ion particle source (summed over ion species) inside the flux surface. Cumulative volume integral of the source term for the total ion density equation
    :ivar momentum_phi : Source term for total toroidal momentum equation
    :ivar torque_phi_inside : Toroidal torque inside the flux surface. Cumulative volume integral of the source term for the total toroidal momentum equation
    :ivar momentum_phi_j_cross_b_field : Contribution to the toroidal momentum source term (already included in the momentum_tor node) corresponding to the toroidal torques onto the thermal plasma due to Lorentz force associated with radial currents. These currents appear as return-currents (enforcing quasi-neutrality, div(J)=0) balancing radial currents of non-thermal particles, e.g. radial currents of fast and trapped neutral-beam-ions.
    :ivar j_parallel : Parallel current density source, average(J.B) / B0, where B0 = core_sources/vacuum_toroidal_field/b0
    :ivar current_parallel_inside : Parallel current driven inside the flux surface. Cumulative surface integral of j_parallel
    :ivar conductivity_parallel : Parallel conductivity due to this source
    :ivar ion : Source terms related to the different ions species, in the sense of isonuclear or isomolecular sequences. Ionization states (and other types of states) must be differentiated at the state level below
    :ivar neutral : Source terms related to the different neutral species
    :ivar time : Time
    """

    class Meta:
        name = "core_sources_source_profiles_1d"
        is_root_ids = False

    grid: Optional[CoreRadialGrid] = field(
        default=None,
        metadata={
            "imas_type": "core_radial_grid",
            "field_type": CoreRadialGrid,
        },
    )
    electrons: Optional[CoreSourcesSourceProfiles1DElectrons] = field(
        default=None,
        metadata={
            "imas_type": "core_sources_source_profiles_1d_electrons",
            "field_type": CoreSourcesSourceProfiles1DElectrons,
        },
    )
    total_ion_energy: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    total_ion_energy_decomposed: Optional[
        CoreSourcesSourceProfiles1DEnergyDecomposed2
    ] = field(
        default=None,
        metadata={
            "imas_type": "core_sources_source_profiles_1d_energy_decomposed_2",
            "field_type": CoreSourcesSourceProfiles1DEnergyDecomposed2,
        },
    )
    total_ion_power_inside: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    total_ion_particles: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    total_ion_particles_decomposed: Optional[
        CoreSourcesSourceProfiles1DParticlesDecomposed2
    ] = field(
        default=None,
        metadata={
            "imas_type": "core_sources_source_profiles_1d_particles_decomposed_2",
            "field_type": CoreSourcesSourceProfiles1DParticlesDecomposed2,
        },
    )
    total_ion_particles_inside: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    momentum_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    torque_phi_inside: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    momentum_phi_j_cross_b_field: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    j_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    current_parallel_inside: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    conductivity_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    ion: Optional[CoreSourcesSourceProfiles1DIons] = field(
        default_factory=lambda: StructArray(
            type_input=CoreSourcesSourceProfiles1DIons
        ),
        metadata={
            "imas_type": "core_sources_source_profiles_1d_ions",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": CoreSourcesSourceProfiles1DIons,
        },
    )
    neutral: Optional[CoreSourcesSourceProfiles1DNeutral] = field(
        default_factory=lambda: StructArray(
            type_input=CoreSourcesSourceProfiles1DNeutral
        ),
        metadata={
            "imas_type": "core_sources_source_profiles_1d_neutral",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": CoreSourcesSourceProfiles1DNeutral,
        },
    )
    time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class CoreSourcesSourceGlobalElectrons(IdsBaseClass):
    """

    :ivar particles : Electron particle source
    :ivar power : Power coupled to electrons
    """

    class Meta:
        name = "core_sources_source_global_electrons"
        is_root_ids = False

    particles: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    power: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class CoreSourcesSourceGlobal(IdsBaseClass):
    """

    :ivar power : Total power coupled to the plasma
    :ivar total_ion_particles : Total ion particle source (summed over ion  species)
    :ivar total_ion_power : Total power coupled to ion species (summed over ion  species)
    :ivar electrons : Sources for electrons
    :ivar torque_phi : Toroidal torque
    :ivar current_parallel : Parallel current driven
    :ivar time : Time
    """

    class Meta:
        name = "core_sources_source_global"
        is_root_ids = False

    power: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    total_ion_particles: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    total_ion_power: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    electrons: Optional[CoreSourcesSourceGlobalElectrons] = field(
        default=None,
        metadata={
            "imas_type": "core_sources_source_global_electrons",
            "field_type": CoreSourcesSourceGlobalElectrons,
        },
    )
    torque_phi: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    current_parallel: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class CoreSourcesSource(IdsBaseClass):
    """

    :ivar species : Species causing this source term (if relevant, e.g. a particular ion or neutral state in case of line radiation)
    :ivar global_quantities : Total source quantities integrated over the plasma volume or surface
    :ivar profiles_1d : Source profiles for various time slices. Source terms are positive (resp. negative) when there is a gain (resp. a loss) to the considered channel.
    :ivar code : Code-specific parameters used for this source
    """

    class Meta:
        name = "core_sources_source"
        is_root_ids = False

    species: Optional[DistributionSpecies] = field(
        default=None,
        metadata={
            "imas_type": "distribution_species",
            "field_type": DistributionSpecies,
        },
    )
    global_quantities: Optional[CoreSourcesSourceGlobal] = field(
        default_factory=lambda: StructArray(type_input=CoreSourcesSourceGlobal),
        metadata={
            "imas_type": "core_sources_source_global",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": CoreSourcesSourceGlobal,
        },
    )
    profiles_1d: Optional[CoreSourcesSourceProfiles1D] = field(
        default_factory=lambda: StructArray(
            type_input=CoreSourcesSourceProfiles1D
        ),
        metadata={
            "imas_type": "core_sources_source_profiles_1d",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": CoreSourcesSourceProfiles1D,
        },
    )
    code: Optional[CodeWithTimebase] = field(
        default=None,
        metadata={
            "imas_type": "code_with_timebase",
            "field_type": CodeWithTimebase,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class CoreSources(IdsBaseClass):
    """

    :ivar ids_properties :
    :ivar vacuum_toroidal_field : Characteristics of the vacuum toroidal field (used in Rho_Tor definition and in the normalization of current densities)
    :ivar source : Set of source terms
    :ivar code :
    :ivar time : Generic time
    """

    class Meta:
        name = "core_sources"
        is_root_ids = True

    ids_properties: Optional[IdsProperties] = field(
        default=None,
        metadata={"imas_type": "ids_properties", "field_type": IdsProperties},
    )
    vacuum_toroidal_field: Optional[BTorVacuum1] = field(
        default=None,
        metadata={"imas_type": "b_tor_vacuum_1", "field_type": BTorVacuum1},
    )
    source: Optional[CoreSourcesSource] = field(
        default_factory=lambda: StructArray(type_input=CoreSourcesSource),
        metadata={
            "imas_type": "core_sources_source",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": CoreSourcesSource,
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
