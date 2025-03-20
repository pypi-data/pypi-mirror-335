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
class StatisticsQuantity2DType(IdsBaseClass):
    """

    :ivar identifier : Identifier of the statistics type
    :ivar value : Value of the statistics for that quantity, the array corresponding to the first dimension of the original 2D quantity
    :ivar grid_subset_index : Only if the statistics value is given on a different GGD grid subset than the original quantity (e.g. if the statistics has worked over a dimension of the GGD), index of the new grid subset the statistics value is provided on. Corresponds to the index used in the grid subset definition: grid_subset(:)/identifier/index
    :ivar grid_index : Only if the statistics value is given on a different GGD grid subset than the original quantity (e.g. if the statistics has worked over a dimension of the GGD), index of the grid used to represent the statistics value
    :ivar uq_input_path : For Sobol index only, path to the related the uq_input quantity, e.g. ../../../uq_input_2d(3)
    """

    class Meta:
        name = "statistics_quantity_2d_type"
        is_root_ids = False

    identifier: Optional[IdentifierDynamicAos3] = field(
        default=None,
        metadata={
            "imas_type": "identifier_dynamic_aos3",
            "field_type": IdentifierDynamicAos3,
        },
    )
    value: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    grid_subset_index: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    grid_index: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    uq_input_path: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
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
class StatisticsDistribution2D(IdsBaseClass):
    """

    :ivar bins : Bins of quantitiy values, defined for each element (first dimension) corresponding to the first dimension of the original 2D quantity
    :ivar probability : Probability to have a value of the quantity between bins(n) and bins(n+1) (thus the size of its second dimension is the size of the second dimension of the bins array - 1). The first dimension correspond to the first dimension of the original 2D quantity
    """

    class Meta:
        name = "statistics_distribution_2d"
        is_root_ids = False

    bins: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {"coordinate1": "1...N", "coordinate2": "1...N"},
            "field_type": np.ndarray,
        },
    )
    probability: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate1_same_as": "../bins",
                "coordinate2": "1...N",
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
class StatisticsQuantity2D(IdsBaseClass):
    """

    :ivar path : Path of the quantity within the IDS, following the syntax given in the link below
    :ivar statistics_type : Set of statistics types applied to the quantity
    :ivar distribution : Probability distribution function of the quantity
    """

    class Meta:
        name = "statistics_quantity_2d"
        is_root_ids = False

    path: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    statistics_type: Optional[StatisticsQuantity2DType] = field(
        default_factory=lambda: StructArray(
            type_input=StatisticsQuantity2DType
        ),
        metadata={
            "imas_type": "statistics_quantity_2d_type",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": StatisticsQuantity2DType,
        },
    )
    distribution: Optional[StatisticsDistribution2D] = field(
        default=None,
        metadata={
            "imas_type": "statistics_distribution_2d",
            "field_type": StatisticsDistribution2D,
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
class StatisticsInput2D(IdsBaseClass):
    """

    :ivar path : Path of the quantity within the IDS, following the syntax given in the link below
    :ivar distribution : Probability distribution function of the quantity
    """

    class Meta:
        name = "statistics_input_2d"
        is_root_ids = False

    path: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    distribution: Optional[StatisticsDistribution2D] = field(
        default=None,
        metadata={
            "imas_type": "statistics_distribution_2d",
            "field_type": StatisticsDistribution2D,
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
class Statistics(IdsBaseClass):
    """

    :ivar quantity_2d : Set of 2D quantities on which statistics are provided. 2D means 1D+time dimension, so either a 1D quantity within a dynamic array of structure, or a 2D dynamic quantity outside of an array of structure. Therefore the resulting statistical value is 1D for a given statistics time slice.
    :ivar uq_input_2d : If the statistics are based on an uncertainty quantification process, set of 2D input quantities that are varied
    :ivar time_width : Width of the time interval over which the statistics have been calculated. By convention, the time interval starts at time-time_width and ends at time.
    :ivar time : Time
    """

    class Meta:
        name = "statistics"
        is_root_ids = False

    quantity_2d: Optional[StatisticsQuantity2D] = field(
        default_factory=lambda: StructArray(type_input=StatisticsQuantity2D),
        metadata={
            "imas_type": "statistics_quantity_2d",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": StatisticsQuantity2D,
        },
    )
    uq_input_2d: Optional[StatisticsInput2D] = field(
        default_factory=lambda: StructArray(type_input=StatisticsInput2D),
        metadata={
            "imas_type": "statistics_input_2d",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": StatisticsInput2D,
        },
    )
    time_width: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
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
class GenericGridVectorComponents(IdsBaseClass):
    """

    :ivar grid_index : Index of the grid used to represent this quantity
    :ivar grid_subset_index : Index of the grid subset the data is provided on. Corresponds to the index used in the grid subset definition: grid_subset(:)/identifier/index
    :ivar radial : Radial component, one scalar value is provided per element in the grid subset.
    :ivar radial_coefficients : Interpolation coefficients for the radial component, to be used for a high precision evaluation of the physical quantity with finite elements, provided per element in the grid subset (first dimension).
    :ivar diamagnetic : Diamagnetic component, one scalar value is provided per element in the grid subset.
    :ivar diamagnetic_coefficients : Interpolation coefficients for the diamagnetic component, to be used for a high precision evaluation of the physical quantity with finite elements, provided per element in the grid subset (first dimension).
    :ivar parallel : Parallel component, one scalar value is provided per element in the grid subset.
    :ivar parallel_coefficients : Interpolation coefficients for the parallel component, to be used for a high precision evaluation of the physical quantity with finite elements, provided per element in the grid subset (first dimension).
    :ivar poloidal : Poloidal component, one scalar value is provided per element in the grid subset.
    :ivar poloidal_coefficients : Interpolation coefficients for the poloidal component, to be used for a high precision evaluation of the physical quantity with finite elements, provided per element in the grid subset (first dimension).
    :ivar r : Component along the major radius axis, one scalar value is provided per element in the grid subset.
    :ivar r_coefficients : Interpolation coefficients for the component along the major radius axis, to be used for a high precision evaluation of the physical quantity with finite elements, provided per element in the grid subset (first dimension).
    :ivar phi : Toroidal component, one scalar value is provided per element in the grid subset.
    :ivar phi_coefficients : Interpolation coefficients for the toroidal component, to be used for a high precision evaluation of the physical quantity with finite elements, provided per element in the grid subset (first dimension).
    :ivar z : Component along the height axis, one scalar value is provided per element in the grid subset.
    :ivar z_coefficients : Interpolation coefficients for the component along the height axis, to be used for a high precision evaluation of the physical quantity with finite elements, provided per element in the grid subset (first dimension).
    """

    class Meta:
        name = "generic_grid_vector_components"
        is_root_ids = False

    grid_index: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    grid_subset_index: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    radial: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    radial_coefficients: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {"coordinate1": "1...N", "coordinate2": "1...N"},
            "field_type": np.ndarray,
        },
    )
    diamagnetic: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    diamagnetic_coefficients: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {"coordinate1": "1...N", "coordinate2": "1...N"},
            "field_type": np.ndarray,
        },
    )
    parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    parallel_coefficients: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {"coordinate1": "1...N", "coordinate2": "1...N"},
            "field_type": np.ndarray,
        },
    )
    poloidal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    poloidal_coefficients: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {"coordinate1": "1...N", "coordinate2": "1...N"},
            "field_type": np.ndarray,
        },
    )
    r: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    r_coefficients: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {"coordinate1": "1...N", "coordinate2": "1...N"},
            "field_type": np.ndarray,
        },
    )
    phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    phi_coefficients: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {"coordinate1": "1...N", "coordinate2": "1...N"},
            "field_type": np.ndarray,
        },
    )
    z: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    z_coefficients: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {"coordinate1": "1...N", "coordinate2": "1...N"},
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
class GenericGridScalarSinglePosition(IdsBaseClass):
    """

    :ivar grid_index : Index of the grid used to represent this quantity
    :ivar grid_subset_index : Index of the grid subset the data is provided on. Corresponds to the index used in the grid subset definition: grid_subset(:)/identifier/index
    :ivar value : Scalar value of the quantity on the grid subset (corresponding to a single local position or to an integrated value over the subset)
    """

    class Meta:
        name = "generic_grid_scalar_single_position"
        is_root_ids = False

    grid_index: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    grid_subset_index: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    value: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
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
class EdgeProfilesVectorComponents1(IdsBaseClass):
    """

    :ivar radial : Radial component
    :ivar diamagnetic : Diamagnetic component
    :ivar parallel : Parallel component
    :ivar poloidal : Poloidal component
    :ivar toroidal : Toroidal component
    """

    class Meta:
        name = "edge_profiles_vector_components_1"
        is_root_ids = False

    radial: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    diamagnetic: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    poloidal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    toroidal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class EdgeProfilesVectorComponents2(IdsBaseClass):
    """

    :ivar radial : Radial component
    :ivar diamagnetic : Diamagnetic component
    :ivar parallel : Parallel component
    :ivar poloidal : Poloidal component
    :ivar toroidal : Toroidal component
    """

    class Meta:
        name = "edge_profiles_vector_components_2"
        is_root_ids = False

    radial: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    diamagnetic: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    poloidal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    toroidal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class EdgeProfilesVectorComponents3(IdsBaseClass):
    """

    :ivar radial : Radial component
    :ivar diamagnetic : Diamagnetic component
    :ivar parallel : Parallel component
    :ivar poloidal : Poloidal component
    :ivar toroidal : Toroidal component
    """

    class Meta:
        name = "edge_profiles_vector_components_3"
        is_root_ids = False

    radial: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    diamagnetic: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    poloidal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    toroidal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class EdgeRadialGrid(IdsBaseClass):
    """

    :ivar rho_pol_norm : Normalized poloidal flux coordinate = sqrt((psi(rho)-psi(magnetic_axis) / (psi(LCFS)-psi(magnetic_axis)))
    :ivar psi : Poloidal magnetic flux. Integral of magnetic field passing through a contour defined by the intersection of a flux surface passing through the point of interest and a Z=constant plane. If the integration surface is flat, the surface normal vector is in the increasing vertical coordinate direction, Z, namely upwards.
    :ivar rho_tor_norm : Normalized toroidal flux coordinate. The normalizing value for rho_tor_norm, is the toroidal flux coordinate at the equilibrium boundary (LCFS or 99.x % of the LCFS in case of a fixed boundary equilibium calculation, see time_slice/boundary/b_flux_pol_norm in the equilibrium IDS)
    :ivar rho_tor : Toroidal flux coordinate. rho_tor = sqrt(b_flux_tor/(pi*b0)) ~ sqrt(pi*r^2*b0/(pi*b0)) ~ r [m]. The toroidal field used in its definition is indicated under vacuum_toroidal_field/b0
    :ivar volume : Volume enclosed inside the magnetic surface
    :ivar area : Cross-sectional area of the flux surface
    :ivar psi_magnetic_axis : Value of the poloidal magnetic flux at the magnetic axis (useful to normalize the psi array values when the radial grid doesn&#39;t go from the magnetic axis to the plasma boundary)
    :ivar psi_boundary : Value of the poloidal magnetic flux at the plasma boundary (useful to normalize the psi array values when the radial grid doesn&#39;t go from the magnetic axis to the plasma boundary)
    """

    class Meta:
        name = "edge_radial_grid"
        is_root_ids = False

    rho_pol_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    psi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    rho_tor_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    rho_tor: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    volume: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    area: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../rho_pol_norm"},
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
class EdgeProfiles1DFit(IdsBaseClass):
    """

    :ivar measured : Measured values. Units are: as_parent for a local measurement, as_parent.m for a line integrated measurement.
    :ivar source : Path to the source data for each measurement in the IMAS data dictionary, e.g. ece/channel(i)/t_e for the electron temperature on the i-th channel in the ECE IDS
    :ivar time_measurement : Exact time slices used from the time array of the measurement source data. If the time slice does not exist in the time array of the source data, it means linear interpolation has been used
    :ivar time_measurement_slice_method : Method used to slice the data : index = 0 means using exact time slice of the measurement, 1 means linear interpolation, ...
    :ivar time_measurement_width : In case the measurements are averaged over a time interval, this node is the full width of this time interval (empty otherwise). In case the slicing/averaging method doesn&#39;t use a hard time interval cutoff, this width is the characteristic time span of the slicing/averaging method. By convention, the time interval starts at time_measurement-time_width and ends at time_measurement.
    :ivar local : Integer flag : 1 means local measurement, 0 means line-integrated measurement
    :ivar rho_tor_norm : Normalized toroidal flux coordinate of each measurement (local value for a local measurement, minimum value reached by the line of sight for a line measurement)
    :ivar rho_pol_norm : Normalized poloidal flux coordinate of each measurement (local value for a local measurement, minimum value reached by the line of sight for a line measurement)
    :ivar weight : Weight given to each measured value
    :ivar reconstructed : Value reconstructed from the fit. Units are: as_parent for a local measurement, as_parent.m for a line integrated measurement.
    :ivar chi_squared : Squared error normalized by the weighted standard deviation considered in the minimization process : chi_squared = weight^2 *(reconstructed - measured)^2 / sigma^2, where sigma is the standard deviation of the measurement error
    :ivar parameters : List of the fit specific parameters in XML format
    """

    class Meta:
        name = "edge_profiles_1d_fit"
        is_root_ids = False

    measured: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    source: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=str),
        metadata={
            "imas_type": "STR_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../measured"},
            "field_type": np.ndarray,
        },
    )
    time_measurement: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../measured"},
            "field_type": np.ndarray,
        },
    )
    time_measurement_slice_method: Optional[IdentifierDynamicAos3] = field(
        default=None,
        metadata={
            "imas_type": "identifier_dynamic_aos3",
            "field_type": IdentifierDynamicAos3,
        },
    )
    time_measurement_width: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../measured"},
            "field_type": np.ndarray,
        },
    )
    local: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=int),
        metadata={
            "imas_type": "INT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../measured"},
            "field_type": np.ndarray,
        },
    )
    rho_tor_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../measured"},
            "field_type": np.ndarray,
        },
    )
    rho_pol_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../measured"},
            "field_type": np.ndarray,
        },
    )
    weight: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../measured"},
            "field_type": np.ndarray,
        },
    )
    reconstructed: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../measured"},
            "field_type": np.ndarray,
        },
    )
    chi_squared: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../measured"},
            "field_type": np.ndarray,
        },
    )
    parameters: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )


