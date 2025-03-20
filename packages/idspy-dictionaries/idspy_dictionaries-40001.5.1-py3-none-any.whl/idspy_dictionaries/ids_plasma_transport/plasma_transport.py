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
class PlasmaRadialGrid(IdsBaseClass):
    """

    :ivar rho_pol_norm : Normalised poloidal flux coordinate = sqrt((psi(rho)-psi(magnetic_axis) / (psi(LCFS)-psi(magnetic_axis)))
    :ivar psi : Poloidal magnetic flux. Integral of magnetic field passing through a contour defined by the intersection of a flux surface passing through the point of interest and a Z=constant plane. If the integration surface is flat, the surface normal vector is in the increasing vertical coordinate direction, Z, namely upwards.
    :ivar rho_tor_norm : Normalised toroidal flux coordinate. The normalizing value for rho_tor_norm, is the toroidal flux coordinate at the equilibrium boundary (LCFS or 99.x % of the LCFS in case of a fixed boundary equilibium calculation, see time_slice/boundary/b_flux_pol_norm in the equilibrium IDS)
    :ivar rho_tor : Toroidal flux coordinate. rho_tor = sqrt(b_flux_tor/(pi*b0)) ~ sqrt(pi*r^2*b0/(pi*b0)) ~ r [m]. The toroidal field used in its definition is indicated under vacuum_toroidal_field/b0
    :ivar volume : Volume enclosed inside the magnetic surface
    :ivar area : Cross-sectional area of the flux surface
    :ivar surface : Surface area of the toroidal flux surface
    :ivar psi_magnetic_axis : Value of the poloidal magnetic flux at the magnetic axis (useful to normalize the psi array values when the radial grid doesn&#39;t go from the magnetic axis to the plasma boundary)
    :ivar psi_boundary : Value of the poloidal magnetic flux at the plasma boundary (useful to normalize the psi array values when the radial grid doesn&#39;t go from the magnetic axis to the plasma boundary)
    """

    class Meta:
        name = "plasma_radial_grid"
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
    surface: Optional[np.ndarray] = field(
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
class PlasmaTransportModel1Density(IdsBaseClass):
    """

    :ivar d : Effective diffusivity
    :ivar v : Effective convection
    :ivar flux : Flux
    """

    class Meta:
        name = "plasma_transport_model_1_density"
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
class PlasmaTransportModel1Energy(IdsBaseClass):
    """

    :ivar d : Effective diffusivity
    :ivar v : Effective convection
    :ivar flux : Flux
    """

    class Meta:
        name = "plasma_transport_model_1_energy"
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
class PlasmaTransportModel1Momentum(IdsBaseClass):
    """

    :ivar d : Effective diffusivity
    :ivar v : Effective convection
    :ivar flux : Flux
    """

    class Meta:
        name = "plasma_transport_model_1_momentum"
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
class PlasmaTransportModel2Density(IdsBaseClass):
    """

    :ivar d : Effective diffusivity
    :ivar v : Effective convection
    :ivar flux : Flux
    """

    class Meta:
        name = "plasma_transport_model_2_density"
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
class PlasmaTransportModel2Energy(IdsBaseClass):
    """

    :ivar d : Effective diffusivity
    :ivar v : Effective convection
    :ivar flux : Flux
    """

    class Meta:
        name = "plasma_transport_model_2_energy"
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
class PlasmaTransportModel3Density(IdsBaseClass):
    """

    :ivar d : Effective diffusivity
    :ivar v : Effective convection
    :ivar flux : Flux
    """

    class Meta:
        name = "plasma_transport_model_3_density"
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
class PlasmaTransportModel3Energy(IdsBaseClass):
    """

    :ivar d : Effective diffusivity
    :ivar v : Effective convection
    :ivar flux : Flux
    """

    class Meta:
        name = "plasma_transport_model_3_energy"
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
class PlasmaTransportModel3Momentum(IdsBaseClass):
    """

    :ivar d : Effective diffusivity
    :ivar v : Effective convection
    :ivar flux : Flux
    :ivar flow_damping_rate : Damping rate for this flow component (e.g. due to collisions, calculated from a neoclassical model)
    """

    class Meta:
        name = "plasma_transport_model_3_momentum"
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
class PlasmaTransportModelComponents3Momentum(IdsBaseClass):
    """

    :ivar radial : Radial component
    :ivar diamagnetic : Diamagnetic component
    :ivar parallel : Parallel component
    :ivar poloidal : Poloidal component
    :ivar toroidal : Toroidal component
    """

    class Meta:
        name = "plasma_transport_model_components_3_momentum"
        is_root_ids = False

    radial: Optional[PlasmaTransportModel3Momentum] = field(
        default=None,
        metadata={
            "imas_type": "plasma_transport_model_3_momentum",
            "field_type": PlasmaTransportModel3Momentum,
        },
    )
    diamagnetic: Optional[PlasmaTransportModel3Momentum] = field(
        default=None,
        metadata={
            "imas_type": "plasma_transport_model_3_momentum",
            "field_type": PlasmaTransportModel3Momentum,
        },
    )
    parallel: Optional[PlasmaTransportModel3Momentum] = field(
        default=None,
        metadata={
            "imas_type": "plasma_transport_model_3_momentum",
            "field_type": PlasmaTransportModel3Momentum,
        },
    )
    poloidal: Optional[PlasmaTransportModel3Momentum] = field(
        default=None,
        metadata={
            "imas_type": "plasma_transport_model_3_momentum",
            "field_type": PlasmaTransportModel3Momentum,
        },
    )
    toroidal: Optional[PlasmaTransportModel3Momentum] = field(
        default=None,
        metadata={
            "imas_type": "plasma_transport_model_3_momentum",
            "field_type": PlasmaTransportModel3Momentum,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class PlasmaTransportModel4Momentum(IdsBaseClass):
    """

    :ivar d : Effective diffusivity
    :ivar v : Effective convection
    :ivar flux : Flux
    :ivar flow_damping_rate : Damping rate for this flow component (e.g. due to collisions, calculated from a neoclassical model)
    """

    class Meta:
        name = "plasma_transport_model_4_momentum"
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
class PlasmaTransportModelComponents4Momentum(IdsBaseClass):
    """

    :ivar radial : Radial component
    :ivar diamagnetic : Diamagnetic component
    :ivar parallel : Parallel component
    :ivar poloidal : Poloidal component
    :ivar toroidal : Toroidal component
    """

    class Meta:
        name = "plasma_transport_model_components_4_momentum"
        is_root_ids = False

    radial: Optional[PlasmaTransportModel4Momentum] = field(
        default=None,
        metadata={
            "imas_type": "plasma_transport_model_4_momentum",
            "field_type": PlasmaTransportModel4Momentum,
        },
    )
    diamagnetic: Optional[PlasmaTransportModel4Momentum] = field(
        default=None,
        metadata={
            "imas_type": "plasma_transport_model_4_momentum",
            "field_type": PlasmaTransportModel4Momentum,
        },
    )
    parallel: Optional[PlasmaTransportModel4Momentum] = field(
        default=None,
        metadata={
            "imas_type": "plasma_transport_model_4_momentum",
            "field_type": PlasmaTransportModel4Momentum,
        },
    )
    poloidal: Optional[PlasmaTransportModel4Momentum] = field(
        default=None,
        metadata={
            "imas_type": "plasma_transport_model_4_momentum",
            "field_type": PlasmaTransportModel4Momentum,
        },
    )
    toroidal: Optional[PlasmaTransportModel4Momentum] = field(
        default=None,
        metadata={
            "imas_type": "plasma_transport_model_4_momentum",
            "field_type": PlasmaTransportModel4Momentum,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class PlasmaTransportModelIonsChargeStates(IdsBaseClass):
    """

    :ivar z_min : Minimum Z of the charge state bundle
    :ivar z_max : Maximum Z of the charge state bundle
    :ivar label : String identifying charge state (e.g. C+, C+2 , C+3, C+4, C+5, C+6, ...)
    :ivar vibrational_level : Vibrational level (can be bundled)
    :ivar vibrational_mode : Vibrational mode of this state, e.g. &#34;A_g&#34;. Need to define, or adopt a standard nomenclature.
    :ivar electron_configuration : Configuration of atomic orbitals of this state, e.g. 1s2-2s1
    :ivar particles : Transport quantities related to density equation of the charge state considered (thermal+non-thermal)
    :ivar energy : Transport quantities related to the energy equation of the charge state considered
    :ivar momentum : Transport coefficients related to the state momentum equations for various components (directions)
    """

    class Meta:
        name = "plasma_transport_model_ions_charge_states"
        is_root_ids = False

    z_min: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    z_max: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    label: Optional[str] = field(
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
    particles: Optional[PlasmaTransportModel3Density] = field(
        default=None,
        metadata={
            "imas_type": "plasma_transport_model_3_density",
            "field_type": PlasmaTransportModel3Density,
        },
    )
    energy: Optional[PlasmaTransportModel3Energy] = field(
        default=None,
        metadata={
            "imas_type": "plasma_transport_model_3_energy",
            "field_type": PlasmaTransportModel3Energy,
        },
    )
    momentum: Optional[PlasmaTransportModelComponents4Momentum] = field(
        default=None,
        metadata={
            "imas_type": "plasma_transport_model_components_4_momentum",
            "field_type": PlasmaTransportModelComponents4Momentum,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class PlasmaTransportModelNeutralState(IdsBaseClass):
    """

    :ivar label : String identifying state
    :ivar vibrational_level : Vibrational level (can be bundled)
    :ivar vibrational_mode : Vibrational mode of this state, e.g. &#34;A_g&#34;. Need to define, or adopt a standard nomenclature.
    :ivar electron_configuration : Configuration of atomic orbitals of this state, e.g. 1s2-2s1
    :ivar particles : Transport quantities related to density equation of the charge state considered (thermal+non-thermal)
    :ivar energy : Transport quantities related to the energy equation of the charge state considered
    """

    class Meta:
        name = "plasma_transport_model_neutral_state"
        is_root_ids = False

    label: Optional[str] = field(
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
    particles: Optional[PlasmaTransportModel3Density] = field(
        default=None,
        metadata={
            "imas_type": "plasma_transport_model_3_density",
            "field_type": PlasmaTransportModel3Density,
        },
    )
    energy: Optional[PlasmaTransportModel3Energy] = field(
        default=None,
        metadata={
            "imas_type": "plasma_transport_model_3_energy",
            "field_type": PlasmaTransportModel3Energy,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class PlasmaTransportModelIons(IdsBaseClass):
    """

    :ivar element : List of elements forming the atom or molecule
    :ivar z_ion : Ion charge (of the dominant ionisation state; lumped ions are allowed)
    :ivar label : String identifying ion (e.g. H, D, T, He, C, D2, ...)
    :ivar neutral_index : Index of the corresponding neutral species in the ../../neutral array
    :ivar particles : Transport related to the ion density equation
    :ivar energy : Transport coefficients related to the ion energy equation
    :ivar momentum : Transport coefficients related to the ion momentum equations for various components (directions)
    :ivar multiple_states_flag : Multiple states calculation flag : 0-Only the &#39;ion&#39; level is considered and the &#39;state&#39; array of structure is empty; 1-Ion states are considered and are described in the &#39;state&#39; array of structure
    :ivar state : Transport coefficients related to the different states of the species
    """

    class Meta:
        name = "plasma_transport_model_ions"
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
    label: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    neutral_index: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    particles: Optional[PlasmaTransportModel2Density] = field(
        default=None,
        metadata={
            "imas_type": "plasma_transport_model_2_density",
            "field_type": PlasmaTransportModel2Density,
        },
    )
    energy: Optional[PlasmaTransportModel2Energy] = field(
        default=None,
        metadata={
            "imas_type": "plasma_transport_model_2_energy",
            "field_type": PlasmaTransportModel2Energy,
        },
    )
    momentum: Optional[PlasmaTransportModelComponents3Momentum] = field(
        default=None,
        metadata={
            "imas_type": "plasma_transport_model_components_3_momentum",
            "field_type": PlasmaTransportModelComponents3Momentum,
        },
    )
    multiple_states_flag: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    state: Optional[PlasmaTransportModelIonsChargeStates] = field(
        default_factory=lambda: StructArray(
            type_input=PlasmaTransportModelIonsChargeStates
        ),
        metadata={
            "imas_type": "plasma_transport_model_ions_charge_states",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": PlasmaTransportModelIonsChargeStates,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class PlasmaTransportModelNeutral(IdsBaseClass):
    """

    :ivar element : List of elements forming the atom or molecule
    :ivar label : String identifying ion (e.g. H+, D+, T+, He+2, C+, ...)
    :ivar ion_index : Index of the corresponding ion species in the ../../ion array
    :ivar particles : Transport related to the neutral density equation
    :ivar energy : Transport coefficients related to the neutral energy equation
    :ivar multiple_states_flag : Multiple states calculation flag : 0-Only one state is considered; 1-Multiple states are considered and are described in the state structure
    :ivar state : Transport coefficients related to the different states of the species
    """

    class Meta:
        name = "plasma_transport_model_neutral"
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
    label: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    ion_index: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    particles: Optional[PlasmaTransportModel2Density] = field(
        default=None,
        metadata={
            "imas_type": "plasma_transport_model_2_density",
            "field_type": PlasmaTransportModel2Density,
        },
    )
    energy: Optional[PlasmaTransportModel2Energy] = field(
        default=None,
        metadata={
            "imas_type": "plasma_transport_model_2_energy",
            "field_type": PlasmaTransportModel2Energy,
        },
    )
    multiple_states_flag: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    state: Optional[PlasmaTransportModelNeutralState] = field(
        default_factory=lambda: StructArray(
            type_input=PlasmaTransportModelNeutralState
        ),
        metadata={
            "imas_type": "plasma_transport_model_neutral_state",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": PlasmaTransportModelNeutralState,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class PlasmaTransportModelElectrons(IdsBaseClass):
    """

    :ivar particles : Transport quantities for the electron density equation
    :ivar energy : Transport quantities for the electron energy equation
    """

    class Meta:
        name = "plasma_transport_model_electrons"
        is_root_ids = False

    particles: Optional[PlasmaTransportModel2Density] = field(
        default=None,
        metadata={
            "imas_type": "plasma_transport_model_2_density",
            "field_type": PlasmaTransportModel2Density,
        },
    )
    energy: Optional[PlasmaTransportModel2Energy] = field(
        default=None,
        metadata={
            "imas_type": "plasma_transport_model_2_energy",
            "field_type": PlasmaTransportModel2Energy,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class PlasmaTransportModelProfiles1D(IdsBaseClass):
    """

    :ivar grid_d : Grid for effective diffusivities and parallel conductivity. Note that some of the radial coordinates listed above are undefined outside the last closed flux surface, thus they must be filled with EMPTY_FLOAT values in such locations
    :ivar grid_v : Grid for effective convections. Note that some of the radial coordinates listed above are undefined outside the last closed flux surface, thus they must be filled with EMPTY_FLOAT values in such locations
    :ivar grid_flux : Grid for fluxes. Note that some of the radial coordinates listed above are undefined outside the last closed flux surface, thus they must be filled with EMPTY_FLOAT values in such locations
    :ivar conductivity_parallel : Parallel conductivity
    :ivar electrons : Transport quantities related to the electrons
    :ivar total_ion_energy : Transport coefficients for the total (summed over ion  species) energy equation
    :ivar momentum_phi : Transport coefficients for total toroidal momentum equation
    :ivar e_field_radial : Radial component of the electric field (calculated e.g. by a neoclassical model)
    :ivar ion : Transport coefficients related to the various ion species, in the sense of isonuclear or isomolecular sequences. Ionisation states (and other types of states) must be differentiated at the state level below
    :ivar neutral : Transport coefficients related to the various neutral species
    :ivar time : Time
    """

    class Meta:
        name = "plasma_transport_model_profiles_1d"
        is_root_ids = False

    grid_d: Optional[PlasmaRadialGrid] = field(
        default=None,
        metadata={
            "imas_type": "plasma_radial_grid",
            "field_type": PlasmaRadialGrid,
        },
    )
    grid_v: Optional[PlasmaRadialGrid] = field(
        default=None,
        metadata={
            "imas_type": "plasma_radial_grid",
            "field_type": PlasmaRadialGrid,
        },
    )
    grid_flux: Optional[PlasmaRadialGrid] = field(
        default=None,
        metadata={
            "imas_type": "plasma_radial_grid",
            "field_type": PlasmaRadialGrid,
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
    electrons: Optional[PlasmaTransportModelElectrons] = field(
        default=None,
        metadata={
            "imas_type": "plasma_transport_model_electrons",
            "field_type": PlasmaTransportModelElectrons,
        },
    )
    total_ion_energy: Optional[PlasmaTransportModel1Energy] = field(
        default=None,
        metadata={
            "imas_type": "plasma_transport_model_1_energy",
            "field_type": PlasmaTransportModel1Energy,
        },
    )
    momentum_phi: Optional[PlasmaTransportModel1Momentum] = field(
        default=None,
        metadata={
            "imas_type": "plasma_transport_model_1_momentum",
            "field_type": PlasmaTransportModel1Momentum,
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
    ion: Optional[PlasmaTransportModelIons] = field(
        default_factory=lambda: StructArray(
            type_input=PlasmaTransportModelIons
        ),
        metadata={
            "imas_type": "plasma_transport_model_ions",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": PlasmaTransportModelIons,
        },
    )
    neutral: Optional[PlasmaTransportModelNeutral] = field(
        default_factory=lambda: StructArray(
            type_input=PlasmaTransportModelNeutral
        ),
        metadata={
            "imas_type": "plasma_transport_model_neutral",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": PlasmaTransportModelNeutral,
        },
    )
    time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class PlasmaTransportModelEnergy(IdsBaseClass):
    """

    :ivar d : Effective diffusivity, on various grid subsets
    :ivar v : Effective convection, on various grid subsets
    :ivar flux : Flux, on various grid subsets
    :ivar flux_limiter : Flux limiter coefficient, on various grid subsets
    :ivar d_radial : Effective diffusivity (in the radial direction), on various grid subsets
    :ivar v_radial : Effective convection (in the radial direction), on various grid subsets
    :ivar flux_radial : Flux in the radial direction, on various grid subsets
    :ivar d_pol : Effective diffusivity (in the poloidal direction), on various grid subsets
    :ivar v_pol : Effective convection (in the poloidal direction), on various grid subsets
    :ivar flux_pol : Flux in the poloidal direction, on various grid subsets
    """

    class Meta:
        name = "plasma_transport_model_energy"
        is_root_ids = False

    d: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    v: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    flux: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    flux_limiter: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    d_radial: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    v_radial: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    flux_radial: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    d_pol: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    v_pol: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    flux_pol: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class PlasmaTransportModelMomentum(IdsBaseClass):
    """

    :ivar d : Effective diffusivity, on various grid subsets
    :ivar v : Effective convection, on various grid subsets
    :ivar flux : Flux, on various grid subsets
    :ivar flux_limiter : Flux limiter coefficient, on various grid subsets
    :ivar d_radial : Effective diffusivity (in the radial direction), on various grid subsets
    :ivar v_radial : Effective convection (in the radial direction), on various grid subsets
    :ivar flux_radial : Flux in the radial direction, on various grid subsets
    :ivar d_pol : Effective diffusivity (in the poloidal direction), on various grid subsets
    :ivar v_pol : Effective convection (in the poloidal direction), on various grid subsets
    :ivar flux_pol : Flux in the poloidal direction, on various grid subsets
    """

    class Meta:
        name = "plasma_transport_model_momentum"
        is_root_ids = False

    d: Optional[GenericGridVectorComponents] = field(
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
    v: Optional[GenericGridVectorComponents] = field(
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
    flux: Optional[GenericGridVectorComponents] = field(
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
    flux_limiter: Optional[GenericGridVectorComponents] = field(
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
    d_radial: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    v_radial: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    flux_radial: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    d_pol: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    v_pol: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    flux_pol: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class PlasmaTransportModelDensity(IdsBaseClass):
    """

    :ivar d : Effective diffusivity (in the direction perpendicular to the edge of faces of the grid), on various grid subsets
    :ivar v : Effective convection (in the direction perpendicular to the edge of faces of the grid), on various grid subsets
    :ivar flux : Flux in the direction perpendicular to the edges or faces of the grid (flow crossing that surface divided by its actual area), on various grid subsets
    :ivar flux_limiter : Flux limiter coefficient, on various grid subsets
    :ivar d_radial : Effective diffusivity (in the radial direction), on various grid subsets
    :ivar v_radial : Effective convection (in the radial direction), on various grid subsets
    :ivar flux_radial : Flux in the radial direction, on various grid subsets
    :ivar d_pol : Effective diffusivity (in the poloidal direction), on various grid subsets
    :ivar v_pol : Effective convection (in the poloidal direction), on various grid subsets
    :ivar flux_pol : Flux in the poloidal direction, on various grid subsets
    """

    class Meta:
        name = "plasma_transport_model_density"
        is_root_ids = False

    d: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    v: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    flux: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    flux_limiter: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    d_radial: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    v_radial: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    flux_radial: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    d_pol: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    v_pol: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    flux_pol: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class PlasmaTransportModelGgdNeutralState(IdsBaseClass):
    """

    :ivar label : String identifying state
    :ivar vibrational_level : Vibrational level (can be bundled)
    :ivar vibrational_mode : Vibrational mode of this state, e.g. &#34;A_g&#34;. Need to define, or adopt a standard nomenclature.
    :ivar neutral_type : Neutral type, in terms of energy. ID =1: cold; 2: thermal; 3: fast; 4: NBI
    :ivar electron_configuration : Configuration of atomic orbitals of this state, e.g. 1s2-2s1
    :ivar particles : Transport quantities related to density equation of the state considered (thermal+non-thermal)
    :ivar energy : Transport quantities related to the energy equation of the state considered
    :ivar momentum : Transport coefficients related to the momentum equations of the state considered. The various components two levels below this node refer to the momentum vector components, while their flux is given in the direction perpendicular to the edges or faces of the grid.
    """

    class Meta:
        name = "plasma_transport_model_ggd_neutral_state"
        is_root_ids = False

    label: Optional[str] = field(
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
    particles: Optional[PlasmaTransportModelDensity] = field(
        default=None,
        metadata={
            "imas_type": "plasma_transport_model_density",
            "field_type": PlasmaTransportModelDensity,
        },
    )
    energy: Optional[PlasmaTransportModelEnergy] = field(
        default=None,
        metadata={
            "imas_type": "plasma_transport_model_energy",
            "field_type": PlasmaTransportModelEnergy,
        },
    )
    momentum: Optional[PlasmaTransportModelMomentum] = field(
        default=None,
        metadata={
            "imas_type": "plasma_transport_model_momentum",
            "field_type": PlasmaTransportModelMomentum,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class PlasmaTransportModelGgdIonState(IdsBaseClass):
    """

    :ivar z_min : Minimum Z of the state bundle
    :ivar z_max : Maximum Z of the state bundle
    :ivar label : String identifying state (e.g. C+, C+2 , C+3, C+4, C+5, C+6, ...)
    :ivar vibrational_level : Vibrational level (can be bundled)
    :ivar vibrational_mode : Vibrational mode of this state, e.g. &#34;A_g&#34;. Need to define, or adopt a standard nomenclature.
    :ivar electron_configuration : Configuration of atomic orbitals of this state, e.g. 1s2-2s1
    :ivar particles : Transport quantities related to density equation of the state considered (thermal+non-thermal)
    :ivar energy : Transport quantities related to the energy equation of the state considered
    :ivar momentum : Transport coefficients related to the momentum equations of the state considered. The various components two levels below this node refer to the momentum vector components, while their flux is given in the direction perpendicular to the edges or faces of the grid.
    """

    class Meta:
        name = "plasma_transport_model_ggd_ion_state"
        is_root_ids = False

    z_min: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    z_max: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    label: Optional[str] = field(
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
    particles: Optional[PlasmaTransportModelDensity] = field(
        default=None,
        metadata={
            "imas_type": "plasma_transport_model_density",
            "field_type": PlasmaTransportModelDensity,
        },
    )
    energy: Optional[PlasmaTransportModelEnergy] = field(
        default=None,
        metadata={
            "imas_type": "plasma_transport_model_energy",
            "field_type": PlasmaTransportModelEnergy,
        },
    )
    momentum: Optional[PlasmaTransportModelMomentum] = field(
        default=None,
        metadata={
            "imas_type": "plasma_transport_model_momentum",
            "field_type": PlasmaTransportModelMomentum,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class PlasmaTransportModelGgdNeutral(IdsBaseClass):
    """

    :ivar element : List of elements forming the atom or molecule
    :ivar label : String identifying neutral (e.g. H, D, T, He, C, ...)
    :ivar ion_index : Index of the corresponding ion species in the ../../ion array
    :ivar particles : Transport related to the ion density equation
    :ivar energy : Transport coefficients related to the ion energy equation
    :ivar momentum : Transport coefficients for the neutral momentum equations. The various components two levels below this node refer to the momentum vector components, while their flux is given in the direction perpendicular to the edges or faces of the grid.
    :ivar multiple_states_flag : Multiple states calculation flag : 0-Only one state is considered; 1-Multiple states are considered and are described in the state structure
    :ivar state : Transport coefficients related to the different states of the species
    """

    class Meta:
        name = "plasma_transport_model_ggd_neutral"
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
    label: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    ion_index: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    particles: Optional[PlasmaTransportModelDensity] = field(
        default=None,
        metadata={
            "imas_type": "plasma_transport_model_density",
            "field_type": PlasmaTransportModelDensity,
        },
    )
    energy: Optional[PlasmaTransportModelEnergy] = field(
        default=None,
        metadata={
            "imas_type": "plasma_transport_model_energy",
            "field_type": PlasmaTransportModelEnergy,
        },
    )
    momentum: Optional[PlasmaTransportModelMomentum] = field(
        default=None,
        metadata={
            "imas_type": "plasma_transport_model_momentum",
            "field_type": PlasmaTransportModelMomentum,
        },
    )
    multiple_states_flag: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    state: Optional[PlasmaTransportModelGgdNeutralState] = field(
        default_factory=lambda: StructArray(
            type_input=PlasmaTransportModelGgdNeutralState
        ),
        metadata={
            "imas_type": "plasma_transport_model_ggd_neutral_state",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": PlasmaTransportModelGgdNeutralState,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class PlasmaTransportModelGgdFastNeutral(IdsBaseClass):
    """

    :ivar element : List of elements forming the atom or molecule
    :ivar label : String identifying neutral (e.g. H, D, T, He, C, ...)
    :ivar ion_index : Index of the corresponding ion species in the ../../ion array
    :ivar particle_flux_integrated : Total number of particles of this species crossing a surface per unit time, for various surfaces (grid subsets)
    """

    class Meta:
        name = "plasma_transport_model_ggd_fast_neutral"
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
    label: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    ion_index: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    particle_flux_integrated: Optional[GenericGridScalarSinglePosition] = field(
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
class PlasmaTransportModelGgdIon(IdsBaseClass):
    """

    :ivar element : List of elements forming the atom or molecule
    :ivar z_ion : Ion charge (of the dominant ionisation state; lumped ions are allowed)
    :ivar label : String identifying ion (e.g. H, D, T, He, C, D2, ...)
    :ivar neutral_index : Index of the corresponding neutral species in the ../../neutral array
    :ivar particles : Transport related to the ion density equation
    :ivar energy : Transport coefficients related to the ion energy equation
    :ivar momentum : Transport coefficients for the ion momentum equations. The various components two levels below this node refer to the momentum vector components, while their flux is given in the direction perpendicular to the edges or faces of the grid.
    :ivar multiple_states_flag : Multiple states calculation flag : 0-Only the &#39;ion&#39; level is considered and the &#39;state&#39; array of structure is empty; 1-Ion states are considered and are described in the &#39;state&#39; array of structure
    :ivar state : Transport coefficients related to the different states of the species
    """

    class Meta:
        name = "plasma_transport_model_ggd_ion"
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
    label: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    neutral_index: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    particles: Optional[PlasmaTransportModelDensity] = field(
        default=None,
        metadata={
            "imas_type": "plasma_transport_model_density",
            "field_type": PlasmaTransportModelDensity,
        },
    )
    energy: Optional[PlasmaTransportModelEnergy] = field(
        default=None,
        metadata={
            "imas_type": "plasma_transport_model_energy",
            "field_type": PlasmaTransportModelEnergy,
        },
    )
    momentum: Optional[PlasmaTransportModelMomentum] = field(
        default=None,
        metadata={
            "imas_type": "plasma_transport_model_momentum",
            "field_type": PlasmaTransportModelMomentum,
        },
    )
    multiple_states_flag: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    state: Optional[PlasmaTransportModelGgdIonState] = field(
        default_factory=lambda: StructArray(
            type_input=PlasmaTransportModelGgdIonState
        ),
        metadata={
            "imas_type": "plasma_transport_model_ggd_ion_state",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": PlasmaTransportModelGgdIonState,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class PlasmaTransportModelGgdFastIon(IdsBaseClass):
    """

    :ivar element : List of elements forming the atom or molecule
    :ivar z_ion : Ion charge (of the dominant ionisation state; lumped ions are allowed)
    :ivar label : String identifying ion (e.g. H, D, T, He, C, D2, ...)
    :ivar neutral_index : Index of the corresponding neutral species in the ../../neutral array
    :ivar particle_flux_integrated : Total number of particles of this species crossing a surface per unit time, for various surfaces (grid subsets)
    """

    class Meta:
        name = "plasma_transport_model_ggd_fast_ion"
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
    label: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    neutral_index: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    particle_flux_integrated: Optional[GenericGridScalarSinglePosition] = field(
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
class PlasmaTransportModelGgdElectrons(IdsBaseClass):
    """

    :ivar particles : Transport quantities for the electron density equation
    :ivar energy : Transport quantities for the electron energy equation
    """

    class Meta:
        name = "plasma_transport_model_ggd_electrons"
        is_root_ids = False

    particles: Optional[PlasmaTransportModelDensity] = field(
        default=None,
        metadata={
            "imas_type": "plasma_transport_model_density",
            "field_type": PlasmaTransportModelDensity,
        },
    )
    energy: Optional[PlasmaTransportModelEnergy] = field(
        default=None,
        metadata={
            "imas_type": "plasma_transport_model_energy",
            "field_type": PlasmaTransportModelEnergy,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class PlasmaTransportModelGgdFastElectrons(IdsBaseClass):
    """

    :ivar particle_flux_integrated : Total number of particles of this species crossing a surface per unit time, for various surfaces (grid subsets)
    :ivar power : Power carried by this species crossing a surface, for various surfaces (grid subsets)
    """

    class Meta:
        name = "plasma_transport_model_ggd_fast_electrons"
        is_root_ids = False

    particle_flux_integrated: Optional[GenericGridScalarSinglePosition] = field(
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
    power: Optional[GenericGridScalarSinglePosition] = field(
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
class PlasmaTransportModelGgdFast(IdsBaseClass):
    """

    :ivar electrons : Transport quantities and flux integrals related to the electrons
    :ivar ion : Transport coefficients and flux integrals related to the various ion species, in the sense of isonuclear or isomolecular sequences. Ionisation states (and other types of states) must be differentiated at the state level below
    :ivar neutral : Transport coefficients and flux integrals related to the various ion and neutral species
    :ivar power_ion_total : Power carried by all ions (sum over ions species) crossing a surface, for various surfaces (grid subsets)
    :ivar energy_flux_max : Maximum power density over a surface, for various surfaces (grid subsets)
    :ivar power : Power (sum over all species) crossing a surface, for various surfaces (grid subsets)
    :ivar time : Time
    """

    class Meta:
        name = "plasma_transport_model_ggd_fast"
        is_root_ids = False

    electrons: Optional[PlasmaTransportModelGgdFastElectrons] = field(
        default=None,
        metadata={
            "imas_type": "plasma_transport_model_ggd_fast_electrons",
            "field_type": PlasmaTransportModelGgdFastElectrons,
        },
    )
    ion: Optional[PlasmaTransportModelGgdFastIon] = field(
        default_factory=lambda: StructArray(
            type_input=PlasmaTransportModelGgdFastIon
        ),
        metadata={
            "imas_type": "plasma_transport_model_ggd_fast_ion",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": PlasmaTransportModelGgdFastIon,
        },
    )
    neutral: Optional[PlasmaTransportModelGgdFastNeutral] = field(
        default_factory=lambda: StructArray(
            type_input=PlasmaTransportModelGgdFastNeutral
        ),
        metadata={
            "imas_type": "plasma_transport_model_ggd_fast_neutral",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": PlasmaTransportModelGgdFastNeutral,
        },
    )
    power_ion_total: Optional[GenericGridScalarSinglePosition] = field(
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
    energy_flux_max: Optional[GenericGridScalarSinglePosition] = field(
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
    power: Optional[GenericGridScalarSinglePosition] = field(
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
class PlasmaTransportModelGgd(IdsBaseClass):
    """

    :ivar conductivity : Conductivity, on various grid subsets
    :ivar electrons : Transport quantities related to the electrons
    :ivar total_ion_energy : Transport coefficients for the total (summed over ion  species) energy equation
    :ivar momentum : Transport coefficients for total momentum equation. The various components two levels below this node refer to the momentum vector components, while their flux is given in the direction perpendicular to the edges or faces of the grid.
    :ivar ion : Transport coefficients related to the various ion species, in the sense of isonuclear or isomolecular sequences. Ionisation states (and other types of states) must be differentiated at the state level below
    :ivar neutral : Transport coefficients related to the various neutral species
    :ivar time : Time
    """

    class Meta:
        name = "plasma_transport_model_ggd"
        is_root_ids = False

    conductivity: Optional[GenericGridVectorComponents] = field(
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
    electrons: Optional[PlasmaTransportModelGgdElectrons] = field(
        default=None,
        metadata={
            "imas_type": "plasma_transport_model_ggd_electrons",
            "field_type": PlasmaTransportModelGgdElectrons,
        },
    )
    total_ion_energy: Optional[PlasmaTransportModelEnergy] = field(
        default=None,
        metadata={
            "imas_type": "plasma_transport_model_energy",
            "field_type": PlasmaTransportModelEnergy,
        },
    )
    momentum: Optional[PlasmaTransportModelMomentum] = field(
        default=None,
        metadata={
            "imas_type": "plasma_transport_model_momentum",
            "field_type": PlasmaTransportModelMomentum,
        },
    )
    ion: Optional[PlasmaTransportModelGgdIon] = field(
        default_factory=lambda: StructArray(
            type_input=PlasmaTransportModelGgdIon
        ),
        metadata={
            "imas_type": "plasma_transport_model_ggd_ion",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": PlasmaTransportModelGgdIon,
        },
    )
    neutral: Optional[PlasmaTransportModelGgdNeutral] = field(
        default_factory=lambda: StructArray(
            type_input=PlasmaTransportModelGgdNeutral
        ),
        metadata={
            "imas_type": "plasma_transport_model_ggd_neutral",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": PlasmaTransportModelGgdNeutral,
        },
    )
    time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class PlasmaTransportModel(IdsBaseClass):
    """

    :ivar comment : Any comment describing the model
    :ivar flux_multiplier : Multiplier applied to the particule flux when adding its contribution in the expression of the heat flux : can be 0, 3/2 or 5/2
    :ivar profiles_1d : Transport coefficient profiles for various time slices. The transport of particles, energy and momentum is described by diffusion coefficients, D, and convection velocities, v. In 1D (radial) equations, these are defined by the total fluxes of particles, energy and momentum, across a flux surface given by : V&#39; [-D Y&#39; &lt;|grad(rho_tor_norm)|^2&gt; + v Y &lt;|grad(rho_tor_norm)|&gt;], where Y represents the particles, energy and momentum density, respectively, while V is the volume inside a flux surface, the primes denote derivatives with respect to rho_tor_norm and &lt; X &gt; is the flux surface average of a quantity X. This formulation remains valid when changing simultaneously rho_tor_norm into rho_tor in the gradient terms and in the derivatives denoted by the prime. The average flux stored in the IDS as sibling of D and v is the total flux described above divided by the flux surface area V&#39; &lt;|grad(rho_tor_norm)|&gt;. Note that the energy flux includes the energy transported by the particle flux, in this form: Q =  V&#39; [- n D (T)&#39; &lt;|grad(rho_tor_norm)|^2&gt; + v (nT) &lt;|grad(rho_tor_norm)|&gt;] + flux_multiplier * T * particle_flux. Fluxes and convection are positive (resp. negative) when outwards i.e. towards the LCFS (resp. inwards i.e.  towards the magnetic axes).
    :ivar ggd : Transport coefficients represented using the general grid description, for various time slices. Fluxes are given in the direction perpendicular to the edges or faces of the grid (flow crossing that surface divided by its actual area). Radial fluxes are positive when they are directed away from the magnetic axis. Poloidal fluxes are positive when they are directed in such a way that they travel clockwise around the magnetic axis (poloidal plane viewed such that the centerline of the tokamak is on the left). Parallel fluxes are positive when they are co-directed with the magnetic field. Toroidal fluxes are positive if travelling counter-clockwise when looking at the plasma from above
    :ivar ggd_fast : Quantities provided at a faster sampling rate than the full ggd quantities. These are either integrated quantities or local quantities provided on a reduced set of positions. Positions and integration domains are described by a set of grid_subsets (of size 1 for a position).
    :ivar code : Code-specific parameters used for this model
    """

    class Meta:
        name = "plasma_transport_model"
        is_root_ids = False

    comment: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    flux_multiplier: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    profiles_1d: Optional[PlasmaTransportModelProfiles1D] = field(
        default_factory=lambda: StructArray(
            type_input=PlasmaTransportModelProfiles1D
        ),
        metadata={
            "imas_type": "plasma_transport_model_profiles_1d",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": PlasmaTransportModelProfiles1D,
        },
    )
    ggd: Optional[PlasmaTransportModelGgd] = field(
        default_factory=lambda: StructArray(type_input=PlasmaTransportModelGgd),
        metadata={
            "imas_type": "plasma_transport_model_ggd",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": PlasmaTransportModelGgd,
        },
    )
    ggd_fast: Optional[PlasmaTransportModelGgdFast] = field(
        default_factory=lambda: StructArray(
            type_input=PlasmaTransportModelGgdFast
        ),
        metadata={
            "imas_type": "plasma_transport_model_ggd_fast",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": PlasmaTransportModelGgdFast,
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
class PlasmaTransport(IdsBaseClass):
    """

    :ivar ids_properties :
    :ivar midplane : Choice of midplane definition (use the lowest index number if more than one value is relevant)
    :ivar vacuum_toroidal_field : Characteristics of the vacuum toroidal field (used in Rho_Tor definition and in the normalization of current densities)
    :ivar grid_ggd : Grid (using the Generic Grid Description), for various time slices. The timebase of this array of structure must be a subset of the ggd timebases
    :ivar model : Transport is described by a combination of various transport models
    :ivar code :
    :ivar time : Generic time
    """

    class Meta:
        name = "plasma_transport"
        is_root_ids = True

    ids_properties: Optional[IdsProperties] = field(
        default=None,
        metadata={"imas_type": "ids_properties", "field_type": IdsProperties},
    )
    midplane: Optional[IdentifierStatic] = field(
        default=None,
        metadata={
            "imas_type": "identifier_static",
            "field_type": IdentifierStatic,
        },
    )
    vacuum_toroidal_field: Optional[BTorVacuum1] = field(
        default=None,
        metadata={"imas_type": "b_tor_vacuum_1", "field_type": BTorVacuum1},
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
    model: Optional[PlasmaTransportModel] = field(
        default_factory=lambda: StructArray(type_input=PlasmaTransportModel),
        metadata={
            "imas_type": "plasma_transport_model",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": PlasmaTransportModel,
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
