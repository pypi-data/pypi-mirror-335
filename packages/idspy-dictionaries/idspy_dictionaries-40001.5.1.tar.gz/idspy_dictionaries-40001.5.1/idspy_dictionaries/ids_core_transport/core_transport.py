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
class CoreTransportModel1Density(IdsBaseClass):
    """

    :ivar d : Effective diffusivity
    :ivar v : Effective convection
    :ivar flux : Flux
    """

    class Meta:
        name = "core_transport_model_1_density"
        is_root_ids = False

    d: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid_d/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    v: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid_v/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    flux: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid_flux/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class CoreTransportModel1Energy(IdsBaseClass):
    """

    :ivar d : Effective diffusivity
    :ivar v : Effective convection
    :ivar flux : Flux
    """

    class Meta:
        name = "core_transport_model_1_energy"
        is_root_ids = False

    d: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid_d/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    v: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid_v/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    flux: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid_flux/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class CoreTransportModel1Momentum(IdsBaseClass):
    """

    :ivar d : Effective diffusivity
    :ivar v : Effective convection
    :ivar flux : Flux
    """

    class Meta:
        name = "core_transport_model_1_momentum"
        is_root_ids = False

    d: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid_d/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    v: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid_v/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    flux: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid_flux/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class CoreTransportModel2Density(IdsBaseClass):
    """

    :ivar d : Effective diffusivity
    :ivar v : Effective convection
    :ivar flux : Flux
    """

    class Meta:
        name = "core_transport_model_2_density"
        is_root_ids = False

    d: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid_d/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    v: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid_v/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    flux: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid_flux/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class CoreTransportModel2Energy(IdsBaseClass):
    """

    :ivar d : Effective diffusivity
    :ivar v : Effective convection
    :ivar flux : Flux
    """

    class Meta:
        name = "core_transport_model_2_energy"
        is_root_ids = False

    d: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid_d/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    v: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid_v/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    flux: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid_flux/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class CoreTransportModel3Density(IdsBaseClass):
    """

    :ivar d : Effective diffusivity
    :ivar v : Effective convection
    :ivar flux : Flux
    """

    class Meta:
        name = "core_transport_model_3_density"
        is_root_ids = False

    d: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../grid_d/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    v: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../grid_v/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    flux: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {
                "coordinate1": "../../../../grid_flux/rho_tor_norm"
            },
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class CoreTransportModel3Energy(IdsBaseClass):
    """

    :ivar d : Effective diffusivity
    :ivar v : Effective convection
    :ivar flux : Flux
    """

    class Meta:
        name = "core_transport_model_3_energy"
        is_root_ids = False

    d: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../grid_d/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    v: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../grid_v/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    flux: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {
                "coordinate1": "../../../../grid_flux/rho_tor_norm"
            },
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class CoreTransportModel3Momentum(IdsBaseClass):
    """

    :ivar d : Effective diffusivity
    :ivar v : Effective convection
    :ivar flux : Flux
    :ivar flow_damping_rate : Damping rate for this flow component (e.g. due to collisions, calculated from a neoclassical model)
    """

    class Meta:
        name = "core_transport_model_3_momentum"
        is_root_ids = False

    d: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../grid_d/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    v: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../grid_v/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    flux: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {
                "coordinate1": "../../../../grid_flux/rho_tor_norm"
            },
            "field_type": np.ndarray,
        },
    )
    flow_damping_rate: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {
                "coordinate1": "../../../../grid_flux/rho_tor_norm"
            },
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class CoreTransportModelComponents3Momentum(IdsBaseClass):
    """

    :ivar radial : Radial component
    :ivar diamagnetic : Diamagnetic component
    :ivar parallel : Parallel component
    :ivar poloidal : Poloidal component
    :ivar toroidal : Toroidal component
    """

    class Meta:
        name = "core_transport_model_components_3_momentum"
        is_root_ids = False

    radial: Optional[CoreTransportModel3Momentum] = field(
        default=None,
        metadata={
            "imas_type": "core_transport_model_3_momentum",
            "field_type": CoreTransportModel3Momentum,
        },
    )
    diamagnetic: Optional[CoreTransportModel3Momentum] = field(
        default=None,
        metadata={
            "imas_type": "core_transport_model_3_momentum",
            "field_type": CoreTransportModel3Momentum,
        },
    )
    parallel: Optional[CoreTransportModel3Momentum] = field(
        default=None,
        metadata={
            "imas_type": "core_transport_model_3_momentum",
            "field_type": CoreTransportModel3Momentum,
        },
    )
    poloidal: Optional[CoreTransportModel3Momentum] = field(
        default=None,
        metadata={
            "imas_type": "core_transport_model_3_momentum",
            "field_type": CoreTransportModel3Momentum,
        },
    )
    toroidal: Optional[CoreTransportModel3Momentum] = field(
        default=None,
        metadata={
            "imas_type": "core_transport_model_3_momentum",
            "field_type": CoreTransportModel3Momentum,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class CoreTransportModel4Momentum(IdsBaseClass):
    """

    :ivar d : Effective diffusivity
    :ivar v : Effective convection
    :ivar flux : Flux
    :ivar flow_damping_rate : Damping rate for this flow component (e.g. due to collisions, calculated from a neoclassical model)
    """

    class Meta:
        name = "core_transport_model_4_momentum"
        is_root_ids = False

    d: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {
                "coordinate1": "../../../../../grid_d/rho_tor_norm"
            },
            "field_type": np.ndarray,
        },
    )
    v: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {
                "coordinate1": "../../../../../grid_v/rho_tor_norm"
            },
            "field_type": np.ndarray,
        },
    )
    flux: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {
                "coordinate1": "../../../../../grid_flux/rho_tor_norm"
            },
            "field_type": np.ndarray,
        },
    )
    flow_damping_rate: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {
                "coordinate1": "../../../../../grid_flux/rho_tor_norm"
            },
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class CoreTransportModelComponents4Momentum(IdsBaseClass):
    """

    :ivar radial : Radial component
    :ivar diamagnetic : Diamagnetic component
    :ivar parallel : Parallel component
    :ivar poloidal : Poloidal component
    :ivar toroidal : Toroidal component
    """

    class Meta:
        name = "core_transport_model_components_4_momentum"
        is_root_ids = False

    radial: Optional[CoreTransportModel4Momentum] = field(
        default=None,
        metadata={
            "imas_type": "core_transport_model_4_momentum",
            "field_type": CoreTransportModel4Momentum,
        },
    )
    diamagnetic: Optional[CoreTransportModel4Momentum] = field(
        default=None,
        metadata={
            "imas_type": "core_transport_model_4_momentum",
            "field_type": CoreTransportModel4Momentum,
        },
    )
    parallel: Optional[CoreTransportModel4Momentum] = field(
        default=None,
        metadata={
            "imas_type": "core_transport_model_4_momentum",
            "field_type": CoreTransportModel4Momentum,
        },
    )
    poloidal: Optional[CoreTransportModel4Momentum] = field(
        default=None,
        metadata={
            "imas_type": "core_transport_model_4_momentum",
            "field_type": CoreTransportModel4Momentum,
        },
    )
    toroidal: Optional[CoreTransportModel4Momentum] = field(
        default=None,
        metadata={
            "imas_type": "core_transport_model_4_momentum",
            "field_type": CoreTransportModel4Momentum,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class CoreTransportModelIonsChargeStates(IdsBaseClass):
    """

    :ivar z_min : Minimum Z of the charge state bundle
    :ivar z_max : Maximum Z of the charge state bundle
    :ivar name : String identifying charge state (e.g. C+, C+2 , C+3, C+4, C+5, C+6, ...)
    :ivar vibrational_level : Vibrational level (can be bundled)
    :ivar vibrational_mode : Vibrational mode of this state, e.g. &#34;A_g&#34;. Need to define, or adopt a standard nomenclature.
    :ivar electron_configuration : Configuration of atomic orbitals of this state, e.g. 1s2-2s1
    :ivar particles : Transport quantities related to density equation of the charge state considered (thermal+non-thermal)
    :ivar energy : Transport quantities related to the energy equation of the charge state considered
    :ivar momentum : Transport coefficients related to the state momentum equations for various components (directions)
    """

    class Meta:
        name = "core_transport_model_ions_charge_states"
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
    particles: Optional[CoreTransportModel3Density] = field(
        default=None,
        metadata={
            "imas_type": "core_transport_model_3_density",
            "field_type": CoreTransportModel3Density,
        },
    )
    energy: Optional[CoreTransportModel3Energy] = field(
        default=None,
        metadata={
            "imas_type": "core_transport_model_3_energy",
            "field_type": CoreTransportModel3Energy,
        },
    )
    momentum: Optional[CoreTransportModelComponents4Momentum] = field(
        default=None,
        metadata={
            "imas_type": "core_transport_model_components_4_momentum",
            "field_type": CoreTransportModelComponents4Momentum,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class CoreTransportModelNeutralState(IdsBaseClass):
    """

    :ivar name : String identifying state
    :ivar vibrational_level : Vibrational level (can be bundled)
    :ivar vibrational_mode : Vibrational mode of this state, e.g. &#34;A_g&#34;. Need to define, or adopt a standard nomenclature.
    :ivar electron_configuration : Configuration of atomic orbitals of this state, e.g. 1s2-2s1
    :ivar particles : Transport quantities related to density equation of the charge state considered (thermal+non-thermal)
    :ivar energy : Transport quantities related to the energy equation of the charge state considered
    """

    class Meta:
        name = "core_transport_model_neutral_state"
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
    electron_configuration: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    particles: Optional[CoreTransportModel3Density] = field(
        default=None,
        metadata={
            "imas_type": "core_transport_model_3_density",
            "field_type": CoreTransportModel3Density,
        },
    )
    energy: Optional[CoreTransportModel3Energy] = field(
        default=None,
        metadata={
            "imas_type": "core_transport_model_3_energy",
            "field_type": CoreTransportModel3Energy,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class CoreTransportModelIons(IdsBaseClass):
    """

    :ivar element : List of elements forming the atom or molecule
    :ivar z_ion : Ion charge (of the dominant ionization state; lumped ions are allowed)
    :ivar name : String identifying ion (e.g. H, D, T, He, C, D2, ...)
    :ivar neutral_index : Index of the corresponding neutral species in the ../../neutral array
    :ivar particles : Transport related to the ion density equation
    :ivar energy : Transport coefficients related to the ion energy equation
    :ivar momentum : Transport coefficients related to the ion momentum equations for various components (directions)
    :ivar multiple_states_flag : Multiple states calculation flag : 0-Only the &#39;ion&#39; level is considered and the &#39;state&#39; array of structure is empty; 1-Ion states are considered and are described in the &#39;state&#39; array of structure
    :ivar state : Transport coefficients related to the different states of the species
    """

    class Meta:
        name = "core_transport_model_ions"
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
    particles: Optional[CoreTransportModel2Density] = field(
        default=None,
        metadata={
            "imas_type": "core_transport_model_2_density",
            "field_type": CoreTransportModel2Density,
        },
    )
    energy: Optional[CoreTransportModel2Energy] = field(
        default=None,
        metadata={
            "imas_type": "core_transport_model_2_energy",
            "field_type": CoreTransportModel2Energy,
        },
    )
    momentum: Optional[CoreTransportModelComponents3Momentum] = field(
        default=None,
        metadata={
            "imas_type": "core_transport_model_components_3_momentum",
            "field_type": CoreTransportModelComponents3Momentum,
        },
    )
    multiple_states_flag: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    state: Optional[CoreTransportModelIonsChargeStates] = field(
        default_factory=lambda: StructArray(
            type_input=CoreTransportModelIonsChargeStates
        ),
        metadata={
            "imas_type": "core_transport_model_ions_charge_states",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": CoreTransportModelIonsChargeStates,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class CoreTransportModelNeutral(IdsBaseClass):
    """

    :ivar element : List of elements forming the atom or molecule
    :ivar name : String identifying ion (e.g. H+, D+, T+, He+2, C+, ...)
    :ivar ion_index : Index of the corresponding ion species in the ../../ion array
    :ivar particles : Transport related to the neutral density equation
    :ivar energy : Transport coefficients related to the neutral energy equation
    :ivar multiple_states_flag : Multiple states calculation flag : 0-Only one state is considered; 1-Multiple states are considered and are described in the state structure
    :ivar state : Transport coefficients related to the different states of the species
    """

    class Meta:
        name = "core_transport_model_neutral"
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
    particles: Optional[CoreTransportModel2Density] = field(
        default=None,
        metadata={
            "imas_type": "core_transport_model_2_density",
            "field_type": CoreTransportModel2Density,
        },
    )
    energy: Optional[CoreTransportModel2Energy] = field(
        default=None,
        metadata={
            "imas_type": "core_transport_model_2_energy",
            "field_type": CoreTransportModel2Energy,
        },
    )
    multiple_states_flag: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    state: Optional[CoreTransportModelNeutralState] = field(
        default_factory=lambda: StructArray(
            type_input=CoreTransportModelNeutralState
        ),
        metadata={
            "imas_type": "core_transport_model_neutral_state",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": CoreTransportModelNeutralState,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class CoreTransportModelElectrons(IdsBaseClass):
    """

    :ivar particles : Transport quantities for the electron density equation
    :ivar energy : Transport quantities for the electron energy equation
    """

    class Meta:
        name = "core_transport_model_electrons"
        is_root_ids = False

    particles: Optional[CoreTransportModel2Density] = field(
        default=None,
        metadata={
            "imas_type": "core_transport_model_2_density",
            "field_type": CoreTransportModel2Density,
        },
    )
    energy: Optional[CoreTransportModel2Energy] = field(
        default=None,
        metadata={
            "imas_type": "core_transport_model_2_energy",
            "field_type": CoreTransportModel2Energy,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class CoreTransportModelProfiles1D(IdsBaseClass):
    """

    :ivar grid_d : Grid for effective diffusivities and parallel conductivity
    :ivar grid_v : Grid for effective convections
    :ivar grid_flux : Grid for fluxes
    :ivar conductivity_parallel : Parallel conductivity
    :ivar electrons : Transport quantities related to the electrons
    :ivar total_ion_energy : Transport coefficients for the total (summed over ion  species) energy equation
    :ivar momentum_phi : Transport coefficients for total toroidal momentum equation
    :ivar e_field_radial : Radial component of the electric field (calculated e.g. by a neoclassical model)
    :ivar ion : Transport coefficients related to the various ion species, in the sense of isonuclear or isomolecular sequences. Ionization states (and other types of states) must be differentiated at the state level below
    :ivar neutral : Transport coefficients related to the various neutral species
    :ivar time : Time
    """

    class Meta:
        name = "core_transport_model_profiles_1d"
        is_root_ids = False

    grid_d: Optional[CoreRadialGrid] = field(
        default=None,
        metadata={
            "imas_type": "core_radial_grid",
            "field_type": CoreRadialGrid,
        },
    )
    grid_v: Optional[CoreRadialGrid] = field(
        default=None,
        metadata={
            "imas_type": "core_radial_grid",
            "field_type": CoreRadialGrid,
        },
    )
    grid_flux: Optional[CoreRadialGrid] = field(
        default=None,
        metadata={
            "imas_type": "core_radial_grid",
            "field_type": CoreRadialGrid,
        },
    )
    conductivity_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid_d/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    electrons: Optional[CoreTransportModelElectrons] = field(
        default=None,
        metadata={
            "imas_type": "core_transport_model_electrons",
            "field_type": CoreTransportModelElectrons,
        },
    )
    total_ion_energy: Optional[CoreTransportModel1Energy] = field(
        default=None,
        metadata={
            "imas_type": "core_transport_model_1_energy",
            "field_type": CoreTransportModel1Energy,
        },
    )
    momentum_phi: Optional[CoreTransportModel1Momentum] = field(
        default=None,
        metadata={
            "imas_type": "core_transport_model_1_momentum",
            "field_type": CoreTransportModel1Momentum,
        },
    )
    e_field_radial: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid_flux/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    ion: Optional[CoreTransportModelIons] = field(
        default_factory=lambda: StructArray(type_input=CoreTransportModelIons),
        metadata={
            "imas_type": "core_transport_model_ions",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": CoreTransportModelIons,
        },
    )
    neutral: Optional[CoreTransportModelNeutral] = field(
        default_factory=lambda: StructArray(
            type_input=CoreTransportModelNeutral
        ),
        metadata={
            "imas_type": "core_transport_model_neutral",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": CoreTransportModelNeutral,
        },
    )
    time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class CoreTransportModel(IdsBaseClass):
    """

    :ivar comment : Any comment describing the model
    :ivar flux_multiplier : Multiplier applied to the particule flux when adding its contribution in the expression of the heat flux : can be 0, 3/2 or 5/2
    :ivar profiles_1d : Transport coefficient profiles for various time slices. Fluxes and convection are positive (resp. negative) when outwards i.e. towards the LCFS (resp. inwards i.e.  towards the magnetic axes).
    :ivar code : Code-specific parameters used for this model
    """

    class Meta:
        name = "core_transport_model"
        is_root_ids = False

    comment: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    flux_multiplier: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    profiles_1d: Optional[CoreTransportModelProfiles1D] = field(
        default_factory=lambda: StructArray(
            type_input=CoreTransportModelProfiles1D
        ),
        metadata={
            "imas_type": "core_transport_model_profiles_1d",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": CoreTransportModelProfiles1D,
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
class CoreTransport(IdsBaseClass):
    """

    :ivar ids_properties :
    :ivar vacuum_toroidal_field : Characteristics of the vacuum toroidal field (used in Rho_Tor definition and in the normalization of current densities)
    :ivar model : Transport is described by a combination of various transport models
    :ivar code :
    :ivar time : Generic time
    """

    class Meta:
        name = "core_transport"
        is_root_ids = True

    ids_properties: Optional[IdsProperties] = field(
        default=None,
        metadata={"imas_type": "ids_properties", "field_type": IdsProperties},
    )
    vacuum_toroidal_field: Optional[BTorVacuum1] = field(
        default=None,
        metadata={"imas_type": "b_tor_vacuum_1", "field_type": BTorVacuum1},
    )
    model: Optional[CoreTransportModel] = field(
        default_factory=lambda: StructArray(type_input=CoreTransportModel),
        metadata={
            "imas_type": "core_transport_model",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": CoreTransportModel,
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