@idspy_dataclass(repr=False, slots=True)
class EdgeProfilesIonsChargeStates2(IdsBaseClass):
    """

    :ivar z_min : Minimum Z of the charge state bundle
    :ivar z_max : Maximum Z of the charge state bundle (equal to z_min if no bundle)
    :ivar z_average : Average Z of the charge state bundle, volume averaged over the plasma radius (equal to z_min if no bundle), = sum (Z*x_z) where x_z is the relative concentration of a given charge state in the bundle, i.e. sum(x_z) = 1 over the bundle.
    :ivar z_square_average : Average Z square of the charge state bundle, volume averaged over the plasma radius (equal to z_min squared if no bundle), = sum (Z^2*x_z) where x_z is the relative concentration of a given charge state in the bundle, i.e. sum(x_z) = 1 over the bundle.
    :ivar z_average_1d : Average charge profile of the charge state bundle (equal to z_min if no bundle), = sum (Z*x_z) where x_z is the relative concentration of a given charge state in the bundle, i.e. sum(x_z) = 1 over the bundle.
    :ivar z_average_square_1d : Average square charge profile of the charge state bundle (equal to z_min squared if no bundle), = sum (Z^2*x_z) where x_z is the relative concentration of a given charge state in the bundle, i.e. sum(x_z) = 1 over the bundle.
    :ivar ionization_potential : Cumulative and average ionization potential to reach a given bundle. Defined as sum (x_z* (sum of Epot from z&#39;=0 to z-1)), where Epot is the ionization potential of ion Xz_+, and x_z is the relative concentration of a given charge state in the bundle, i.e. sum(x_z) = 1 over the bundle.
    :ivar name : String identifying state (e.g. C+, C+2 , C+3, C+4, C+5, C+6, ...)
    :ivar electron_configuration : Configuration of atomic orbitals of this state, e.g. 1s2-2s1
    :ivar vibrational_level : Vibrational level (can be bundled)
    :ivar vibrational_mode : Vibrational mode of this state, e.g. &#34;A_g&#34;. Need to define, or adopt a standard nomenclature.
    :ivar rotation_frequency_tor : Toroidal rotation frequency (i.e. toroidal velocity divided by the major radius at which the toroidal velocity is taken)
    :ivar temperature : Temperature
    :ivar density : Density (thermal+non-thermal)
    :ivar density_fit : Information on the fit used to obtain the density profile
    :ivar density_thermal : Density of thermal particles
    :ivar density_fast : Density of fast (non-thermal) particles
    :ivar pressure : Pressure (thermal+non-thermal)
    :ivar pressure_thermal : Pressure (thermal) associated with random motion ~average((v-average(v))^2)
    :ivar pressure_fast_perpendicular : Fast (non-thermal) perpendicular pressure
    :ivar pressure_fast_parallel : Fast (non-thermal) parallel pressure
    """

    class Meta:
        name = "edge_profiles_ions_charge_states2"
        is_root_ids = False

    z_min: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    z_max: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    z_average: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    z_square_average: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    z_average_1d: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    z_average_square_1d: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    ionization_potential: Optional[float] = field(
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
    rotation_frequency_tor: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    temperature: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    density: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    density_fit: Optional[EdgeProfiles1DFit] = field(
        default=None,
        metadata={
            "imas_type": "edge_profiles_1d_fit",
            "field_type": EdgeProfiles1DFit,
        },
    )
    density_thermal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    density_fast: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    pressure: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    pressure_thermal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    pressure_fast_perpendicular: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    pressure_fast_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class EdgeProfileIons(IdsBaseClass):
    """

    :ivar element : List of elements forming the atom or molecule
    :ivar z_ion : Ion charge (of the dominant ionization state; lumped ions are allowed), volume averaged over plasma radius
    :ivar name : String identifying ion (e.g. H, D, T, He, C, D2, ...)
    :ivar neutral_index : Index of the corresponding neutral species in the ../../neutral array
    :ivar z_ion_1d : Average charge of the ion species (sum of states charge weighted by state density and divided by ion density)
    :ivar z_ion_square_1d : Average square charge of the ion species (sum of states square charge weighted by state density and divided by ion density)
    :ivar temperature : Temperature (average over charge states when multiple charge states are considered)
    :ivar temperature_validity : Indicator of the validity of the temperature profile. 0: valid from automated processing, 1: valid and certified by the RO; - 1 means problem identified in the data processing (request verification by the RO), -2: invalid data, should not be used
    :ivar temperature_fit : Information on the fit used to obtain the temperature profile
    :ivar density : Density (thermal+non-thermal) (sum over charge states when multiple charge states are considered)
    :ivar density_validity : Indicator of the validity of the density profile. 0: valid from automated processing, 1: valid and certified by the RO; - 1 means problem identified in the data processing (request verification by the RO), -2: invalid data, should not be used
    :ivar density_fit : Information on the fit used to obtain the density profile
    :ivar density_thermal : Density (thermal) (sum over charge states when multiple charge states are considered)
    :ivar density_fast : Density of fast (non-thermal) particles (sum over charge states when multiple charge states are considered)
    :ivar pressure : Pressure (thermal+non-thermal) (sum over charge states when multiple charge states are considered)
    :ivar pressure_thermal : Pressure (thermal) associated with random motion ~average((v-average(v))^2) (sum over charge states when multiple charge states are considered)
    :ivar pressure_fast_perpendicular : Fast (non-thermal) perpendicular pressure  (sum over charge states when multiple charge states are considered)
    :ivar pressure_fast_parallel : Fast (non-thermal) parallel pressure  (sum over charge states when multiple charge states are considered)
    :ivar rotation_frequency_tor : Toroidal rotation frequency  (i.e. toroidal velocity divided by the major radius at which the toroidal velocity is taken) (average over charge states when multiple charge states are considered)
    :ivar velocity : Velocity (average over charge states when multiple charge states are considered) at the position of maximum major radius on every flux surface
    :ivar multiple_states_flag : Multiple states calculation flag : 0-Only the &#39;ion&#39; level is considered and the &#39;state&#39; array of structure is empty; 1-Ion states are considered and are described in the &#39;state&#39; array of structure
    :ivar state : Quantities related to the different states of the species (ionization, energy, excitation, ...)
    """

    class Meta:
        name = "edge_profile_ions"
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
    z_ion_1d: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    z_ion_square_1d: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    temperature: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    temperature_validity: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    temperature_fit: Optional[EdgeProfiles1DFit] = field(
        default=None,
        metadata={
            "imas_type": "edge_profiles_1d_fit",
            "field_type": EdgeProfiles1DFit,
        },
    )
    density: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    density_validity: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    density_fit: Optional[EdgeProfiles1DFit] = field(
        default=None,
        metadata={
            "imas_type": "edge_profiles_1d_fit",
            "field_type": EdgeProfiles1DFit,
        },
    )
    density_thermal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    density_fast: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    pressure: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    pressure_thermal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    pressure_fast_perpendicular: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    pressure_fast_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    rotation_frequency_tor: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    velocity: Optional[EdgeProfilesVectorComponents2] = field(
        default=None,
        metadata={
            "imas_type": "edge_profiles_vector_components_2",
            "field_type": EdgeProfilesVectorComponents2,
        },
    )
    multiple_states_flag: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    state: Optional[EdgeProfilesIonsChargeStates2] = field(
        default_factory=lambda: StructArray(
            type_input=EdgeProfilesIonsChargeStates2
        ),
        metadata={
            "imas_type": "edge_profiles_ions_charge_states2",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": EdgeProfilesIonsChargeStates2,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class EdgeProfilesNeutralState(IdsBaseClass):
    """

    :ivar name : String identifying state
    :ivar electron_configuration : Configuration of atomic orbitals of this state, e.g. 1s2-2s1
    :ivar vibrational_level : Vibrational level (can be bundled)
    :ivar vibrational_mode : Vibrational mode of this state, e.g. &#34;A_g&#34;. Need to define, or adopt a standard nomenclature.
    :ivar neutral_type : Neutral type (if the considered state is a neutral), in terms of energy. ID =1: cold; 2: thermal; 3: fast; 4: NBI
    :ivar temperature : Temperature
    :ivar density : Density (thermal+non-thermal)
    :ivar density_thermal : Density of thermal particles
    :ivar density_fast : Density of fast (non-thermal) particles
    :ivar pressure : Pressure (thermal+non-thermal)
    :ivar pressure_thermal : Pressure (thermal) associated with random motion ~average((v-average(v))^2)
    :ivar pressure_fast_perpendicular : Fast (non-thermal) perpendicular pressure
    :ivar pressure_fast_parallel : Fast (non-thermal) parallel pressure
    """

    class Meta:
        name = "edge_profiles_neutral_state"
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
    neutral_type: Optional[IdentifierDynamicAos3] = field(
        default=None,
        metadata={
            "imas_type": "identifier_dynamic_aos3",
            "field_type": IdentifierDynamicAos3,
        },
    )
    temperature: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    density: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    density_thermal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    density_fast: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    pressure: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    pressure_thermal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    pressure_fast_perpendicular: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    pressure_fast_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class EdgeProfileNeutral(IdsBaseClass):
    """

    :ivar element : List of elements forming the atom or molecule
    :ivar name : String identifying the species (e.g. H, D, T, He, C, D2, DT, CD4, ...)
    :ivar ion_index : Index of the corresponding ion species in the ../../ion array
    :ivar temperature : Temperature (average over charge states when multiple charge states are considered)
    :ivar density : Density (thermal+non-thermal) (sum over charge states when multiple charge states are considered)
    :ivar density_thermal : Density (thermal) (sum over charge states when multiple charge states are considered)
    :ivar density_fast : Density of fast (non-thermal) particles (sum over charge states when multiple charge states are considered)
    :ivar pressure : Pressure (thermal+non-thermal) (sum over charge states when multiple charge states are considered)
    :ivar pressure_thermal : Pressure (thermal) associated with random motion ~average((v-average(v))^2) (sum over charge states when multiple charge states are considered)
    :ivar pressure_fast_perpendicular : Fast (non-thermal) perpendicular pressure  (sum over charge states when multiple charge states are considered)
    :ivar pressure_fast_parallel : Fast (non-thermal) parallel pressure  (sum over charge states when multiple charge states are considered)
    :ivar multiple_states_flag : Multiple states calculation flag : 0-Only one state is considered; 1-Multiple states are considered and are described in the state structure
    :ivar state : Quantities related to the different states of the species (energy, excitation, ...)
    """

    class Meta:
        name = "edge_profile_neutral"
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
    temperature: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    density: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    density_thermal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    density_fast: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    pressure: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    pressure_thermal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    pressure_fast_perpendicular: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    pressure_fast_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    multiple_states_flag: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    state: Optional[EdgeProfilesNeutralState] = field(
        default_factory=lambda: StructArray(
            type_input=EdgeProfilesNeutralState
        ),
        metadata={
            "imas_type": "edge_profiles_neutral_state",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": EdgeProfilesNeutralState,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class EdgeProfilesProfiles1DElectrons(IdsBaseClass):
    """

    :ivar temperature : Temperature
    :ivar temperature_validity : Indicator of the validity of the temperature profile. 0: valid from automated processing, 1: valid and certified by the RO; - 1 means problem identified in the data processing (request verification by the RO), -2: invalid data, should not be used
    :ivar temperature_fit : Information on the fit used to obtain the temperature profile
    :ivar density : Density (thermal+non-thermal)
    :ivar density_validity : Indicator of the validity of the density profile. 0: valid from automated processing, 1: valid and certified by the RO; - 1 means problem identified in the data processing (request verification by the RO), -2: invalid data, should not be used
    :ivar density_fit : Information on the fit used to obtain the density profile
    :ivar density_thermal : Density of thermal particles
    :ivar density_fast : Density of fast (non-thermal) particles
    :ivar pressure : Pressure (thermal+non-thermal)
    :ivar pressure_thermal : Pressure (thermal) associated with random motion ~average((v-average(v))^2)
    :ivar pressure_fast_perpendicular : Fast (non-thermal) perpendicular pressure
    :ivar pressure_fast_parallel : Fast (non-thermal) parallel pressure
    :ivar collisionality_norm : Collisionality normalized to the bounce frequency
    """

    class Meta:
        name = "edge_profiles_profiles_1d_electrons"
        is_root_ids = False

    temperature: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    temperature_validity: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    temperature_fit: Optional[EdgeProfiles1DFit] = field(
        default=None,
        metadata={
            "imas_type": "edge_profiles_1d_fit",
            "field_type": EdgeProfiles1DFit,
        },
    )
    density: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    density_validity: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    density_fit: Optional[EdgeProfiles1DFit] = field(
        default=None,
        metadata={
            "imas_type": "edge_profiles_1d_fit",
            "field_type": EdgeProfiles1DFit,
        },
    )
    density_thermal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    density_fast: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    pressure: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    pressure_thermal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    pressure_fast_perpendicular: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    pressure_fast_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    collisionality_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class EdgeProfilesProfiles1D(IdsBaseClass):
    """

    :ivar grid : Radial grid
    :ivar electrons : Quantities related to the electrons
    :ivar ion : Quantities related to the different ion species, in the sense of isonuclear or isomolecular sequences. Ionization states (and other types of states) must be differentiated at the state level below
    :ivar neutral : Quantities related to the different neutral species
    :ivar t_i_average : Ion temperature (averaged on charge states and ion species)
    :ivar t_i_average_fit : Information on the fit used to obtain the t_i_average profile
    :ivar n_i_total_over_n_e : Ratio of total ion density (sum over species and charge states) over electron density. (thermal+non-thermal)
    :ivar n_i_thermal_total : Total ion thermal density (sum over species and charge states)
    :ivar momentum_phi : Total plasma toroidal momentum, summed over ion species and electrons weighted by their density and major radius, i.e. sum_over_species(n*R*m*Vphi)
    :ivar zeff : Effective charge
    :ivar zeff_fit : Information on the fit used to obtain the zeff profile
    :ivar pressure_ion_total : Total (sum over ion species) thermal ion pressure
    :ivar pressure_thermal : Thermal pressure (electrons+ions)
    :ivar pressure_perpendicular : Total perpendicular pressure (electrons+ions, thermal+non-thermal)
    :ivar pressure_parallel : Total parallel pressure (electrons+ions, thermal+non-thermal)
    :ivar j_total : Total parallel current density = average(jtot.B) / B0, where B0 = edge_profiles/Vacuum_Toroidal_Field/ B0
    :ivar current_parallel_inside : Parallel current driven inside the flux surface. Cumulative surface integral of j_total
    :ivar j_phi : Total toroidal current density = average(J_phi/R) / average(1/R)
    :ivar j_ohmic : Ohmic parallel current density = average(J_Ohmic.B) / B0, where B0 = edge_profiles/Vacuum_Toroidal_Field/ B0
    :ivar j_non_inductive : Non-inductive (includes bootstrap) parallel current density = average(jni.B) / B0, where B0 = edge_profiles/Vacuum_Toroidal_Field/ B0
    :ivar j_bootstrap : Bootstrap current density = average(J_Bootstrap.B) / B0, where B0 = edge_profiles/Vacuum_Toroidal_Field/ B0
    :ivar conductivity_parallel : Parallel conductivity
    :ivar e_field : Electric field, averaged on the magnetic surface. E.g for the parallel component, average(E.B) / B0, using edge_profiles/vacuum_toroidal_field/b0
    :ivar phi_potential : Electrostatic potential, averaged on the magnetic flux surface
    :ivar rotation_frequency_tor_sonic : Derivative of the flux surface averaged electrostatic potential with respect to the poloidal flux, multiplied by -1. This quantity is the toroidal angular rotation frequency due to the ExB drift, introduced in formula (43) of Hinton and Wong, Physics of Fluids 3082 (1985), also referred to as sonic flow in regimes in which the toroidal velocity is dominant over the poloidal velocity
    :ivar q : Safety factor
    :ivar magnetic_shear : Magnetic shear, defined as rho_tor/q . dq/drho_tor
    :ivar time : Time
    """

    class Meta:
        name = "edge_profiles_profiles_1d"
        is_root_ids = False

    grid: Optional[EdgeRadialGrid] = field(
        default=None,
        metadata={
            "imas_type": "edge_radial_grid",
            "field_type": EdgeRadialGrid,
        },
    )
    electrons: Optional[EdgeProfilesProfiles1DElectrons] = field(
        default=None,
        metadata={
            "imas_type": "edge_profiles_profiles_1d_electrons",
            "field_type": EdgeProfilesProfiles1DElectrons,
        },
    )
    ion: Optional[EdgeProfileIons] = field(
        default_factory=lambda: StructArray(type_input=EdgeProfileIons),
        metadata={
            "imas_type": "edge_profile_ions",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": EdgeProfileIons,
        },
    )
    neutral: Optional[EdgeProfileNeutral] = field(
        default_factory=lambda: StructArray(type_input=EdgeProfileNeutral),
        metadata={
            "imas_type": "edge_profile_neutral",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": EdgeProfileNeutral,
        },
    )
    t_i_average: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    t_i_average_fit: Optional[EdgeProfiles1DFit] = field(
        default=None,
        metadata={
            "imas_type": "edge_profiles_1d_fit",
            "field_type": EdgeProfiles1DFit,
        },
    )
    n_i_total_over_n_e: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    n_i_thermal_total: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    momentum_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    zeff: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    zeff_fit: Optional[EdgeProfiles1DFit] = field(
        default=None,
        metadata={
            "imas_type": "edge_profiles_1d_fit",
            "field_type": EdgeProfiles1DFit,
        },
    )
    pressure_ion_total: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    pressure_thermal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    pressure_perpendicular: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    pressure_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    j_total: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    current_parallel_inside: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    j_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    j_ohmic: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    j_non_inductive: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    j_bootstrap: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    conductivity_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    e_field: Optional[EdgeProfilesVectorComponents1] = field(
        default=None,
        metadata={
            "imas_type": "edge_profiles_vector_components_1",
            "field_type": EdgeProfilesVectorComponents1,
        },
    )
    phi_potential: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    rotation_frequency_tor_sonic: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    q: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    magnetic_shear: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_pol_norm"},
            "field_type": np.ndarray,
        },
    )
    time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class EdgeProfilesTimeSliceNeutralState(IdsBaseClass):
    """

    :ivar name : String identifying state
    :ivar electron_configuration : Configuration of atomic orbitals of this state, e.g. 1s2-2s1
    :ivar vibrational_level : Vibrational level (can be bundled)
    :ivar vibrational_mode : Vibrational mode of this state, e.g. &#34;A_g&#34;. Need to define, or adopt a standard nomenclature.
    :ivar neutral_type : Neutral type, in terms of energy. ID =1: cold; 2: thermal; 3: fast; 4: NBI
    :ivar temperature : Temperature, given on various grid subsets
    :ivar density : Density (thermal+non-thermal), given on various grid subsets
    :ivar density_fast : Density of fast (non-thermal) particles, given on various grid subsets
    :ivar pressure : Pressure, given on various grid subsets
    :ivar pressure_fast_perpendicular : Fast (non-thermal) perpendicular pressure, given on various grid subsets
    :ivar pressure_fast_parallel : Fast (non-thermal) parallel pressure, given on various grid subsets
    :ivar velocity : Velocity, given on various grid subsets
    :ivar velocity_diamagnetic : Velocity due to the diamagnetic drift, given on various grid subsets
    :ivar velocity_exb : Velocity due to the ExB drift, given on various grid subsets
    :ivar energy_density_kinetic : Kinetic energy density, given on various grid subsets
    :ivar distribution_function : Distribution function, given on various grid subsets
    """

    class Meta:
        name = "edge_profiles_time_slice_neutral_state"
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
    neutral_type: Optional[IdentifierDynamicAos3] = field(
        default=None,
        metadata={
            "imas_type": "identifier_dynamic_aos3",
            "field_type": IdentifierDynamicAos3,
        },
    )
    temperature: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    density: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    density_fast: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    pressure: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    pressure_fast_perpendicular: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    pressure_fast_parallel: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    velocity: Optional[GenericGridVectorComponents] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridVectorComponents
        ),
        metadata={
            "imas_type": "generic_grid_vector_components",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridVectorComponents,
        },
    )
    velocity_diamagnetic: Optional[GenericGridVectorComponents] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridVectorComponents
        ),
        metadata={
            "imas_type": "generic_grid_vector_components",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridVectorComponents,
        },
    )
    velocity_exb: Optional[GenericGridVectorComponents] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridVectorComponents
        ),
        metadata={
            "imas_type": "generic_grid_vector_components",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridVectorComponents,
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
    distribution_function: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class EdgeProfilesTimeSliceIonChargeState(IdsBaseClass):
    """

    :ivar z_min : Minimum Z of the state bundle (z_min = z_max = 0 for a neutral)
    :ivar z_max : Maximum Z of the state bundle (equal to z_min if no bundle)
    :ivar z_average : Average Z of the state bundle (equal to z_min if no bundle), = sum (Z*x_z) where x_z is the relative concentration of a given charge state in the bundle, i.e. sum(x_z) = 1 over the bundle, given on various grid subsets
    :ivar z_square_average : Average Z square of the state bundle (equal to z_min if no bundle), = sum (Z^2*x_z) where x_z is the relative concentration of a given charge state in the bundle, i.e. sum(x_z) = 1 over the bundle, given on various grid subsets
    :ivar ionization_potential : Cumulative and average ionization potential to reach a given bundle. Defined as sum (x_z* (sum of Epot from z&#39;=0 to z-1)), where Epot is the ionization potential of ion Xz_+, and x_z is the relative concentration of a given charge state in the bundle, i.e. sum(x_z) = 1 over the bundle, given on various grid subsets
    :ivar name : String identifying state (e.g. C+, C+2 , C+3, C+4, C+5, C+6, ...)
    :ivar electron_configuration : Configuration of atomic orbitals of this state, e.g. 1s2-2s1
    :ivar vibrational_level : Vibrational level (can be bundled)
    :ivar vibrational_mode : Vibrational mode of this state, e.g. &#34;A_g&#34;. Need to define, or adopt a standard nomenclature.
    :ivar temperature : Temperature, given on various grid subsets
    :ivar density : Density (thermal+non-thermal), given on various grid subsets
    :ivar density_fast : Density of fast (non-thermal) particles, given on various grid subsets
    :ivar pressure : Pressure, given on various grid subsets
    :ivar pressure_fast_perpendicular : Fast (non-thermal) perpendicular pressure, given on various grid subsets
    :ivar pressure_fast_parallel : Fast (non-thermal) parallel pressure, given on various grid subsets
    :ivar velocity : Velocity, given on various grid subsets
    :ivar velocity_diamagnetic : Velocity due to the diamagnetic drift, given on various grid subsets
    :ivar velocity_exb : Velocity due to the ExB drift, given on various grid subsets
    :ivar energy_density_kinetic : Kinetic energy density, given on various grid subsets
    :ivar distribution_function : Distribution function, given on various grid subsets
    """

    class Meta:
        name = "edge_profiles_time_slice_ion_charge_state"
        is_root_ids = False

    z_min: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    z_max: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    z_average: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    z_square_average: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    ionization_potential: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
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
    temperature: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    density: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    density_fast: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    pressure: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    pressure_fast_perpendicular: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    pressure_fast_parallel: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    velocity: Optional[GenericGridVectorComponents] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridVectorComponents
        ),
        metadata={
            "imas_type": "generic_grid_vector_components",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridVectorComponents,
        },
    )
    velocity_diamagnetic: Optional[GenericGridVectorComponents] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridVectorComponents
        ),
        metadata={
            "imas_type": "generic_grid_vector_components",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridVectorComponents,
        },
    )
    velocity_exb: Optional[GenericGridVectorComponents] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridVectorComponents
        ),
        metadata={
            "imas_type": "generic_grid_vector_components",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridVectorComponents,
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
    distribution_function: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class EdgeProfilesTimeSliceNeutral(IdsBaseClass):
    """

    :ivar element : List of elements forming the atom or molecule
    :ivar name : String identifying the species (e.g. H, D, T, He, C, D2, DT, CD4, ...)
    :ivar ion_index : Index of the corresponding ion species in the ../../ion array
    :ivar temperature : Temperature (average over states when multiple states are considered), given on various grid subsets
    :ivar density : Density (thermal+non-thermal) (sum over states when multiple states are considered), given on various grid subsets
    :ivar density_fast : Density of fast (non-thermal) particles (sum over states when multiple states are considered), given on various grid subsets
    :ivar pressure : Pressure (average over states when multiple states are considered), given on various grid subsets
    :ivar pressure_fast_perpendicular : Fast (non-thermal) perpendicular pressure (average over states when multiple states are considered), given on various grid subsets
    :ivar pressure_fast_parallel : Fast (non-thermal) parallel pressure (average over states when multiple states are considered), given on various grid subsets
    :ivar velocity : Velocity (average over states when multiple states are considered), given on various grid subsets
    :ivar energy_density_kinetic : Kinetic energy density (sum over states when multiple states are considered), given on various grid subsets
    :ivar multiple_states_flag : Multiple state calculation flag : 0-Only one state is considered; 1-Multiple states are considered and are described in the state structure
    :ivar state : Quantities related to the different states of the species (energy, excitation, ...)
    """

    class Meta:
        name = "edge_profiles_time_slice_neutral"
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
    temperature: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    density: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    density_fast: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    pressure: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    pressure_fast_perpendicular: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    pressure_fast_parallel: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    velocity: Optional[GenericGridVectorComponents] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridVectorComponents
        ),
        metadata={
            "imas_type": "generic_grid_vector_components",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridVectorComponents,
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
    multiple_states_flag: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    state: Optional[EdgeProfilesTimeSliceNeutralState] = field(
        default_factory=lambda: StructArray(
            type_input=EdgeProfilesTimeSliceNeutralState
        ),
        metadata={
            "imas_type": "edge_profiles_time_slice_neutral_state",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": EdgeProfilesTimeSliceNeutralState,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class EdgeProfilesTimeSliceIon(IdsBaseClass):
    """

    :ivar element : List of elements forming the atom or molecule
    :ivar z_ion : Ion charge (of the dominant ionization state; lumped ions are allowed).
    :ivar name : String identifying the species (e.g. H+, D+, T+, He+2, C+, D2, DT, CD4, ...)
    :ivar neutral_index : Index of the corresponding neutral species in the ../../neutral array
    :ivar temperature : Temperature (average over states when multiple states are considered), given on various grid subsets
    :ivar density : Density (thermal+non-thermal) (sum over states when multiple states are considered), given on various grid subsets
    :ivar density_fast : Density of fast (non-thermal) particles (sum over states when multiple states are considered), given on various grid subsets
    :ivar pressure : Pressure (average over states when multiple states are considered), given on various grid subsets
    :ivar pressure_fast_perpendicular : Fast (non-thermal) perpendicular pressure (average over states when multiple states are considered), given on various grid subsets
    :ivar pressure_fast_parallel : Fast (non-thermal) parallel pressure (average over states when multiple states are considered), given on various grid subsets
    :ivar velocity : Velocity (average over states when multiple states are considered), given on various grid subsets
    :ivar energy_density_kinetic : Kinetic energy density (sum over states when multiple states are considered), given on various grid subsets
    :ivar multiple_states_flag : Multiple state calculation flag : 0-Only one state is considered; 1-Multiple states are considered and are described in the state structure
    :ivar state : Quantities related to the different states of the species (ionization, energy, excitation, ...)
    """

    class Meta:
        name = "edge_profiles_time_slice_ion"
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
    temperature: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    density: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    density_fast: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    pressure: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    pressure_fast_perpendicular: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    pressure_fast_parallel: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    velocity: Optional[GenericGridVectorComponents] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridVectorComponents
        ),
        metadata={
            "imas_type": "generic_grid_vector_components",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridVectorComponents,
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
    multiple_states_flag: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    state: Optional[EdgeProfilesTimeSliceIonChargeState] = field(
        default_factory=lambda: StructArray(
            type_input=EdgeProfilesTimeSliceIonChargeState
        ),
        metadata={
            "imas_type": "edge_profiles_time_slice_ion_charge_state",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": EdgeProfilesTimeSliceIonChargeState,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class EdgeProfilesGgdFastIon(IdsBaseClass):
    """

    :ivar element : List of elements forming the atom or molecule
    :ivar z_ion : Ion charge (of the dominant ionization state; lumped ions are allowed).
    :ivar name : String identifying the species (e.g. H+, D+, T+, He+2, C+, D2, DT, CD4, ...)
    :ivar neutral_index : Index of the corresponding neutral species in the ../../neutral array
    :ivar content : Particle content = total number of particles for this ion species in the volume of the grid subset, for various grid subsets
    :ivar temperature : Temperature (average over states when multiple states are considered), given at various positions (grid subset of size 1)
    :ivar density : Density (thermal+non-thermal) (sum over states when multiple states are considered), given at various positions (grid subset of size 1)
    """

    class Meta:
        name = "edge_profiles_ggd_fast_ion"
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
    content: Optional[GenericGridScalarSinglePosition] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridScalarSinglePosition
        ),
        metadata={
            "imas_type": "generic_grid_scalar_single_position",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalarSinglePosition,
        },
    )
    temperature: Optional[GenericGridScalarSinglePosition] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridScalarSinglePosition
        ),
        metadata={
            "imas_type": "generic_grid_scalar_single_position",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalarSinglePosition,
        },
    )
    density: Optional[GenericGridScalarSinglePosition] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridScalarSinglePosition
        ),
        metadata={
            "imas_type": "generic_grid_scalar_single_position",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalarSinglePosition,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class EdgeProfilesTimeSliceElectrons(IdsBaseClass):
    """

    :ivar temperature : Temperature, given on various grid subsets
    :ivar density : Density (thermal+non-thermal), given on various grid subsets
    :ivar density_fast : Density of fast (non-thermal) particles, given on various grid subsets
    :ivar pressure : Pressure, given on various grid subsets
    :ivar pressure_fast_perpendicular : Fast (non-thermal) perpendicular pressure, given on various grid subsets
    :ivar pressure_fast_parallel : Fast (non-thermal) parallel pressure, given on various grid subsets
    :ivar velocity : Velocity, given on various grid subsets
    :ivar distribution_function : Distribution function, given on various grid subsets
    """

    class Meta:
        name = "edge_profiles_time_slice_electrons"
        is_root_ids = False

    temperature: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    density: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    density_fast: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    pressure: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    pressure_fast_perpendicular: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    pressure_fast_parallel: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    velocity: Optional[GenericGridVectorComponents] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridVectorComponents
        ),
        metadata={
            "imas_type": "generic_grid_vector_components",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridVectorComponents,
        },
    )
    distribution_function: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class EdgeProfilesGgdFastElectrons(IdsBaseClass):
    """

    :ivar temperature : Temperature, given at various positions (grid subset of size 1)
    :ivar density : Density (thermal+non-thermal), given at various positions (grid subset of size 1)
    """

    class Meta:
        name = "edge_profiles_ggd_fast_electrons"
        is_root_ids = False

    temperature: Optional[GenericGridScalarSinglePosition] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridScalarSinglePosition
        ),
        metadata={
            "imas_type": "generic_grid_scalar_single_position",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalarSinglePosition,
        },
    )
    density: Optional[GenericGridScalarSinglePosition] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridScalarSinglePosition
        ),
        metadata={
            "imas_type": "generic_grid_scalar_single_position",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalarSinglePosition,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class EdgeProfilesTimeSlice(IdsBaseClass):
    """

    :ivar electrons : Quantities related to the electrons
    :ivar ion : Quantities related to the different ion species
    :ivar neutral : Quantities related to the different neutral species
    :ivar t_i_average : Ion temperature (averaged on ion species), given on various grid subsets
    :ivar n_i_total_over_n_e : Ratio of total ion density (sum over ion species) over electron density. (thermal+non-thermal), given on various grid subsets
    :ivar zeff : Effective charge, given on various grid subsets
    :ivar pressure_thermal : Thermal pressure (electrons+ions), given on various grid subsets
    :ivar pressure_perpendicular : Total perpendicular pressure (electrons+ions, thermal+non-thermal), given on various grid subsets
    :ivar pressure_parallel : Total parallel pressure (electrons+ions, thermal+non-thermal), given on various grid subsets
    :ivar j_total : Total current density, given on various grid subsets
    :ivar j_parallel : Current due to parallel electric and thermo-electric conductivity and potential and electron temperature gradients along the field line, differences away from ambipolar flow in the parallel direction between ions and electrons (this is not the parallel component of j_total)
    :ivar j_anomalous : Anomalous current density, given on various grid subsets
    :ivar j_inertial : Inertial current density, given on various grid subsets
    :ivar j_ion_neutral_friction : Current density due to ion neutral friction, given on various grid subsets
    :ivar j_parallel_viscosity : Current density due to the parallel viscosity, given on various grid subsets
    :ivar j_perpendicular_viscosity : Current density due to the perpendicular viscosity, given on various grid subsets
    :ivar j_heat_viscosity : Current density due to the heat viscosity, given on various grid subsets
    :ivar j_pfirsch_schlueter : Current density due to Pfirsch-Schlüter effects, given on various grid subsets
    :ivar j_diamagnetic : Current density due to the diamgnetic drift, given on various grid subsets
    :ivar e_field : Electric field, given on various grid subsets
    :ivar phi_potential : Electric potential, given on various grid subsets
    :ivar a_field_parallel : Parallel (to the local magnetic field) component of the magnetic vector potential, given on various grid subsets
    :ivar time : Time
    """

    class Meta:
        name = "edge_profiles_time_slice"
        is_root_ids = False

    electrons: Optional[EdgeProfilesTimeSliceElectrons] = field(
        default=None,
        metadata={
            "imas_type": "edge_profiles_time_slice_electrons",
            "field_type": EdgeProfilesTimeSliceElectrons,
        },
    )
    ion: Optional[EdgeProfilesTimeSliceIon] = field(
        default_factory=lambda: StructArray(
            type_input=EdgeProfilesTimeSliceIon
        ),
        metadata={
            "imas_type": "edge_profiles_time_slice_ion",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": EdgeProfilesTimeSliceIon,
        },
    )
    neutral: Optional[EdgeProfilesTimeSliceNeutral] = field(
        default_factory=lambda: StructArray(
            type_input=EdgeProfilesTimeSliceNeutral
        ),
        metadata={
            "imas_type": "edge_profiles_time_slice_neutral",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": EdgeProfilesTimeSliceNeutral,
        },
    )
    t_i_average: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    n_i_total_over_n_e: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    zeff: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    pressure_thermal: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    pressure_perpendicular: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    pressure_parallel: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    j_total: Optional[GenericGridVectorComponents] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridVectorComponents
        ),
        metadata={
            "imas_type": "generic_grid_vector_components",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridVectorComponents,
        },
    )
    j_parallel: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    j_anomalous: Optional[GenericGridVectorComponents] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridVectorComponents
        ),
        metadata={
            "imas_type": "generic_grid_vector_components",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridVectorComponents,
        },
    )
    j_inertial: Optional[GenericGridVectorComponents] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridVectorComponents
        ),
        metadata={
            "imas_type": "generic_grid_vector_components",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridVectorComponents,
        },
    )
    j_ion_neutral_friction: Optional[GenericGridVectorComponents] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridVectorComponents
        ),
        metadata={
            "imas_type": "generic_grid_vector_components",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridVectorComponents,
        },
    )
    j_parallel_viscosity: Optional[GenericGridVectorComponents] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridVectorComponents
        ),
        metadata={
            "imas_type": "generic_grid_vector_components",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridVectorComponents,
        },
    )
    j_perpendicular_viscosity: Optional[GenericGridVectorComponents] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridVectorComponents
        ),
        metadata={
            "imas_type": "generic_grid_vector_components",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridVectorComponents,
        },
    )
    j_heat_viscosity: Optional[GenericGridVectorComponents] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridVectorComponents
        ),
        metadata={
            "imas_type": "generic_grid_vector_components",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridVectorComponents,
        },
    )
    j_pfirsch_schlueter: Optional[GenericGridVectorComponents] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridVectorComponents
        ),
        metadata={
            "imas_type": "generic_grid_vector_components",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridVectorComponents,
        },
    )
    j_diamagnetic: Optional[GenericGridVectorComponents] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridVectorComponents
        ),
        metadata={
            "imas_type": "generic_grid_vector_components",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridVectorComponents,
        },
    )
    e_field: Optional[GenericGridVectorComponents] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridVectorComponents
        ),
        metadata={
            "imas_type": "generic_grid_vector_components",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridVectorComponents,
        },
    )
    phi_potential: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    a_field_parallel: Optional[GenericGridScalar] = field(
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
class EdgeProfilesGgdFast(IdsBaseClass):
    """

    :ivar electrons : Quantities related to the electrons
    :ivar ion : Quantities related to the different ion species
    :ivar energy_thermal : Plasma energy content = 3/2 * integral over the volume of the grid subset of the thermal pressure (summed over all species), for various grid subsets
    :ivar time : Time
    """

    class Meta:
        name = "edge_profiles_ggd_fast"
        is_root_ids = False

    electrons: Optional[EdgeProfilesGgdFastElectrons] = field(
        default=None,
        metadata={
            "imas_type": "edge_profiles_ggd_fast_electrons",
            "field_type": EdgeProfilesGgdFastElectrons,
        },
    )
    ion: Optional[EdgeProfilesGgdFastIon] = field(
        default_factory=lambda: StructArray(type_input=EdgeProfilesGgdFastIon),
        metadata={
            "imas_type": "edge_profiles_ggd_fast_ion",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": EdgeProfilesGgdFastIon,
        },
    )
    energy_thermal: Optional[GenericGridScalarSinglePosition] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridScalarSinglePosition
        ),
        metadata={
            "imas_type": "generic_grid_scalar_single_position",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalarSinglePosition,
        },
    )
    time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class EdgeProfiles(IdsBaseClass):
    """

    :ivar ids_properties :
    :ivar vacuum_toroidal_field : Characteristics of the vacuum toroidal field (used in rho_tor definition and in the normalization of current densities)
    :ivar midplane : Choice of midplane definition (use the lowest index number if more than one value is relevant)
    :ivar profiles_1d : SOL radial profiles for various time slices, taken on outboard equatorial mid-plane
    :ivar grid_ggd : Grid (using the Generic Grid Description), for various time slices. The timebase of this array of structure must be a subset of the ggd timebase
    :ivar ggd : Edge plasma quantities represented using the general grid description, for various time slices. The timebase of this array of structure must be a subset of the ggd_fast timebase (only if the ggd_fast array of structure is used)
    :ivar ggd_fast : Quantities provided at a faster sampling rate than the full ggd quantities. These are either integrated quantities or local quantities provided on a reduced set of positions. Positions and integration domains are described by a set of grid_subsets (of size 1 for a position).
    :ivar statistics : Statistics for various time slices
    :ivar code :
    :ivar time : Generic time
    """

    class Meta:
        name = "edge_profiles"
        is_root_ids = True

    ids_properties: Optional[IdsProperties] = field(
        default=None,
        metadata={"imas_type": "ids_properties", "field_type": IdsProperties},
    )
    vacuum_toroidal_field: Optional[BTorVacuum1] = field(
        default=None,
        metadata={"imas_type": "b_tor_vacuum_1", "field_type": BTorVacuum1},
    )
    midplane: Optional[IdentifierStatic] = field(
        default=None,
        metadata={
            "imas_type": "identifier_static",
            "field_type": IdentifierStatic,
        },
    )
    profiles_1d: Optional[EdgeProfilesProfiles1D] = field(
        default_factory=lambda: StructArray(type_input=EdgeProfilesProfiles1D),
        metadata={
            "imas_type": "edge_profiles_profiles_1d",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": EdgeProfilesProfiles1D,
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
    ggd: Optional[EdgeProfilesTimeSlice] = field(
        default_factory=lambda: StructArray(type_input=EdgeProfilesTimeSlice),
        metadata={
            "imas_type": "edge_profiles_time_slice",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": EdgeProfilesTimeSlice,
        },
    )
    ggd_fast: Optional[EdgeProfilesGgdFast] = field(
        default_factory=lambda: StructArray(type_input=EdgeProfilesGgdFast),
        metadata={
            "imas_type": "edge_profiles_ggd_fast",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": EdgeProfilesGgdFast,
        },
    )
    statistics: Optional[Statistics] = field(
        default_factory=lambda: StructArray(type_input=Statistics),
        metadata={
            "imas_type": "statistics",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": Statistics,
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
