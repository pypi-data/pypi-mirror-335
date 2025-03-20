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
class CodePartialConstant(IdsBaseClass):
    """

    :ivar parameters : List of the code specific parameters in XML format
    :ivar output_flag : Output flag : 0 means the run is successful, other values mean some difficulty has been encountered, the exact meaning is then code specific. Negative values mean the result shall not be used.
    """

    class Meta:
        name = "code_partial_constant"
        is_root_ids = False

    parameters: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    output_flag: Optional[int] = field(
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
class Species(IdsBaseClass):
    """

    :ivar charge_norm : normalized charge
    :ivar mass_norm : normalized mass
    :ivar density_norm : normalized density
    :ivar density_log_gradient_norm : normalized logarithmic gradient (with respect to r_minor_norm) of the density
    :ivar temperature_norm : normalized temperature
    :ivar temperature_log_gradient_norm : normalized logarithmic gradient (with respect to r_minor_norm) of the temperature
    :ivar velocity_phi_gradient_norm : Normalized gradient (with respect to r_minor_norm) of the toroidal velocity
    :ivar potential_energy_norm : normalized gradient (with respect to r_minor_norm) of the effective potential energy
    :ivar potential_energy_gradient_norm : Effective potential energy determining the poloidal variation of the species background density
    """

    class Meta:
        name = "species"
        is_root_ids = False

    charge_norm: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    mass_norm: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    density_norm: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    density_log_gradient_norm: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    temperature_norm: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    temperature_log_gradient_norm: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    velocity_phi_gradient_norm: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    potential_energy_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {
                "coordinate1": "../../species_all/angle_pol_equilibrium"
            },
            "field_type": np.ndarray,
        },
    )
    potential_energy_gradient_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {
                "coordinate1": "../../species_all/angle_pol_equilibrium"
            },
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class FluxSurface(IdsBaseClass):
    """

    :ivar r_minor_norm : normalized minor radius of the flux surface of interest = 1/2 * (max(R) - min(R))/L_ref
    :ivar elongation : Elongation
    :ivar delongation_dr_minor_norm : Derivative of the elongation with respect to r_minor_norm
    :ivar dgeometric_axis_r_dr_minor : Derivative of the major radius of the surface geometric axis with respect to r_minor
    :ivar dgeometric_axis_z_dr_minor : Derivative of the height of the surface geometric axis with respect to r_minor
    :ivar q : Safety factor
    :ivar magnetic_shear_r_minor : Magnetic shear, defined as r_minor_norm/q . dq/dr_minor_norm (different definition from the equilibrium IDS)
    :ivar pressure_gradient_norm : normalized pressure gradient (derivative with respect to r_minor_norm)
    :ivar ip_sign : Sign of the plasma current
    :ivar b_field_phi_sign : Sign of the toroidal magnetic field
    :ivar shape_coefficients_c : &#39;c&#39; coefficients in the formula defining the shape of the flux surface
    :ivar dc_dr_minor_norm : Derivative of the &#39;c&#39; shape coefficients with respect to r_minor_norm
    :ivar shape_coefficients_s : &#39;s&#39; coefficients in the formula defining the shape of the flux surface
    :ivar ds_dr_minor_norm : Derivative of the &#39;s&#39; shape coefficients with respect to r_minor_norm
    """

    class Meta:
        name = "flux_surface"
        is_root_ids = False

    r_minor_norm: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    elongation: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    delongation_dr_minor_norm: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    dgeometric_axis_r_dr_minor: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    dgeometric_axis_z_dr_minor: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    q: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    magnetic_shear_r_minor: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    pressure_gradient_norm: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    ip_sign: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    b_field_phi_sign: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    shape_coefficients_c: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    dc_dr_minor_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../shape_coefficients_c"},
            "field_type": np.ndarray,
        },
    )
    shape_coefficients_s: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    ds_dr_minor_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../shape_coefficients_s"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class InputSpeciesGlobal(IdsBaseClass):
    """

    :ivar beta_reference : Reference plasma beta (see detailed documentation at the root of the IDS)
    :ivar velocity_phi_norm : normalized toroidal velocity of species (all species are assumed to have a purely toroidal velocity with a common toroidal angular frequency)
    :ivar debye_length_norm : Debye length computed from the reference quantities (see detailed documentation at the root of the IDS)
    :ivar shearing_rate_norm : normalized ExB shearing rate (for non-linear runs only)
    :ivar angle_pol_equilibrium : Poloidal angle grid, from -pi to pi, on which the species dependent effective potential energy (which determines the poloidal variation of the density) is expressed. The angle is defined with respect to (R0,Z0) with R0=(Rmax-Rmin)/2 and Z0=(Zmax-Zmin)/2. It is increasing clockwise. So (r,theta,phi) is right-handed. theta=0 for Z=Z0 and R&gt;R0 (LFS)
    """

    class Meta:
        name = "input_species_global"
        is_root_ids = False

    beta_reference: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    velocity_phi_norm: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    debye_length_norm: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    shearing_rate_norm: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    angle_pol_equilibrium: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class InputNormalizing(IdsBaseClass):
    """

    :ivar t_e : Electron temperature at outboard equatorial midplane of the flux surface (angle_pol = 0)
    :ivar n_e : Electron density at outboard equatorial midplane of the flux surface (angle_pol = 0)
    :ivar r : Major radius of the flux surface of interest, defined as (min(R)+max(R))/2
    :ivar b_field_phi : Toroidal magnetic field at major radius r
    """

    class Meta:
        name = "input_normalizing"
        is_root_ids = False

    t_e: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    n_e: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    r: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    b_field_phi: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class Model(IdsBaseClass):
    """

    :ivar include_a_field_parallel : Flag = 1 if fluctuations of the parallel vector potential are retained, 0 otherwise
    :ivar include_b_field_parallel : Flag = 1 if fluctuations of the parallel magnetic field are retained, 0 otherwise
    :ivar use_mhd_approximation : Flag = 1 if the geometric dependence of the grad-B drift is approximated to be that of the curvature drift (including the pressure gradient contribution), 0 otherwise. Using this approximation (Flag=1) is only recommended together with the neglect of parallel magnetic field fluctuations
    :ivar include_coriolis_drift : Flag = 1 if Coriolis drift is included, 0 otherwise
    :ivar include_centrifugal_effects : Flag = 1 if centrifugal effects are retained, 0 otherwise
    :ivar collisions_pitch_only : Flag = 1 if only pitch-angle scattering is retained, 0 otherwise
    :ivar collisions_momentum_conservation : Flag = 1 if the collision operator conserves momentum, 0 otherwise
    :ivar collisions_energy_conservation : Flag = 1 if the collision operator conserves energy, 0 otherwise
    :ivar collisions_finite_larmor_radius : Flag = 1 if finite larmor radius effects are retained in the collision operator, 0 otherwise
    :ivar adiabatic_electrons : Flag = 1 if electrons are adiabatic, 0 otherwise
    """

    class Meta:
        name = "model"
        is_root_ids = False

    include_a_field_parallel: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    include_b_field_parallel: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    use_mhd_approximation: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    include_coriolis_drift: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    include_centrifugal_effects: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    collisions_pitch_only: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    collisions_momentum_conservation: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    collisions_energy_conservation: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    collisions_finite_larmor_radius: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    adiabatic_electrons: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )


