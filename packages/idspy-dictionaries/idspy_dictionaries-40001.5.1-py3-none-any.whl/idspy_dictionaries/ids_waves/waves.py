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
class GenericGridDynamicSpaceDimensionObjectBoundary(IdsBaseClass):
    """

    :ivar index : Index of this (n-1)-dimensional boundary object
    :ivar neighbours : List of indices of the n-dimensional objects adjacent to the given n-dimensional object. An object can possibly have multiple neighbours on a boundary
    """

    class Meta:
        name = "generic_grid_dynamic_space_dimension_object_boundary"
        is_root_ids = False

    index: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    neighbours: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=int),
        metadata={
            "imas_type": "INT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class GenericGridDynamicGridSubsetElementObject(IdsBaseClass):
    """

    :ivar space : Index of the space from which that object is taken
    :ivar dimension : Dimension of the object - using the convention  1=nodes, 2=edges, 3=faces, 4=cells/volumes
    :ivar index : Object index
    """

    class Meta:
        name = "generic_grid_dynamic_grid_subset_element_object"
        is_root_ids = False

    space: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    dimension: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    index: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )


@idspy_dataclass(repr=False, slots=True)
class GenericGridDynamicSpaceDimensionObject(IdsBaseClass):
    """

    :ivar boundary : Set of  (n-1)-dimensional objects defining the boundary of this n-dimensional object
    :ivar geometry : Geometry data associated with the object, its detailed content is defined by ../../geometry_content. Its dimension depends on the type of object, geometry and coordinate considered.
    :ivar nodes : List of nodes forming this object (indices to objects_per_dimension(1)%object(:) in Fortran notation)
    :ivar measure : Measure of the space object, i.e. physical size (length for 1d, area for 2d, volume for 3d objects,...)
    :ivar geometry_2d : 2D geometry data associated with the object. Its dimension depends on the type of object, geometry and coordinate considered. Typically, the first dimension represents the object coordinates, while the second dimension would represent the values of the various degrees of freedom of the finite element attached to the object.
    """

    class Meta:
        name = "generic_grid_dynamic_space_dimension_object"
        is_root_ids = False

    boundary: Optional[GenericGridDynamicSpaceDimensionObjectBoundary] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridDynamicSpaceDimensionObjectBoundary
        ),
        metadata={
            "imas_type": "generic_grid_dynamic_space_dimension_object_boundary",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridDynamicSpaceDimensionObjectBoundary,
        },
    )
    geometry: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "flt_1d_type",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    nodes: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=int),
        metadata={
            "imas_type": "INT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    measure: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
    )
    geometry_2d: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "flt_2d_type",
            "ndims": 2,
            "coordinates": {"coordinate1": "1...N", "coordinate2": "1...N"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class GenericGridDynamicGridSubsetMetric(IdsBaseClass):
    """

    :ivar jacobian : Metric Jacobian
    :ivar tensor_covariant : Covariant metric tensor, given on each element of the subgrid (first dimension)
    :ivar tensor_contravariant : Contravariant metric tensor, given on each element of the subgrid (first dimension)
    """

    class Meta:
        name = "generic_grid_dynamic_grid_subset_metric"
        is_root_ids = False

    jacobian: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../element"},
            "field_type": np.ndarray,
        },
    )
    tensor_covariant: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "../../element",
                "coordinate2": "1...N",
                "coordinate3": "1...N",
            },
            "field_type": np.ndarray,
        },
    )
    tensor_contravariant: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 5, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 5,
            "coordinates": {
                "coordinate1": "../../element",
                "coordinate2": "1...N",
                "coordinate2_same_as": "../tensor_covariant",
                "coordinate3": "1...N",
                "coordinate3_same_as": "../tensor_covariant",
            },
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class GenericGridDynamicGridSubsetElement(IdsBaseClass):
    """

    :ivar object : Set of objects defining the element
    """

    class Meta:
        name = "generic_grid_dynamic_grid_subset_element"
        is_root_ids = False

    object: Optional[GenericGridDynamicGridSubsetElementObject] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridDynamicGridSubsetElementObject
        ),
        metadata={
            "imas_type": "generic_grid_dynamic_grid_subset_element_object",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridDynamicGridSubsetElementObject,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class GenericGridDynamicSpaceDimension(IdsBaseClass):
    """

    :ivar object : Set of objects for a given dimension
    :ivar geometry_content : Content of the ../object/geometry node for this dimension
    """

    class Meta:
        name = "generic_grid_dynamic_space_dimension"
        is_root_ids = False

    object: Optional[GenericGridDynamicSpaceDimensionObject] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridDynamicSpaceDimensionObject
        ),
        metadata={
            "imas_type": "generic_grid_dynamic_space_dimension_object",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridDynamicSpaceDimensionObject,
        },
    )
    geometry_content: Optional[IdentifierDynamicAos3] = field(
        default=None,
        metadata={
            "imas_type": "identifier_dynamic_aos3",
            "field_type": IdentifierDynamicAos3,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class GenericGridDynamicGridSubset(IdsBaseClass):
    """

    :ivar identifier : Grid subset identifier
    :ivar dimension : Space dimension of the grid subset elements, using the convention 1=nodes, 2=edges, 3=faces, 4=cells/volumes
    :ivar element : Set of elements defining the grid subset. An element is defined by a combination of objects from potentially all spaces
    :ivar base : Set of bases for the grid subset. For each base, the structure describes the projection of the base vectors on the canonical frame of the grid.
    :ivar metric : Metric of the canonical frame onto Cartesian coordinates
    """

    class Meta:
        name = "generic_grid_dynamic_grid_subset"
        is_root_ids = False

    identifier: Optional[IdentifierDynamicAos3] = field(
        default=None,
        metadata={
            "imas_type": "identifier_dynamic_aos3",
            "field_type": IdentifierDynamicAos3,
        },
    )
    dimension: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    element: Optional[GenericGridDynamicGridSubsetElement] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridDynamicGridSubsetElement
        ),
        metadata={
            "imas_type": "generic_grid_dynamic_grid_subset_element",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridDynamicGridSubsetElement,
        },
    )
    base: Optional[GenericGridDynamicGridSubsetMetric] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridDynamicGridSubsetMetric
        ),
        metadata={
            "imas_type": "generic_grid_dynamic_grid_subset_metric",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridDynamicGridSubsetMetric,
        },
    )
    metric: Optional[GenericGridDynamicGridSubsetMetric] = field(
        default=None,
        metadata={
            "imas_type": "generic_grid_dynamic_grid_subset_metric",
            "field_type": GenericGridDynamicGridSubsetMetric,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WavesCpx1D(IdsBaseClass):
    """

    :ivar real : Real part
    :ivar imaginary : Imaginary part
    """

    class Meta:
        name = "waves_CPX_1D"
        is_root_ids = False

    real: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../length"},
            "field_type": np.ndarray,
        },
    )
    imaginary: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../length"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class GenericGridDynamicSpace(IdsBaseClass):
    """

    :ivar identifier : Space identifier
    :ivar geometry_type : Type of space geometry (0: standard, 1:Fourier, &gt;1: Fourier with periodicity)
    :ivar coordinates_type : Type of coordinates describing the physical space, for every coordinate of the space. The size of this node therefore defines the dimension of the space.
    :ivar objects_per_dimension : Definition of the space objects for every dimension (from one to the dimension of the highest-dimensional objects). The index correspond to 1=nodes, 2=edges, 3=faces, 4=cells/volumes, .... For every index, a collection of objects of that dimension is described.
    """

    class Meta:
        name = "generic_grid_dynamic_space"
        is_root_ids = False

    identifier: Optional[IdentifierDynamicAos3] = field(
        default=None,
        metadata={
            "imas_type": "identifier_dynamic_aos3",
            "field_type": IdentifierDynamicAos3,
        },
    )
    geometry_type: Optional[IdentifierDynamicAos3] = field(
        default=None,
        metadata={
            "imas_type": "identifier_dynamic_aos3",
            "field_type": IdentifierDynamicAos3,
        },
    )
    coordinates_type: Optional[IdentifierDynamicAos3] = field(
        default_factory=lambda: StructArray(type_input=IdentifierDynamicAos3),
        metadata={
            "imas_type": "identifier_dynamic_aos3",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": IdentifierDynamicAos3,
        },
    )
    objects_per_dimension: Optional[GenericGridDynamicSpaceDimension] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridDynamicSpaceDimension
        ),
        metadata={
            "imas_type": "generic_grid_dynamic_space_dimension",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridDynamicSpaceDimension,
        },
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
class WavesCoherentWaveIdentifier(IdsBaseClass):
    """

    :ivar antenna_name : Name of the antenna that launches this wave. Corresponds to the name specified in antennas/ec(i)/name, or antennas/ic(i)/name or antennas/lh(i)/name (depends of antenna/wave type) in the ANTENNAS IDS.
    :ivar index_in_antenna : Index of the wave (starts at 1), separating different waves generated from a single antenna.
    """

    class Meta:
        name = "waves_coherent_wave_identifier"
        is_root_ids = False

    antenna_name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    index_in_antenna: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
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
class WavesBeamTracingBeamK(IdsBaseClass):
    """

    :ivar k_r : Wave vector component in the major radius direction
    :ivar k_z : Wave vector component in the vertical direction
    :ivar k_phi : Wave vector component in the toroidal direction
    :ivar k_r_norm : Normalized wave vector component in the major radius direction = k_r / norm(k)
    :ivar k_z_norm : Normalized wave vector component in the vertical direction = k_z / norm(k)
    :ivar k_phi_norm : Normalized wave vector component in the toroidal direction = k_phi / norm(k)
    :ivar n_parallel : Parallel refractive index
    :ivar n_perpendicular : Perpendicular refractive index
    :ivar n_phi : Toroidal wave number, contains a single value if varying_n_phi = 0 to avoid useless repetition of constant values. The wave vector toroidal component is defined as k_phi = n_phi grad phi where phi is the toroidal angle so that a positive n_phi means a wave propagating in the positive phi direction
    :ivar varying_n_phi : Flag telling whether n_phi is constant along the ray path (0) or varying (1)
    """

    class Meta:
        name = "waves_beam_tracing_beam_k"
        is_root_ids = False

    k_r: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../length"},
            "field_type": np.ndarray,
        },
    )
    k_z: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../length"},
            "field_type": np.ndarray,
        },
    )
    k_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../length"},
            "field_type": np.ndarray,
        },
    )
    k_r_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../length"},
            "field_type": np.ndarray,
        },
    )
    k_z_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../length"},
            "field_type": np.ndarray,
        },
    )
    k_phi_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../length"},
            "field_type": np.ndarray,
        },
    )
    n_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../length"},
            "field_type": np.ndarray,
        },
    )
    n_perpendicular: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../length"},
            "field_type": np.ndarray,
        },
    )
    n_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=int),
        metadata={
            "imas_type": "INT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../length OR 1...1"},
            "field_type": np.ndarray,
        },
    )
    varying_n_phi: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )


