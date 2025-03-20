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
class GenericGridConstantSpaceDimensionObjectBoundary(IdsBaseClass):
    """

    :ivar index : Index of this (n-1)-dimensional boundary object
    :ivar neighbours : List of indices of the n-dimensional objects adjacent to the given n-dimensional object. An object may have multiple neighbours on a boundary
    """

    class Meta:
        name = "generic_grid_constant_space_dimension_object_boundary"
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
class GenericGridConstantSpaceDimensionObject(IdsBaseClass):
    """

    :ivar boundary : Set of (n-1)-dimensional objects defining the boundary of this n-dimensional object
    :ivar geometry : Geometry data associated with the object. Its detailed content is defined by ../../geometry_content. Its dimension depends on the type of object, geometry and coordinate considered.
    :ivar nodes : List of nodes forming this object (indices to objects_per_dimension(1)%object(:) in Fortran notation)
    :ivar measure : Measure of the space object, i.e. physical size (length for 1d, area for 2d, volume for 3d objects,...)
    :ivar geometry_2d : 2D geometry data associated with the object. Its dimension depends on the type of object, geometry and coordinate considered. Typically, the first dimension represents the object coordinates, while the second dimension would represent the values of the various degrees of freedom of the finite element attached to the object.
    """

    class Meta:
        name = "generic_grid_constant_space_dimension_object"
        is_root_ids = False

    boundary: Optional[GenericGridConstantSpaceDimensionObjectBoundary] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridConstantSpaceDimensionObjectBoundary
        ),
        metadata={
            "imas_type": "generic_grid_constant_space_dimension_object_boundary",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridConstantSpaceDimensionObjectBoundary,
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
class GenericGridConstantGridSubsetElementObject(IdsBaseClass):
    """

    :ivar space : Index of the space from which that object is taken
    :ivar dimension : Dimension of the object
    :ivar index : Object index
    """

    class Meta:
        name = "generic_grid_constant_grid_subset_element_object"
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
class GenericGridConstantGridSubsetElement(IdsBaseClass):
    """

    :ivar object : Set of objects defining the element
    """

    class Meta:
        name = "generic_grid_constant_grid_subset_element"
        is_root_ids = False

    object: Optional[GenericGridConstantGridSubsetElementObject] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridConstantGridSubsetElementObject
        ),
        metadata={
            "imas_type": "generic_grid_constant_grid_subset_element_object",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridConstantGridSubsetElementObject,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class Rz0DStatic(IdsBaseClass):
    """

    :ivar r : Major radius
    :ivar z : Height
    """

    class Meta:
        name = "rz0d_static"
        is_root_ids = False

    r: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    z: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class GenericGridConstantGridSubsetMetric(IdsBaseClass):
    """

    :ivar jacobian : Metric Jacobian
    :ivar tensor_covariant : Covariant metric tensor, given on each element of the subgrid (first dimension)
    :ivar tensor_contravariant : Contravariant metric tensor, given on each element of the subgrid (first dimension)
    """

    class Meta:
        name = "generic_grid_constant_grid_subset_metric"
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
class GenericGridConstantSpaceDimension(IdsBaseClass):
    """

    :ivar object : Set of objects for a given dimension
    """

    class Meta:
        name = "generic_grid_constant_space_dimension"
        is_root_ids = False

    object: Optional[GenericGridConstantSpaceDimensionObject] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridConstantSpaceDimensionObject
        ),
        metadata={
            "imas_type": "generic_grid_constant_space_dimension_object",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridConstantSpaceDimensionObject,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class ThickLineStatic(IdsBaseClass):
    """

    :ivar first_point : Position of the first point
    :ivar second_point : Position of the second point
    :ivar thickness : Thickness
    """

    class Meta:
        name = "thick_line_static"
        is_root_ids = False

    first_point: Optional[Rz0DStatic] = field(
        default=None,
        metadata={"imas_type": "rz0d_static", "field_type": Rz0DStatic},
    )
    second_point: Optional[Rz0DStatic] = field(
        default=None,
        metadata={"imas_type": "rz0d_static", "field_type": Rz0DStatic},
    )
    thickness: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class AnnulusStatic(IdsBaseClass):
    """

    :ivar r : Centre major radius
    :ivar z : Centre height
    :ivar radius_inner : Inner radius
    :ivar radius_outer : Outer radius
    """

    class Meta:
        name = "annulus_static"
        is_root_ids = False

    r: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    z: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    radius_inner: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    radius_outer: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class GenericGridConstantGridSubset(IdsBaseClass):
    """

    :ivar dimension : Space dimension of the grid subset elements. This must be equal to the sum of the dimensions of the individual objects forming the element.
    :ivar element : Set of elements defining the grid subset. An element is defined by a combination of objects from potentially all spaces
    :ivar base : Set of bases for the grid subset. For each base, the structure describes the projection of the base vectors on the canonical frame of the grid.
    :ivar metric : Metric of the canonical frame onto Cartesian coordinates
    """

    class Meta:
        name = "generic_grid_constant_grid_subset"
        is_root_ids = False

    dimension: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    element: Optional[GenericGridConstantGridSubsetElement] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridConstantGridSubsetElement
        ),
        metadata={
            "imas_type": "generic_grid_constant_grid_subset_element",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridConstantGridSubsetElement,
        },
    )
    base: Optional[GenericGridConstantGridSubsetMetric] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridConstantGridSubsetMetric
        ),
        metadata={
            "imas_type": "generic_grid_constant_grid_subset_metric",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridConstantGridSubsetMetric,
        },
    )
    metric: Optional[GenericGridConstantGridSubsetMetric] = field(
        default=None,
        metadata={
            "imas_type": "generic_grid_constant_grid_subset_metric",
            "field_type": GenericGridConstantGridSubsetMetric,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class ArcsOfCircleStatic(IdsBaseClass):
    """

    :ivar r : Major radii of the start point of each arc of circle
    :ivar z : Height of the start point of each arc of circle
    :ivar curvature_radii : Curvature radius of each arc of circle
    """

    class Meta:
        name = "arcs_of_circle_static"
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
    curvature_radii: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../r"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class RectangleStatic(IdsBaseClass):
    """

    :ivar r : Geometric centre R
    :ivar z : Geometric centre Z
    :ivar width : Horizontal full width
    :ivar height : Vertical full height
    """

    class Meta:
        name = "rectangle_static"
        is_root_ids = False

    r: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    z: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    width: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    height: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class GenericGridConstantSpace(IdsBaseClass):
    """

    :ivar objects_per_dimension : Definition of the space objects for every dimension (from one to the dimension of the highest-dimensional objects). The index correspond to 1=nodes, 2=edges, 3=faces, 4=cells/volumes, .... For every index, a collection of objects of that dimension is described.
    """

    class Meta:
        name = "generic_grid_constant_space"
        is_root_ids = False

    objects_per_dimension: Optional[GenericGridConstantSpaceDimension] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridConstantSpaceDimension
        ),
        metadata={
            "imas_type": "generic_grid_constant_space_dimension",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridConstantSpaceDimension,
        },
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
class ObliqueStatic(IdsBaseClass):
    """

    :ivar r : Major radius of the reference point (from which the alpha and beta angles are defined, marked by a + on the diagram)
    :ivar z : Height of the reference point (from which the alpha and beta angles are defined, marked by a + on the diagram)
    :ivar length_alpha : Length of the parallelogram side inclined with angle alpha with respect to the major radius axis
    :ivar length_beta : Length of the parallelogram side inclined with angle beta with respect to the height axis
    :ivar alpha : Inclination of first angle measured counter-clockwise from horizontal outwardly directed radial vector (grad R).
    :ivar beta : Inclination of second angle measured counter-clockwise from vertically upwards directed vector (grad Z). If both alpha and beta are zero (rectangle) then the simpler rectangular elements description should be used.
    """

    class Meta:
        name = "oblique_static"
        is_root_ids = False

    r: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    z: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    length_alpha: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    length_beta: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    alpha: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    beta: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class GenericGridConstant(IdsBaseClass):
    """

    :ivar path : Path of the grid, including the IDS name, in case of implicit reference to a grid_ggd node described in another IDS. To be filled only if the grid is not described explicitly in this grid_ggd structure. Example syntax: IDS::wall/0/description_ggd(1)/grid_ggd, means that the grid is located in the wall IDS, occurrence 0, with relative path description_ggd(1)/grid_ggd, using Fortran index convention (here : first index of the array)
    :ivar space : Set of grid spaces
    :ivar grid_subset : Grid subsets
    """

    class Meta:
        name = "generic_grid_constant"
        is_root_ids = False

    path: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    space: Optional[GenericGridConstantSpace] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridConstantSpace
        ),
        metadata={
            "imas_type": "generic_grid_constant_space",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridConstantSpace,
        },
    )
    grid_subset: Optional[GenericGridConstantGridSubset] = field(
        default_factory=lambda: StructArray(
            type_input=GenericGridConstantGridSubset
        ),
        metadata={
            "imas_type": "generic_grid_constant_grid_subset",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridConstantGridSubset,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class Outline2DGeometryStatic(IdsBaseClass):
    """

    :ivar geometry_type : Type used to describe the element shape (1:&#39;outline&#39;, 2:&#39;rectangle&#39;, 3:&#39;oblique&#39;, 4:&#39;arcs of circle, 5: &#39;annulus&#39;, 6 : &#39;thick line&#39;)
    :ivar outline : Irregular outline of the element. Repeat the first point since this is a closed contour
    :ivar rectangle : Rectangular description of the element
    :ivar oblique : Parallelogram description of the element
    :ivar arcs_of_circle : Description of the element contour by a set of arcs of circle. For each of these, the position of the start point is given together with the curvature radius. The end point is given by the start point of the next arc of circle.
    :ivar annulus : The element is an annulus of centre R, Z, with inner radius radius_inner and outer radius radius_outer
    :ivar thick_line : The element is approximated by a rectangle defined by a central segment and a thickness in the direction perpendicular to the segment
    """

    class Meta:
        name = "outline_2d_geometry_static"
        is_root_ids = False

    geometry_type: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    outline: Optional[Rz1DStatic] = field(
        default=None,
        metadata={"imas_type": "rz1d_static", "field_type": Rz1DStatic},
    )
    rectangle: Optional[RectangleStatic] = field(
        default=None,
        metadata={
            "imas_type": "rectangle_static",
            "field_type": RectangleStatic,
        },
    )
    oblique: Optional[ObliqueStatic] = field(
        default=None,
        metadata={"imas_type": "oblique_static", "field_type": ObliqueStatic},
    )
    arcs_of_circle: Optional[ArcsOfCircleStatic] = field(
        default=None,
        metadata={
            "imas_type": "arcs_of_circle_static",
            "field_type": ArcsOfCircleStatic,
        },
    )
    annulus: Optional[AnnulusStatic] = field(
        default=None,
        metadata={"imas_type": "annulus_static", "field_type": AnnulusStatic},
    )
    thick_line: Optional[ThickLineStatic] = field(
        default=None,
        metadata={
            "imas_type": "thick_line_static",
            "field_type": ThickLineStatic,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class Xyz1DPositionsStatic(IdsBaseClass):
    """

    :ivar x : List of X coordinates
    :ivar y : List of Y coordinates
    :ivar z : List of Z coordinates
    """

    class Meta:
        name = "xyz1d_positions_static"
        is_root_ids = False

    x: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    y: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../x"},
            "field_type": np.ndarray,
        },
    )
    z: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../x"},
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
class FerriticObjectTimeSlice(IdsBaseClass):
    """

    :ivar b_field_r : R component of the magnetic field at each centroid
    :ivar b_field_phi : Toroidal component of the magnetic field at each centroid
    :ivar b_field_z : Z component of the magnetic field at each centroid
    :ivar magnetic_moment_r : R component of the magnetic moment of each element
    :ivar magnetic_moment_phi : Toroidal component of the magnetic moment of each element
    :ivar magnetic_moment_z : Z component of the magnetic moment of each element
    :ivar time : Time
    """

    class Meta:
        name = "ferritic_object_time_slice"
        is_root_ids = False

    b_field_r: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../centroid/x"},
            "field_type": np.ndarray,
        },
    )
    b_field_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../centroid/x"},
            "field_type": np.ndarray,
        },
    )
    b_field_z: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../centroid/x"},
            "field_type": np.ndarray,
        },
    )
    magnetic_moment_r: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../centroid/x"},
            "field_type": np.ndarray,
        },
    )
    magnetic_moment_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../centroid/x"},
            "field_type": np.ndarray,
        },
    )
    magnetic_moment_z: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../centroid/x"},
            "field_type": np.ndarray,
        },
    )
    time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class FerriticObject(IdsBaseClass):
    """

    :ivar centroid : List of positions of the centroids, in Cartesian coordinates
    :ivar volume : Volume of each element of this object
    :ivar saturated_relative_permeability : Saturated relative magnetic permeability of each element
    :ivar permeability_table_index : Index of permeability table to be used for each element. If not allocated or if an element is equal to EMPTY_INT, use the sibling saturated relative permeability instead ../relative_permeability, for that element
    :ivar axisymmetric : Optional equivalent axisymmetric representation of the geometry of each element (e.g. for each iron core segment), typically used to represent iron core in axisymmetric equilibrium solvers
    :ivar ggd_object_index : Index of GGD volumic object corresponding to each element. Refers to the array /grid_ggd/space(1)/objects_per_dimension(4)/object
    :ivar time_slice : Dynamic quantities, per time slice
    """

    class Meta:
        name = "ferritic_object"
        is_root_ids = False

    centroid: Optional[Xyz1DPositionsStatic] = field(
        default=None,
        metadata={
            "imas_type": "xyz1d_positions_static",
            "field_type": Xyz1DPositionsStatic,
        },
    )
    volume: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../centroid/x"},
            "field_type": np.ndarray,
        },
    )
    saturated_relative_permeability: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../centroid/x"},
            "field_type": np.ndarray,
        },
    )
    permeability_table_index: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=int),
        metadata={
            "imas_type": "INT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../centroid/x"},
            "field_type": np.ndarray,
        },
    )
    axisymmetric: Optional[Outline2DGeometryStatic] = field(
        default_factory=lambda: StructArray(type_input=Outline2DGeometryStatic),
        metadata={
            "imas_type": "outline_2d_geometry_static",
            "ndims": 1,
            "coordinates": {"coordinate1": "../centroid/x"},
            "field_type": Outline2DGeometryStatic,
        },
    )
    ggd_object_index: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=int),
        metadata={
            "imas_type": "INT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../centroid/x"},
            "field_type": np.ndarray,
        },
    )
    time_slice: Optional[FerriticObjectTimeSlice] = field(
        default_factory=lambda: StructArray(type_input=FerriticObjectTimeSlice),
        metadata={
            "imas_type": "ferritic_object_time_slice",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": FerriticObjectTimeSlice,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class FerriticPermeabilityTable(IdsBaseClass):
    """

    :ivar name : Name of this table
    :ivar description : Description of this table
    :ivar b_field : Array of magnetic field values, for each of which the relative permeability is given
    :ivar relative_permeability : Relative permeability as a function of the magnetic field
    """

    class Meta:
        name = "ferritic_permeability_table"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    description: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    b_field: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    relative_permeability: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../b_field"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class Ferritic(IdsBaseClass):
    """

    :ivar ids_properties :
    :ivar object : Set of n objects characterized by a list of centroids, volumes, and permeabilities. Optionally a full 3D description of the n volumes may be given in ../grid_ggd. Here the index for each element given in the grid_ggd should be referenced by the object set.
    :ivar permeability_table : Set of tables for relative permeability as a function of the magnetic field
    :ivar grid_ggd : GGD for describing the 3D geometry of the various objects and their elements
    :ivar code :
    :ivar time : Generic time
    """

    class Meta:
        name = "ferritic"
        is_root_ids = True

    ids_properties: Optional[IdsProperties] = field(
        default=None,
        metadata={"imas_type": "ids_properties", "field_type": IdsProperties},
    )
    object: Optional[FerriticObject] = field(
        default_factory=lambda: StructArray(type_input=FerriticObject),
        metadata={
            "imas_type": "ferritic_object",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": FerriticObject,
        },
    )
    permeability_table: Optional[FerriticPermeabilityTable] = field(
        default_factory=lambda: StructArray(
            type_input=FerriticPermeabilityTable
        ),
        metadata={
            "imas_type": "ferritic_permeability_table",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": FerriticPermeabilityTable,
        },
    )
    grid_ggd: Optional[GenericGridConstant] = field(
        default=None,
        metadata={
            "imas_type": "generic_grid_constant",
            "field_type": GenericGridConstant,
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