@idspy_dataclass(repr=False, slots=True)
class MomentsLinear(IdsBaseClass):
    """

    :ivar density : normalized density
    :ivar j_parallel : normalized parallel current density
    :ivar pressure_parallel : Normalized parallel pressure
    :ivar pressure_perpendicular : Normalized perpendicular pressure
    :ivar pressure : Normalised pressure, defined as the sum of pressure_parallel and pressure_perpendicular
    :ivar heat_flux_parallel : Normalized parallel heat flux (integral of 0.5 * m * v_par * v^2)
    :ivar v_parallel_energy_perpendicular : Normalized moment (integral over 0.5 * m * v_par * v_perp^2)
    :ivar v_perpendicular_square_energy : Normalized moment (integral over 0.5 * m * v_perp^2 * v^2)
    """

    class Meta:
        name = "moments_linear"
        is_root_ids = False

    density: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=complex),
        metadata={
            "imas_type": "CPX_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "../../../../../species",
                "coordinate2": "../../angle_pol",
                "coordinate3": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    j_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=complex),
        metadata={
            "imas_type": "CPX_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "../../../../../species",
                "coordinate2": "../../angle_pol",
                "coordinate3": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    pressure_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=complex),
        metadata={
            "imas_type": "CPX_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "../../../../../species",
                "coordinate2": "../../angle_pol",
                "coordinate3": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    pressure_perpendicular: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=complex),
        metadata={
            "imas_type": "CPX_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "../../../../../species",
                "coordinate2": "../../angle_pol",
                "coordinate3": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    pressure: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=complex),
        metadata={
            "imas_type": "CPX_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "../../../../../species",
                "coordinate2": "../../angle_pol",
                "coordinate3": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    heat_flux_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=complex),
        metadata={
            "imas_type": "CPX_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "../../../../../species",
                "coordinate2": "../../angle_pol",
                "coordinate3": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    v_parallel_energy_perpendicular: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=complex),
        metadata={
            "imas_type": "CPX_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "../../../../../species",
                "coordinate2": "../../angle_pol",
                "coordinate3": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    v_perpendicular_square_energy: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=complex),
        metadata={
            "imas_type": "CPX_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "../../../../../species",
                "coordinate2": "../../angle_pol",
                "coordinate3": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class FieldsNl1D(IdsBaseClass):
    """

    :ivar phi_potential_perturbed_norm : Normalized perturbed electrostatic potential
    :ivar a_field_parallel_perturbed_norm : Normalized perturbed parallel vector potential
    :ivar b_field_parallel_perturbed_norm : normalized perturbed parallel magnetic field
    """

    class Meta:
        name = "fields_nl_1d"
        is_root_ids = False

    phi_potential_perturbed_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../binormal_wavevector_norm"},
            "field_type": np.ndarray,
        },
    )
    a_field_parallel_perturbed_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../binormal_wavevector_norm"},
            "field_type": np.ndarray,
        },
    )
    b_field_parallel_perturbed_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../binormal_wavevector_norm"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class FieldsNl2DKy0(IdsBaseClass):
    """

    :ivar phi_potential_perturbed_norm : normalized perturbed electrostatic potential
    :ivar a_field_parallel_perturbed_norm : Normalized perturbed parallel vector potential
    :ivar b_field_parallel_perturbed_norm : Normalized perturbed parallel magnetic field
    """

    class Meta:
        name = "fields_nl_2d_ky0"
        is_root_ids = False

    phi_potential_perturbed_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=complex),
        metadata={
            "imas_type": "CPX_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../radial_wavevector_norm",
                "coordinate2": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    a_field_parallel_perturbed_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=complex),
        metadata={
            "imas_type": "CPX_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../radial_wavevector_norm",
                "coordinate2": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    b_field_parallel_perturbed_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=complex),
        metadata={
            "imas_type": "CPX_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../radial_wavevector_norm",
                "coordinate2": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class FieldsNl2DFsAverage(IdsBaseClass):
    """

    :ivar phi_potential_perturbed_norm : Normalized perturbed electrostatic potential
    :ivar a_field_parallel_perturbed_norm : Normalized perturbed parallel vector potential
    :ivar b_field_parallel_perturbed_norm : Normalized perturbed parallel magnetic field
    """

    class Meta:
        name = "fields_nl_2d_fs_average"
        is_root_ids = False

    phi_potential_perturbed_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../binormal_wavevector_norm",
                "coordinate2": "../../radial_wavevector_norm",
            },
            "field_type": np.ndarray,
        },
    )
    a_field_parallel_perturbed_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../binormal_wavevector_norm",
                "coordinate2": "../../radial_wavevector_norm",
            },
            "field_type": np.ndarray,
        },
    )
    b_field_parallel_perturbed_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../binormal_wavevector_norm",
                "coordinate2": "../../radial_wavevector_norm",
            },
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class FieldsNl3D(IdsBaseClass):
    """

    :ivar phi_potential_perturbed_norm : Normalized perturbed electrostatic potential
    :ivar a_field_parallel_perturbed_norm : Normalized perturbed parallel vector potential
    :ivar b_field_parallel_perturbed_norm : Normalized perturbed parallel magnetic field
    """

    class Meta:
        name = "fields_nl_3d"
        is_root_ids = False

    phi_potential_perturbed_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "../../binormal_wavevector_norm",
                "coordinate2": "../../radial_wavevector_norm",
                "coordinate3": "../../angle_pol",
            },
            "field_type": np.ndarray,
        },
    )
    a_field_parallel_perturbed_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "../../binormal_wavevector_norm",
                "coordinate2": "../../radial_wavevector_norm",
                "coordinate3": "../../angle_pol",
            },
            "field_type": np.ndarray,
        },
    )
    b_field_parallel_perturbed_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "../../binormal_wavevector_norm",
                "coordinate2": "../../radial_wavevector_norm",
                "coordinate3": "../../angle_pol",
            },
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class FieldsNl4D(IdsBaseClass):
    """

    :ivar phi_potential_perturbed_norm : Normalized perturbed electrostatic potential
    :ivar a_field_parallel_perturbed_norm : Normalized perturbed parallel vector potential
    :ivar b_field_parallel_perturbed_norm : Normalized perturbed parallel magnetic field
    """

    class Meta:
        name = "fields_nl_4d"
        is_root_ids = False

    phi_potential_perturbed_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 4, dtype=complex),
        metadata={
            "imas_type": "CPX_4D",
            "ndims": 4,
            "coordinates": {
                "coordinate1": "../../binormal_wavevector_norm",
                "coordinate2": "../../radial_wavevector_norm",
                "coordinate3": "../../angle_pol",
                "coordinate4": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    a_field_parallel_perturbed_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 4, dtype=complex),
        metadata={
            "imas_type": "CPX_4D",
            "ndims": 4,
            "coordinates": {
                "coordinate1": "../../binormal_wavevector_norm",
                "coordinate2": "../../radial_wavevector_norm",
                "coordinate3": "../../angle_pol",
                "coordinate4": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    b_field_parallel_perturbed_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 4, dtype=complex),
        metadata={
            "imas_type": "CPX_4D",
            "ndims": 4,
            "coordinates": {
                "coordinate1": "../../binormal_wavevector_norm",
                "coordinate2": "../../radial_wavevector_norm",
                "coordinate3": "../../angle_pol",
                "coordinate4": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class FluxesNl1D(IdsBaseClass):
    """

    :ivar particles_phi_potential : Contribution of the perturbed electrostatic potential to the normalized particle flux
    :ivar particles_a_field_parallel : Contribution of the perturbed parallel electromagnetic potential to the normalized particle flux
    :ivar particles_b_field_parallel : Contribution of the perturbed parallel magnetic field to the normalized particle flux
    :ivar energy_phi_potential : Contribution of the perturbed electrostatic potential to the normalized energy flux
    :ivar energy_a_field_parallel : Contribution of the perturbed parallel electromagnetic potential to the normalized energy flux
    :ivar energy_b_field_parallel : Contribution of the perturbed parallel magnetic field to the normalized energy flux
    :ivar momentum_phi_parallel_phi_potential : Contribution of the perturbed electrostatic potential to the parallel component of the normalized toroidal momentum flux
    :ivar momentum_phi_parallel_a_field_parallel : Contribution of the perturbed parallel electromagnetic potential to the parallel component of the normalized toroidal momentum flux
    :ivar momentum_phi_parallel_b_field_parallel : Contribution of the perturbed parallel magnetic field to the parallel component of the normalized toroidal momentum flux
    :ivar momentum_phi_perpendicular_phi_potential : Contribution of the perturbed electrostatic potential to the perpendicular component of the normalized toroidal momentum flux
    :ivar momentum_phi_perpendicular_a_field_parallel : Contribution of the perturbed parallel electromagnetic potential to the perpendicular component of the normalized toroidal momentum flux
    :ivar momentum_phi_perpendicular_b_field_parallel : Contribution of the perturbed parallel magnetic field to the perpendicular component of the normalized toroidal momentum flux
    """

    class Meta:
        name = "fluxes_nl_1d"
        is_root_ids = False

    particles_phi_potential: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "/species"},
            "field_type": np.ndarray,
        },
    )
    particles_a_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "/species"},
            "field_type": np.ndarray,
        },
    )
    particles_b_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "/species"},
            "field_type": np.ndarray,
        },
    )
    energy_phi_potential: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "/species"},
            "field_type": np.ndarray,
        },
    )
    energy_a_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "/species"},
            "field_type": np.ndarray,
        },
    )
    energy_b_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "/species"},
            "field_type": np.ndarray,
        },
    )
    momentum_phi_parallel_phi_potential: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "/species"},
            "field_type": np.ndarray,
        },
    )
    momentum_phi_parallel_a_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "/species"},
            "field_type": np.ndarray,
        },
    )
    momentum_phi_parallel_b_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "/species"},
            "field_type": np.ndarray,
        },
    )
    momentum_phi_perpendicular_phi_potential: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "/species"},
            "field_type": np.ndarray,
        },
    )
    momentum_phi_perpendicular_a_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "/species"},
            "field_type": np.ndarray,
        },
    )
    momentum_phi_perpendicular_b_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "/species"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class FluxesNl2DSumKxKy(IdsBaseClass):
    """

    :ivar particles_phi_potential : Contribution of the perturbed electrostatic potential to the normalized particle flux
    :ivar particles_a_field_parallel : Contribution of the perturbed parallel electromagnetic potential to the normalized particle flux
    :ivar particles_b_field_parallel : Contribution of the perturbed parallel magnetic field to the normalized particle flux
    :ivar energy_phi_potential : Contribution of the perturbed electrostatic potential to the normalized energy flux
    :ivar energy_a_field_parallel : Contribution of the perturbed parallel electromagnetic potential to the normalized energy flux
    :ivar energy_b_field_parallel : Contribution of the perturbed parallel magnetic field to the normalized energy flux
    :ivar momentum_phi_parallel_phi_potential : Contribution of the perturbed electrostatic potential to the parallel component of the normalized toroidal momentum flux
    :ivar momentum_phi_parallel_a_field_parallel : Contribution of the perturbed parallel electromagnetic potential to the parallel component of the normalized toroidal momentum flux
    :ivar momentum_phi_parallel_b_field_parallel : Contribution of the perturbed parallel magnetic field to the parallel component of the normalized toroidal momentum flux
    :ivar momentum_phi_perpendicular_phi_potential : Contribution of the perturbed electrostatic potential to the perpendicular component of the normalized toroidal momentum flux
    :ivar momentum_phi_perpendicular_a_field_parallel : Contribution of the perturbed parallel electromagnetic potential to the perpendicular component of the normalized toroidal momentum flux
    :ivar momentum_phi_perpendicular_b_field_parallel : Contribution of the perturbed parallel magnetic field to the perpendicular component of the normalized toroidal momentum flux
    """

    class Meta:
        name = "fluxes_nl_2d_sum_kx_ky"
        is_root_ids = False

    particles_phi_potential: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    particles_a_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    particles_b_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    energy_phi_potential: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    energy_a_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    energy_b_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    momentum_phi_parallel_phi_potential: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    momentum_phi_parallel_a_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    momentum_phi_parallel_b_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    momentum_phi_perpendicular_phi_potential: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    momentum_phi_perpendicular_a_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    momentum_phi_perpendicular_b_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class FluxesNl2DSumKx(IdsBaseClass):
    """

    :ivar particles_phi_potential : Contribution of the perturbed electrostatic potential to the normalized particle flux
    :ivar particles_a_field_parallel : Contribution of the perturbed parallel electromagnetic potential to the normalized particle flux
    :ivar particles_b_field_parallel : Contribution of the perturbed parallel magnetic field to the normalized particle flux
    :ivar energy_phi_potential : Contribution of the perturbed electrostatic potential to the normalized energy flux
    :ivar energy_a_field_parallel : Contribution of the perturbed parallel electromagnetic potential to the normalized energy flux
    :ivar energy_b_field_parallel : Contribution of the perturbed parallel magnetic field to the normalized energy flux
    :ivar momentum_phi_parallel_phi_potential : Contribution of the perturbed electrostatic potential to the parallel component of the normalized toroidal momentum flux
    :ivar momentum_phi_parallel_a_field_parallel : Contribution of the perturbed parallel electromagnetic potential to the parallel component of the normalized toroidal momentum flux
    :ivar momentum_phi_parallel_b_field_parallel : Contribution of the perturbed parallel magnetic field to the parallel component of the normalized toroidal momentum flux
    :ivar momentum_phi_perpendicular_phi_potential : Contribution of the perturbed electrostatic potential to the perpendicular component of the normalized toroidal momentum flux
    :ivar momentum_phi_perpendicular_a_field_parallel : Contribution of the perturbed parallel electromagnetic potential to the perpendicular component of the normalized toroidal momentum flux
    :ivar momentum_phi_perpendicular_b_field_parallel : Contribution of the perturbed parallel magnetic field to the perpendicular component of the normalized toroidal momentum flux
    """

    class Meta:
        name = "fluxes_nl_2d_sum_kx"
        is_root_ids = False

    particles_phi_potential: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
            },
            "field_type": np.ndarray,
        },
    )
    particles_a_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
            },
            "field_type": np.ndarray,
        },
    )
    particles_b_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
            },
            "field_type": np.ndarray,
        },
    )
    energy_phi_potential: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
            },
            "field_type": np.ndarray,
        },
    )
    energy_a_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
            },
            "field_type": np.ndarray,
        },
    )
    energy_b_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
            },
            "field_type": np.ndarray,
        },
    )
    momentum_phi_parallel_phi_potential: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
            },
            "field_type": np.ndarray,
        },
    )
    momentum_phi_parallel_a_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
            },
            "field_type": np.ndarray,
        },
    )
    momentum_phi_parallel_b_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
            },
            "field_type": np.ndarray,
        },
    )
    momentum_phi_perpendicular_phi_potential: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
            },
            "field_type": np.ndarray,
        },
    )
    momentum_phi_perpendicular_a_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
            },
            "field_type": np.ndarray,
        },
    )
    momentum_phi_perpendicular_b_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
            },
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class FluxesNl3DSumKx(IdsBaseClass):
    """

    :ivar particles_phi_potential : Contribution of the perturbed electrostatic potential to the normalised particle flux
    :ivar particles_a_field_parallel : Contribution of the perturbed parallel electromagnetic potential to the normalised particle flux
    :ivar particles_b_field_parallel : Contribution of the perturbed parallel magnetic field to the normalised particle flux
    :ivar energy_phi_potential : Contribution of the perturbed electrostatic potential to the normalised energy flux
    :ivar energy_a_field_parallel : Contribution of the perturbed parallel electromagnetic potential to the normalised energy flux
    :ivar energy_b_field_parallel : Contribution of the perturbed parallel magnetic field to the normalised energy flux
    :ivar momentum_phi_parallel_phi_potential : Contribution of the perturbed electrostatic potential to the parallel component of the normalised toroidal momentum flux
    :ivar momentum_phi_parallel_a_field_parallel : Contribution of the perturbed parallel electromagnetic potential to the parallel component of the normalised toroidal momentum flux
    :ivar momentum_phi_parallel_b_field_parallel : Contribution of the perturbed parallel magnetic field to the parallel component of the normalised toroidal momentum flux
    :ivar momentum_phi_perpendicular_phi_potential : Contribution of the perturbed electrostatic potential to the perpendicular component of the normalised toroidal momentum flux
    :ivar momentum_phi_perpendicular_a_field_parallel : Contribution of the perturbed parallel electromagnetic potential to the perpendicular component of the normalised toroidal momentum flux
    :ivar momentum_phi_perpendicular_b_field_parallel : Contribution of the perturbed parallel magnetic field to the perpendicular component of the normalised toroidal momentum flux
    """

    class Meta:
        name = "fluxes_nl_3d_sum_kx"
        is_root_ids = False

    particles_phi_potential: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    particles_a_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    particles_b_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    energy_phi_potential: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    energy_a_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    energy_b_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    momentum_phi_parallel_phi_potential: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    momentum_phi_parallel_a_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    momentum_phi_parallel_b_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    momentum_phi_perpendicular_phi_potential: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    momentum_phi_perpendicular_a_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    momentum_phi_perpendicular_b_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class FluxesNl3D(IdsBaseClass):
    """

    :ivar particles_phi_potential : Contribution of the perturbed electrostatic potential to the normalized particle flux
    :ivar particles_a_field_parallel : Contribution of the perturbed parallel electromagnetic potential to the normalized particle flux
    :ivar particles_b_field_parallel : Contribution of the perturbed parallel magnetic field to the normalized particle flux
    :ivar energy_phi_potential : Contribution of the perturbed electrostatic potential to the normalized energy flux
    :ivar energy_a_field_parallel : Contribution of the perturbed parallel electromagnetic potential to the normalized energy flux
    :ivar energy_b_field_parallel : Contribution of the perturbed parallel magnetic field to the normalized energy flux
    :ivar momentum_phi_parallel_phi_potential : Contribution of the perturbed electrostatic potential to the parallel component of the normalized toroidal momentum flux
    :ivar momentum_phi_parallel_a_field_parallel : Contribution of the perturbed parallel electromagnetic potential to the parallel component of the normalized toroidal momentum flux
    :ivar momentum_phi_parallel_b_field_parallel : Contribution of the perturbed parallel magnetic field to the parallel component of the normalized toroidal momentum flux
    :ivar momentum_phi_perpendicular_phi_potential : Contribution of the perturbed electrostatic potential to the perpendicular component of the normalized toroidal momentum flux
    :ivar momentum_phi_perpendicular_a_field_parallel : Contribution of the perturbed parallel electromagnetic potential to the perpendicular component of the normalized toroidal momentum flux
    :ivar momentum_phi_perpendicular_b_field_parallel : Contribution of the perturbed parallel magnetic field to the perpendicular component of the normalized toroidal momentum flux
    """

    class Meta:
        name = "fluxes_nl_3d"
        is_root_ids = False

    particles_phi_potential: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../radial_wavevector_norm",
            },
            "field_type": np.ndarray,
        },
    )
    particles_a_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../radial_wavevector_norm",
            },
            "field_type": np.ndarray,
        },
    )
    particles_b_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../radial_wavevector_norm",
            },
            "field_type": np.ndarray,
        },
    )
    energy_phi_potential: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../radial_wavevector_norm",
            },
            "field_type": np.ndarray,
        },
    )
    energy_a_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../radial_wavevector_norm",
            },
            "field_type": np.ndarray,
        },
    )
    energy_b_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../radial_wavevector_norm",
            },
            "field_type": np.ndarray,
        },
    )
    momentum_phi_parallel_phi_potential: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../radial_wavevector_norm",
            },
            "field_type": np.ndarray,
        },
    )
    momentum_phi_parallel_a_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../radial_wavevector_norm",
            },
            "field_type": np.ndarray,
        },
    )
    momentum_phi_parallel_b_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../radial_wavevector_norm",
            },
            "field_type": np.ndarray,
        },
    )
    momentum_phi_perpendicular_phi_potential: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../radial_wavevector_norm",
            },
            "field_type": np.ndarray,
        },
    )
    momentum_phi_perpendicular_a_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../radial_wavevector_norm",
            },
            "field_type": np.ndarray,
        },
    )
    momentum_phi_perpendicular_b_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../radial_wavevector_norm",
            },
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class FluxesNl4D(IdsBaseClass):
    """

    :ivar particles_phi_potential : Contribution of the perturbed electrostatic potential to the normalized particle flux
    :ivar particles_a_field_parallel : Contribution of the perturbed parallel electromagnetic potential to the normalized particle flux
    :ivar particles_b_field_parallel : Contribution of the perturbed parallel magnetic field to the normalized particle flux
    :ivar energy_phi_potential : Contribution of the perturbed electrostatic potential to the normalized energy flux
    :ivar energy_a_field_parallel : Contribution of the perturbed parallel electromagnetic potential to the normalized energy flux
    :ivar energy_b_field_parallel : Contribution of the perturbed parallel magnetic field to the normalized energy flux
    :ivar momentum_phi_parallel_phi_potential : Contribution of the perturbed electrostatic potential to the parallel component of the normalized toroidal momentum flux
    :ivar momentum_phi_parallel_a_field_parallel : Contribution of the perturbed parallel electromagnetic potential to the parallel component of the normalized toroidal momentum flux
    :ivar momentum_phi_parallel_b_field_parallel : Contribution of the perturbed parallel magnetic field to the parallel component of the normalized toroidal momentum flux
    :ivar momentum_phi_perpendicular_phi_potential : Contribution of the perturbed electrostatic potential to the perpendicular component of the normalized toroidal momentum flux
    :ivar momentum_phi_perpendicular_a_field_parallel : Contribution of the perturbed parallel electromagnetic potential to the perpendicular component of the normalized toroidal momentum flux
    :ivar momentum_phi_perpendicular_b_field_parallel : Contribution of the perturbed parallel magnetic field to the perpendicular component of the normalized toroidal momentum flux
    """

    class Meta:
        name = "fluxes_nl_4d"
        is_root_ids = False

    particles_phi_potential: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 4, dtype=float),
        metadata={
            "imas_type": "FLT_4D",
            "ndims": 4,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../radial_wavevector_norm",
                "coordinate4": "../../angle_pol",
            },
            "field_type": np.ndarray,
        },
    )
    particles_a_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 4, dtype=float),
        metadata={
            "imas_type": "FLT_4D",
            "ndims": 4,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../radial_wavevector_norm",
                "coordinate4": "../../angle_pol",
            },
            "field_type": np.ndarray,
        },
    )
    particles_b_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 4, dtype=float),
        metadata={
            "imas_type": "FLT_4D",
            "ndims": 4,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../radial_wavevector_norm",
                "coordinate4": "../../angle_pol",
            },
            "field_type": np.ndarray,
        },
    )
    energy_phi_potential: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 4, dtype=float),
        metadata={
            "imas_type": "FLT_4D",
            "ndims": 4,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../radial_wavevector_norm",
                "coordinate4": "../../angle_pol",
            },
            "field_type": np.ndarray,
        },
    )
    energy_a_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 4, dtype=float),
        metadata={
            "imas_type": "FLT_4D",
            "ndims": 4,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../radial_wavevector_norm",
                "coordinate4": "../../angle_pol",
            },
            "field_type": np.ndarray,
        },
    )
    energy_b_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 4, dtype=float),
        metadata={
            "imas_type": "FLT_4D",
            "ndims": 4,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../radial_wavevector_norm",
                "coordinate4": "../../angle_pol",
            },
            "field_type": np.ndarray,
        },
    )
    momentum_phi_parallel_phi_potential: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 4, dtype=float),
        metadata={
            "imas_type": "FLT_4D",
            "ndims": 4,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../radial_wavevector_norm",
                "coordinate4": "../../angle_pol",
            },
            "field_type": np.ndarray,
        },
    )
    momentum_phi_parallel_a_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 4, dtype=float),
        metadata={
            "imas_type": "FLT_4D",
            "ndims": 4,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../radial_wavevector_norm",
                "coordinate4": "../../angle_pol",
            },
            "field_type": np.ndarray,
        },
    )
    momentum_phi_parallel_b_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 4, dtype=float),
        metadata={
            "imas_type": "FLT_4D",
            "ndims": 4,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../radial_wavevector_norm",
                "coordinate4": "../../angle_pol",
            },
            "field_type": np.ndarray,
        },
    )
    momentum_phi_perpendicular_phi_potential: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 4, dtype=float),
        metadata={
            "imas_type": "FLT_4D",
            "ndims": 4,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../radial_wavevector_norm",
                "coordinate4": "../../angle_pol",
            },
            "field_type": np.ndarray,
        },
    )
    momentum_phi_perpendicular_a_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 4, dtype=float),
        metadata={
            "imas_type": "FLT_4D",
            "ndims": 4,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../radial_wavevector_norm",
                "coordinate4": "../../angle_pol",
            },
            "field_type": np.ndarray,
        },
    )
    momentum_phi_perpendicular_b_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 4, dtype=float),
        metadata={
            "imas_type": "FLT_4D",
            "ndims": 4,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../radial_wavevector_norm",
                "coordinate4": "../../angle_pol",
            },
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class FluxesNl5D(IdsBaseClass):
    """

    :ivar particles_phi_potential : Contribution of the perturbed electrostatic potential to the normalized particle flux
    :ivar particles_a_field_parallel : Contribution of the perturbed parallel electromagnetic potential to the normalized particle flux
    :ivar particles_b_field_parallel : Contribution of the perturbed parallel magnetic field to the normalized particle flux
    :ivar energy_phi_potential : Contribution of the perturbed electrostatic potential to the normalized energy flux
    :ivar energy_a_field_parallel : Contribution of the perturbed parallel electromagnetic potential to the normalized energy flux
    :ivar energy_b_field_parallel : Contribution of the perturbed parallel magnetic field to the normalized energy flux
    :ivar momentum_phi_parallel_phi_potential : Contribution of the perturbed electrostatic potential to the parallel component of the normalized toroidal momentum flux
    :ivar momentum_phi_parallel_a_field_parallel : Contribution of the perturbed parallel electromagnetic potential to the parallel component of the normalized toroidal momentum flux
    :ivar momentum_phi_parallel_b_field_parallel : Contribution of the perturbed parallel magnetic field to the parallel component of the normalized toroidal momentum flux
    :ivar momentum_phi_perpendicular_phi_potential : Contribution of the perturbed electrostatic potential to the perpendicular component of the normalized toroidal momentum flux
    :ivar momentum_phi_perpendicular_a_field_parallel : Contribution of the perturbed parallel electromagnetic potential to the perpendicular component of the normalized toroidal momentum flux
    :ivar momentum_phi_perpendicular_b_field_parallel : Contribution of the perturbed parallel magnetic field to the perpendicular component of the normalized toroidal momentum flux
    """

    class Meta:
        name = "fluxes_nl_5d"
        is_root_ids = False

    particles_phi_potential: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 5, dtype=float),
        metadata={
            "imas_type": "FLT_5D",
            "ndims": 5,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../radial_wavevector_norm",
                "coordinate4": "../../angle_pol",
                "coordinate5": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    particles_a_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 5, dtype=float),
        metadata={
            "imas_type": "FLT_5D",
            "ndims": 5,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../radial_wavevector_norm",
                "coordinate4": "../../angle_pol",
                "coordinate5": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    particles_b_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 5, dtype=float),
        metadata={
            "imas_type": "FLT_5D",
            "ndims": 5,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../radial_wavevector_norm",
                "coordinate4": "../../angle_pol",
                "coordinate5": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    energy_phi_potential: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 5, dtype=float),
        metadata={
            "imas_type": "FLT_5D",
            "ndims": 5,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../radial_wavevector_norm",
                "coordinate4": "../../angle_pol",
                "coordinate5": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    energy_a_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 5, dtype=float),
        metadata={
            "imas_type": "FLT_5D",
            "ndims": 5,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../radial_wavevector_norm",
                "coordinate4": "../../angle_pol",
                "coordinate5": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    energy_b_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 5, dtype=float),
        metadata={
            "imas_type": "FLT_5D",
            "ndims": 5,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../radial_wavevector_norm",
                "coordinate4": "../../angle_pol",
                "coordinate5": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    momentum_phi_parallel_phi_potential: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 5, dtype=float),
        metadata={
            "imas_type": "FLT_5D",
            "ndims": 5,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../radial_wavevector_norm",
                "coordinate4": "../../angle_pol",
                "coordinate5": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    momentum_phi_parallel_a_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 5, dtype=float),
        metadata={
            "imas_type": "FLT_5D",
            "ndims": 5,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../radial_wavevector_norm",
                "coordinate4": "../../angle_pol",
                "coordinate5": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    momentum_phi_parallel_b_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 5, dtype=float),
        metadata={
            "imas_type": "FLT_5D",
            "ndims": 5,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../radial_wavevector_norm",
                "coordinate4": "../../angle_pol",
                "coordinate5": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    momentum_phi_perpendicular_phi_potential: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 5, dtype=float),
        metadata={
            "imas_type": "FLT_5D",
            "ndims": 5,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../radial_wavevector_norm",
                "coordinate4": "../../angle_pol",
                "coordinate5": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    momentum_phi_perpendicular_a_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 5, dtype=float),
        metadata={
            "imas_type": "FLT_5D",
            "ndims": 5,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../radial_wavevector_norm",
                "coordinate4": "../../angle_pol",
                "coordinate5": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    momentum_phi_perpendicular_b_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 5, dtype=float),
        metadata={
            "imas_type": "FLT_5D",
            "ndims": 5,
            "coordinates": {
                "coordinate1": "/species",
                "coordinate2": "../../binormal_wavevector_norm",
                "coordinate3": "../../radial_wavevector_norm",
                "coordinate4": "../../angle_pol",
                "coordinate5": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class Fluxes(IdsBaseClass):
    """

    :ivar particles_phi_potential : Contribution of the perturbed electrostatic potential to the normalized particle flux
    :ivar particles_a_field_parallel : Contribution of the perturbed parallel electromagnetic potential to the normalized particle flux
    :ivar particles_b_field_parallel : Contribution of the perturbed parallel magnetic field to the normalized particle flux
    :ivar energy_phi_potential : Contribution of the perturbed electrostatic potential to the normalized energy flux
    :ivar energy_a_field_parallel : Contribution of the perturbed parallel electromagnetic potential to the normalized energy flux
    :ivar energy_b_field_parallel : Contribution of the perturbed parallel magnetic field to the normalized energy flux
    :ivar momentum_phi_parallel_phi_potential : Contribution of the perturbed electrostatic potential to the parallel component of the normalized toroidal momentum flux
    :ivar momentum_phi_parallel_a_field_parallel : Contribution of the perturbed parallel electromagnetic potential to the parallel component of the normalized toroidal momentum flux
    :ivar momentum_phi_parallel_b_field_parallel : Contribution of the perturbed parallel magnetic field to the parallel component of the normalized toroidal momentum flux
    :ivar momentum_phi_perpendicular_phi_potential : Contribution of the perturbed electrostatic potential to the perpendicular component of the normalized toroidal momentum flux
    :ivar momentum_phi_perpendicular_a_field_parallel : Contribution of the perturbed parallel electromagnetic potential to the perpendicular component of the normalized toroidal momentum flux
    :ivar momentum_phi_perpendicular_b_field_parallel : Contribution of the perturbed parallel magnetic field to the perpendicular component of the normalized toroidal momentum flux
    """

    class Meta:
        name = "fluxes"
        is_root_ids = False

    particles_phi_potential: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../../species"},
            "field_type": np.ndarray,
        },
    )
    particles_a_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../../species"},
            "field_type": np.ndarray,
        },
    )
    particles_b_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../../species"},
            "field_type": np.ndarray,
        },
    )
    energy_phi_potential: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../../species"},
            "field_type": np.ndarray,
        },
    )
    energy_a_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../../species"},
            "field_type": np.ndarray,
        },
    )
    energy_b_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../../species"},
            "field_type": np.ndarray,
        },
    )
    momentum_phi_parallel_phi_potential: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../../species"},
            "field_type": np.ndarray,
        },
    )
    momentum_phi_parallel_a_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../../species"},
            "field_type": np.ndarray,
        },
    )
    momentum_phi_parallel_b_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../../species"},
            "field_type": np.ndarray,
        },
    )
    momentum_phi_perpendicular_phi_potential: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../../species"},
            "field_type": np.ndarray,
        },
    )
    momentum_phi_perpendicular_a_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../../species"},
            "field_type": np.ndarray,
        },
    )
    momentum_phi_perpendicular_b_field_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../../species"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class EigenmodeFields(IdsBaseClass):
    """

    :ivar phi_potential_perturbed_weight : Amplitude of the perturbed electrostatic potential normalized to the sum of amplitudes of all perturbed fields
    :ivar phi_potential_perturbed_parity : Parity of the perturbed electrostatic potential with respect to theta = 0 (poloidal angle)
    :ivar a_field_parallel_perturbed_weight : Amplitude of the perturbed parallel vector potential normalized to the sum of amplitudes of all perturbed fields
    :ivar a_field_parallel_perturbed_parity : Parity of the perturbed parallel vector potential with respect to theta = 0 (poloidal angle)
    :ivar b_field_parallel_perturbed_weight : Amplitude of the perturbed parallel magnetic field normalized to the sum of amplitudes of all perturbed fields
    :ivar b_field_parallel_perturbed_parity : Parity of the perturbed parallel magnetic field with respect to theta = 0 (poloidal angle)
    :ivar phi_potential_perturbed_norm : normalized perturbed electrostatic potential
    :ivar a_field_parallel_perturbed_norm : normalized perturbed parallel vector potential
    :ivar b_field_parallel_perturbed_norm : normalized perturbed parallel magnetic field
    """

    class Meta:
        name = "eigenmode_fields"
        is_root_ids = False

    phi_potential_perturbed_weight: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time_norm"},
            "field_type": np.ndarray,
        },
    )
    phi_potential_perturbed_parity: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time_norm"},
            "field_type": np.ndarray,
        },
    )
    a_field_parallel_perturbed_weight: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time_norm"},
            "field_type": np.ndarray,
        },
    )
    a_field_parallel_perturbed_parity: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time_norm"},
            "field_type": np.ndarray,
        },
    )
    b_field_parallel_perturbed_weight: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time_norm"},
            "field_type": np.ndarray,
        },
    )
    b_field_parallel_perturbed_parity: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time_norm"},
            "field_type": np.ndarray,
        },
    )
    phi_potential_perturbed_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=complex),
        metadata={
            "imas_type": "CPX_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../angle_pol",
                "coordinate2": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    a_field_parallel_perturbed_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=complex),
        metadata={
            "imas_type": "CPX_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../angle_pol",
                "coordinate2": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )
    b_field_parallel_perturbed_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=complex),
        metadata={
            "imas_type": "CPX_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../angle_pol",
                "coordinate2": "../../time_norm",
            },
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class Eigenmode(IdsBaseClass):
    """

    :ivar poloidal_turns : Number of poloidal turns considered in the flux-tube simulation
    :ivar growth_rate_norm : Growth rate
    :ivar frequency_norm : Frequency
    :ivar growth_rate_tolerance : Relative tolerance on the growth rate (convergence of the simulation)
    :ivar angle_pol : Poloidal angle grid. The angle is defined with respect to (R0,Z0) with R0=(Rmax-Rmin)/2 and Z0=(Zmax-Zmin)/2. It is increasing clockwise. So (r,theta,phi) is right-handed. theta=0 for Z=Z0 and R&gt;R0 (LFS)
    :ivar time_norm : normalized time of the gyrokinetic simulation
    :ivar fields : Electrostatic potential, magnetic field and magnetic vector potential
    :ivar code : Code-specific parameters used for this eigenmode
    :ivar initial_value_run : Flag = 1 if this is an initial value run, 0 for an eigenvalue run
    :ivar moments_norm_gyrocenter : Moments (normalized) of the perturbed distribution function of gyrocenters
    :ivar moments_norm_particle : Moments (normalized) of the perturbed distribution function of particles
    :ivar moments_norm_gyrocenter_bessel_0 : Moments (normalized) of the perturbed distribution function of gyrocenters times 0th order Bessel function of the first kind
    :ivar moments_norm_gyrocenter_bessel_1 : Moments (normalized) of the perturbed distribution function of gyrocenters times 1st order Bessel function of the first kind
    :ivar linear_weights : normalized fluxes in the laboratory frame
    :ivar linear_weights_rotating_frame : normalized fluxes in the rotating frame
    """

    class Meta:
        name = "eigenmode"
        is_root_ids = False

    poloidal_turns: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    growth_rate_norm: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    frequency_norm: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    growth_rate_tolerance: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    angle_pol: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    time_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    fields: Optional[EigenmodeFields] = field(
        default=None,
        metadata={
            "imas_type": "eigenmode_fields",
            "field_type": EigenmodeFields,
        },
    )
    code: Optional[CodePartialConstant] = field(
        default=None,
        metadata={
            "imas_type": "code_partial_constant",
            "field_type": CodePartialConstant,
        },
    )
    initial_value_run: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    moments_norm_gyrocenter: Optional[MomentsLinear] = field(
        default=None,
        metadata={"imas_type": "moments_linear", "field_type": MomentsLinear},
    )
    moments_norm_particle: Optional[MomentsLinear] = field(
        default=None,
        metadata={"imas_type": "moments_linear", "field_type": MomentsLinear},
    )
    moments_norm_gyrocenter_bessel_0: Optional[MomentsLinear] = field(
        default=None,
        metadata={"imas_type": "moments_linear", "field_type": MomentsLinear},
    )
    moments_norm_gyrocenter_bessel_1: Optional[MomentsLinear] = field(
        default=None,
        metadata={"imas_type": "moments_linear", "field_type": MomentsLinear},
    )
    linear_weights: Optional[Fluxes] = field(
        default=None, metadata={"imas_type": "fluxes", "field_type": Fluxes}
    )
    linear_weights_rotating_frame: Optional[Fluxes] = field(
        default=None, metadata={"imas_type": "fluxes", "field_type": Fluxes}
    )