@idspy_dataclass(repr=False, slots=True)
class Rz1DDynamic1(IdsBaseClass):
    """

    :ivar r : Major radius
    :ivar z : Height
    """

    class Meta:
        name = "rz1d_dynamic_1"
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
class GenericGridScalar(IdsBaseClass):
    """

    :ivar grid_index : Index of the grid used to represent this quantity
    :ivar grid_subset_index : Index of the grid subset the data is provided on. Corresponds to the index used in the grid subset definition: grid_subset(:)/identifier/index
    :ivar values : One scalar value is provided per element in the grid subset.
    :ivar coefficients : Interpolation coefficients, to be used for a high precision evaluation of the physical quantity with finite elements, provided per element in the grid subset (first dimension).
    """

    class Meta:
        name = "generic_grid_scalar"
        is_root_ids = False

    grid_index: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    grid_subset_index: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    values: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    coefficients: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {"coordinate1": "../values", "coordinate2": "1...N"},
            "field_type": np.ndarray,
        },
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
class WavesBeamTracingElectrons(IdsBaseClass):
    """

    :ivar power : Power absorbed along the beam by the species
    """

    class Meta:
        name = "waves_beam_tracing_electrons"
        is_root_ids = False

    power: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../length"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WavesRphizpsitheta1DDynamicAos3(IdsBaseClass):
    """

    :ivar r : Major radius
    :ivar z : Height
    :ivar phi : Toroidal angle
    :ivar psi : Poloidal flux
    :ivar rho_tor_norm : Normalised toroidal flux coordinate
    :ivar theta : Poloidal angle (oriented clockwise when viewing the poloidal cross section on the right hand side of the tokamak axis of symmetry, with the origin placed on the plasma magnetic axis)
    """

    class Meta:
        name = "waves_rphizpsitheta1d_dynamic_aos3"
        is_root_ids = False

    r: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../length"},
            "field_type": np.ndarray,
        },
    )
    z: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../length"},
            "field_type": np.ndarray,
        },
    )
    phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../length"},
            "field_type": np.ndarray,
        },
    )
    psi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../length"},
            "field_type": np.ndarray,
        },
    )
    rho_tor_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../length"},
            "field_type": np.ndarray,
        },
    )
    theta: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../length"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WavesBeamPhase(IdsBaseClass):
    """

    :ivar curvature : Inverse curvature radii for the phase ellipse, positive/negative for divergent/convergent beams, in the horizontal direction (first index of the first coordinate) and in the vertical direction (second index of the first coordinate)
    :ivar angle : Rotation angle for the phase ellipse
    """

    class Meta:
        name = "waves_beam_phase"
        is_root_ids = False

    curvature: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "1...2",
                "coordinate2": "../../length",
            },
            "field_type": np.ndarray,
        },
    )
    angle: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../length"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WavesBeamSpot(IdsBaseClass):
    """

    :ivar size : Size of the spot ellipse: distance between the central ray and the peripheral rays in the horizontal (first index of the first coordinate) and vertical direction (second index of the first coordinate)
    :ivar angle : Rotation angle for the spot ellipse
    """

    class Meta:
        name = "waves_beam_spot"
        is_root_ids = False

    size: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "1...2",
                "coordinate2": "../../length",
            },
            "field_type": np.ndarray,
        },
    )
    angle: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../length"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class GenericGridScalarComplex(IdsBaseClass):
    """

    :ivar grid_index : Index of the grid used to represent this quantity
    :ivar grid_subset_index : Index of the grid subset the data is provided on
    :ivar values : One scalar value is provided per element in the grid subset.
    :ivar coefficients : Interpolation coefficients, to be used for a high precision evaluation of the physical quantity with finite elements, provided per element in the grid subset (first dimension).
    """

    class Meta:
        name = "generic_grid_scalar_complex"
        is_root_ids = False

    grid_index: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    grid_subset_index: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    values: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=complex),
        metadata={
            "imas_type": "CPX_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    coefficients: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=complex),
        metadata={
            "imas_type": "CPX_2D",
            "ndims": 2,
            "coordinates": {"coordinate1": "../values", "coordinate2": "1...N"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WavesBeamTracingPowerFlow(IdsBaseClass):
    """

    :ivar perpendicular : Normalized power flow in the direction perpendicular to the magnetic field
    :ivar parallel : Normalized power flow in the direction parallel to the magnetic field
    """

    class Meta:
        name = "waves_beam_tracing_power_flow"
        is_root_ids = False

    perpendicular: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../length"},
            "field_type": np.ndarray,
        },
    )
    parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../length"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class GenericGridDynamic(IdsBaseClass):
    """

    :ivar identifier : Grid identifier
    :ivar path : Path of the grid, including the IDS name, in case of implicit reference to a grid_ggd node described in another IDS. To be filled only if the grid is not described explicitly in this grid_ggd structure. Example syntax: &#39;wall:0/description_ggd(1)/grid_ggd&#39;, means that the grid is located in the wall IDS, occurrence 0, with ids path &#39;description_ggd(1)/grid_ggd&#39;. See the link below for more details about IDS paths
    :ivar space : Set of grid spaces
    :ivar grid_subset : Grid subsets
    """

    class Meta:
        name = "generic_grid_dynamic"
        is_root_ids = False

    identifier: Optional[IdentifierDynamicAos3] = field(
        default=None,
        metadata={
            "imas_type": "identifier_dynamic_aos3",
            "field_type": IdentifierDynamicAos3,
        },
    )
    path: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    space: Optional[GenericGridDynamicSpace] = field(
        default_factory=lambda: StructArray(type_input=GenericGridDynamicSpace),
        metadata={
            "imas_type": "generic_grid_dynamic_space",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridDynamicSpace,
        },
    )
    grid_subset: Optional[GenericGridDynamicGridSubset] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridDynamicGridSubset
        ),
        metadata={
            "imas_type": "generic_grid_dynamic_grid_subset",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridDynamicGridSubset,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WavesBeamTracingBeamEField(IdsBaseClass):
    """

    :ivar plus : Left hand polarised electric field component
    :ivar minus : Right hand polarised electric field component
    :ivar parallel : Parallel to magnetic field polarised electric field component
    """

    class Meta:
        name = "waves_beam_tracing_beam_e_field"
        is_root_ids = False

    plus: Optional[WavesCpx1D] = field(
        default=None,
        metadata={"imas_type": "waves_CPX_1D", "field_type": WavesCpx1D},
    )
    minus: Optional[WavesCpx1D] = field(
        default=None,
        metadata={"imas_type": "waves_CPX_1D", "field_type": WavesCpx1D},
    )
    parallel: Optional[WavesCpx1D] = field(
        default=None,
        metadata={"imas_type": "waves_CPX_1D", "field_type": WavesCpx1D},
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
class WavesCpxAmpPhase1D(IdsBaseClass):
    """

    :ivar amplitude : Amplitude
    :ivar phase : Phase
    """

    class Meta:
        name = "waves_CPX_amp_phase_1D"
        is_root_ids = False

    amplitude: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    phase: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WavesCpxAmpPhase2D(IdsBaseClass):
    """

    :ivar amplitude : Amplitude
    :ivar phase : Phase
    """

    class Meta:
        name = "waves_CPX_amp_phase_2D"
        is_root_ids = False

    amplitude: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 4, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 4,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate2": "1...N",
                "coordinate1_same_as": "../../../grid/r",
                "coordinate2_same_as": "../../../grid/r",
            },
            "field_type": np.ndarray,
        },
    )
    phase: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 4, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 4,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate2": "1...N",
                "coordinate1_same_as": "../../../grid/r",
                "coordinate2_same_as": "../../../grid/r",
            },
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WavesCoherentWaveBeamTracingIonState(IdsBaseClass):
    """

    :ivar z_min : Minimum Z of the charge state bundle (z_min = z_max = 0 for a neutral)
    :ivar z_max : Maximum Z of the charge state bundle (equal to z_min if no bundle)
    :ivar name : String identifying charge state (e.g. C+, C+2 , C+3, C+4, C+5, C+6, ...)
    :ivar electron_configuration : Configuration of atomic orbitals of this state, e.g. 1s2-2s1
    :ivar vibrational_level : Vibrational level (can be bundled)
    :ivar vibrational_mode : Vibrational mode of this state, e.g. &#34;A_g&#34;. Need to define, or adopt a standard nomenclature.
    :ivar power : Power absorbed along the beam by the species
    """

    class Meta:
        name = "waves_coherent_wave_beam_tracing_ion_state"
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
    power: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../length"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WavesCoherentWaveBeamTracingIon(IdsBaseClass):
    """

    :ivar element : List of elements forming the atom or molecule
    :ivar z_ion : Ion charge (of the dominant ionisation state; lumped ions are allowed).
    :ivar name : String identifying the species (e.g. H+, D+, T+, He+2, C+, D2, DT, CD4, ...)
    :ivar power : Power absorbed along the beam by the species
    :ivar multiple_states_flag : Multiple state calculation flag : 0-Only one state is considered; 1-Multiple states are considered and are described in the state structure
    :ivar state : Collisional exchange with the various states of the ion species (ionisation, energy, excitation, ...)
    """

    class Meta:
        name = "waves_coherent_wave_beam_tracing_ion"
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
    power: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../length"},
            "field_type": np.ndarray,
        },
    )
    multiple_states_flag: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    state: Optional[WavesCoherentWaveBeamTracingIonState] = field(
        default_factory=lambda: StructArray(
            type_input=WavesCoherentWaveBeamTracingIonState
        ),
        metadata={
            "imas_type": "waves_coherent_wave_beam_tracing_ion_state",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": WavesCoherentWaveBeamTracingIonState,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WavesCoherentWaveBeamTracingBeam(IdsBaseClass):
    """

    :ivar power_initial : Initial power in the ray/beam
    :ivar length : Ray/beam curvilinear length
    :ivar position : Position of the ray/beam along its path
    :ivar wave_vector : Wave vector of the ray/beam along its path
    :ivar e_field : Electric field polarization of the ray/beam along its path
    :ivar power_flow_norm : Normalized power flow
    :ivar electrons : Quantities related to the electrons
    :ivar ion : Quantities related to the different ion species
    :ivar spot : Spot ellipse characteristics
    :ivar phase : Phase ellipse characteristics
    """

    class Meta:
        name = "waves_coherent_wave_beam_tracing_beam"
        is_root_ids = False

    power_initial: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    length: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    position: Optional[WavesRphizpsitheta1DDynamicAos3] = field(
        default=None,
        metadata={
            "imas_type": "waves_rphizpsitheta1d_dynamic_aos3",
            "field_type": WavesRphizpsitheta1DDynamicAos3,
        },
    )
    wave_vector: Optional[WavesBeamTracingBeamK] = field(
        default=None,
        metadata={
            "imas_type": "waves_beam_tracing_beam_k",
            "field_type": WavesBeamTracingBeamK,
        },
    )
    e_field: Optional[WavesBeamTracingBeamEField] = field(
        default=None,
        metadata={
            "imas_type": "waves_beam_tracing_beam_e_field",
            "field_type": WavesBeamTracingBeamEField,
        },
    )
    power_flow_norm: Optional[WavesBeamTracingPowerFlow] = field(
        default=None,
        metadata={
            "imas_type": "waves_beam_tracing_power_flow",
            "field_type": WavesBeamTracingPowerFlow,
        },
    )
    electrons: Optional[WavesBeamTracingElectrons] = field(
        default=None,
        metadata={
            "imas_type": "waves_beam_tracing_electrons",
            "field_type": WavesBeamTracingElectrons,
        },
    )
    ion: Optional[WavesCoherentWaveBeamTracingIon] = field(
        default_factory=lambda: StructArray(
            type_input=WavesCoherentWaveBeamTracingIon
        ),
        metadata={
            "imas_type": "waves_coherent_wave_beam_tracing_ion",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": WavesCoherentWaveBeamTracingIon,
        },
    )
    spot: Optional[WavesBeamSpot] = field(
        default=None,
        metadata={"imas_type": "waves_beam_spot", "field_type": WavesBeamSpot},
    )
    phase: Optional[WavesBeamPhase] = field(
        default=None,
        metadata={
            "imas_type": "waves_beam_phase",
            "field_type": WavesBeamPhase,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WavesCoherentWaveBeamTracing(IdsBaseClass):
    """

    :ivar beam : Set of rays/beams describing the wave propagation
    :ivar time : Time
    """

    class Meta:
        name = "waves_coherent_wave_beam_tracing"
        is_root_ids = False

    beam: Optional[WavesCoherentWaveBeamTracingBeam] = field(
        default_factory=lambda: StructArray(
            type_input=WavesCoherentWaveBeamTracingBeam
        ),
        metadata={
            "imas_type": "waves_coherent_wave_beam_tracing_beam",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": WavesCoherentWaveBeamTracingBeam,
        },
    )
    time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class WavesCoherentWaveGlobalQuantitiesIonState(IdsBaseClass):
    """

    :ivar z_min : Minimum Z of the charge state bundle (z_min = z_max = 0 for a neutral)
    :ivar z_max : Maximum Z of the charge state bundle (equal to z_min if no bundle)
    :ivar name : String identifying charge state (e.g. C+, C+2 , C+3, C+4, C+5, C+6, ...)
    :ivar electron_configuration : Configuration of atomic orbitals of this state, e.g. 1s2-2s1
    :ivar vibrational_level : Vibrational level (can be bundled)
    :ivar vibrational_mode : Vibrational mode of this state, e.g. &#34;A_g&#34;. Need to define, or adopt a standard nomenclature.
    :ivar power_thermal : Wave power absorbed by the thermal particle population
    :ivar power_thermal_n_phi : Wave power absorbed by the thermal particle population per toroidal mode number
    :ivar power_fast : Wave power absorbed by the fast particle population
    :ivar power_fast_n_phi : Wave power absorbed by the fast particle population per toroidal mode number
    """

    class Meta:
        name = "waves_coherent_wave_global_quantities_ion_state"
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
    power_thermal: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    power_thermal_n_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../n_phi"},
            "field_type": np.ndarray,
        },
    )
    power_fast: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    power_fast_n_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../n_phi"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WavesCoherentWaveGlobalQuantitiesIon(IdsBaseClass):
    """

    :ivar element : List of elements forming the atom or molecule
    :ivar z_ion : Ion charge (of the dominant ionisation state; lumped ions are allowed).
    :ivar name : String identifying the species (e.g. H+, D+, T+, He+2, C+, D2, DT, CD4, ...)
    :ivar power_thermal : Wave power absorbed by the thermal particle population
    :ivar power_thermal_n_phi : Wave power absorbed by the thermal particle population per toroidal mode number
    :ivar power_fast : Wave power absorbed by the fast particle population
    :ivar power_fast_n_phi : Wave power absorbed by the fast particle population per toroidal mode number
    :ivar multiple_states_flag : Multiple state calculation flag : 0-Only one state is considered; 1-Multiple states are considered and are described in the state structure
    :ivar distribution_assumption : Assumption on the distribution function used by the wave solver to calculate the power deposition on this species: 0 = Maxwellian (linear absorption); 1 = quasi-linear (F given by a distributions IDS).
    :ivar state : Collisional exchange with the various states of the ion species (ionisation, energy, excitation, ...)
    """

    class Meta:
        name = "waves_coherent_wave_global_quantities_ion"
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
    power_thermal: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    power_thermal_n_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../n_phi"},
            "field_type": np.ndarray,
        },
    )
    power_fast: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    power_fast_n_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../n_phi"},
            "field_type": np.ndarray,
        },
    )
    multiple_states_flag: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    distribution_assumption: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    state: Optional[WavesCoherentWaveGlobalQuantitiesIonState] = field(
        default_factory=lambda: StructArray(
            type_input=WavesCoherentWaveGlobalQuantitiesIonState
        ),
        metadata={
            "imas_type": "waves_coherent_wave_global_quantities_ion_state",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": WavesCoherentWaveGlobalQuantitiesIonState,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WavesCoherentWaveGlobalQuantitiesElectrons(IdsBaseClass):
    """

    :ivar power_thermal : Wave power absorbed by the thermal particle population
    :ivar power_thermal_n_phi : Wave power absorbed by the thermal particle population per toroidal mode number
    :ivar power_fast : Wave power absorbed by the fast particle population
    :ivar power_fast_n_phi : Wave power absorbed by the fast particle population per toroidal mode number
    :ivar distribution_assumption : Assumption on the distribution function used by the wave solver to calculate the power deposition on this species: 0 = Maxwellian (linear absorption); 1 = quasi-linear (F given by a distributions IDS).
    """

    class Meta:
        name = "waves_coherent_wave_global_quantities_electrons"
        is_root_ids = False

    power_thermal: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    power_thermal_n_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../n_phi"},
            "field_type": np.ndarray,
        },
    )
    power_fast: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    power_fast_n_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../n_phi"},
            "field_type": np.ndarray,
        },
    )
    distribution_assumption: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )


