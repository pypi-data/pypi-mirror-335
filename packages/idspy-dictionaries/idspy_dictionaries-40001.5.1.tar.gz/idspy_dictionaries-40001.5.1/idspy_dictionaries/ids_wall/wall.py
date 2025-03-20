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
class Vessel2DAnnular(IdsBaseClass):
    """

    :ivar outline_inner : Inner vessel outline. Repeat the first point in case of a closed contour
    :ivar outline_outer : Outer vessel outline. Repeat the first point in case of a closed contour
    :ivar centreline : Centreline, i.e. middle of the vessel layer as a series of point. Repeat the first point in case of a closed contour
    :ivar thickness : Thickness of the vessel layer  in the perpendicular direction to the centreline. Thickness(i) is the thickness of the layer between centreline/r(i),z(i) and centreline/r(i+1),z(i+1), so its size is equal to the length of centreline/r-1 if the thickness is varying. If the thickness is constant for all points, allocate this node to size 1 to store a single value.
    :ivar resistivity : Resistivity of the vessel unit
    """

    class Meta:
        name = "vessel_2d_annular"
        is_root_ids = False

    outline_inner: Optional[Rz1DStatic] = field(
        default=None,
        metadata={"imas_type": "rz1d_static", "field_type": Rz1DStatic},
    )
    outline_outer: Optional[Rz1DStatic] = field(
        default=None,
        metadata={"imas_type": "rz1d_static", "field_type": Rz1DStatic},
    )
    centreline: Optional[Rz1DStatic] = field(
        default=None,
        metadata={"imas_type": "rz1d_static", "field_type": Rz1DStatic},
    )
    thickness: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    resistivity: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
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
class Vessel2DElement(IdsBaseClass):
    """

    :ivar name : Name of the block element
    :ivar outline : Outline of the block element. Repeat the first point in case of a closed contour
    :ivar resistivity : Resistivity of the block element
    :ivar j_phi : Toroidal current induced in this block element
    :ivar resistance : Resistance of the block element
    """

    class Meta:
        name = "vessel_2d_element"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    outline: Optional[Rz1DStatic] = field(
        default=None,
        metadata={"imas_type": "rz1d_static", "field_type": Rz1DStatic},
    )
    resistivity: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    j_phi: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )
    resistance: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class IdentifierDynamicAos31D(IdsBaseClass):
    """

    :ivar names : Short string identifiers
    :ivar indices : Integer identifiers (enumeration index within a list). Private identifier values must be indicated by a negative index.
    :ivar descriptions : Verbose description
    """

    class Meta:
        name = "identifier_dynamic_aos3_1d"
        is_root_ids = False

    names: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=str),
        metadata={
            "imas_type": "STR_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    indices: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=int),
        metadata={
            "imas_type": "INT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../names"},
            "field_type": np.ndarray,
        },
    )
    descriptions: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=str),
        metadata={
            "imas_type": "STR_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../names"},
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
class Vessel2DUnit(IdsBaseClass):
    """

    :ivar name : Short string identifier (unique for a given device)
    :ivar description : Description, e.g. “channel viewing the upper divertor”
    :ivar annular : Annular representation of a layer by two contours, inner and outer. Alternatively, the layer can be described by a centreline and thickness.
    :ivar element : Set of block elements
    """

    class Meta:
        name = "vessel_2d_unit"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    description: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    annular: Optional[Vessel2DAnnular] = field(
        default=None,
        metadata={
            "imas_type": "vessel_2d_annular",
            "field_type": Vessel2DAnnular,
        },
    )
    element: Optional[Vessel2DElement] = field(
        default_factory=lambda: StructArray(type_input=Vessel2DElement),
        metadata={
            "imas_type": "vessel_2d_element",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": Vessel2DElement,
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
class GenericGridIdentifierSingle(IdsBaseClass):
    """

    :ivar grid_index : Index of the grid used to represent this quantity
    :ivar grid_subset_index : Index of the grid subset the data is provided on. Corresponds to the index used in the grid subset definition: grid_subset(:)/identifier/index
    :ivar identifier : Identifier value for the grid subset
    """

    class Meta:
        name = "generic_grid_identifier_single"
        is_root_ids = False

    grid_index: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    grid_subset_index: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    identifier: Optional[IdentifierDynamicAos3] = field(
        default=None,
        metadata={
            "imas_type": "identifier_dynamic_aos3",
            "field_type": IdentifierDynamicAos3,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class GenericGridIdentifier(IdsBaseClass):
    """

    :ivar grid_index : Index of the grid used to represent this quantity
    :ivar grid_subset_index : Index of the grid subset the data is provided on. Corresponds to the index used in the grid subset definition: grid_subset(:)/identifier/index
    :ivar identifiers : Identifier values, one value is provided per element in the grid subset. If the size of the child arrays is 1, their value applies to all elements of the subset.
    """

    class Meta:
        name = "generic_grid_identifier"
        is_root_ids = False

    grid_index: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    grid_subset_index: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    identifiers: Optional[IdentifierDynamicAos31D] = field(
        default=None,
        metadata={
            "imas_type": "identifier_dynamic_aos3_1d",
            "field_type": IdentifierDynamicAos31D,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class GenericGridVectorComponentsRphiz(IdsBaseClass):
    """

    :ivar grid_index : Index of the grid used to represent this quantity
    :ivar grid_subset_index : Index of the grid subset the data is provided on. Corresponds to the index used in the grid subset definition: grid_subset(:)/identifier/index
    :ivar r : Component along the major radius axis, one scalar value is provided per element in the grid subset.
    :ivar r_coefficients : Interpolation coefficients for the component along the major radius axis, to be used for a high precision evaluation of the physical quantity with finite elements, provided per element in the grid subset (first dimension).
    :ivar phi : Toroidal component, one scalar value is provided per element in the grid subset.
    :ivar phi_coefficients : Interpolation coefficients for the toroidal component, to be used for a high precision evaluation of the physical quantity with finite elements, provided per element in the grid subset (first dimension).
    :ivar z : Component along the height axis, one scalar value is provided per element in the grid subset.
    :ivar z_coefficients : Interpolation coefficients for the component along the height axis, to be used for a high precision evaluation of the physical quantity with finite elements, provided per element in the grid subset (first dimension).
    """

    class Meta:
        name = "generic_grid_vector_components_rphiz"
        is_root_ids = False

    grid_index: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    grid_subset_index: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
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
            "coordinates": {"coordinate1": "../r"},
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
            "coordinates": {"coordinate1": "../r"},
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
class SignalFlt1D(IdsBaseClass):
    """

    :ivar data : Data
    :ivar time : Time
    """

    class Meta:
        name = "signal_flt_1d"
        is_root_ids = False

    data: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
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
class TemperatureReference(IdsBaseClass):
    """

    :ivar description : Description of how the reference temperature is defined : for which object, at which location, ...
    :ivar data : Reference temperature
    """

    class Meta:
        name = "temperature_reference"
        is_root_ids = False

    description: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    data: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
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
class Rz1DDynamicAosTime(IdsBaseClass):
    """

    :ivar r : Major radius
    :ivar z : Height
    :ivar time : Time
    """

    class Meta:
        name = "rz1d_dynamic_aos_time"
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
    z: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../r"},
            "field_type": np.ndarray,
        },
    )
    time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class Rz1DStatic(IdsBaseClass):
    """

    :ivar r : Major radius
    :ivar z : Height
    """

    class Meta:
        name = "rz1d_static"
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
class Vessel2D(IdsBaseClass):
    """

    :ivar type : Type of the description. index = 0 for the official single/multiple annular representation and 1 for the official block element representation for each unit. Additional representations needed on a code-by-code basis follow same incremental pair tagging starting on index=2
    :ivar unit : Set of units
    """

    class Meta:
        name = "vessel_2d"
        is_root_ids = False

    type: Optional[IdentifierStatic] = field(
        default=None,
        metadata={
            "imas_type": "identifier_static",
            "field_type": IdentifierStatic,
        },
    )
    unit: Optional[Vessel2DUnit] = field(
        default_factory=lambda: StructArray(type_input=Vessel2DUnit),
        metadata={
            "imas_type": "vessel_2d_unit",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": Vessel2DUnit,
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
class WallGlobalQuantititesElectrons(IdsBaseClass):
    """

    :ivar pumping_speed : Pumped particle flux (in equivalent electrons)
    :ivar particle_flux_from_plasma : Particle flux from the plasma (in equivalent electrons)
    :ivar particle_flux_from_wall : Particle flux from the wall corresponding to the conversion into various neutral types (first dimension: 1: cold; 2: thermal; 3: fast), in equivalent electrons
    :ivar gas_puff : Gas puff rate (in equivalent electrons)
    :ivar power_inner_target : Electron power on the inner target
    :ivar power_outer_target : Electron power on the inner target
    """

    class Meta:
        name = "wall_global_quantitites_electrons"
        is_root_ids = False

    pumping_speed: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../time"},
            "field_type": np.ndarray,
        },
    )
    particle_flux_from_plasma: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../time"},
            "field_type": np.ndarray,
        },
    )
    particle_flux_from_wall: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "1...3",
                "coordinate2": "../../../time",
            },
            "field_type": np.ndarray,
        },
    )
    gas_puff: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../time"},
            "field_type": np.ndarray,
        },
    )
    power_inner_target: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../time"},
            "field_type": np.ndarray,
        },
    )
    power_outer_target: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../time"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WallGlobalQuantititesNeutralOrigin(IdsBaseClass):
    """

    :ivar element : List of elements forming the atom or molecule of the incident species
    :ivar name : String identifying the incident species (e.g. H, D, CD4, ...)
    :ivar energies : Array of energies of this incident species, on which the sputtering_physical_coefficient is tabulated
    :ivar sputtering_physical_coefficient : Effective coefficient of physical sputtering for various neutral types (first dimension: 1: cold; 2: thermal; 3: fast), due to this incident species and for various energies (second dimension)
    :ivar sputtering_chemical_coefficient : Effective coefficient of chemical sputtering for various neutral types (first dimension: 1: cold; 2: thermal; 3: fast), due to this incident species
    """

    class Meta:
        name = "wall_global_quantitites_neutral_origin"
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
    energies: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    sputtering_physical_coefficient: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "1...3",
                "coordinate2": "../energies",
                "coordinate3": "/time",
            },
            "field_type": np.ndarray,
        },
    )
    sputtering_chemical_coefficient: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {"coordinate1": "1...3", "coordinate2": "/time"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WallGlobalQuantititesNeutral(IdsBaseClass):
    """

    :ivar element : List of elements forming the atom or molecule
    :ivar name : String identifying the species (e.g. H, D, CD4, ...)
    :ivar pumping_speed : Pumped particle flux for that species
    :ivar particle_flux_from_plasma : Particle flux from the plasma for that species
    :ivar particle_flux_from_wall : Particle flux from the wall corresponding to the conversion into various neutral types (first dimension: 1: cold; 2: thermal; 3: fast)
    :ivar gas_puff : Gas puff rate for that species
    :ivar wall_inventory : Wall inventory, i.e. cumulated exchange of neutral species between plasma and wall from t = 0, positive if a species has gone to the wall, for that species
    :ivar recycling_particles_coefficient : Particle recycling coefficient corresponding to the conversion into various neutral types (first dimension: 1: cold; 2: thermal; 3: fast)
    :ivar recycling_energy_coefficient : Energy recycling coefficient corresponding to the conversion into various neutral types (first dimension: 1: cold; 2: thermal; 3: fast)
    :ivar incident_species : Sputtering coefficients due to a set of incident species
    """

    class Meta:
        name = "wall_global_quantitites_neutral"
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
    pumping_speed: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "/time"},
            "field_type": np.ndarray,
        },
    )
    particle_flux_from_plasma: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "/time"},
            "field_type": np.ndarray,
        },
    )
    particle_flux_from_wall: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {"coordinate1": "1...3", "coordinate2": "/time"},
            "field_type": np.ndarray,
        },
    )
    gas_puff: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "/time"},
            "field_type": np.ndarray,
        },
    )
    wall_inventory: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "/time"},
            "field_type": np.ndarray,
        },
    )
    recycling_particles_coefficient: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {"coordinate1": "1...3", "coordinate2": "/time"},
            "field_type": np.ndarray,
        },
    )
    recycling_energy_coefficient: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {"coordinate1": "1...3", "coordinate2": "/time"},
            "field_type": np.ndarray,
        },
    )
    incident_species: Optional[WallGlobalQuantititesNeutralOrigin] = field(
        default_factory=lambda: StructArray(
            type_input=WallGlobalQuantititesNeutralOrigin
        ),
        metadata={
            "imas_type": "wall_global_quantitites_neutral_origin",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": WallGlobalQuantititesNeutralOrigin,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WallGlobalQuantitites(IdsBaseClass):
    """

    :ivar electrons : Quantities related to electrons
    :ivar neutral : Quantities related to the various neutral species
    :ivar temperature : Wall temperature
    :ivar power_incident : Total power incident on the wall. This power is split in the various physical categories listed below
    :ivar power_conducted : Power conducted by the plasma onto the wall
    :ivar power_convected : Power convected by the plasma onto the wall
    :ivar power_radiated : Net radiated power from plasma onto the wall (incident-reflected)
    :ivar power_black_body : Black body radiated power emitted from the wall (emissivity is included)
    :ivar power_neutrals : Net power from neutrals on the wall  (positive means power is deposited on the wall)
    :ivar power_recombination_plasma : Power deposited on the wall due to recombination of plasma ions
    :ivar power_recombination_neutrals : Power deposited on the wall due to recombination of neutrals into a ground state (e.g. molecules)
    :ivar power_currents : Power deposited on the wall due to electric currents (positive means power is deposited on the target)
    :ivar power_to_cooling : Power to cooling systems
    :ivar power_inner_target_ion_total : Total ion (summed over ion species) power on the inner target
    :ivar power_density_inner_target_max : Maximum power density on the inner target
    :ivar power_density_outer_target_max : Maximum power density on the outer target
    :ivar current_phi : Toroidal current flowing in the vacuum vessel
    """

    class Meta:
        name = "wall_global_quantitites"
        is_root_ids = False

    electrons: Optional[WallGlobalQuantititesElectrons] = field(
        default=None,
        metadata={
            "imas_type": "wall_global_quantitites_electrons",
            "field_type": WallGlobalQuantititesElectrons,
        },
    )
    neutral: Optional[WallGlobalQuantititesNeutral] = field(
        default_factory=lambda: StructArray(
            type_input=WallGlobalQuantititesNeutral
        ),
        metadata={
            "imas_type": "wall_global_quantitites_neutral",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": WallGlobalQuantititesNeutral,
        },
    )
    temperature: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time"},
            "field_type": np.ndarray,
        },
    )
    power_incident: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time"},
            "field_type": np.ndarray,
        },
    )
    power_conducted: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time"},
            "field_type": np.ndarray,
        },
    )
    power_convected: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time"},
            "field_type": np.ndarray,
        },
    )
    power_radiated: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time"},
            "field_type": np.ndarray,
        },
    )
    power_black_body: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time"},
            "field_type": np.ndarray,
        },
    )
    power_neutrals: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time"},
            "field_type": np.ndarray,
        },
    )
    power_recombination_plasma: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time"},
            "field_type": np.ndarray,
        },
    )
    power_recombination_neutrals: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time"},
            "field_type": np.ndarray,
        },
    )
    power_currents: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time"},
            "field_type": np.ndarray,
        },
    )
    power_to_cooling: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time"},
            "field_type": np.ndarray,
        },
    )
    power_inner_target_ion_total: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time"},
            "field_type": np.ndarray,
        },
    )
    power_density_inner_target_max: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time"},
            "field_type": np.ndarray,
        },
    )
    power_density_outer_target_max: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time"},
            "field_type": np.ndarray,
        },
    )
    current_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class Wall2DLimiterUnit(IdsBaseClass):
    """

    :ivar name : Short string identifier (unique for a given device). Although the details may be machine-specific, a tree-like syntax must be followed, listing first top level components, then going down to finer element description. The tree levels are separated by a /, using a number of levels relevant to the granularity of the description. Example : ic_antenna/a1/bumpers refers to the bumpers of the a1 IC antenna
    :ivar description : Description, e.g. “channel viewing the upper divertor”
    :ivar component_type : Type of component of this unit
    :ivar outline : Irregular outline of the limiting surface. Repeat the first point in case of a closed contour
    :ivar phi_extensions : Simplified description of toroidal angle extensions of the unit, by a list of zones defined by their centre and full width (in toroidal angle).  In each of these zones, the unit outline remains the same. Leave this node empty for an axisymmetric unit. The first dimension gives the centre and full width toroidal angle values for the unit. The second dimension represents the toroidal occurrences of the unit countour (i.e. the number of toroidal zones).
    :ivar resistivity : Resistivity of the limiter unit
    """

    class Meta:
        name = "wall_2d_limiter_unit"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    description: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    component_type: Optional[IdentifierStatic] = field(
        default=None,
        metadata={
            "imas_type": "identifier_static",
            "field_type": IdentifierStatic,
        },
    )
    outline: Optional[Rz1DStatic] = field(
        default=None,
        metadata={"imas_type": "rz1d_static", "field_type": Rz1DStatic},
    )
    phi_extensions: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {"coordinate1": "1...2", "coordinate2": "1...N"},
            "field_type": np.ndarray,
        },
    )
    resistivity: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class Wall2DLimiter(IdsBaseClass):
    """

    :ivar type : Type of the limiter description. index = 0 for the official single contour limiter and 1 for the official disjoint PFC structure like first wall. Additional representations needed on a code-by-code basis follow same incremental pair tagging starting on index =2
    :ivar unit : Set of limiter units. Whenever relevant, multiple units should be ordered so that they define contiguous sections, clockwise in the poloidal direction.
    """

    class Meta:
        name = "wall_2d_limiter"
        is_root_ids = False

    type: Optional[IdentifierStatic] = field(
        default=None,
        metadata={
            "imas_type": "identifier_static",
            "field_type": IdentifierStatic,
        },
    )
    unit: Optional[Wall2DLimiterUnit] = field(
        default_factory=lambda: StructArray(type_input=Wall2DLimiterUnit),
        metadata={
            "imas_type": "wall_2d_limiter_unit",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": Wall2DLimiterUnit,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class Wall2DMobileUnit(IdsBaseClass):
    """

    :ivar name : Name of the mobile unit
    :ivar outline : Irregular outline of the mobile unit, for a set of time slices. Repeat the first point in case of a closed contour
    :ivar phi_extensions : Simplified description of toroidal angle extensions of the unit, by a list of zones defined by their centre and full width (in toroidal angle).  In each of these zones, the unit outline remains the same. Leave this node empty for an axisymmetric unit. The first dimension gives the centre and full width toroidal angle values for the unit. The second dimension represents the toroidal occurrences of the unit countour (i.e. the number of toroidal zones).
    :ivar resistivity : Resistivity of the mobile unit
    """

    class Meta:
        name = "wall_2d_mobile_unit"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    outline: Optional[Rz1DDynamicAosTime] = field(
        default_factory=lambda: StructArray(type_input=Rz1DDynamicAosTime),
        metadata={
            "imas_type": "rz1d_dynamic_aos_time",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": Rz1DDynamicAosTime,
        },
    )
    phi_extensions: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {"coordinate1": "1...2", "coordinate2": "1...N"},
            "field_type": np.ndarray,
        },
    )
    resistivity: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class Wall2DMobile(IdsBaseClass):
    """

    :ivar type : Type of the description
    :ivar unit : Set of mobile units
    """

    class Meta:
        name = "wall_2d_mobile"
        is_root_ids = False

    type: Optional[IdentifierStatic] = field(
        default=None,
        metadata={
            "imas_type": "identifier_static",
            "field_type": IdentifierStatic,
        },
    )
    unit: Optional[Wall2DMobileUnit] = field(
        default_factory=lambda: StructArray(type_input=Wall2DMobileUnit),
        metadata={
            "imas_type": "wall_2d_mobile_unit",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": Wall2DMobileUnit,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class Wall2D(IdsBaseClass):
    """

    :ivar type : Type of the description
    :ivar limiter : Description of the immobile limiting surface(s) or plasma facing components for defining the Last Closed Flux Surface.
    :ivar mobile : In case of mobile plasma facing components, use the time-dependent description below this node to provide the full outline of the closest PFC surfaces to the plasma. Even in such a case, the &#39;limiter&#39; structure is still used to provide the outermost limiting surface (can be used e.g. to define the boundary of the mesh of equilibrium reconstruction codes)
    :ivar vessel : Mechanical structure of the vacuum vessel. The vessel is described as a set of nested layers with given physics properties; Two representations are admitted for each vessel unit : annular (two contours) or block elements.
    """

    class Meta:
        name = "wall_2d"
        is_root_ids = False

    type: Optional[IdentifierStatic] = field(
        default=None,
        metadata={
            "imas_type": "identifier_static",
            "field_type": IdentifierStatic,
        },
    )
    limiter: Optional[Wall2DLimiter] = field(
        default=None,
        metadata={"imas_type": "wall_2d_limiter", "field_type": Wall2DLimiter},
    )
    mobile: Optional[Wall2DMobile] = field(
        default=None,
        metadata={"imas_type": "wall_2d_mobile", "field_type": Wall2DMobile},
    )
    vessel: Optional[Vessel2D] = field(
        default=None,
        metadata={"imas_type": "vessel_2d", "field_type": Vessel2D},
    )


@idspy_dataclass(repr=False, slots=True)
class WallDescriptionGgdEnergySimple(IdsBaseClass):
    """

    :ivar incident : Incident fluxes for various wall components (grid subsets)
    :ivar emitted : Emitted fluxes for various wall components (grid subsets)
    """

    class Meta:
        name = "wall_description_ggd_energy_simple"
        is_root_ids = False

    incident: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    emitted: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WallDescriptionGgdEnergyNeutralState(IdsBaseClass):
    """

    :ivar name : String identifying state
    :ivar vibrational_level : Vibrational level (can be bundled)
    :ivar vibrational_mode : Vibrational mode of this state, e.g. &#34;A_g&#34;. Need to define, or adopt a standard nomenclature.
    :ivar neutral_type : Neutral type, in terms of energy. ID =1: cold; 2: thermal; 3: fast; 4: NBI
    :ivar electron_configuration : Configuration of atomic orbitals of this state, e.g. 1s2-2s1
    :ivar incident : Incident fluxes for various wall components (grid subsets)
    :ivar emitted : Emitted fluxes for various wall components (grid subsets)
    """

    class Meta:
        name = "wall_description_ggd_energy_neutral_state"
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
    incident: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    emitted: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WallDescriptionGgdEnergyNeutral(IdsBaseClass):
    """

    :ivar element : List of elements forming the atom or molecule
    :ivar name : String identifying neutral (e.g. H, D, T, He, C, ...)
    :ivar ion_index : Index of the corresponding ion species in the ../../ion array
    :ivar incident : Incident fluxes for various wall components (grid subsets)
    :ivar emitted : Emitted fluxes for various wall components (grid subsets)
    :ivar multiple_states_flag : Multiple states calculation flag : 0-Only one state is considered; 1-Multiple states are considered and are described in the state structure
    :ivar state : Fluxes related to the different states of the species
    """

    class Meta:
        name = "wall_description_ggd_energy_neutral"
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
    incident: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    emitted: Optional[GenericGridScalar] = field(
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
    state: Optional[WallDescriptionGgdEnergyNeutralState] = field(
        default_factory=lambda: StructArray(
            type_input=WallDescriptionGgdEnergyNeutralState
        ),
        metadata={
            "imas_type": "wall_description_ggd_energy_neutral_state",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": WallDescriptionGgdEnergyNeutralState,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WallDescriptionGgdEnergyIonState(IdsBaseClass):
    """

    :ivar z_min : Minimum Z of the charge state bundle
    :ivar z_max : Maximum Z of the charge state bundle
    :ivar name : String identifying charge state (e.g. C+, C+2 , C+3, C+4, C+5, C+6, ...)
    :ivar vibrational_level : Vibrational level (can be bundled)
    :ivar vibrational_mode : Vibrational mode of this state, e.g. &#34;A_g&#34;. Need to define, or adopt a standard nomenclature.
    :ivar electron_configuration : Configuration of atomic orbitals of this state, e.g. 1s2-2s1
    :ivar incident : Incident fluxes for various wall components (grid subsets)
    :ivar emitted : Emitted fluxes for various wall components (grid subsets)
    """

    class Meta:
        name = "wall_description_ggd_energy_ion_state"
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
    incident: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    emitted: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WallDescriptionGgdEnergyIon(IdsBaseClass):
    """

    :ivar element : List of elements forming the atom or molecule
    :ivar z_ion : Ion charge (of the dominant ionization state; lumped ions are allowed)
    :ivar name : String identifying ion (e.g. H, D, T, He, C, D2, ...)
    :ivar neutral_index : Index of the corresponding neutral species in the ../../neutral array
    :ivar incident : Incident fluxes for various wall components (grid subsets)
    :ivar emitted : Emitted fluxes for various wall components (grid subsets)
    :ivar multiple_states_flag : Multiple states calculation flag : 0-Only the &#39;ion&#39; level is considered and the &#39;state&#39; array of structure is empty; 1-Ion states are considered and are described in the &#39;state&#39; array of structure
    :ivar state : Fluxes related to the different states of the species
    """

    class Meta:
        name = "wall_description_ggd_energy_ion"
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
    incident: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    emitted: Optional[GenericGridScalar] = field(
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
    state: Optional[WallDescriptionGgdEnergyIonState] = field(
        default_factory=lambda: StructArray(
            type_input=WallDescriptionGgdEnergyIonState
        ),
        metadata={
            "imas_type": "wall_description_ggd_energy_ion_state",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": WallDescriptionGgdEnergyIonState,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WallDescriptionGgdKinetic(IdsBaseClass):
    """

    :ivar electrons : Electron fluxes. Fluxes are given at the wall, after the sheath.
    :ivar ion : Fluxes related to the various ion species, in the sense of isonuclear or isomolecular sequences. Ionization states (and other types of states) must be differentiated at the state level below. Fluxes are given at the wall, after the sheath.
    :ivar neutral : Neutral species fluxes
    """

    class Meta:
        name = "wall_description_ggd_kinetic"
        is_root_ids = False

    electrons: Optional[WallDescriptionGgdEnergySimple] = field(
        default=None,
        metadata={
            "imas_type": "wall_description_ggd_energy_simple",
            "field_type": WallDescriptionGgdEnergySimple,
        },
    )
    ion: Optional[WallDescriptionGgdEnergyIon] = field(
        default_factory=lambda: StructArray(
            type_input=WallDescriptionGgdEnergyIon
        ),
        metadata={
            "imas_type": "wall_description_ggd_energy_ion",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": WallDescriptionGgdEnergyIon,
        },
    )
    neutral: Optional[WallDescriptionGgdParticleNeutral] = field(
        default_factory=lambda: StructArray(
            type_input=WallDescriptionGgdParticleNeutral
        ),
        metadata={
            "imas_type": "wall_description_ggd_particle_neutral",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": WallDescriptionGgdParticleNeutral,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WallDescriptionGgdRecombination(IdsBaseClass):
    """

    :ivar ion : Fluxes related to the various ion species, in the sense of isonuclear or isomolecular sequences. Ionization states (and other types of states) must be differentiated at the state level below
    :ivar neutral : Neutral species fluxes
    """

    class Meta:
        name = "wall_description_ggd_recombination"
        is_root_ids = False

    ion: Optional[WallDescriptionGgdEnergyIon] = field(
        default_factory=lambda: StructArray(
            type_input=WallDescriptionGgdEnergyIon
        ),
        metadata={
            "imas_type": "wall_description_ggd_energy_ion",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": WallDescriptionGgdEnergyIon,
        },
    )
    neutral: Optional[WallDescriptionGgdParticleNeutral] = field(
        default_factory=lambda: StructArray(
            type_input=WallDescriptionGgdParticleNeutral
        ),
        metadata={
            "imas_type": "wall_description_ggd_particle_neutral",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": WallDescriptionGgdParticleNeutral,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WallDescriptionGgdEnergy(IdsBaseClass):
    """

    :ivar radiation : Total radiation, not split by process
    :ivar current : Current energy fluxes
    :ivar recombination : Wall recombination
    :ivar kinetic : Energy fluxes due to the kinetic energy of particles
    """

    class Meta:
        name = "wall_description_ggd_energy"
        is_root_ids = False

    radiation: Optional[WallDescriptionGgdEnergySimple] = field(
        default=None,
        metadata={
            "imas_type": "wall_description_ggd_energy_simple",
            "field_type": WallDescriptionGgdEnergySimple,
        },
    )
    current: Optional[WallDescriptionGgdEnergySimple] = field(
        default=None,
        metadata={
            "imas_type": "wall_description_ggd_energy_simple",
            "field_type": WallDescriptionGgdEnergySimple,
        },
    )
    recombination: Optional[WallDescriptionGgdRecombination] = field(
        default=None,
        metadata={
            "imas_type": "wall_description_ggd_recombination",
            "field_type": WallDescriptionGgdRecombination,
        },
    )
    kinetic: Optional[WallDescriptionGgdKinetic] = field(
        default=None,
        metadata={
            "imas_type": "wall_description_ggd_kinetic",
            "field_type": WallDescriptionGgdKinetic,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WallDescriptionGgdParticleNeutralState(IdsBaseClass):
    """

    :ivar name : String identifying state
    :ivar vibrational_level : Vibrational level (can be bundled)
    :ivar vibrational_mode : Vibrational mode of this state, e.g. &#34;A_g&#34;. Need to define, or adopt a standard nomenclature.
    :ivar neutral_type : Neutral type, in terms of energy. ID =1: cold; 2: thermal; 3: fast; 4: NBI
    :ivar electron_configuration : Configuration of atomic orbitals of this state, e.g. 1s2-2s1
    :ivar incident : Incident fluxes for various wall components (grid subsets)
    :ivar emitted : Emitted fluxes for various wall components (grid subsets)
    """

    class Meta:
        name = "wall_description_ggd_particle_neutral_state"
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
    incident: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    emitted: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WallDescriptionGgdParticleNeutral(IdsBaseClass):
    """

    :ivar element : List of elements forming the atom or molecule
    :ivar name : String identifying neutral (e.g. H, D, T, He, C, ...)
    :ivar ion_index : Index of the corresponding ion species in the ../../ion array
    :ivar incident : Incident fluxes for various wall components (grid subsets)
    :ivar emitted : Emitted fluxes for various wall components (grid subsets)
    :ivar multiple_states_flag : Multiple states calculation flag : 0-Only one state is considered; 1-Multiple states are considered and are described in the state structure
    :ivar state : Fluxes related to the different states of the species
    """

    class Meta:
        name = "wall_description_ggd_particle_neutral"
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
    incident: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    emitted: Optional[GenericGridScalar] = field(
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
    state: Optional[WallDescriptionGgdParticleNeutralState] = field(
        default_factory=lambda: StructArray(
            type_input=WallDescriptionGgdParticleNeutralState
        ),
        metadata={
            "imas_type": "wall_description_ggd_particle_neutral_state",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": WallDescriptionGgdParticleNeutralState,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WallDescriptionGgdParticleIonState(IdsBaseClass):
    """

    :ivar z_min : Minimum Z of the charge state bundle
    :ivar z_max : Maximum Z of the charge state bundle
    :ivar name : String identifying charge state (e.g. C+, C+2 , C+3, C+4, C+5, C+6, ...)
    :ivar vibrational_level : Vibrational level (can be bundled)
    :ivar vibrational_mode : Vibrational mode of this state, e.g. &#34;A_g&#34;. Need to define, or adopt a standard nomenclature.
    :ivar electron_configuration : Configuration of atomic orbitals of this state, e.g. 1s2-2s1
    :ivar incident : Incident fluxes for various wall components (grid subsets)
    :ivar emitted : Emitted fluxes for various wall components (grid subsets)
    """

    class Meta:
        name = "wall_description_ggd_particle_ion_state"
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
    incident: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    emitted: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WallDescriptionGgdParticleIon(IdsBaseClass):
    """

    :ivar element : List of elements forming the atom or molecule
    :ivar z_ion : Ion charge (of the dominant ionization state; lumped ions are allowed)
    :ivar name : String identifying ion (e.g. H, D, T, He, C, D2, ...)
    :ivar neutral_index : Index of the corresponding neutral species in the ../../neutral array
    :ivar incident : Incident fluxes for various wall components (grid subsets)
    :ivar emitted : Emitted fluxes for various wall components (grid subsets)
    :ivar multiple_states_flag : Multiple states calculation flag : 0-Only the &#39;ion&#39; level is considered and the &#39;state&#39; array of structure is empty; 1-Ion states are considered and are described in the &#39;state&#39; array of structure
    :ivar state : Fluxes related to the different states of the species
    """

    class Meta:
        name = "wall_description_ggd_particle_ion"
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
    incident: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    emitted: Optional[GenericGridScalar] = field(
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
    state: Optional[WallDescriptionGgdParticleIonState] = field(
        default_factory=lambda: StructArray(
            type_input=WallDescriptionGgdParticleIonState
        ),
        metadata={
            "imas_type": "wall_description_ggd_particle_ion_state",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": WallDescriptionGgdParticleIonState,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WallDescriptionGgdParticleEl(IdsBaseClass):
    """

    :ivar incident : Incident fluxes for various wall components (grid subsets)
    :ivar emitted : Emitted fluxes for various wall components (grid subsets)
    """

    class Meta:
        name = "wall_description_ggd_particle_el"
        is_root_ids = False

    incident: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    emitted: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WallDescriptionGgdParticle(IdsBaseClass):
    """

    :ivar electrons : Electron fluxes
    :ivar ion : Fluxes related to the various ion species, in the sense of isonuclear or isomolecular sequences. Ionization states (and other types of states) must be differentiated at the state level below
    :ivar neutral : Neutral species fluxes
    """

    class Meta:
        name = "wall_description_ggd_particle"
        is_root_ids = False

    electrons: Optional[WallDescriptionGgdParticleEl] = field(
        default=None,
        metadata={
            "imas_type": "wall_description_ggd_particle_el",
            "field_type": WallDescriptionGgdParticleEl,
        },
    )
    ion: Optional[WallDescriptionGgdParticleIon] = field(
        default_factory=lambda: StructArray(
            type_input=WallDescriptionGgdParticleIon
        ),
        metadata={
            "imas_type": "wall_description_ggd_particle_ion",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": WallDescriptionGgdParticleIon,
        },
    )
    neutral: Optional[WallDescriptionGgdParticleNeutral] = field(
        default_factory=lambda: StructArray(
            type_input=WallDescriptionGgdParticleNeutral
        ),
        metadata={
            "imas_type": "wall_description_ggd_particle_neutral",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": WallDescriptionGgdParticleNeutral,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WallDescriptionGgdRecyclingNeutralState(IdsBaseClass):
    """

    :ivar name : String identifying state
    :ivar vibrational_level : Vibrational level (can be bundled)
    :ivar vibrational_mode : Vibrational mode of this state, e.g. &#34;A_g&#34;. Need to define, or adopt a standard nomenclature.
    :ivar neutral_type : Neutral type, in terms of energy. ID =1: cold; 2: thermal; 3: fast; 4: NBI
    :ivar electron_configuration : Configuration of atomic orbitals of this state, e.g. 1s2-2s1
    :ivar coefficient : Recycling coefficient for various wall components (grid subsets)
    """

    class Meta:
        name = "wall_description_ggd_recycling_neutral_state"
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
    coefficient: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WallDescriptionGgdRecyclingNeutral(IdsBaseClass):
    """

    :ivar element : List of elements forming the atom or molecule
    :ivar name : String identifying neutral (e.g. H, D, T, He, C, ...)
    :ivar ion_index : Index of the corresponding ion species in the ../../ion array
    :ivar coefficient : Recycling coefficient for various wall components (grid subsets)
    :ivar multiple_states_flag : Multiple states calculation flag : 0-Only one state is considered; 1-Multiple states are considered and are described in the state structure
    :ivar state : Fluxes related to the different states of the species
    """

    class Meta:
        name = "wall_description_ggd_recycling_neutral"
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
    coefficient: Optional[GenericGridScalar] = field(
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
    state: Optional[WallDescriptionGgdRecyclingNeutralState] = field(
        default_factory=lambda: StructArray(
            type_input=WallDescriptionGgdRecyclingNeutralState
        ),
        metadata={
            "imas_type": "wall_description_ggd_recycling_neutral_state",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": WallDescriptionGgdRecyclingNeutralState,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WallDescriptionGgdRecyclingIonState(IdsBaseClass):
    """

    :ivar z_min : Minimum Z of the charge state bundle
    :ivar z_max : Maximum Z of the charge state bundle
    :ivar name : String identifying charge state (e.g. C+, C+2 , C+3, C+4, C+5, C+6, ...)
    :ivar vibrational_level : Vibrational level (can be bundled)
    :ivar vibrational_mode : Vibrational mode of this state, e.g. &#34;A_g&#34;. Need to define, or adopt a standard nomenclature.
    :ivar electron_configuration : Configuration of atomic orbitals of this state, e.g. 1s2-2s1
    :ivar coefficient : Recycling coefficient for various wall components (grid subsets)
    """

    class Meta:
        name = "wall_description_ggd_recycling_ion_state"
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
    coefficient: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WallDescriptionGgdRecyclingIon(IdsBaseClass):
    """

    :ivar element : List of elements forming the atom or molecule
    :ivar z_ion : Ion charge (of the dominant ionization state; lumped ions are allowed)
    :ivar name : String identifying ion (e.g. H, D, T, He, C, D2, ...)
    :ivar neutral_index : Index of the corresponding neutral species in the ../../neutral array
    :ivar coefficient : Recycling coefficient for various wall components (grid subsets)
    :ivar multiple_states_flag : Multiple states calculation flag : 0-Only the &#39;ion&#39; level is considered and the &#39;state&#39; array of structure is empty; 1-Ion states are considered and are described in the &#39;state&#39; array of structure
    :ivar state : Fluxes related to the different states of the species
    """

    class Meta:
        name = "wall_description_ggd_recycling_ion"
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
    coefficient: Optional[GenericGridScalar] = field(
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
    state: Optional[WallDescriptionGgdRecyclingIonState] = field(
        default_factory=lambda: StructArray(
            type_input=WallDescriptionGgdRecyclingIonState
        ),
        metadata={
            "imas_type": "wall_description_ggd_recycling_ion_state",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": WallDescriptionGgdRecyclingIonState,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WallDescriptionGgdRecycling(IdsBaseClass):
    """

    :ivar ion : Recycling coefficients for the various ion species, in the sense of isonuclear or isomolecular sequences. Ionization states (and other types of states) must be differentiated at the state level below
    :ivar neutral : Recycling coefficients for the various neutral species
    """

    class Meta:
        name = "wall_description_ggd_recycling"
        is_root_ids = False

    ion: Optional[WallDescriptionGgdRecyclingIon] = field(
        default_factory=lambda: StructArray(
            type_input=WallDescriptionGgdRecyclingIon
        ),
        metadata={
            "imas_type": "wall_description_ggd_recycling_ion",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": WallDescriptionGgdRecyclingIon,
        },
    )
    neutral: Optional[WallDescriptionGgdRecyclingNeutral] = field(
        default_factory=lambda: StructArray(
            type_input=WallDescriptionGgdRecyclingNeutral
        ),
        metadata={
            "imas_type": "wall_description_ggd_recycling_neutral",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": WallDescriptionGgdRecyclingNeutral,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WallDescriptionGgdGgd(IdsBaseClass):
    """

    :ivar power_density : Net power density arriving on the wall surface, for various wall components (grid subsets)
    :ivar temperature : Temperature of the wall, for various wall components (grid subsets)
    :ivar v_biasing : Electric potential applied to the wall element by outside means, for various wall components (grid subsets). Different from the plasma electric potential or the sheath potential drop.
    :ivar recycling : Fraction of incoming particles that is reflected back to the vacuum chamber
    :ivar particle_fluxes : Particle fluxes. The incident and emitted components are distinguished. The net flux received by the wall is equal to incident - emitted
    :ivar energy_fluxes : Energy fluxes. The incident and emitted components are distinguished. The net flux received by the wall is equal to incident - emitted
    :ivar j_total : Total current density, given on various grid subsets
    :ivar b_field : Magnetic field, given on various grid subsets
    :ivar em_force_density : Electromagnetic force density computed by the cross-product of j_total x b_field and given on various grid subsets
    :ivar e_field : Electric field, given on various grid subsets
    :ivar a_field : Magnetic vector potential, given on various grid subsets
    :ivar psi : Poloidal flux, given on various grid subsets
    :ivar phi_potential : Electric potential, given on various grid subsets
    :ivar resistivity : Resistivity, given on various grid subsets
    :ivar time : Time
    """

    class Meta:
        name = "wall_description_ggd_ggd"
        is_root_ids = False

    power_density: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
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
    v_biasing: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    recycling: Optional[WallDescriptionGgdRecycling] = field(
        default=None,
        metadata={
            "imas_type": "wall_description_ggd_recycling",
            "field_type": WallDescriptionGgdRecycling,
        },
    )
    particle_fluxes: Optional[WallDescriptionGgdParticle] = field(
        default=None,
        metadata={
            "imas_type": "wall_description_ggd_particle",
            "field_type": WallDescriptionGgdParticle,
        },
    )
    energy_fluxes: Optional[WallDescriptionGgdEnergy] = field(
        default=None,
        metadata={
            "imas_type": "wall_description_ggd_energy",
            "field_type": WallDescriptionGgdEnergy,
        },
    )
    j_total: Optional[GenericGridVectorComponentsRphiz] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridVectorComponentsRphiz
        ),
        metadata={
            "imas_type": "generic_grid_vector_components_rphiz",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridVectorComponentsRphiz,
        },
    )
    b_field: Optional[GenericGridVectorComponentsRphiz] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridVectorComponentsRphiz
        ),
        metadata={
            "imas_type": "generic_grid_vector_components_rphiz",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridVectorComponentsRphiz,
        },
    )
    em_force_density: Optional[GenericGridVectorComponentsRphiz] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridVectorComponentsRphiz
        ),
        metadata={
            "imas_type": "generic_grid_vector_components_rphiz",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridVectorComponentsRphiz,
        },
    )
    e_field: Optional[GenericGridVectorComponentsRphiz] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridVectorComponentsRphiz
        ),
        metadata={
            "imas_type": "generic_grid_vector_components_rphiz",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridVectorComponentsRphiz,
        },
    )
    a_field: Optional[GenericGridVectorComponentsRphiz] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridVectorComponentsRphiz
        ),
        metadata={
            "imas_type": "generic_grid_vector_components_rphiz",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridVectorComponentsRphiz,
        },
    )
    psi: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
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
    resistivity: Optional[GenericGridScalar] = field(
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
class WallDescriptionGgdThickness(IdsBaseClass):
    """

    :ivar grid_subset : The thickness is given for various wall components (grid subsets)
    :ivar time : Time
    """

    class Meta:
        name = "wall_description_ggd_thickness"
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
    time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class WallDescriptionGgdMaterial(IdsBaseClass):
    """

    :ivar grid_subset : Material is described for various wall components (grid subsets), using the identifier convention below
    :ivar time : Time
    """

    class Meta:
        name = "wall_description_ggd_material"
        is_root_ids = False

    grid_subset: Optional[GenericGridIdentifier] = field(
        default_factory=lambda: StructArray(type_input=GenericGridIdentifier),
        metadata={
            "imas_type": "generic_grid_identifier",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridIdentifier,
        },
    )
    time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class WallDescriptionGgdComponent(IdsBaseClass):
    """

    :ivar identifiers : Identifiers of the components (described in the various grid_subsets). Although the details may be machine-specific, a tree-like syntax must be followed, listing first top level components, then going down to finer element description. The tree levels are separated by a /, using a number of levels relevant to the granularity of the description. Example : ic_antenna/a1/bumpers refers to the bumpers of the a1 IC antenna
    :ivar type : The component type is given for various grid_subsets, using the identifier convention below
    :ivar time : Time
    """

    class Meta:
        name = "wall_description_ggd_component"
        is_root_ids = False

    identifiers: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=str),
        metadata={
            "imas_type": "STR_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    type: Optional[GenericGridIdentifierSingle] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridIdentifierSingle
        ),
        metadata={
            "imas_type": "generic_grid_identifier_single",
            "ndims": 1,
            "coordinates": {"coordinate1": "../identifiers"},
            "field_type": GenericGridIdentifierSingle,
        },
    )
    time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class WallDescriptionGgd(IdsBaseClass):
    """

    :ivar type : Type of wall: index = 0 for gas tight, 1 for a wall with holes/open ports, 2 for a thin wall description
    :ivar grid_ggd : Wall geometry described using the Generic Grid Description, for various time slices (in case of mobile wall elements). The timebase of this array of structure must be a subset of the timebase on which physical quantities are described (../ggd structure). Grid_subsets are used to describe various  wall components in a modular way.
    :ivar material : Material of each grid_ggd object, given for each slice of the grid_ggd time base (the material is not supposed to change, but grid_ggd may evolve with time)
    :ivar component : Description of the components represented by various subsets, given for each slice of the grid_ggd time base (the component description is not supposed to change, but grid_ggd may evolve with time)
    :ivar thickness : In the case of a thin wall description, effective thickness of each surface element of grid_ggd, given for each slice of the grid_ggd time base (the thickness is not supposed to change, but grid_ggd may evolve with time)
    :ivar ggd : Wall physics quantities represented using the general grid description, for various time slices.
    """

    class Meta:
        name = "wall_description_ggd"
        is_root_ids = False

    type: Optional[IdentifierStatic] = field(
        default=None,
        metadata={
            "imas_type": "identifier_static",
            "field_type": IdentifierStatic,
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
    material: Optional[WallDescriptionGgdMaterial] = field(
        default_factory=lambda: StructArray(
            type_input=WallDescriptionGgdMaterial
        ),
        metadata={
            "imas_type": "wall_description_ggd_material",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "time",
                "coordinate1_same_as": "../grid_ggd",
            },
            "field_type": WallDescriptionGgdMaterial,
        },
    )
    component: Optional[WallDescriptionGgdComponent] = field(
        default_factory=lambda: StructArray(
            type_input=WallDescriptionGgdComponent
        ),
        metadata={
            "imas_type": "wall_description_ggd_component",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "time",
                "coordinate1_same_as": "../grid_ggd",
            },
            "field_type": WallDescriptionGgdComponent,
        },
    )
    thickness: Optional[WallDescriptionGgdThickness] = field(
        default_factory=lambda: StructArray(
            type_input=WallDescriptionGgdThickness
        ),
        metadata={
            "imas_type": "wall_description_ggd_thickness",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "time",
                "coordinate1_same_as": "../grid_ggd",
            },
            "field_type": WallDescriptionGgdThickness,
        },
    )
    ggd: Optional[WallDescriptionGgdGgd] = field(
        default_factory=lambda: StructArray(type_input=WallDescriptionGgdGgd),
        metadata={
            "imas_type": "wall_description_ggd_ggd",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": WallDescriptionGgdGgd,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class Wall(IdsBaseClass):
    """

    :ivar ids_properties :
    :ivar temperature_reference : Reference temperature for which the machine description data is given in this IDS
    :ivar first_wall_surface_area : First wall surface area
    :ivar first_wall_power_flux_peak : Peak power flux on the first wall
    :ivar first_wall_enclosed_volume : Volume available to gas or plasma enclosed by the first wall contour
    :ivar global_quantities : Simple 0D description of plasma-wall interaction
    :ivar description_2d : Set of 2D wall descriptions, for each type of possible physics or engineering configurations necessary (gas tight vs wall with ports and holes, coarse vs fine representation, single contour limiter, disjoint gapped plasma facing components, ...). A simplified description of the toroidal extension of the 2D contours is also provided by using the phi_extensions nodes.
    :ivar description_ggd : Set of 3D wall descriptions, described using the GGD, for each type of possible physics or engineering configurations necessary (gas tight vs wall with ports and holes, coarse vs fine representation, ...).
    :ivar code :
    :ivar time : Generic time
    """

    class Meta:
        name = "wall"
        is_root_ids = True

    ids_properties: Optional[IdsProperties] = field(
        default=None,
        metadata={"imas_type": "ids_properties", "field_type": IdsProperties},
    )
    temperature_reference: Optional[TemperatureReference] = field(
        default=None,
        metadata={
            "imas_type": "temperature_reference",
            "field_type": TemperatureReference,
        },
    )
    first_wall_surface_area: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    first_wall_power_flux_peak: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )
    first_wall_enclosed_volume: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    global_quantities: Optional[WallGlobalQuantitites] = field(
        default=None,
        metadata={
            "imas_type": "wall_global_quantitites",
            "field_type": WallGlobalQuantitites,
        },
    )
    description_2d: Optional[Wall2D] = field(
        default_factory=lambda: StructArray(type_input=Wall2D),
        metadata={
            "imas_type": "wall_2d",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": Wall2D,
        },
    )
    description_ggd: Optional[WallDescriptionGgd] = field(
        default_factory=lambda: StructArray(type_input=WallDescriptionGgd),
        metadata={
            "imas_type": "wall_description_ggd",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": WallDescriptionGgd,
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
