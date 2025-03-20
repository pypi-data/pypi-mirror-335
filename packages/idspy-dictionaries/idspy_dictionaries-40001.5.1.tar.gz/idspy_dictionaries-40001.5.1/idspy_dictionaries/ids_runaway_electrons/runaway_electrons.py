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
class DistributionsDGgdExpansion(IdsBaseClass):
    """

    :ivar grid_subset : Values of the distribution function expansion, for various grid subsets
    """

    class Meta:
        name = "distributions_d_ggd_expansion"
        is_root_ids = False

    grid_subset: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
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
class DistributionMarkersOrbitInstant(IdsBaseClass):
    """

    :ivar expressions : List of the expressions f(eq) used in the orbit integrals
    :ivar time_orbit : Time array along the markers last orbit
    :ivar values : Values of the orbit integrals
    """

    class Meta:
        name = "distribution_markers_orbit_instant"
        is_root_ids = False

    expressions: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=str),
        metadata={
            "imas_type": "STR_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    time_orbit: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    values: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=complex),
        metadata={
            "imas_type": "CPX_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "../expressions",
                "coordinate2": "../../weights",
                "coordinate3": "../time_orbit",
            },
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
class DistributionMarkersOrbit(IdsBaseClass):
    """

    :ivar expressions : List of the expressions f(n_tor,m_pol,k,q,...) used in the orbit integrals
    :ivar n_phi : Array of toroidal mode numbers, where quantities vary as exp(i.n_phi.phi) and phi runs anticlockwise when viewed from above
    :ivar m_pol : Array of poloidal mode numbers, where quantities vary as exp(-i.m_pol.theta) and theta is the angle defined by the choice of ../../coordinate_identifier, with its centre at the magnetic axis recalled at the root of this IDS
    :ivar bounce_harmonics : Array of bounce harmonics k
    :ivar values : Values of the orbit integrals
    """

    class Meta:
        name = "distribution_markers_orbit"
        is_root_ids = False

    expressions: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=str),
        metadata={
            "imas_type": "STR_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
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
    m_pol: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=int),
        metadata={
            "imas_type": "INT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    bounce_harmonics: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=int),
        metadata={
            "imas_type": "INT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    values: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 5, dtype=complex),
        metadata={
            "imas_type": "CPX_5D",
            "ndims": 5,
            "coordinates": {
                "coordinate1": "../expressions",
                "coordinate2": "../../weights",
                "coordinate3": "../n_tor",
                "coordinate4": "../m_pol",
                "coordinate5": "../bounce_harmonics",
            },
            "field_type": np.ndarray,
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
class DistributionMarkers(IdsBaseClass):
    """

    :ivar coordinate_identifier : Set of coordinate identifiers, coordinates on which the markers are represented
    :ivar weights : Weight of the markers, i.e. number of real particles represented by each marker. The dimension of the vector correspond to the number of markers
    :ivar positions : Position of the markers in the set of coordinates. The first dimension corresponds to the number of markers, the second dimension to the set of coordinates
    :ivar orbit_integrals : Integrals along the markers orbit. These dimensionless expressions are of the form: (1/tau) integral (f(n_tor,m_pol,k,eq,...) dt) from time - tau to time, where tau is the transit/trapping time of the marker and f() a dimensionless function (phase factor,drift,etc) of the equilibrium (e.g. q) and perturbation (Fourier harmonics n_tor,m_pol and bounce harmonic k) along the particles orbits. In fact the integrals are taken during the last orbit of each marker at the time value of the time node below
    :ivar orbit_integrals_instant : Integrals/quantities along the markers orbit. These dimensionless expressions are of the form: (1/tau) integral ( f(eq) dt) from time - tau to time_orbit for different values of time_orbit in the interval from time - tau to time, where tau is the transit/trapping time of the marker and f(eq) a dimensionless function (phase, drift,q,etc) of the equilibrium along the markers orbits. The integrals are taken during the last orbit of each marker at the time value of the time node below
    :ivar toroidal_mode : In case the orbit integrals are calculated for a given MHD perturbation, index of the toroidal mode considered. Refers to the time_slice/toroidal_mode array of the MHD_LINEAR IDS in which this perturbation is described
    :ivar time : Time
    """

    class Meta:
        name = "distribution_markers"
        is_root_ids = False

    coordinate_identifier: Optional[IdentifierDynamicAos3] = field(
        default_factory=lambda: StructArray(type_input=IdentifierDynamicAos3),
        metadata={
            "imas_type": "identifier_dynamic_aos3",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": IdentifierDynamicAos3,
        },
    )
    weights: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    positions: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../weights",
                "coordinate2": "../coordinate_identifier",
            },
            "field_type": np.ndarray,
        },
    )
    orbit_integrals: Optional[DistributionMarkersOrbit] = field(
        default=None,
        metadata={
            "imas_type": "distribution_markers_orbit",
            "field_type": DistributionMarkersOrbit,
        },
    )
    orbit_integrals_instant: Optional[DistributionMarkersOrbitInstant] = field(
        default=None,
        metadata={
            "imas_type": "distribution_markers_orbit_instant",
            "field_type": DistributionMarkersOrbitInstant,
        },
    )
    toroidal_mode: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
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
class DistributionsDGgdNogrid(IdsBaseClass):
    """

    :ivar temperature : Reference temperature profile used to define the local thermal energy and the thermal velocity (for normalization of the grid coordinates)
    :ivar expansion : Distribution function expanded into a vector of successive approximations. The first element in the vector (expansion(1)) is the zeroth order distribution function, while the K:th element in the vector (expansion(K)) is the K:th correction, such that the total distribution function is a sum over all elements in the expansion vector.
    :ivar expansion_fd3v : Distribution function multiplied by the volume of the local velocity cell d3v, expanded into a vector of successive approximations. The first element in the vector (expansion(1)) is the zeroth order distribution function, while the K:th element in the vector (expansion(K)) is the K:th correction, such that the total distribution function is a sum over all elements in the expansion vector.
    :ivar time : Time
    """

    class Meta:
        name = "distributions_d_ggd_nogrid"
        is_root_ids = False

    temperature: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {
                "coordinate1": "../../../profiles_1d(itime)/grid/rho_tor_norm"
            },
            "field_type": np.ndarray,
        },
    )
    expansion: Optional[DistributionsDGgdExpansion] = field(
        default_factory=lambda: StructArray(
            type_input=DistributionsDGgdExpansion
        ),
        metadata={
            "imas_type": "distributions_d_ggd_expansion",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": DistributionsDGgdExpansion,
        },
    )
    expansion_fd3v: Optional[DistributionsDGgdExpansion] = field(
        default_factory=lambda: StructArray(
            type_input=DistributionsDGgdExpansion
        ),
        metadata={
            "imas_type": "distributions_d_ggd_expansion",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": DistributionsDGgdExpansion,
        },
    )
    time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class GenericGridAos3Root(IdsBaseClass):
    """

    :ivar identifier : Grid identifier
    :ivar path : Path of the grid, including the IDS name, in case of implicit reference to a grid_ggd node described in another IDS. To be filled only if the grid is not described explicitly in this grid_ggd structure. Example syntax: IDS::wall/0/description_ggd(1)/grid_ggd, means that the grid is located in the wall IDS, occurrence 0, with relative path description_ggd(1)/grid_ggd, using Fortran index convention (here : first index of the array)
    :ivar space : Set of grid spaces
    :ivar grid_subset : Grid subsets
    :ivar time : Time
    """

    class Meta:
        name = "generic_grid_aos3_root"
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
    time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
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
class RunawayElectronsTransport(IdsBaseClass):
    """

    :ivar d : Effective diffusivity
    :ivar v : Effective convection
    :ivar flux : Flux
    """

    class Meta:
        name = "runaway_electrons_transport"
        is_root_ids = False

    d: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    v: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    flux: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class RunawayElectronsGlobalVolume(IdsBaseClass):
    """

    :ivar density : Runaway electrons density
    :ivar current_density : Runaways parallel current density = average(j.B) / B0, where B0 = runaway_electrons/vacuum_toroidal_field/b0
    :ivar e_field_dreicer : Dreicer electric field (parallel to magnetic field)
    :ivar e_field_critical : Critical electric field
    :ivar energy_density_kinetic : Runaways kinetic mean energy density
    :ivar pitch_angle : Average pitch angle of the runaways distribution function (v_parallel/|v|)
    :ivar momentum_critical_avalanche : Critical momentum for avalanche, Compton and tritium
    :ivar momentum_critical_hot_tail : Critical momentum for hot tail
    :ivar ddensity_dt_total : Total source of runaway electrons
    :ivar ddensity_dt_compton : Compton source of runaway electrons
    :ivar ddensity_dt_tritium : Tritium source of runaway electrons
    :ivar ddensity_dt_hot_tail : Hot tail source of runaway electrons
    :ivar ddensity_dt_dreicer : Dreicer source of runaway electrons
    """

    class Meta:
        name = "runaway_electrons_global_volume"
        is_root_ids = False

    density: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../time"},
            "field_type": np.ndarray,
        },
    )
    current_density: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../time"},
            "field_type": np.ndarray,
        },
    )
    e_field_dreicer: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../time"},
            "field_type": np.ndarray,
        },
    )
    e_field_critical: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../time"},
            "field_type": np.ndarray,
        },
    )
    energy_density_kinetic: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../time"},
            "field_type": np.ndarray,
        },
    )
    pitch_angle: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../time"},
            "field_type": np.ndarray,
        },
    )
    momentum_critical_avalanche: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../time"},
            "field_type": np.ndarray,
        },
    )
    momentum_critical_hot_tail: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../time"},
            "field_type": np.ndarray,
        },
    )
    ddensity_dt_total: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../time"},
            "field_type": np.ndarray,
        },
    )
    ddensity_dt_compton: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../time"},
            "field_type": np.ndarray,
        },
    )
    ddensity_dt_tritium: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../time"},
            "field_type": np.ndarray,
        },
    )
    ddensity_dt_hot_tail: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../time"},
            "field_type": np.ndarray,
        },
    )
    ddensity_dt_dreicer: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../time"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class RunawayElectronsGlobalQuantities(IdsBaseClass):
    """

    :ivar current_phi : Total runaway current (toroidal component)
    :ivar energy_kinetic : Total runaway kinetic energy
    :ivar volume_average : Volume average runaways parameters
    """

    class Meta:
        name = "runaway_electrons_global_quantities"
        is_root_ids = False

    current_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time"},
            "field_type": np.ndarray,
        },
    )
    energy_kinetic: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time"},
            "field_type": np.ndarray,
        },
    )
    volume_average: Optional[RunawayElectronsGlobalVolume] = field(
        default=None,
        metadata={
            "imas_type": "runaway_electrons_global_volume",
            "field_type": RunawayElectronsGlobalVolume,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class RunawayElectronsDistribution(IdsBaseClass):
    """

    :ivar gyro_type : Defines how to interpret the spatial coordinates: 1 = given at the actual particle birth point; 2 =given at the gyro centre of the birth point
    :ivar ggd : Distribution represented using the ggd, for various time slices
    :ivar markers : Distribution represented by a set of markers (test particles)
    """

    class Meta:
        name = "runaway_electrons_distribution"
        is_root_ids = False

    gyro_type: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    ggd: Optional[DistributionsDGgdNogrid] = field(
        default_factory=lambda: StructArray(type_input=DistributionsDGgdNogrid),
        metadata={
            "imas_type": "distributions_d_ggd_nogrid",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": DistributionsDGgdNogrid,
        },
    )
    markers: Optional[DistributionMarkers] = field(
        default_factory=lambda: StructArray(type_input=DistributionMarkers),
        metadata={
            "imas_type": "distribution_markers",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": DistributionMarkers,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class RunawayElectronsGgd(IdsBaseClass):
    """

    :ivar density : Runaway electrons density, given on various grid subsets
    :ivar current_density : Runaways parallel current density = average(j.B) / B0, where B0 = runaway_electrons/vacuum_toroidal_field/b0, given on various grid subsets
    :ivar e_field_dreicer : Dreicer electric field (parallel to B), given on various grid subsets
    :ivar e_field_critical : Critical electric field, given on various grid subsets
    :ivar energy_density_kinetic : Runaways kinetic energy density, given on various grid subsets
    :ivar pitch_angle : Average pitch angle of the runaways distribution function (v_parallel/|v|), given on various grid subsets
    :ivar momentum_critical_avalanche : Critical momentum for avalanche, Compton and tritium, given on various grid subsets
    :ivar momentum_critical_hot_tail : Critical momentum for hot tail, given on various grid subsets
    :ivar ddensity_dt_total : Total source of runaway electrons, given on various grid subsets
    :ivar ddensity_dt_compton : Compton source of runaway electrons, given on various grid subsets
    :ivar ddensity_dt_tritium : Tritium source of runaway electrons, given on various grid subsets
    :ivar ddensity_dt_hot_tail : Hot tail source of runaway electrons, given on various grid subsets
    :ivar ddensity_dt_dreicer : Dreicer source of runaway electrons, given on various grid subsets
    :ivar time : Time
    """

    class Meta:
        name = "runaway_electrons_ggd"
        is_root_ids = False

    density: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    current_density: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    e_field_dreicer: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    e_field_critical: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    energy_density_kinetic: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    pitch_angle: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    momentum_critical_avalanche: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    momentum_critical_hot_tail: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    ddensity_dt_total: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    ddensity_dt_compton: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    ddensity_dt_tritium: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    ddensity_dt_hot_tail: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    ddensity_dt_dreicer: Optional[GenericGridScalar] = field(
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
class RunawayElectronsProfiles1D(IdsBaseClass):
    """

    :ivar grid : Radial grid
    :ivar density : Runaway electrons density
    :ivar current_density : Runaways parallel current density = average(j.B) / B0, where B0 = runaway_electrons/vacuum_toroidal_field/b0
    :ivar e_field_dreicer : Dreicer electric field (parallel to B)
    :ivar e_field_critical : Critical electric field
    :ivar energy_density_kinetic : Runaways kinetic mean energy density
    :ivar pitch_angle : Average pitch angle of the runaways distribution function (v_parallel/|v|)
    :ivar momentum_critical_avalanche : Critical momentum for avalanche, Compton and tritium
    :ivar momentum_critical_hot_tail : Critical momentum for hot tail
    :ivar ddensity_dt_total : Total source of runaway electrons
    :ivar ddensity_dt_compton : Compton source of runaway electrons
    :ivar ddensity_dt_tritium : Tritium source of runaway electrons
    :ivar ddensity_dt_hot_tail : Hot tail source of runaway electrons
    :ivar ddensity_dt_dreicer : Dreicer source of runaway electrons
    :ivar transport_perpendicular : Effective perpendicular transport to the magnetic field for runaways
    :ivar time : Time
    """

    class Meta:
        name = "runaway_electrons_profiles_1d"
        is_root_ids = False

    grid: Optional[CoreRadialGrid] = field(
        default=None,
        metadata={
            "imas_type": "core_radial_grid",
            "field_type": CoreRadialGrid,
        },
    )
    density: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    current_density: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    e_field_dreicer: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    e_field_critical: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    energy_density_kinetic: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    pitch_angle: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    momentum_critical_avalanche: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    momentum_critical_hot_tail: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    ddensity_dt_total: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    ddensity_dt_compton: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    ddensity_dt_tritium: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    ddensity_dt_hot_tail: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    ddensity_dt_dreicer: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    transport_perpendicular: Optional[RunawayElectronsTransport] = field(
        default=None,
        metadata={
            "imas_type": "runaway_electrons_transport",
            "field_type": RunawayElectronsTransport,
        },
    )
    time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class RunawayElectrons(IdsBaseClass):
    """

    :ivar ids_properties :
    :ivar global_quantities : Global quantities
    :ivar profiles_1d : Radial flux surface averaged profiles for a set of time slices
    :ivar grid_ggd : Grid (using the Generic Grid Description), for various time slices
    :ivar ggd_fluid : Fluid quantities represented using the general grid description for 2D or 3D description
    :ivar distribution : Distribution function of the runaway electrons
    :ivar vacuum_toroidal_field : Characteristics of the vacuum toroidal field (used in rho_tor definition and in the normalization of current densities)
    :ivar code :
    :ivar time : Generic time
    """

    class Meta:
        name = "runaway_electrons"
        is_root_ids = True

    ids_properties: Optional[IdsProperties] = field(
        default=None,
        metadata={"imas_type": "ids_properties", "field_type": IdsProperties},
    )
    global_quantities: Optional[RunawayElectronsGlobalQuantities] = field(
        default=None,
        metadata={
            "imas_type": "runaway_electrons_global_quantities",
            "field_type": RunawayElectronsGlobalQuantities,
        },
    )
    profiles_1d: Optional[RunawayElectronsProfiles1D] = field(
        default_factory=lambda: StructArray(
            type_input=RunawayElectronsProfiles1D
        ),
        metadata={
            "imas_type": "runaway_electrons_profiles_1d",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": RunawayElectronsProfiles1D,
        },
    )
    grid_ggd: Optional[GenericGridAos3Root] = field(
        default_factory=lambda: StructArray(type_input=GenericGridAos3Root),
        metadata={
            "imas_type": "generic_grid_aos3_root",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": GenericGridAos3Root,
        },
    )
    ggd_fluid: Optional[RunawayElectronsGgd] = field(
        default_factory=lambda: StructArray(type_input=RunawayElectronsGgd),
        metadata={
            "imas_type": "runaway_electrons_ggd",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": RunawayElectronsGgd,
        },
    )
    distribution: Optional[RunawayElectronsDistribution] = field(
        default=None,
        metadata={
            "imas_type": "runaway_electrons_distribution",
            "field_type": RunawayElectronsDistribution,
        },
    )
    vacuum_toroidal_field: Optional[BTorVacuum1] = field(
        default=None,
        metadata={"imas_type": "b_tor_vacuum_1", "field_type": BTorVacuum1},
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