@idspy_dataclass(repr=False, slots=True)
class Wavevector(IdsBaseClass):
    """

    :ivar radial_wavevector_norm : normalized radial component of the wavevector
    :ivar binormal_wavevector_norm : normalized binormal component of the wavevector
    :ivar eigenmode : Set of eigenmode for this wavector
    """

    class Meta:
        name = "wavevector"
        is_root_ids = False

    radial_wavevector_norm: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    binormal_wavevector_norm: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    eigenmode: Optional[Eigenmode] = field(
        default_factory=lambda: StructArray(type_input=Eigenmode),
        metadata={
            "imas_type": "eigenmode",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": Eigenmode,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class Collisions(IdsBaseClass):
    """

    :ivar collisionality_norm : normalized collisionality between two species
    """

    class Meta:
        name = "collisions"
        is_root_ids = False

    collisionality_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../species",
                "coordinate2": "../../species",
            },
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class Linear(IdsBaseClass):
    """

    :ivar wavevector : Set of wavevectors
    """

    class Meta:
        name = "linear"
        is_root_ids = False

    wavevector: Optional[Wavevector] = field(
        default_factory=lambda: StructArray(type_input=Wavevector),
        metadata={
            "imas_type": "wavevector",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": Wavevector,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class NonLinear(IdsBaseClass):
    """

    :ivar binormal_wavevector_norm : Array of normalized binormal wavevectors
    :ivar radial_wavevector_norm : Array of normalized radial wavevectors
    :ivar angle_pol : Poloidal angle grid. The angle is defined with respect to (R0,Z0) with R0=(Rmax-Rmin)/2 and Z0=(Zmax-Zmin)/2. It is increasing clockwise. So (r,theta,phi) is right-handed. theta=0 for Z=Z0 and R&gt;R0 (LFS)
    :ivar time_norm : normalized time of the gyrokinetic simulation
    :ivar time_interval_norm : normalized time interval used to average fluxes in non-linear runs
    :ivar quasi_linear : Flag = 1 if the non-linear fluxes are in fact calculated by a quasi-linear model, 0 if non-linear
    :ivar code : Code-specific parameters used for the non-linear simulation
    :ivar fluxes_5d : 5D fluxes
    :ivar fluxes_4d : 4D fluxes (time averaged)
    :ivar fluxes_3d : 3D fluxes (time and flux surface averaged)
    :ivar fluxes_3d_k_x_sum : 3D fluxes (flux surface averaged, summed over kx)
    :ivar fluxes_2d_k_x_sum : 2D fluxes (time and flux-surface averaged), summed over kx
    :ivar fluxes_2d_k_x_k_y_sum : 2D fluxes (flux-surface averaged), summed over kx and ky
    :ivar fluxes_1d : 1D fluxes (flux-surface and time averaged), summed over kx and ky
    :ivar fields_4d : 4D fields
    :ivar fields_intensity_3d : 3D fields (time averaged)
    :ivar fields_intensity_2d_surface_average : 2D fields (time averaged and flux surface averaged)
    :ivar fields_zonal_2d : 2D zonal fields (taken at ky=0, flux surface averaged)
    :ivar fields_intensity_1d : 1D fields (summed over kx, time averaged and flux surface averaged)
    :ivar fluxes_5d_rotating_frame : 5D fluxes in the rotating frame
    :ivar fluxes_4d_rotating_frame : 4D fluxes (time averaged) in the rotating frame
    :ivar fluxes_3d_rotating_frame : 3D fluxes (time and flux surface averaged) in the rotating frame
    :ivar fluxes_3d_k_x_sum_rotating_frame : 3D fluxes (flux surface averaged, summed over kx)
    :ivar fluxes_2d_k_x_sum_rotating_frame : 2D fluxes (time and flux-surface averaged), summed over kx in the rotating frame
    :ivar fluxes_2d_k_x_k_y_sum_rotating_frame : 2D fluxes (flux-surface averaged), summed over kx and ky in the rotating frame
    :ivar fluxes_1d_rotating_frame : 1D fluxes (flux-surface and time averaged), summed over kx and ky in the rotating frame
    """

    class Meta:
        name = "non_linear"
        is_root_ids = False

    binormal_wavevector_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    radial_wavevector_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    angle_pol: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    time_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    time_interval_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...2"},
            "field_type": np.ndarray,
        },
    )
    quasi_linear: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    code: Optional[CodePartialConstant] = field(
        default=None,
        metadata={
            "imas_type": "code_partial_constant",
            "field_type": CodePartialConstant,
        },
    )
    fluxes_5d: Optional[FluxesNl5D] = field(
        default=None,
        metadata={"imas_type": "fluxes_nl_5d", "field_type": FluxesNl5D},
    )
    fluxes_4d: Optional[FluxesNl4D] = field(
        default=None,
        metadata={"imas_type": "fluxes_nl_4d", "field_type": FluxesNl4D},
    )
    fluxes_3d: Optional[FluxesNl3D] = field(
        default=None,
        metadata={"imas_type": "fluxes_nl_3d", "field_type": FluxesNl3D},
    )
    fluxes_3d_k_x_sum: Optional[FluxesNl3DSumKx] = field(
        default=None,
        metadata={
            "imas_type": "fluxes_nl_3d_sum_kx",
            "field_type": FluxesNl3DSumKx,
        },
    )
    fluxes_2d_k_x_sum: Optional[FluxesNl2DSumKx] = field(
        default=None,
        metadata={
            "imas_type": "fluxes_nl_2d_sum_kx",
            "field_type": FluxesNl2DSumKx,
        },
    )
    fluxes_2d_k_x_k_y_sum: Optional[FluxesNl2DSumKxKy] = field(
        default=None,
        metadata={
            "imas_type": "fluxes_nl_2d_sum_kx_ky",
            "field_type": FluxesNl2DSumKxKy,
        },
    )
    fluxes_1d: Optional[FluxesNl1D] = field(
        default=None,
        metadata={"imas_type": "fluxes_nl_1d", "field_type": FluxesNl1D},
    )
    fields_4d: Optional[FieldsNl4D] = field(
        default=None,
        metadata={"imas_type": "fields_nl_4d", "field_type": FieldsNl4D},
    )
    fields_intensity_3d: Optional[FieldsNl3D] = field(
        default=None,
        metadata={"imas_type": "fields_nl_3d", "field_type": FieldsNl3D},
    )
    fields_intensity_2d_surface_average: Optional[FieldsNl2DFsAverage] = field(
        default=None,
        metadata={
            "imas_type": "fields_nl_2d_fs_average",
            "field_type": FieldsNl2DFsAverage,
        },
    )
    fields_zonal_2d: Optional[FieldsNl2DKy0] = field(
        default=None,
        metadata={"imas_type": "fields_nl_2d_ky0", "field_type": FieldsNl2DKy0},
    )
    fields_intensity_1d: Optional[FieldsNl1D] = field(
        default=None,
        metadata={"imas_type": "fields_nl_1d", "field_type": FieldsNl1D},
    )
    fluxes_5d_rotating_frame: Optional[FluxesNl5D] = field(
        default=None,
        metadata={"imas_type": "fluxes_nl_5d", "field_type": FluxesNl5D},
    )
    fluxes_4d_rotating_frame: Optional[FluxesNl4D] = field(
        default=None,
        metadata={"imas_type": "fluxes_nl_4d", "field_type": FluxesNl4D},
    )
    fluxes_3d_rotating_frame: Optional[FluxesNl3D] = field(
        default=None,
        metadata={"imas_type": "fluxes_nl_3d", "field_type": FluxesNl3D},
    )
    fluxes_3d_k_x_sum_rotating_frame: Optional[FluxesNl3DSumKx] = field(
        default=None,
        metadata={
            "imas_type": "fluxes_nl_3d_sum_kx",
            "field_type": FluxesNl3DSumKx,
        },
    )
    fluxes_2d_k_x_sum_rotating_frame: Optional[FluxesNl2DSumKx] = field(
        default=None,
        metadata={
            "imas_type": "fluxes_nl_2d_sum_kx",
            "field_type": FluxesNl2DSumKx,
        },
    )
    fluxes_2d_k_x_k_y_sum_rotating_frame: Optional[FluxesNl2DSumKxKy] = field(
        default=None,
        metadata={
            "imas_type": "fluxes_nl_2d_sum_kx_ky",
            "field_type": FluxesNl2DSumKxKy,
        },
    )
    fluxes_1d_rotating_frame: Optional[FluxesNl1D] = field(
        default=None,
        metadata={"imas_type": "fluxes_nl_1d", "field_type": FluxesNl1D},
    )


@idspy_dataclass(repr=False, slots=True)
class GyrokineticsLocal(IdsBaseClass):
    """

    :ivar ids_properties :
    :ivar normalizing_quantities : Physical quantities used for normalization (useful to link to the original simulation/experience)
    :ivar flux_surface : Flux surface characteristics
    :ivar linear : Linear simulation
    :ivar non_linear : Non-linear simulation
    :ivar model : Assumptions of the GK calculations
    :ivar species_all : Physical quantities common to all species
    :ivar species : Set of species (including electrons) used in the calculation and related quantities
    :ivar collisions : Collisions related quantities
    :ivar code : Generic decription of the code-specific parameters for the code that has produced this IDS
    """

    class Meta:
        name = "gyrokinetics_local"
        is_root_ids = True

    ids_properties: Optional[IdsProperties] = field(
        default=None,
        metadata={"imas_type": "ids_properties", "field_type": IdsProperties},
    )
    normalizing_quantities: Optional[InputNormalizing] = field(
        default=None,
        metadata={
            "imas_type": "input_normalizing",
            "field_type": InputNormalizing,
        },
    )
    flux_surface: Optional[FluxSurface] = field(
        default=None,
        metadata={"imas_type": "flux_surface", "field_type": FluxSurface},
    )
    linear: Optional[Linear] = field(
        default=None, metadata={"imas_type": "linear", "field_type": Linear}
    )
    non_linear: Optional[NonLinear] = field(
        default=None,
        metadata={"imas_type": "non_linear", "field_type": NonLinear},
    )
    model: Optional[Model] = field(
        default=None, metadata={"imas_type": "model", "field_type": Model}
    )
    species_all: Optional[InputSpeciesGlobal] = field(
        default=None,
        metadata={
            "imas_type": "input_species_global",
            "field_type": InputSpeciesGlobal,
        },
    )
    species: Optional[Species] = field(
        default_factory=lambda: StructArray(type_input=Species),
        metadata={
            "imas_type": "species",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": Species,
        },
    )
    collisions: Optional[Collisions] = field(
        default=None,
        metadata={"imas_type": "collisions", "field_type": Collisions},
    )
    code: Optional[CodeConstant] = field(
        default=None,
        metadata={"imas_type": "code_constant", "field_type": CodeConstant},
    )