@idspy_dataclass(repr=False, slots=True)
class WavesCoherentWaveGlobalQuantities(IdsBaseClass):
    """

    :ivar frequency : Wave frequency
    :ivar n_phi : Toroidal mode numbers, the wave vector toroidal component being defined as k_tor = n_tor grad phi where phi is the toroidal angle so that a positive n_tor means a wave propagating in the positive phi direction
    :ivar power : Total absorbed wave power
    :ivar power_n_phi : Absorbed wave power per toroidal mode number
    :ivar current_phi : Wave driven toroidal current from a stand alone calculation (not consistent with other sources)
    :ivar current_phi_n_phi : Wave driven toroidal current from a stand alone calculation (not consistent with other sources) per toroidal mode number
    :ivar electrons : Quantities related to the electrons
    :ivar ion : Quantities related to the different ion species
    :ivar time : Time
    """

    class Meta:
        name = "waves_coherent_wave_global_quantities"
        is_root_ids = False

    frequency: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    n_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=int),
        metadata={
            "imas_type": "INT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    power: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    power_n_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../n_phi"},
            "field_type": np.ndarray,
        },
    )
    current_phi: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    current_phi_n_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../n_phi"},
            "field_type": np.ndarray,
        },
    )
    electrons: Optional[WavesCoherentWaveGlobalQuantitiesElectrons] = field(
        default=None,
        metadata={
            "imas_type": "waves_coherent_wave_global_quantities_electrons",
            "field_type": WavesCoherentWaveGlobalQuantitiesElectrons,
        },
    )
    ion: Optional[WavesCoherentWaveGlobalQuantitiesIon] = field(
        default_factory=lambda: StructArray(
            type_input=WavesCoherentWaveGlobalQuantitiesIon
        ),
        metadata={
            "imas_type": "waves_coherent_wave_global_quantities_ion",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": WavesCoherentWaveGlobalQuantitiesIon,
        },
    )
    time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class WavesCoherentWaveProfiles1DIonState(IdsBaseClass):
    """

    :ivar z_min : Minimum Z of the charge state bundle (z_min = z_max = 0 for a neutral)
    :ivar z_max : Maximum Z of the charge state bundle (equal to z_min if no bundle)
    :ivar name : String identifying charge state (e.g. C+, C+2 , C+3, C+4, C+5, C+6, ...)
    :ivar electron_configuration : Configuration of atomic orbitals of this state, e.g. 1s2-2s1
    :ivar vibrational_level : Vibrational level (can be bundled)
    :ivar vibrational_mode : Vibrational mode of this state, e.g. &#34;A_g&#34;. Need to define, or adopt a standard nomenclature.
    :ivar power_density_thermal : Flux surface averaged absorbed wave power density on the thermal species
    :ivar power_density_thermal_n_phi : Flux surface averaged absorbed wave power density on the thermal species, per toroidal mode number
    :ivar power_density_fast : Flux surface averaged absorbed wave power density on the fast species
    :ivar power_density_fast_n_phi : Flux surface averaged absorbed wave power density on the fast species, per toroidal mode number
    :ivar power_inside_thermal : Absorbed wave power on thermal species inside a flux surface (cumulative volume integral of the absorbed power density)
    :ivar power_inside_thermal_n_phi : Absorbed wave power on thermal species inside a flux surface (cumulative volume integral of the absorbed power density), per toroidal mode number
    :ivar power_inside_fast : Absorbed wave power on thermal species inside a flux surface (cumulative volume integral of the absorbed power density)
    :ivar power_inside_fast_n_phi : Absorbed wave power on thermal species inside a flux surface (cumulative volume integral of the absorbed power density), per toroidal mode number
    """

    class Meta:
        name = "waves_coherent_wave_profiles_1d_ion_state"
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
    power_density_thermal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    power_density_thermal_n_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../../grid/rho_tor_norm",
                "coordinate2": "../../../n_phi",
            },
            "field_type": np.ndarray,
        },
    )
    power_density_fast: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    power_density_fast_n_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../../grid/rho_tor_norm",
                "coordinate2": "../../../n_phi",
            },
            "field_type": np.ndarray,
        },
    )
    power_inside_thermal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    power_inside_thermal_n_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../../grid/rho_tor_norm",
                "coordinate2": "../../../n_phi",
            },
            "field_type": np.ndarray,
        },
    )
    power_inside_fast: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    power_inside_fast_n_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../../grid/rho_tor_norm",
                "coordinate2": "../../../n_phi",
            },
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WavesCoherentWaveProfiles1DIon(IdsBaseClass):
    """

    :ivar element : List of elements forming the atom or molecule
    :ivar z_ion : Ion charge (of the dominant ionisation state; lumped ions are allowed).
    :ivar name : String identifying the species (e.g. H+, D+, T+, He+2, C+, D2, DT, CD4, ...)
    :ivar power_density_thermal : Flux surface averaged absorbed wave power density on the thermal species
    :ivar power_density_thermal_n_phi : Flux surface averaged absorbed wave power density on the thermal species, per toroidal mode number
    :ivar power_density_fast : Flux surface averaged absorbed wave power density on the fast species
    :ivar power_density_fast_n_phi : Flux surface averaged absorbed wave power density on the fast species, per toroidal mode number
    :ivar power_inside_thermal : Absorbed wave power on thermal species inside a flux surface (cumulative volume integral of the absorbed power density)
    :ivar power_inside_thermal_n_phi : Absorbed wave power on thermal species inside a flux surface (cumulative volume integral of the absorbed power density), per toroidal mode number
    :ivar power_inside_fast : Absorbed wave power on thermal species inside a flux surface (cumulative volume integral of the absorbed power density)
    :ivar power_inside_fast_n_phi : Absorbed wave power on thermal species inside a flux surface (cumulative volume integral of the absorbed power density), per toroidal mode number
    :ivar multiple_states_flag : Multiple state calculation flag : 0-Only one state is considered; 1-Multiple states are considered and are described in the state structure
    :ivar state : Collisional exchange with the various states of the ion species (ionisation, energy, excitation, ...)
    """

    class Meta:
        name = "waves_coherent_wave_profiles_1d_ion"
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
    power_density_thermal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    power_density_thermal_n_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../grid/rho_tor_norm",
                "coordinate2": "../../n_phi",
            },
            "field_type": np.ndarray,
        },
    )
    power_density_fast: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    power_density_fast_n_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../grid/rho_tor_norm",
                "coordinate2": "../../n_phi",
            },
            "field_type": np.ndarray,
        },
    )
    power_inside_thermal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    power_inside_thermal_n_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../grid/rho_tor_norm",
                "coordinate2": "../../n_phi",
            },
            "field_type": np.ndarray,
        },
    )
    power_inside_fast: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    power_inside_fast_n_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../grid/rho_tor_norm",
                "coordinate2": "../../n_phi",
            },
            "field_type": np.ndarray,
        },
    )
    multiple_states_flag: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    state: Optional[WavesCoherentWaveProfiles1DIonState] = field(
        default_factory=lambda: StructArray(
            type_input=WavesCoherentWaveProfiles1DIonState
        ),
        metadata={
            "imas_type": "waves_coherent_wave_profiles_1d_ion_state",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": WavesCoherentWaveProfiles1DIonState,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WavesCoherentWaveProfiles1DElectrons(IdsBaseClass):
    """

    :ivar power_density_thermal : Flux surface averaged absorbed wave power density on the thermal species
    :ivar power_density_thermal_n_phi : Flux surface averaged absorbed wave power density on the thermal species, per toroidal mode number
    :ivar power_density_fast : Flux surface averaged absorbed wave power density on the fast species
    :ivar power_density_fast_n_phi : Flux surface averaged absorbed wave power density on the fast species, per toroidal mode number
    :ivar power_inside_thermal : Absorbed wave power on thermal species inside a flux surface (cumulative volume integral of the absorbed power density)
    :ivar power_inside_thermal_n_phi : Absorbed wave power on thermal species inside a flux surface (cumulative volume integral of the absorbed power density), per toroidal mode number
    :ivar power_inside_fast : Absorbed wave power on thermal species inside a flux surface (cumulative volume integral of the absorbed power density)
    :ivar power_inside_fast_n_phi : Absorbed wave power on thermal species inside a flux surface (cumulative volume integral of the absorbed power density), per toroidal mode number
    """

    class Meta:
        name = "waves_coherent_wave_profiles_1d_electrons"
        is_root_ids = False

    power_density_thermal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    power_density_thermal_n_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../grid/rho_tor_norm",
                "coordinate2": "../../n_phi",
            },
            "field_type": np.ndarray,
        },
    )
    power_density_fast: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    power_density_fast_n_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../grid/rho_tor_norm",
                "coordinate2": "../../n_phi",
            },
            "field_type": np.ndarray,
        },
    )
    power_inside_thermal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    power_inside_thermal_n_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../grid/rho_tor_norm",
                "coordinate2": "../../n_phi",
            },
            "field_type": np.ndarray,
        },
    )
    power_inside_fast: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    power_inside_fast_n_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../grid/rho_tor_norm",
                "coordinate2": "../../n_phi",
            },
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WavesProfiles1DEFieldNPhi(IdsBaseClass):
    """

    :ivar plus : Left hand polarized electric field component for every flux surface
    :ivar minus : Right hand polarized electric field component for every flux surface
    :ivar parallel : Parallel electric field component for every flux surface
    """

    class Meta:
        name = "waves_profiles_1d_e_field_n_phi"
        is_root_ids = False

    plus: Optional[WavesCpxAmpPhase1D] = field(
        default=None,
        metadata={
            "imas_type": "waves_CPX_amp_phase_1D",
            "field_type": WavesCpxAmpPhase1D,
        },
    )
    minus: Optional[WavesCpxAmpPhase1D] = field(
        default=None,
        metadata={
            "imas_type": "waves_CPX_amp_phase_1D",
            "field_type": WavesCpxAmpPhase1D,
        },
    )
    parallel: Optional[WavesCpxAmpPhase1D] = field(
        default=None,
        metadata={
            "imas_type": "waves_CPX_amp_phase_1D",
            "field_type": WavesCpxAmpPhase1D,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WavesCoherentWaveProfiles1D(IdsBaseClass):
    """

    :ivar grid : Radial grid
    :ivar n_phi : Toroidal mode numbers, the wave vector toroidal component being defined as k_phi = n_phi grad phi where phi is the toroidal angle so that a positive n_phi means a wave propagating in the positive phi direction
    :ivar power_density : Flux surface averaged total absorbed wave power density (electrons + ion + fast populations)
    :ivar power_density_n_phi : Flux surface averaged absorbed wave power density per toroidal mode number
    :ivar power_inside : Total absorbed wave power (electrons + ion + fast populations) inside a flux surface (cumulative volume integral of the absorbed power density)
    :ivar power_inside_n_phi : Total absorbed wave power (electrons + ion + fast populations) inside a flux surface (cumulative volume integral of the absorbed power density), per toroidal mode number
    :ivar current_phi_inside : Wave driven toroidal current, inside a flux surface
    :ivar current_phi_inside_n_phi : Wave driven toroidal current, inside a flux surface, per toroidal mode number
    :ivar current_parallel_density : Flux surface averaged wave driven parallel current density = average(j.B) / B0, where B0 = vacuum_toroidal_field/b0.
    :ivar current_parallel_density_n_phi : Flux surface averaged wave driven parallel current density, per toroidal mode number
    :ivar e_field_n_phi : Components of the electric field per toroidal mode number, averaged over the flux surface, where the averaged is weighted with the power deposition density, such that e_field = ave(e_field.power_density) / ave(power_density)
    :ivar k_perpendicular : Perpendicular wave vector,  averaged over the flux surface, where the averaged is weighted with the power deposition density, such that k_perpendicular = ave(k_perpendicular.power_density) / ave(power_density), for every flux surface and every toroidal number
    :ivar electrons : Quantities related to the electrons
    :ivar ion : Quantities related to the different ion species
    :ivar time : Time
    """

    class Meta:
        name = "waves_coherent_wave_profiles_1d"
        is_root_ids = False

    grid: Optional[CoreRadialGrid] = field(
        default=None,
        metadata={
            "imas_type": "core_radial_grid",
            "field_type": CoreRadialGrid,
        },
    )
    n_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=int),
        metadata={
            "imas_type": "INT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    power_density: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    power_density_n_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../grid/rho_tor_norm",
                "coordinate2": "../n_phi",
            },
            "field_type": np.ndarray,
        },
    )
    power_inside: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    power_inside_n_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../grid/rho_tor_norm",
                "coordinate2": "../n_phi",
            },
            "field_type": np.ndarray,
        },
    )
    current_phi_inside: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    current_phi_inside_n_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../grid/rho_tor_norm",
                "coordinate2": "../n_phi",
            },
            "field_type": np.ndarray,
        },
    )
    current_parallel_density: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    current_parallel_density_n_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../grid/rho_tor_norm",
                "coordinate2": "../n_phi",
            },
            "field_type": np.ndarray,
        },
    )
    e_field_n_phi: Optional[WavesProfiles1DEFieldNPhi] = field(
        default_factory=lambda: StructArray(
            type_input=WavesProfiles1DEFieldNPhi
        ),
        metadata={
            "imas_type": "waves_profiles_1d_e_field_n_phi",
            "ndims": 1,
            "coordinates": {"coordinate1": "../n_phi"},
            "field_type": WavesProfiles1DEFieldNPhi,
        },
    )
    k_perpendicular: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../grid/rho_tor_norm",
                "coordinate2": "../n_phi",
            },
            "field_type": np.ndarray,
        },
    )
    electrons: Optional[WavesCoherentWaveProfiles1DElectrons] = field(
        default=None,
        metadata={
            "imas_type": "waves_coherent_wave_profiles_1d_electrons",
            "field_type": WavesCoherentWaveProfiles1DElectrons,
        },
    )
    ion: Optional[WavesCoherentWaveProfiles1DIon] = field(
        default_factory=lambda: StructArray(
            type_input=WavesCoherentWaveProfiles1DIon
        ),
        metadata={
            "imas_type": "waves_coherent_wave_profiles_1d_ion",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": WavesCoherentWaveProfiles1DIon,
        },
    )
    time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class WavesCoherentWaveFullWaveEField(IdsBaseClass):
    """

    :ivar plus : Left hand circularly polarized component of the perpendicular (to the static magnetic field) electric field, given on various grid subsets
    :ivar minus : Right hand circularly polarized component of the perpendicular (to the static magnetic field) electric field, given on various grid subsets
    :ivar parallel : Parallel (to the static magnetic field) component of electric field, given on various grid subsets
    :ivar normal : Magnitude of wave electric field normal to a flux surface, given on various grid subsets
    :ivar bi_normal : Magnitude of perpendicular (to the static magnetic field) wave electric field tangent to a flux surface, given on various grid subsets
    """

    class Meta:
        name = "waves_coherent_wave_full_wave_e_field"
        is_root_ids = False

    plus: Optional[GenericGridScalarComplex] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridScalarComplex
        ),
        metadata={
            "imas_type": "generic_grid_scalar_complex",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalarComplex,
        },
    )
    minus: Optional[GenericGridScalarComplex] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridScalarComplex
        ),
        metadata={
            "imas_type": "generic_grid_scalar_complex",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalarComplex,
        },
    )
    parallel: Optional[GenericGridScalarComplex] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridScalarComplex
        ),
        metadata={
            "imas_type": "generic_grid_scalar_complex",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalarComplex,
        },
    )
    normal: Optional[GenericGridScalarComplex] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridScalarComplex
        ),
        metadata={
            "imas_type": "generic_grid_scalar_complex",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalarComplex,
        },
    )
    bi_normal: Optional[GenericGridScalarComplex] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridScalarComplex
        ),
        metadata={
            "imas_type": "generic_grid_scalar_complex",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalarComplex,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WavesCoherentWaveFullWaveBField(IdsBaseClass):
    """

    :ivar parallel : Parallel (to the static magnetic field) component of the wave magnetic field, given on various grid subsets
    :ivar normal : Magnitude of wave magnetic field normal to a flux surface, given on various grid subsets
    :ivar bi_normal : Magnitude of perpendicular (to the static magnetic field) wave magnetic field tangent to a flux surface, given on various grid subsets
    """

    class Meta:
        name = "waves_coherent_wave_full_wave_b_field"
        is_root_ids = False

    parallel: Optional[GenericGridScalarComplex] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridScalarComplex
        ),
        metadata={
            "imas_type": "generic_grid_scalar_complex",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalarComplex,
        },
    )
    normal: Optional[GenericGridScalarComplex] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridScalarComplex
        ),
        metadata={
            "imas_type": "generic_grid_scalar_complex",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalarComplex,
        },
    )
    bi_normal: Optional[GenericGridScalarComplex] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridScalarComplex
        ),
        metadata={
            "imas_type": "generic_grid_scalar_complex",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalarComplex,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WavesCoherentWaveFullWave(IdsBaseClass):
    """

    :ivar grid : Grid description
    :ivar e_field : Components of the wave electric field, represented as Fourier coefficients E(n_tor,frequency) such that the electric is equal to real(E(n_tor,frequency).exp(i(n_tor.phi - 2.pi.frequency.t)))
    :ivar b_field : Components of the wave magnetic field, , represented as Fourier coefficients B(n_tor,frequency) such that the electric is equal to real(B(n_tor,frequency).exp(i(n_tor.phi - 2.pi.frequency.t)))
    :ivar k_perpendicular : Perpendicular wave vector, given on various grid subsets
    :ivar time : Time
    """

    class Meta:
        name = "waves_coherent_wave_full_wave"
        is_root_ids = False

    grid: Optional[GenericGridDynamic] = field(
        default=None,
        metadata={
            "imas_type": "generic_grid_dynamic",
            "field_type": GenericGridDynamic,
        },
    )
    e_field: Optional[WavesCoherentWaveFullWaveEField] = field(
        default=None,
        metadata={
            "imas_type": "waves_coherent_wave_full_wave_e_field",
            "field_type": WavesCoherentWaveFullWaveEField,
        },
    )
    b_field: Optional[WavesCoherentWaveFullWaveBField] = field(
        default=None,
        metadata={
            "imas_type": "waves_coherent_wave_full_wave_b_field",
            "field_type": WavesCoherentWaveFullWaveBField,
        },
    )
    k_perpendicular: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class WavesCoherentWaveProfiles2DGrid(IdsBaseClass):
    """

    :ivar type : Grid type: index=0: Rectangular grid in the (R,Z) coordinates; index=1: Rectangular grid in the (radial, theta_geometric) coordinates; index=2: Rectangular grid in the (radial, theta_straight) coordinates. index=3: unstructured grid.
    :ivar r : Major radius
    :ivar z : Height
    :ivar theta_straight : Straight field line poloidal angle
    :ivar theta_geometric : Geometrical poloidal angle
    :ivar rho_tor_norm : Normalized toroidal flux coordinate. The normalizing value for rho_tor_norm, is the toroidal flux coordinate at the equilibrium boundary (LCFS or 99.x % of the LCFS in case of a fixed boundary equilibium calculation)
    :ivar rho_tor : Toroidal flux coordinate. The toroidal field used in its definition is indicated under vacuum_toroidal_field/b0
    :ivar psi : Poloidal magnetic flux
    :ivar volume : Volume enclosed inside the magnetic surface
    :ivar area : Cross-sectional area of the flux surface
    """

    class Meta:
        name = "waves_coherent_wave_profiles_2d_grid"
        is_root_ids = False

    type: Optional[IdentifierDynamicAos3] = field(
        default=None,
        metadata={
            "imas_type": "identifier_dynamic_aos3",
            "field_type": IdentifierDynamicAos3,
        },
    )
    r: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {"coordinate1": "1...N", "coordinate2": "1...N"},
            "field_type": np.ndarray,
        },
    )
    z: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 4, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 4,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate2": "1...N",
                "coordinate1_same_as": "../r",
                "coordinate2_same_as": "../r",
            },
            "field_type": np.ndarray,
        },
    )
    theta_straight: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 4, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 4,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate2": "1...N",
                "coordinate1_same_as": "../r",
                "coordinate2_same_as": "../r",
            },
            "field_type": np.ndarray,
        },
    )
    theta_geometric: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 4, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 4,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate2": "1...N",
                "coordinate1_same_as": "../r",
                "coordinate2_same_as": "../r",
            },
            "field_type": np.ndarray,
        },
    )
    rho_tor_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 4, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 4,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate2": "1...N",
                "coordinate1_same_as": "../r",
                "coordinate2_same_as": "../r",
            },
            "field_type": np.ndarray,
        },
    )
    rho_tor: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 4, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 4,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate2": "1...N",
                "coordinate1_same_as": "../r",
                "coordinate2_same_as": "../r",
            },
            "field_type": np.ndarray,
        },
    )
    psi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 4, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 4,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate2": "1...N",
                "coordinate1_same_as": "../r",
                "coordinate2_same_as": "../r",
            },
            "field_type": np.ndarray,
        },
    )
    volume: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 4, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 4,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate2": "1...N",
                "coordinate1_same_as": "../r",
                "coordinate2_same_as": "../r",
            },
            "field_type": np.ndarray,
        },
    )
    area: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 4, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 4,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate2": "1...N",
                "coordinate1_same_as": "../r",
                "coordinate2_same_as": "../r",
            },
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WavesCoherentWaveProfiles2DIonState(IdsBaseClass):
    """

    :ivar z_min : Minimum Z of the charge state bundle (z_min = z_max = 0 for a neutral)
    :ivar z_max : Maximum Z of the charge state bundle (equal to z_min if no bundle)
    :ivar name : String identifying charge state (e.g. C+, C+2 , C+3, C+4, C+5, C+6, ...)
    :ivar electron_configuration : Configuration of atomic orbitals of this state, e.g. 1s2-2s1
    :ivar vibrational_level : Vibrational level (can be bundled)
    :ivar vibrational_mode : Vibrational mode of this state, e.g. &#34;A_g&#34;. Need to define, or adopt a standard nomenclature.
    :ivar power_density_thermal : Absorbed wave power density on the thermal species
    :ivar power_density_thermal_n_phi : Absorbed wave power density on the thermal species, per toroidal mode number
    :ivar power_density_fast : Absorbed wave power density on the fast species
    :ivar power_density_fast_n_phi : Absorbed wave power density on the fast species, per toroidal mode number
    """

    class Meta:
        name = "waves_coherent_wave_profiles_2d_ion_state"
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
    power_density_thermal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 4, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 4,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate2": "1...N",
                "coordinate1_same_as": "../../../grid/r",
                "coordinate2_same_as": "../../../grid/r",
            },
            "field_type": np.ndarray,
        },
    )
    power_density_thermal_n_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 5, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 5,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate2": "1...N",
                "coordinate1_same_as": "../../../grid/r",
                "coordinate2_same_as": "../../../grid/r",
                "coordinate3": "../../../n_phi",
            },
            "field_type": np.ndarray,
        },
    )
    power_density_fast: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 4, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 4,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate2": "1...N",
                "coordinate1_same_as": "../../../grid/r",
                "coordinate2_same_as": "../../../grid/r",
            },
            "field_type": np.ndarray,
        },
    )
    power_density_fast_n_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 5, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 5,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate2": "1...N",
                "coordinate1_same_as": "../../../grid/r",
                "coordinate2_same_as": "../../../grid/r",
                "coordinate3": "../../../n_phi",
            },
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WavesCoherentWaveProfiles2DIon(IdsBaseClass):
    """

    :ivar element : List of elements forming the atom or molecule
    :ivar z_ion : Ion charge (of the dominant ionisation state; lumped ions are allowed).
    :ivar name : String identifying the species (e.g. H+, D+, T+, He+2, C+, D2, DT, CD4, ...)
    :ivar power_density_thermal : Absorbed wave power density on the thermal species
    :ivar power_density_thermal_n_phi : Absorbed wave power density on the thermal species, per toroidal mode number
    :ivar power_density_fast : Absorbed wave power density on the fast species
    :ivar power_density_fast_n_phi : Absorbed wave power density on the fast species, per toroidal mode number
    :ivar multiple_states_flag : Multiple state calculation flag : 0-Only one state is considered; 1-Multiple states are considered and are described in the state structure
    :ivar state : Collisional exchange with the various states of the ion species (ionisation, energy, excitation, ...)
    """

    class Meta:
        name = "waves_coherent_wave_profiles_2d_ion"
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
    power_density_thermal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 4, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 4,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate2": "1...N",
                "coordinate1_same_as": "../../grid/r",
                "coordinate2_same_as": "../../grid/r",
            },
            "field_type": np.ndarray,
        },
    )
    power_density_thermal_n_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 5, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 5,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate2": "1...N",
                "coordinate1_same_as": "../../grid/r",
                "coordinate2_same_as": "../../grid/r",
                "coordinate3": "../../n_phi",
            },
            "field_type": np.ndarray,
        },
    )
    power_density_fast: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 4, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 4,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate2": "1...N",
                "coordinate1_same_as": "../../grid/r",
                "coordinate2_same_as": "../../grid/r",
            },
            "field_type": np.ndarray,
        },
    )
    power_density_fast_n_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 5, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 5,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate2": "1...N",
                "coordinate1_same_as": "../../grid/r",
                "coordinate2_same_as": "../../grid/r",
                "coordinate3": "../../n_phi",
            },
            "field_type": np.ndarray,
        },
    )
    multiple_states_flag: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    state: Optional[WavesCoherentWaveProfiles2DIonState] = field(
        default_factory=lambda: StructArray(
            type_input=WavesCoherentWaveProfiles2DIonState
        ),
        metadata={
            "imas_type": "waves_coherent_wave_profiles_2d_ion_state",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": WavesCoherentWaveProfiles2DIonState,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WavesCoherentWaveProfiles2DElectrons(IdsBaseClass):
    """

    :ivar power_density_thermal : Absorbed wave power density on the thermal species
    :ivar power_density_thermal_n_phi : Absorbed wave power density on the thermal species, per toroidal mode number
    :ivar power_density_fast : Absorbed wave power density on the fast species
    :ivar power_density_fast_n_phi : Absorbed wave power density on the fast species, per toroidal mode number
    """

    class Meta:
        name = "waves_coherent_wave_profiles_2d_electrons"
        is_root_ids = False

    power_density_thermal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 4, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 4,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate2": "1...N",
                "coordinate1_same_as": "../../grid/r",
                "coordinate2_same_as": "../../grid/r",
            },
            "field_type": np.ndarray,
        },
    )
    power_density_thermal_n_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 5, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 5,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate2": "1...N",
                "coordinate1_same_as": "../../grid/r",
                "coordinate2_same_as": "../../grid/r",
                "coordinate3": "../../n_phi",
            },
            "field_type": np.ndarray,
        },
    )
    power_density_fast: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 4, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 4,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate2": "1...N",
                "coordinate1_same_as": "../../grid/r",
                "coordinate2_same_as": "../../grid/r",
            },
            "field_type": np.ndarray,
        },
    )
    power_density_fast_n_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 5, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 5,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate2": "1...N",
                "coordinate1_same_as": "../../grid/r",
                "coordinate2_same_as": "../../grid/r",
                "coordinate3": "../../n_phi",
            },
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WavesProfiles2DEFieldNPhi(IdsBaseClass):
    """

    :ivar plus : Left hand polarized electric field component
    :ivar minus : Right hand polarized electric field component
    :ivar parallel : Parallel electric field component
    """

    class Meta:
        name = "waves_profiles_2d_e_field_n_phi"
        is_root_ids = False

    plus: Optional[WavesCpxAmpPhase2D] = field(
        default=None,
        metadata={
            "imas_type": "waves_CPX_amp_phase_2D",
            "field_type": WavesCpxAmpPhase2D,
        },
    )
    minus: Optional[WavesCpxAmpPhase2D] = field(
        default=None,
        metadata={
            "imas_type": "waves_CPX_amp_phase_2D",
            "field_type": WavesCpxAmpPhase2D,
        },
    )
    parallel: Optional[WavesCpxAmpPhase2D] = field(
        default=None,
        metadata={
            "imas_type": "waves_CPX_amp_phase_2D",
            "field_type": WavesCpxAmpPhase2D,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WavesCoherentWaveProfiles2D(IdsBaseClass):
    """

    :ivar grid : 2D grid in a poloidal cross-section
    :ivar n_phi : Toroidal mode numbers, the wave vector toroidal component being defined as k_phi = n_phi grad phi where phi is the toroidal angle so that a positive n_phi means a wave propagating in the positive phi direction
    :ivar power_density : Total absorbed wave power density (electrons + ion + fast populations)
    :ivar power_density_n_phi : Absorbed wave power density per toroidal mode number
    :ivar e_field_n_phi : Components of the electric field per toroidal mode number
    :ivar electrons : Quantities related to the electrons
    :ivar ion : Quantities related to the different ion species
    :ivar time : Time
    """

    class Meta:
        name = "waves_coherent_wave_profiles_2d"
        is_root_ids = False

    grid: Optional[WavesCoherentWaveProfiles2DGrid] = field(
        default=None,
        metadata={
            "imas_type": "waves_coherent_wave_profiles_2d_grid",
            "field_type": WavesCoherentWaveProfiles2DGrid,
        },
    )
    n_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=int),
        metadata={
            "imas_type": "INT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    power_density: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 4, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 4,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate2": "1...N",
                "coordinate1_same_as": "../grid/r",
                "coordinate2_same_as": "../grid/r",
            },
            "field_type": np.ndarray,
        },
    )
    power_density_n_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 5, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 5,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate2": "1...N",
                "coordinate1_same_as": "../grid/r",
                "coordinate2_same_as": "../grid/r",
                "coordinate3": "../n_phi",
            },
            "field_type": np.ndarray,
        },
    )
    e_field_n_phi: Optional[WavesProfiles2DEFieldNPhi] = field(
        default_factory=lambda: StructArray(
            type_input=WavesProfiles2DEFieldNPhi
        ),
        metadata={
            "imas_type": "waves_profiles_2d_e_field_n_phi",
            "ndims": 1,
            "coordinates": {"coordinate1": "../n_phi"},
            "field_type": WavesProfiles2DEFieldNPhi,
        },
    )
    electrons: Optional[WavesCoherentWaveProfiles2DElectrons] = field(
        default=None,
        metadata={
            "imas_type": "waves_coherent_wave_profiles_2d_electrons",
            "field_type": WavesCoherentWaveProfiles2DElectrons,
        },
    )
    ion: Optional[WavesCoherentWaveProfiles2DIon] = field(
        default_factory=lambda: StructArray(
            type_input=WavesCoherentWaveProfiles2DIon
        ),
        metadata={
            "imas_type": "waves_coherent_wave_profiles_2d_ion",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": WavesCoherentWaveProfiles2DIon,
        },
    )
    time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class WavesCoherentWave(IdsBaseClass):
    """

    :ivar identifier : Identifier of the coherent wave, in terms of the type and name of the antenna driving the wave and an index separating waves driven by the same antenna.
    :ivar global_quantities : Global quantities for various time slices
    :ivar profiles_1d : Source radial profiles (flux surface averaged quantities) for various time slices
    :ivar profiles_2d : 2D profiles in poloidal cross-section, for various time slices
    :ivar beam_tracing : Beam tracing calculations, for various time slices
    :ivar full_wave : Solution by a full wave code, given on a generic grid description, for various time slices
    """

    class Meta:
        name = "waves_coherent_wave"
        is_root_ids = False

    identifier: Optional[WavesCoherentWaveIdentifier] = field(
        default=None,
        metadata={
            "imas_type": "waves_coherent_wave_identifier",
            "field_type": WavesCoherentWaveIdentifier,
        },
    )
    global_quantities: Optional[WavesCoherentWaveGlobalQuantities] = field(
        default_factory=lambda: StructArray(
            type_input=WavesCoherentWaveGlobalQuantities
        ),
        metadata={
            "imas_type": "waves_coherent_wave_global_quantities",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": WavesCoherentWaveGlobalQuantities,
        },
    )
    profiles_1d: Optional[WavesCoherentWaveProfiles1D] = field(
        default_factory=lambda: StructArray(
            type_input=WavesCoherentWaveProfiles1D
        ),
        metadata={
            "imas_type": "waves_coherent_wave_profiles_1d",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": WavesCoherentWaveProfiles1D,
        },
    )
    profiles_2d: Optional[WavesCoherentWaveProfiles2D] = field(
        default_factory=lambda: StructArray(
            type_input=WavesCoherentWaveProfiles2D
        ),
        metadata={
            "imas_type": "waves_coherent_wave_profiles_2d",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": WavesCoherentWaveProfiles2D,
        },
    )
    beam_tracing: Optional[WavesCoherentWaveBeamTracing] = field(
        default_factory=lambda: StructArray(
            type_input=WavesCoherentWaveBeamTracing
        ),
        metadata={
            "imas_type": "waves_coherent_wave_beam_tracing",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": WavesCoherentWaveBeamTracing,
        },
    )
    full_wave: Optional[WavesCoherentWaveFullWave] = field(
        default_factory=lambda: StructArray(
            type_input=WavesCoherentWaveFullWave
        ),
        metadata={
            "imas_type": "waves_coherent_wave_full_wave",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": WavesCoherentWaveFullWave,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class Waves(IdsBaseClass):
    """

    :ivar ids_properties :
    :ivar coherent_wave : Wave description for each frequency
    :ivar vacuum_toroidal_field : Characteristics of the vacuum toroidal field (used in rho_tor definition)
    :ivar magnetic_axis : Magnetic axis position (used to define a poloidal angle for the 2D profiles)
    :ivar code :
    :ivar time : Generic time
    """

    class Meta:
        name = "waves"
        is_root_ids = True

    ids_properties: Optional[IdsProperties] = field(
        default=None,
        metadata={"imas_type": "ids_properties", "field_type": IdsProperties},
    )
    coherent_wave: Optional[WavesCoherentWave] = field(
        default_factory=lambda: StructArray(type_input=WavesCoherentWave),
        metadata={
            "imas_type": "waves_coherent_wave",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": WavesCoherentWave,
        },
    )
    vacuum_toroidal_field: Optional[BTorVacuum1] = field(
        default=None,
        metadata={"imas_type": "b_tor_vacuum_1", "field_type": BTorVacuum1},
    )
    magnetic_axis: Optional[Rz1DDynamic1] = field(
        default=None,
        metadata={"imas_type": "rz1d_dynamic_1", "field_type": Rz1DDynamic1},
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
