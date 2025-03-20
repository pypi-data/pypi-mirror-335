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
class EquilibriumProfiles2DGrid(IdsBaseClass):
    """

    :ivar dim1 : First dimension values
    :ivar dim2 : Second dimension values
    :ivar volume_element : Elementary plasma volume of plasma enclosed in the cell formed by the nodes [dim1(i) dim2(j)], [dim1(i+1) dim2(j)], [dim1(i) dim2(j+1)] and [dim1(i+1) dim2(j+1)]
    """

    class Meta:
        name = "equilibrium_profiles_2d_grid"
        is_root_ids = False

    dim1: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    dim2: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    volume_element: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {"coordinate1": "../dim1", "coordinate2": "../dim2"},
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
class MhdCoordinateSystem(IdsBaseClass):
    """

    :ivar grid_type : Selection of one of a set of grid types
    :ivar grid : Definition of the 2D grid
    :ivar r : Values of the major radius on the grid
    :ivar z : Values of the Height on the grid
    :ivar jacobian : Absolute value of the jacobian of the coordinate system
    :ivar tensor_covariant : Covariant metric tensor on every point of the grid described by grid_type
    :ivar tensor_contravariant : Contravariant metric tensor on every point of the grid described by grid_type
    """

    class Meta:
        name = "mhd_coordinate_system"
        is_root_ids = False

    grid_type: Optional[IdentifierDynamicAos3] = field(
        default=None,
        metadata={
            "imas_type": "identifier_dynamic_aos3",
            "field_type": IdentifierDynamicAos3,
        },
    )
    grid: Optional[EquilibriumProfiles2DGrid] = field(
        default=None,
        metadata={
            "imas_type": "equilibrium_profiles_2d_grid",
            "field_type": EquilibriumProfiles2DGrid,
        },
    )
    r: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../grid/dim1",
                "coordinate2": "../grid/dim2",
            },
            "field_type": np.ndarray,
        },
    )
    z: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../grid/dim1",
                "coordinate2": "../grid/dim2",
            },
            "field_type": np.ndarray,
        },
    )
    jacobian: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../grid/dim1",
                "coordinate2": "../grid/dim2",
            },
            "field_type": np.ndarray,
        },
    )
    tensor_covariant: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 4, dtype=float),
        metadata={
            "imas_type": "FLT_4D",
            "ndims": 4,
            "coordinates": {
                "coordinate1": "../grid/dim1",
                "coordinate2": "../grid/dim2",
                "coordinate3": "1...3",
                "coordinate4": "1...3",
            },
            "field_type": np.ndarray,
        },
    )
    tensor_contravariant: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 4, dtype=float),
        metadata={
            "imas_type": "FLT_4D",
            "ndims": 4,
            "coordinates": {
                "coordinate1": "../grid/dim1",
                "coordinate2": "../grid/dim2",
                "coordinate3": "1...3",
                "coordinate4": "1...3",
            },
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class Complex2DDynamicAosMhdLinearVector(IdsBaseClass):
    """

    :ivar real : Real part
    :ivar imaginary : Imaginary part
    :ivar coefficients_real : Interpolation coefficients, to be used for a high precision evaluation of the physical quantity (real part) with finite elements, provided on the 2D grid
    :ivar coefficients_imaginary : Interpolation coefficients, to be used for a high precision evaluation of the physical quantity (imaginary part) with finite elements, provided on the 2D grid
    """

    class Meta:
        name = "complex_2d_dynamic_aos_mhd_linear_vector"
        is_root_ids = False

    real: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../../grid/dim1",
                "coordinate2": "../../../grid/dim2",
            },
            "field_type": np.ndarray,
        },
    )
    imaginary: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../../grid/dim1",
                "coordinate2": "../../../grid/dim2",
            },
            "field_type": np.ndarray,
        },
    )
    coefficients_real: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "../../../grid/dim1",
                "coordinate2": "../../../grid/dim2",
                "coordinate3": "1...N",
            },
            "field_type": np.ndarray,
        },
    )
    coefficients_imaginary: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "../../../grid/dim1",
                "coordinate2": "../../../grid/dim2",
                "coordinate3": "1...N",
            },
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class Complex2DDynamicAosMhdScalar(IdsBaseClass):
    """

    :ivar real : Real part
    :ivar imaginary : Imaginary part
    :ivar coefficients_real : Interpolation coefficients, to be used for a high precision evaluation of the physical quantity (real part) with finite elements, provided on the 2D grid
    :ivar coefficients_imaginary : Interpolation coefficients, to be used for a high precision evaluation of the physical quantity (imaginary part) with finite elements, provided on the 2D grid
    """

    class Meta:
        name = "complex_2d_dynamic_aos_mhd_scalar"
        is_root_ids = False

    real: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../grid/dim1",
                "coordinate2": "../../grid/dim2",
            },
            "field_type": np.ndarray,
        },
    )
    imaginary: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../grid/dim1",
                "coordinate2": "../../grid/dim2",
            },
            "field_type": np.ndarray,
        },
    )
    coefficients_real: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "../../grid/dim1",
                "coordinate2": "../../grid/dim2",
                "coordinate3": "1...N",
            },
            "field_type": np.ndarray,
        },
    )
    coefficients_imaginary: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "../../grid/dim1",
                "coordinate2": "../../grid/dim2",
                "coordinate3": "1...N",
            },
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class Complex1DMhdAlfvenSpectrum(IdsBaseClass):
    """

    :ivar real : Real part of the frequency, for a given radial position and every root found at this position
    :ivar imaginary : Imaginary part of the frequency, for a given radial position and every root found at this position
    """

    class Meta:
        name = "complex_1d_mhd_alfven_spectrum"
        is_root_ids = False

    real: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    imaginary: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../real"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class Complex3DMhdStressTensor(IdsBaseClass):
    """

    :ivar real : Real part of the stress tensor, for various radial positions
    :ivar imaginary : Imaginary part of the stress tensor, for various radial positions
    """

    class Meta:
        name = "complex_3d_mhd_stress_tensor"
        is_root_ids = False

    real: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "../../grid/dim1",
                "coordinate2": "1...N",
                "coordinate3": "1...N",
            },
            "field_type": np.ndarray,
        },
    )
    imaginary: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 5, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 5,
            "coordinates": {
                "coordinate1": "../../grid/dim1",
                "coordinate2": "1...N",
                "coordinate2_same_as": "../real",
                "coordinate3": "1...N",
                "coordinate3_same_as": "../real",
            },
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class MhdLinearVector(IdsBaseClass):
    """

    :ivar coordinate1 : First coordinate (radial)
    :ivar coordinate2 : Second coordinate (poloidal)
    :ivar coordinate3 : Third coordinate (toroidal)
    """

    class Meta:
        name = "mhd_linear_vector"
        is_root_ids = False

    coordinate1: Optional[Complex2DDynamicAosMhdLinearVector] = field(
        default=None,
        metadata={
            "imas_type": "complex_2d_dynamic_aos_mhd_linear_vector",
            "field_type": Complex2DDynamicAosMhdLinearVector,
        },
    )
    coordinate2: Optional[Complex2DDynamicAosMhdLinearVector] = field(
        default=None,
        metadata={
            "imas_type": "complex_2d_dynamic_aos_mhd_linear_vector",
            "field_type": Complex2DDynamicAosMhdLinearVector,
        },
    )
    coordinate3: Optional[Complex2DDynamicAosMhdLinearVector] = field(
        default=None,
        metadata={
            "imas_type": "complex_2d_dynamic_aos_mhd_linear_vector",
            "field_type": Complex2DDynamicAosMhdLinearVector,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class MhdLinearTimeSliceToroidalModeVacuum(IdsBaseClass):
    """

    :ivar grid_type : Selection of one of a set of grid types
    :ivar grid : Definition of the 2D grid (the content of dim1 and dim2 is defined by the selected grid_type)
    :ivar coordinate_system : Flux surface coordinate system of the equilibrium used for the MHD calculation on a square grid of flux and poloidal angle
    :ivar a_field_perturbed : Pertubed vector potential for given toroidal mode number
    :ivar b_field_perturbed : Pertubed magnetic field for given toroidal mode number
    """

    class Meta:
        name = "mhd_linear_time_slice_toroidal_mode_vacuum"
        is_root_ids = False

    grid_type: Optional[IdentifierDynamicAos3] = field(
        default=None,
        metadata={
            "imas_type": "identifier_dynamic_aos3",
            "field_type": IdentifierDynamicAos3,
        },
    )
    grid: Optional[EquilibriumProfiles2DGrid] = field(
        default=None,
        metadata={
            "imas_type": "equilibrium_profiles_2d_grid",
            "field_type": EquilibriumProfiles2DGrid,
        },
    )
    coordinate_system: Optional[MhdCoordinateSystem] = field(
        default=None,
        metadata={
            "imas_type": "mhd_coordinate_system",
            "field_type": MhdCoordinateSystem,
        },
    )
    a_field_perturbed: Optional[MhdLinearVector] = field(
        default=None,
        metadata={
            "imas_type": "mhd_linear_vector",
            "field_type": MhdLinearVector,
        },
    )
    b_field_perturbed: Optional[MhdLinearVector] = field(
        default=None,
        metadata={
            "imas_type": "mhd_linear_vector",
            "field_type": MhdLinearVector,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class MhdLinearTimeSliceToroidalModePlasma(IdsBaseClass):
    """

    :ivar grid_type : Selection of one of a set of grid types
    :ivar grid : Definition of the 2D grid (the content of dim1 and dim2 is defined by the selected grid_type)
    :ivar coordinate_system : Flux surface coordinate system of the equilibrium used for the MHD calculation on a square grid of flux and poloidal angle
    :ivar displacement_perpendicular : Perpendicular displacement of the modes
    :ivar displacement_parallel : Parallel displacement of the modes
    :ivar tau_alfven : Alven time=R/vA=R0 sqrt(mi ni(rho))/B0
    :ivar tau_resistive : Resistive time = mu_0 rho*rho/1.22/eta_neo
    :ivar a_field_perturbed : Pertubed vector potential for given toroidal mode number
    :ivar b_field_perturbed : Pertubed magnetic field for given toroidal mode number
    :ivar velocity_perturbed : Pertubed velocity for given toroidal mode number
    :ivar pressure_perturbed : Perturbed pressure for given toroidal mode number
    :ivar mass_density_perturbed : Perturbed mass density for given toroidal mode number
    :ivar temperature_perturbed : Perturbed temperature for given toroidal mode number
    :ivar phi_potential_perturbed : Perturbed electrostatic potential for given toroidal mode number
    :ivar psi_potential_perturbed : Perturbed electromagnetic super-potential for given toroidal mode number, see ref [Antonsen/Lane Phys Fluids 23(6) 1980, formula 34], so that A_field_parallel=1/(i*2pi*frequency) (grad psi_potential)_parallel
    :ivar alfven_frequency_spectrum : Local shear Alfven spectrum as a function of radius (only in case grid/dim1 is a radial coordinate)
    :ivar stress_maxwell : Maxwell stress tensor
    :ivar stress_reynolds : Reynolds stress tensor
    :ivar ntv : Neoclassical toroidal viscosity tensor
    """

    class Meta:
        name = "mhd_linear_time_slice_toroidal_mode_plasma"
        is_root_ids = False

    grid_type: Optional[IdentifierDynamicAos3] = field(
        default=None,
        metadata={
            "imas_type": "identifier_dynamic_aos3",
            "field_type": IdentifierDynamicAos3,
        },
    )
    grid: Optional[EquilibriumProfiles2DGrid] = field(
        default=None,
        metadata={
            "imas_type": "equilibrium_profiles_2d_grid",
            "field_type": EquilibriumProfiles2DGrid,
        },
    )
    coordinate_system: Optional[MhdCoordinateSystem] = field(
        default=None,
        metadata={
            "imas_type": "mhd_coordinate_system",
            "field_type": MhdCoordinateSystem,
        },
    )
    displacement_perpendicular: Optional[Complex2DDynamicAosMhdScalar] = field(
        default=None,
        metadata={
            "imas_type": "complex_2d_dynamic_aos_mhd_scalar",
            "field_type": Complex2DDynamicAosMhdScalar,
        },
    )
    displacement_parallel: Optional[Complex2DDynamicAosMhdScalar] = field(
        default=None,
        metadata={
            "imas_type": "complex_2d_dynamic_aos_mhd_scalar",
            "field_type": Complex2DDynamicAosMhdScalar,
        },
    )
    tau_alfven: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/dim1"},
            "field_type": np.ndarray,
        },
    )
    tau_resistive: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/dim1"},
            "field_type": np.ndarray,
        },
    )
    a_field_perturbed: Optional[MhdLinearVector] = field(
        default=None,
        metadata={
            "imas_type": "mhd_linear_vector",
            "field_type": MhdLinearVector,
        },
    )
    b_field_perturbed: Optional[MhdLinearVector] = field(
        default=None,
        metadata={
            "imas_type": "mhd_linear_vector",
            "field_type": MhdLinearVector,
        },
    )
    velocity_perturbed: Optional[MhdLinearVector] = field(
        default=None,
        metadata={
            "imas_type": "mhd_linear_vector",
            "field_type": MhdLinearVector,
        },
    )
    pressure_perturbed: Optional[Complex2DDynamicAosMhdScalar] = field(
        default=None,
        metadata={
            "imas_type": "complex_2d_dynamic_aos_mhd_scalar",
            "field_type": Complex2DDynamicAosMhdScalar,
        },
    )
    mass_density_perturbed: Optional[Complex2DDynamicAosMhdScalar] = field(
        default=None,
        metadata={
            "imas_type": "complex_2d_dynamic_aos_mhd_scalar",
            "field_type": Complex2DDynamicAosMhdScalar,
        },
    )
    temperature_perturbed: Optional[Complex2DDynamicAosMhdScalar] = field(
        default=None,
        metadata={
            "imas_type": "complex_2d_dynamic_aos_mhd_scalar",
            "field_type": Complex2DDynamicAosMhdScalar,
        },
    )
    phi_potential_perturbed: Optional[Complex2DDynamicAosMhdScalar] = field(
        default=None,
        metadata={
            "imas_type": "complex_2d_dynamic_aos_mhd_scalar",
            "field_type": Complex2DDynamicAosMhdScalar,
        },
    )
    psi_potential_perturbed: Optional[Complex2DDynamicAosMhdScalar] = field(
        default=None,
        metadata={
            "imas_type": "complex_2d_dynamic_aos_mhd_scalar",
            "field_type": Complex2DDynamicAosMhdScalar,
        },
    )
    alfven_frequency_spectrum: Optional[Complex1DMhdAlfvenSpectrum] = field(
        default_factory=lambda: StructArray(
            type_input=Complex1DMhdAlfvenSpectrum
        ),
        metadata={
            "imas_type": "complex_1d_mhd_alfven_spectrum",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/dim1"},
            "field_type": Complex1DMhdAlfvenSpectrum,
        },
    )
    stress_maxwell: Optional[Complex3DMhdStressTensor] = field(
        default=None,
        metadata={
            "imas_type": "complex_3d_mhd_stress_tensor",
            "field_type": Complex3DMhdStressTensor,
        },
    )
    stress_reynolds: Optional[Complex3DMhdStressTensor] = field(
        default=None,
        metadata={
            "imas_type": "complex_3d_mhd_stress_tensor",
            "field_type": Complex3DMhdStressTensor,
        },
    )
    ntv: Optional[Complex3DMhdStressTensor] = field(
        default=None,
        metadata={
            "imas_type": "complex_3d_mhd_stress_tensor",
            "field_type": Complex3DMhdStressTensor,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class MhdLinearTimeSliceToroidalModes(IdsBaseClass):
    """

    :ivar perturbation_type : Type of the perturbation
    :ivar n_phi : Toroidal mode number of the MHD mode
    :ivar m_pol_dominant : Dominant poloidal mode number defining the mode rational surface; for TAEs the lower of the two main m&#39;s has to be specified
    :ivar ballooning_type : Ballooning type of the mode : ballooning 0; anti-ballooning:1; flute-like:2
    :ivar radial_mode_number : Radial mode number
    :ivar growthrate : Linear growthrate of the mode
    :ivar frequency : Frequency of the mode
    :ivar phase : Additional phase offset of mode
    :ivar energy_perturbed : Perturbed energy associated to the mode
    :ivar amplitude_multiplier : Multiplier that is needed to convert the linear mode structures to the amplitude of a non-linearly saturated mode in physical units. If empty, it means that the structures contains no information about non-linearly saturated mode
    :ivar plasma : MHD modes in the confined plasma
    :ivar vacuum : MHD modes in the vacuum
    """

    class Meta:
        name = "mhd_linear_time_slice_toroidal_modes"
        is_root_ids = False

    perturbation_type: Optional[IdentifierDynamicAos3] = field(
        default=None,
        metadata={
            "imas_type": "identifier_dynamic_aos3",
            "field_type": IdentifierDynamicAos3,
        },
    )
    n_phi: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    m_pol_dominant: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    ballooning_type: Optional[IdentifierDynamicAos3] = field(
        default=None,
        metadata={
            "imas_type": "identifier_dynamic_aos3",
            "field_type": IdentifierDynamicAos3,
        },
    )
    radial_mode_number: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    growthrate: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    frequency: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    phase: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    energy_perturbed: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    amplitude_multiplier: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    plasma: Optional[MhdLinearTimeSliceToroidalModePlasma] = field(
        default=None,
        metadata={
            "imas_type": "mhd_linear_time_slice_toroidal_mode_plasma",
            "field_type": MhdLinearTimeSliceToroidalModePlasma,
        },
    )
    vacuum: Optional[MhdLinearTimeSliceToroidalModeVacuum] = field(
        default=None,
        metadata={
            "imas_type": "mhd_linear_time_slice_toroidal_mode_vacuum",
            "field_type": MhdLinearTimeSliceToroidalModeVacuum,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class MhdLinearTimeSlice(IdsBaseClass):
    """

    :ivar toroidal_mode : Vector of toroidal modes. Each mode is described as exp(i(n_tor.phi - m_pol.theta - 2.pi.frequency.t - phase))
    :ivar time : Time
    """

    class Meta:
        name = "mhd_linear_time_slice"
        is_root_ids = False

    toroidal_mode: Optional[MhdLinearTimeSliceToroidalModes] = field(
        default_factory=lambda: StructArray(
            type_input=MhdLinearTimeSliceToroidalModes
        ),
        metadata={
            "imas_type": "mhd_linear_time_slice_toroidal_modes",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": MhdLinearTimeSliceToroidalModes,
        },
    )
    time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class MhdLinear(IdsBaseClass):
    """

    :ivar ids_properties :
    :ivar fluids_n : Number of fluids considered in the model
    :ivar ideal_flag : 1 if ideal MHD is used to populate this IDS, 0 for non-ideal MHD
    :ivar vacuum_toroidal_field : Characteristics of the vacuum toroidal field (used in rho_tor definition and in the normalization of current densities)
    :ivar time_slice : Core plasma radial profiles for various time slices
    :ivar code :
    :ivar time : Generic time
    """

    class Meta:
        name = "mhd_linear"
        is_root_ids = True

    ids_properties: Optional[IdsProperties] = field(
        default=None,
        metadata={"imas_type": "ids_properties", "field_type": IdsProperties},
    )
    fluids_n: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    ideal_flag: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    vacuum_toroidal_field: Optional[BTorVacuum1] = field(
        default=None,
        metadata={"imas_type": "b_tor_vacuum_1", "field_type": BTorVacuum1},
    )
    time_slice: Optional[MhdLinearTimeSlice] = field(
        default_factory=lambda: StructArray(type_input=MhdLinearTimeSlice),
        metadata={
            "imas_type": "mhd_linear_time_slice",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": MhdLinearTimeSlice,
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
