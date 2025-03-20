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
class Rz0DDynamicAos(IdsBaseClass):
    """

    :ivar r : Major radius
    :ivar z : Height
    """

    class Meta:
        name = "rz0d_dynamic_aos"
        is_root_ids = False

    r: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    z: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
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
class Rz1DDynamicAos(IdsBaseClass):
    """

    :ivar r : Major radius
    :ivar z : Height
    """

    class Meta:
        name = "rz1d_dynamic_aos"
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
class Rphizpsirho0DDynamicAos3(IdsBaseClass):
    """

    :ivar r : Major radius
    :ivar phi : Toroidal angle (oriented counter-clockwise when viewing from above)
    :ivar z : Height
    :ivar rho_tor_norm : Normalized toroidal flux coordinate. The normalizing value for rho_tor_norm, is the toroidal flux coordinate at the equilibrium boundary (LCFS or 99.x % of the LCFS in case of a fixed boundary equilibium calculation, see time_slice/boundary/b_flux_pol_norm in the equilibrium IDS)
    :ivar psi : Poloidal magnetic flux
    """

    class Meta:
        name = "rphizpsirho0d_dynamic_aos3"
        is_root_ids = False

    r: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    phi: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    z: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    rho_tor_norm: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    psi: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
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
class EquilibriumCoordinateSystem(IdsBaseClass):
    """

    :ivar grid_type : Type of coordinate system
    :ivar grid : Definition of the 2D grid
    :ivar r : Values of the major radius on the grid
    :ivar z : Values of the Height on the grid
    :ivar jacobian : Absolute value of the jacobian of the coordinate system
    :ivar tensor_covariant : Covariant metric tensor on every point of the grid described by grid_type
    :ivar tensor_contravariant : Contravariant metric tensor on every point of the grid described by grid_type
    """

    class Meta:
        name = "equilibrium_coordinate_system"
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
class EquilibriumContourTreeNode(IdsBaseClass):
    """

    :ivar critical_type : 0-minimum, 1-saddle, 2-maximum
    :ivar r : Major radius
    :ivar z : Height
    :ivar psi : Value of the poloidal flux at the node
    :ivar levelset : Single poloidal flux contour including critical point (x-point only)
    """

    class Meta:
        name = "equilibrium_contour_tree_node"
        is_root_ids = False

    critical_type: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    r: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    z: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    psi: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    levelset: Optional[Rz1DDynamicAos] = field(
        default=None,
        metadata={
            "imas_type": "rz1d_dynamic_aos",
            "field_type": Rz1DDynamicAos,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class EquilibriumContourTree(IdsBaseClass):
    """

    :ivar node : Set of nodes. A contour tree node is defined by its critical type and position within the poloidal plane. A critical type of 1 references an x-point whilst a critical type of 0 or 2 references an o-point. Both X-points and O-points are rarely coincident with nodes defining the poloidal upon which the poloidal flux map is defined. The order in which the critical points are stored in the nodes array of structure is only important for the primary plasma O-point and X-points. If present, the primary plasma O-point should be placed as the first element of the nodes array of structure. If present, the primary plasma X-point should be the second element in the nodes structure
    :ivar edges : Edges connect nodes to one another. A single node may connect to multiple edges such as the case where a single maximum (a hill) may topologically link to multiple minima (the floors of different valleys). For each edge (1st dimension), the index of the two connected nodes are listed (index referring to the ../node array)
    """

    class Meta:
        name = "equilibrium_contour_tree"
        is_root_ids = False

    node: Optional[EquilibriumContourTreeNode] = field(
        default_factory=lambda: StructArray(
            type_input=EquilibriumContourTreeNode
        ),
        metadata={
            "imas_type": "equilibrium_contour_tree_node",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": EquilibriumContourTreeNode,
        },
    )
    edges: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=int),
        metadata={
            "imas_type": "INT_2D",
            "ndims": 2,
            "coordinates": {"coordinate1": "1...N", "coordinate2": "1...2"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class EquilibriumGap(IdsBaseClass):
    """

    :ivar name : Short string identifier (unique for a given device)
    :ivar description : Description, e.g. mid-plane gap
    :ivar r : Major radius of the reference point
    :ivar z : Height of the reference point
    :ivar angle : Angle measured clockwise from radial cylindrical vector (grad R) to gap vector (pointing away from reference point)
    :ivar value : Value of the gap, i.e. distance between the reference point and the separatrix along the gap direction
    """

    class Meta:
        name = "equilibrium_gap"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    description: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    r: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    z: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    angle: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    value: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class EquilibriumProfiles1DRz1DDynamicAos(IdsBaseClass):
    """

    :ivar r : Major radius
    :ivar z : Height
    """

    class Meta:
        name = "equilibrium_profiles_1d_rz1d_dynamic_aos"
        is_root_ids = False

    r: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../psi"},
            "field_type": np.ndarray,
        },
    )
    z: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../psi"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class EquilibriumConvergence(IdsBaseClass):
    """

    :ivar iterations_n : Number of iterations carried out in the convergence loop
    :ivar grad_shafranov_deviation_expression : Expression for calculating the residual deviation between the left and right hand side of the Grad Shafranov equation
    :ivar grad_shafranov_deviation_value : Value of the residual deviation between the left and right hand side of the Grad Shafranov equation, evaluated as per grad_shafranov_deviation_expression
    :ivar result : Convergence result
    """

    class Meta:
        name = "equilibrium_convergence"
        is_root_ids = False

    iterations_n: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    grad_shafranov_deviation_expression: Optional[IdentifierDynamicAos3] = (
        field(
            default=None,
            metadata={
                "imas_type": "identifier_dynamic_aos3",
                "field_type": IdentifierDynamicAos3,
            },
        )
    )
    grad_shafranov_deviation_value: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    result: Optional[IdentifierDynamicAos3] = field(
        default=None,
        metadata={
            "imas_type": "identifier_dynamic_aos3",
            "field_type": IdentifierDynamicAos3,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class EquilibriumBoundaryClosest(IdsBaseClass):
    """

    :ivar r : Major radius
    :ivar z : Height
    :ivar distance : Distance to the plasma boundary
    """

    class Meta:
        name = "equilibrium_boundary_closest"
        is_root_ids = False

    r: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    z: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    distance: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class EquilibriumBoundary(IdsBaseClass):
    """

    :ivar type : 0 (limiter) or 1 (diverted)
    :ivar outline : RZ outline of the plasma boundary
    :ivar psi_norm : Value of the normalized poloidal flux at which the boundary is taken, the flux being normalized to its value at the separatrix (so psi_norm = 1 if the boundary is the separatrix)
    :ivar psi : Value of the poloidal flux at which the boundary is taken
    :ivar geometric_axis : RZ position of the geometric axis (defined as (Rmin+Rmax) / 2 and (Zmin+Zmax) / 2 of the boundary)
    :ivar minor_radius : Minor radius of the plasma boundary (defined as (Rmax-Rmin) / 2 of the boundary)
    :ivar elongation : Elongation of the plasma boundary
    :ivar triangularity : Triangularity of the plasma boundary
    :ivar triangularity_upper : Upper triangularity of the plasma boundary
    :ivar triangularity_lower : Lower triangularity of the plasma boundary
    :ivar squareness_upper_inner : Upper inner squareness of the plasma boundary (definition from T. Luce, Plasma Phys. Control. Fusion 55 (2013) 095009)
    :ivar squareness_upper_outer : Upper outer squareness of the plasma boundary (definition from T. Luce, Plasma Phys. Control. Fusion 55 (2013) 095009)
    :ivar squareness_lower_inner : Lower inner squareness of the plasma boundary (definition from T. Luce, Plasma Phys. Control. Fusion 55 (2013) 095009)
    :ivar squareness_lower_outer : Lower outer squareness of the plasma boundary (definition from T. Luce, Plasma Phys. Control. Fusion 55 (2013) 095009)
    :ivar closest_wall_point : Position and distance to the plasma boundary of the point of the first wall which is the closest to plasma boundary
    :ivar dr_dz_zero_point : Outboard point on the separatrix on which dr/dz = 0 (local maximum of the major radius of the separatrix). In case of multiple local maxima, the closest one from z=z_magnetic_axis is chosen.
    :ivar gap : Set of gaps, defined by a reference point and a direction.
    """

    class Meta:
        name = "equilibrium_boundary"
        is_root_ids = False

    type: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    outline: Optional[Rz1DDynamicAos] = field(
        default=None,
        metadata={
            "imas_type": "rz1d_dynamic_aos",
            "field_type": Rz1DDynamicAos,
        },
    )
    psi_norm: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    psi: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    geometric_axis: Optional[Rz0DDynamicAos] = field(
        default=None,
        metadata={
            "imas_type": "rz0d_dynamic_aos",
            "field_type": Rz0DDynamicAos,
        },
    )
    minor_radius: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    elongation: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    triangularity: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    triangularity_upper: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    triangularity_lower: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    squareness_upper_inner: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    squareness_upper_outer: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    squareness_lower_inner: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    squareness_lower_outer: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    closest_wall_point: Optional[EquilibriumBoundaryClosest] = field(
        default=None,
        metadata={
            "imas_type": "equilibrium_boundary_closest",
            "field_type": EquilibriumBoundaryClosest,
        },
    )
    dr_dz_zero_point: Optional[Rz0DDynamicAos] = field(
        default=None,
        metadata={
            "imas_type": "rz0d_dynamic_aos",
            "field_type": Rz0DDynamicAos,
        },
    )
    gap: Optional[EquilibriumGap] = field(
        default_factory=lambda: StructArray(type_input=EquilibriumGap),
        metadata={
            "imas_type": "equilibrium_gap",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": EquilibriumGap,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class EquilibriumGlobalQuantitiesCurrentCentre(IdsBaseClass):
    """

    :ivar r : Major radius of the current center, defined as integral over the poloidal cross section of (j_tor*r*dS) / Ip
    :ivar z : Height of the current center, defined as integral over the poloidal cross section of (j_tor*z*dS) / Ip
    :ivar velocity_z : Vertical velocity of the current center
    """

    class Meta:
        name = "equilibrium_global_quantities_current_centre"
        is_root_ids = False

    r: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    z: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    velocity_z: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class EquilibriumGlobalQuantitiesMagneticAxis(IdsBaseClass):
    """

    :ivar r : Major radius of the magnetic axis
    :ivar z : Height of the magnetic axis
    :ivar b_field_phi : Total toroidal magnetic field at the magnetic axis
    """

    class Meta:
        name = "equilibrium_global_quantities_magnetic_axis"
        is_root_ids = False

    r: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    z: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    b_field_phi: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class EquilibriumGlobalQuantitiesQmin(IdsBaseClass):
    """

    :ivar value : Minimum q value
    :ivar rho_tor_norm : Minimum q position in normalized toroidal flux coordinate
    :ivar psi_norm : Minimum q position in normalised poloidal flux
    :ivar psi : Minimum q position in poloidal flux
    """

    class Meta:
        name = "equilibrium_global_quantities_qmin"
        is_root_ids = False

    value: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    rho_tor_norm: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    psi_norm: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    psi: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class EqulibriumGlobalQuantities(IdsBaseClass):
    """

    :ivar beta_pol : Poloidal beta. Defined as betap = 4 int(p dV) / [R_0 * mu_0 * Ip^2]
    :ivar beta_tor : Toroidal beta, defined as the volume-averaged total perpendicular pressure divided by (B0^2/(2*mu0)), i.e. beta_toroidal = 2 mu0 int(p dV) / V / B0^2
    :ivar beta_tor_norm : Normalized toroidal beta, defined as 100 * beta_tor * a[m] * B0 [T] / ip [MA]
    :ivar ip : Plasma current (toroidal component). Positive sign means anti-clockwise when viewed from above.
    :ivar li_3 : Internal inductance
    :ivar volume : Total plasma volume
    :ivar area : Area of the LCFS poloidal cross section
    :ivar surface : Surface area of the toroidal flux surface
    :ivar length_pol : Poloidal length of the magnetic surface
    :ivar psi_axis : Poloidal flux at the magnetic axis
    :ivar psi_boundary : Poloidal flux at the selected plasma boundary
    :ivar rho_tor_boundary : Toroidal flux coordinate at the selected plasma boundary
    :ivar magnetic_axis : Magnetic axis position and toroidal field
    :ivar current_centre : Position and vertical velocity of the current centre
    :ivar q_axis : q at the magnetic axis
    :ivar q_95 : q at the 95% poloidal flux surface (only positive when toroidal current and magnetic field are in same direction)
    :ivar q_min : Minimum q value and position
    :ivar energy_mhd : Plasma energy content = 3/2 * int(p,dV) with p being the total pressure (thermal + fast particles) [J]. Time-dependent; Scalar
    :ivar psi_external_average : Average (over the plasma poloidal cross section) plasma poloidal magnetic flux produced by all external circuits (CS and PF coils, eddy currents, VS in-vessel coils), given by the following formula : int(psi_external.j_tor.dS) / Ip
    :ivar v_external : External voltage, i.e. time derivative of psi_external_average (with a minus sign : - d_psi_external_average/d_time)
    :ivar plasma_inductance : Plasma inductance 2 E_magnetic/Ip^2, where E_magnetic = 1/2 * int(psi.j_tor.dS) (integral over the plasma poloidal cross-section)
    :ivar plasma_resistance : Plasma resistance = int(e_field.j.dV) / Ip^2
    """

    class Meta:
        name = "equlibrium_global_quantities"
        is_root_ids = False

    beta_pol: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    beta_tor: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    beta_tor_norm: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    ip: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    li_3: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    volume: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    area: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    surface: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    length_pol: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    psi_axis: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    psi_boundary: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    rho_tor_boundary: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    magnetic_axis: Optional[EquilibriumGlobalQuantitiesMagneticAxis] = field(
        default=None,
        metadata={
            "imas_type": "equilibrium_global_quantities_magnetic_axis",
            "field_type": EquilibriumGlobalQuantitiesMagneticAxis,
        },
    )
    current_centre: Optional[EquilibriumGlobalQuantitiesCurrentCentre] = field(
        default=None,
        metadata={
            "imas_type": "equilibrium_global_quantities_current_centre",
            "field_type": EquilibriumGlobalQuantitiesCurrentCentre,
        },
    )
    q_axis: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    q_95: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    q_min: Optional[EquilibriumGlobalQuantitiesQmin] = field(
        default=None,
        metadata={
            "imas_type": "equilibrium_global_quantities_qmin",
            "field_type": EquilibriumGlobalQuantitiesQmin,
        },
    )
    energy_mhd: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    psi_external_average: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    v_external: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    plasma_inductance: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    plasma_resistance: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class EquilibriumConstraintsPurePosition(IdsBaseClass):
    """

    :ivar position_measured : Measured or estimated position
    :ivar source : Path to the source data for this measurement in the IMAS data dictionary
    :ivar time_measurement : Exact time slice used from the time array of the measurement source data. If the time slice does not exist in the time array of the source data, it means linear interpolation has been used
    :ivar exact : Integer flag : 1 means exact data, taken as an exact input without being fitted; 0 means the equilibrium code does a least square fit
    :ivar weight : Weight given to the measurement
    :ivar position_reconstructed : Position estimated from the reconstructed equilibrium
    :ivar chi_squared_r : Squared error on the major radius normalized by the variance considered in the minimization process : chi_squared = weight^2 *(position_reconstructed/r - position_measured/r)^2 / sigma^2, where sigma is the standard deviation of the measurement error
    :ivar chi_squared_z : Squared error on the altitude normalized by the variance considered in the minimization process : chi_squared = weight^2 *(position_reconstructed/z - position_measured/z)^2 / sigma^2, where sigma is the standard deviation of the measurement error
    """

    class Meta:
        name = "equilibrium_constraints_pure_position"
        is_root_ids = False

    position_measured: Optional[Rz0DDynamicAos] = field(
        default=None,
        metadata={
            "imas_type": "rz0d_dynamic_aos",
            "field_type": Rz0DDynamicAos,
        },
    )
    source: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    time_measurement: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    exact: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    weight: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    position_reconstructed: Optional[Rz0DDynamicAos] = field(
        default=None,
        metadata={
            "imas_type": "rz0d_dynamic_aos",
            "field_type": Rz0DDynamicAos,
        },
    )
    chi_squared_r: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    chi_squared_z: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class EquilibriumConstraints0DPosition(IdsBaseClass):
    """

    :ivar measured : Measured value
    :ivar position : Position at which this measurement is given
    :ivar source : Path to the source data for this measurement in the IMAS data dictionary
    :ivar time_measurement : Exact time slice used from the time array of the measurement source data. If the time slice does not exist in the time array of the source data, it means linear interpolation has been used
    :ivar exact : Integer flag : 1 means exact data, taken as an exact input without being fitted; 0 means the equilibrium code does a least square fit
    :ivar weight : Weight given to the measurement
    :ivar reconstructed : Value calculated from the reconstructed equilibrium
    :ivar chi_squared : Squared error normalized by the variance considered in the minimization process : chi_squared = weight^2 *(reconstructed - measured)^2 / sigma^2, where sigma is the standard deviation of the measurement error
    """

    class Meta:
        name = "equilibrium_constraints_0D_position"
        is_root_ids = False

    measured: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    position: Optional[Rphizpsirho0DDynamicAos3] = field(
        default=None,
        metadata={
            "imas_type": "rphizpsirho0d_dynamic_aos3",
            "field_type": Rphizpsirho0DDynamicAos3,
        },
    )
    source: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    time_measurement: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    exact: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    weight: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    reconstructed: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    chi_squared: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class EquilibriumConstraints0DB0Like(IdsBaseClass):
    """

    :ivar measured : Measured value
    :ivar source : Path to the source data for this measurement in the IMAS data dictionary
    :ivar time_measurement : Exact time slice used from the time array of the measurement source data. If the time slice does not exist in the time array of the source data, it means linear interpolation has been used
    :ivar exact : Integer flag : 1 means exact data, taken as an exact input without being fitted; 0 means the equilibrium code does a least square fit
    :ivar weight : Weight given to the measurement
    :ivar reconstructed : Value calculated from the reconstructed equilibrium
    :ivar chi_squared : Squared error normalized by the variance considered in the minimization process : chi_squared = weight^2 *(reconstructed - measured)^2 / sigma^2, where sigma is the standard deviation of the measurement error
    """

    class Meta:
        name = "equilibrium_constraints_0D_b0_like"
        is_root_ids = False

    measured: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    source: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    time_measurement: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    exact: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    weight: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    reconstructed: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    chi_squared: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class EquilibriumConstraints0DIpLike(IdsBaseClass):
    """

    :ivar measured : Measured value
    :ivar source : Path to the source data for this measurement in the IMAS data dictionary
    :ivar time_measurement : Exact time slice used from the time array of the measurement source data. If the time slice does not exist in the time array of the source data, it means linear interpolation has been used
    :ivar exact : Integer flag : 1 means exact data, taken as an exact input without being fitted; 0 means the equilibrium code does a least square fit
    :ivar weight : Weight given to the measurement
    :ivar reconstructed : Value calculated from the reconstructed equilibrium
    :ivar chi_squared : Squared error normalized by the variance considered in the minimization process : chi_squared = weight^2 *(reconstructed - measured)^2 / sigma^2, where sigma is the standard deviation of the measurement error
    """

    class Meta:
        name = "equilibrium_constraints_0D_ip_like"
        is_root_ids = False

    measured: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    source: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    time_measurement: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    exact: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    weight: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    reconstructed: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    chi_squared: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class EquilibriumConstraints0DOneLike(IdsBaseClass):
    """

    :ivar measured : Measured value
    :ivar source : Path to the source data for this measurement in the IMAS data dictionary
    :ivar time_measurement : Exact time slice used from the time array of the measurement source data. If the time slice does not exist in the time array of the source data, it means linear interpolation has been used
    :ivar exact : Integer flag : 1 means exact data, taken as an exact input without being fitted; 0 means the equilibrium code does a least square fit
    :ivar weight : Weight given to the measurement
    :ivar reconstructed : Value calculated from the reconstructed equilibrium
    :ivar chi_squared : Squared error normalized by the variance considered in the minimization process : chi_squared = weight^2 *(reconstructed - measured)^2 / sigma^2, where sigma is the standard deviation of the measurement error
    """

    class Meta:
        name = "equilibrium_constraints_0D_one_like"
        is_root_ids = False

    measured: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    source: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    time_measurement: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    exact: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    weight: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    reconstructed: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    chi_squared: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class EquilibriumConstraints0D(IdsBaseClass):
    """

    :ivar measured : Measured value
    :ivar source : Path to the source data for this measurement in the IMAS data dictionary
    :ivar time_measurement : Exact time slice used from the time array of the measurement source data. If the time slice does not exist in the time array of the source data, it means linear interpolation has been used
    :ivar exact : Integer flag : 1 means exact data, taken as an exact input without being fitted; 0 means the equilibrium code does a least square fit
    :ivar weight : Weight given to the measurement
    :ivar reconstructed : Value calculated from the reconstructed equilibrium
    :ivar chi_squared : Squared error normalized by the variance considered in the minimization process : chi_squared = weight^2 *(reconstructed - measured)^2 / sigma^2, where sigma is the standard deviation of the measurement error
    """

    class Meta:
        name = "equilibrium_constraints_0D"
        is_root_ids = False

    measured: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    source: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    time_measurement: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    exact: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    weight: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    reconstructed: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    chi_squared: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class EquilibriumConstraintsMagnetization(IdsBaseClass):
    """

    :ivar magnetization_r : Magnetization M of the iron core segment along the major radius axis, assumed to be constant inside a given iron segment. Reminder : H = 1/mu0 * B - mur * M;
    :ivar magnetization_z : Magnetization M of the iron core segment along the vertical axis, assumed to be constant inside a given iron segment. Reminder : H = 1/mu0 * B - mur * M;
    """

    class Meta:
        name = "equilibrium_constraints_magnetization"
        is_root_ids = False

    magnetization_r: Optional[EquilibriumConstraints0D] = field(
        default=None,
        metadata={
            "imas_type": "equilibrium_constraints_0D",
            "field_type": EquilibriumConstraints0D,
        },
    )
    magnetization_z: Optional[EquilibriumConstraints0D] = field(
        default=None,
        metadata={
            "imas_type": "equilibrium_constraints_0D",
            "field_type": EquilibriumConstraints0D,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class EquilibriumConstraints(IdsBaseClass):
    """

    :ivar b_field_tor_vacuum_r : Vacuum field times major radius in the toroidal field magnet. Positive sign means anti-clockwise when viewed from above
    :ivar b_field_pol_probe : Set of poloidal field probes
    :ivar diamagnetic_flux : Diamagnetic flux
    :ivar faraday_angle : Set of faraday angles
    :ivar mse_polarization_angle : Set of MSE polarization angles
    :ivar flux_loop : Set of flux loops
    :ivar ip : Plasma current. Positive sign means anti-clockwise when viewed from above
    :ivar iron_core_segment : Magnetization M of a set of iron core segments
    :ivar n_e : Set of local density measurements
    :ivar n_e_line : Set of line integrated density measurements
    :ivar pf_current : Current in a set of poloidal field coils
    :ivar pf_passive_current : Current in a set of axisymmetric passive conductors
    :ivar pressure : Set of total pressure estimates
    :ivar pressure_rotational : Set of rotational pressure estimates. The rotational pressure is defined as R0^2*rho*omega^2 / 2, where omega is the toroidal rotation frequency, rho=ne(R0,psi)*m, and m is the plasma equivalent mass.
    :ivar q : Set of safety factor estimates at various positions
    :ivar j_phi : Set of flux-surface averaged toroidal current density approximations at various positions  (= average(j_tor/R) / average(1/R))
    :ivar j_parallel : Set of flux-surface averaged parallel current density approximations at various positions (= average(j.B) / B0, where B0 = /vacuum_toroidal_field/b0)
    :ivar x_point : Array of X-points, for each of them the RZ position is given
    :ivar strike_point : Array of strike points, for each of them the RZ position is given
    :ivar chi_squared_reduced : Sum of the chi_squared of all constraints used for the equilibrium reconstruction, divided by the number of degrees of freedom of the identification model
    :ivar freedom_degrees_n : Number of degrees of freedom of the identification model
    :ivar constraints_n : Number of constraints used (i.e. having a non-zero weight)
    """

    class Meta:
        name = "equilibrium_constraints"
        is_root_ids = False

    b_field_tor_vacuum_r: Optional[EquilibriumConstraints0D] = field(
        default=None,
        metadata={
            "imas_type": "equilibrium_constraints_0D",
            "field_type": EquilibriumConstraints0D,
        },
    )
    b_field_pol_probe: Optional[EquilibriumConstraints0DOneLike] = field(
        default_factory=lambda: StructArray(
            type_input=EquilibriumConstraints0DOneLike
        ),
        metadata={
            "imas_type": "equilibrium_constraints_0D_one_like",
            "ndims": 1,
            "coordinates": {"coordinate1": "IDS:magnetics/b_field_pol_probe"},
            "field_type": EquilibriumConstraints0DOneLike,
        },
    )
    diamagnetic_flux: Optional[EquilibriumConstraints0DB0Like] = field(
        default=None,
        metadata={
            "imas_type": "equilibrium_constraints_0D_b0_like",
            "field_type": EquilibriumConstraints0DB0Like,
        },
    )
    faraday_angle: Optional[EquilibriumConstraints0D] = field(
        default_factory=lambda: StructArray(
            type_input=EquilibriumConstraints0D
        ),
        metadata={
            "imas_type": "equilibrium_constraints_0D",
            "ndims": 1,
            "coordinates": {"coordinate1": "IDS:polarimeter/channel"},
            "field_type": EquilibriumConstraints0D,
        },
    )
    mse_polarization_angle: Optional[EquilibriumConstraints0D] = field(
        default_factory=lambda: StructArray(
            type_input=EquilibriumConstraints0D
        ),
        metadata={
            "imas_type": "equilibrium_constraints_0D",
            "ndims": 1,
            "coordinates": {"coordinate1": "IDS:mse/channel"},
            "field_type": EquilibriumConstraints0D,
        },
    )
    flux_loop: Optional[EquilibriumConstraints0D] = field(
        default_factory=lambda: StructArray(
            type_input=EquilibriumConstraints0D
        ),
        metadata={
            "imas_type": "equilibrium_constraints_0D",
            "ndims": 1,
            "coordinates": {"coordinate1": "IDS:magnetics/flux_loop"},
            "field_type": EquilibriumConstraints0D,
        },
    )
    ip: Optional[EquilibriumConstraints0DIpLike] = field(
        default=None,
        metadata={
            "imas_type": "equilibrium_constraints_0D_ip_like",
            "field_type": EquilibriumConstraints0DIpLike,
        },
    )
    iron_core_segment: Optional[EquilibriumConstraintsMagnetization] = field(
        default_factory=lambda: StructArray(
            type_input=EquilibriumConstraintsMagnetization
        ),
        metadata={
            "imas_type": "equilibrium_constraints_magnetization",
            "ndims": 1,
            "coordinates": {"coordinate1": "IDS:iron_core/segment"},
            "field_type": EquilibriumConstraintsMagnetization,
        },
    )
    n_e: Optional[EquilibriumConstraints0DPosition] = field(
        default_factory=lambda: StructArray(
            type_input=EquilibriumConstraints0DPosition
        ),
        metadata={
            "imas_type": "equilibrium_constraints_0D_position",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": EquilibriumConstraints0DPosition,
        },
    )
    n_e_line: Optional[EquilibriumConstraints0D] = field(
        default_factory=lambda: StructArray(
            type_input=EquilibriumConstraints0D
        ),
        metadata={
            "imas_type": "equilibrium_constraints_0D",
            "ndims": 1,
            "coordinates": {"coordinate1": "IDS:interferometer/channel"},
            "field_type": EquilibriumConstraints0D,
        },
    )
    pf_current: Optional[EquilibriumConstraints0DIpLike] = field(
        default_factory=lambda: StructArray(
            type_input=EquilibriumConstraints0DIpLike
        ),
        metadata={
            "imas_type": "equilibrium_constraints_0D_ip_like",
            "ndims": 1,
            "coordinates": {"coordinate1": "IDS:pf_active/coil"},
            "field_type": EquilibriumConstraints0DIpLike,
        },
    )
    pf_passive_current: Optional[EquilibriumConstraints0D] = field(
        default_factory=lambda: StructArray(
            type_input=EquilibriumConstraints0D
        ),
        metadata={
            "imas_type": "equilibrium_constraints_0D",
            "ndims": 1,
            "coordinates": {"coordinate1": "IDS:pf_passive/loop"},
            "field_type": EquilibriumConstraints0D,
        },
    )
    pressure: Optional[EquilibriumConstraints0DPosition] = field(
        default_factory=lambda: StructArray(
            type_input=EquilibriumConstraints0DPosition
        ),
        metadata={
            "imas_type": "equilibrium_constraints_0D_position",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": EquilibriumConstraints0DPosition,
        },
    )
    pressure_rotational: Optional[EquilibriumConstraints0DPosition] = field(
        default_factory=lambda: StructArray(
            type_input=EquilibriumConstraints0DPosition
        ),
        metadata={
            "imas_type": "equilibrium_constraints_0D_position",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": EquilibriumConstraints0DPosition,
        },
    )
    q: Optional[EquilibriumConstraints0DPosition] = field(
        default_factory=lambda: StructArray(
            type_input=EquilibriumConstraints0DPosition
        ),
        metadata={
            "imas_type": "equilibrium_constraints_0D_position",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": EquilibriumConstraints0DPosition,
        },
    )
    j_phi: Optional[EquilibriumConstraints0DPosition] = field(
        default_factory=lambda: StructArray(
            type_input=EquilibriumConstraints0DPosition
        ),
        metadata={
            "imas_type": "equilibrium_constraints_0D_position",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": EquilibriumConstraints0DPosition,
        },
    )
    j_parallel: Optional[EquilibriumConstraints0DPosition] = field(
        default_factory=lambda: StructArray(
            type_input=EquilibriumConstraints0DPosition
        ),
        metadata={
            "imas_type": "equilibrium_constraints_0D_position",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": EquilibriumConstraints0DPosition,
        },
    )
    x_point: Optional[EquilibriumConstraintsPurePosition] = field(
        default_factory=lambda: StructArray(
            type_input=EquilibriumConstraintsPurePosition
        ),
        metadata={
            "imas_type": "equilibrium_constraints_pure_position",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": EquilibriumConstraintsPurePosition,
        },
    )
    strike_point: Optional[EquilibriumConstraintsPurePosition] = field(
        default_factory=lambda: StructArray(
            type_input=EquilibriumConstraintsPurePosition
        ),
        metadata={
            "imas_type": "equilibrium_constraints_pure_position",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": EquilibriumConstraintsPurePosition,
        },
    )
    chi_squared_reduced: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    freedom_degrees_n: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    constraints_n: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )


@idspy_dataclass(repr=False, slots=True)
class EquilibriumProfiles1D(IdsBaseClass):
    """

    :ivar psi : Poloidal flux. Integral of magnetic field passing through a contour defined by the intersection of a flux surface passing through the point of interest and a Z=constant plane. If the integration surface is flat, the surface normal vector is in the increasing vertical coordinate direction, Z, namely upwards.
    :ivar psi_norm : Normalised poloidal flux, namely (psi(rho)-psi(magnetic_axis)) / (psi(LCFS)-psi(magnetic_axis))
    :ivar phi : Toroidal flux
    :ivar pressure : Pressure
    :ivar f : Diamagnetic function (F=R B_Phi)
    :ivar dpressure_dpsi : Derivative of pressure w.r.t. psi
    :ivar f_df_dpsi : Derivative of F w.r.t. Psi, multiplied with F
    :ivar j_phi : Flux surface averaged toroidal current density = average(j_tor/R) / average(1/R)
    :ivar j_parallel : Flux surface averaged approximation to parallel current density = average(j.B) / B0, where B0 = /vacuum_toroidal_field/b0
    :ivar q : Safety factor (only positive when toroidal current and magnetic field are in same direction)
    :ivar magnetic_shear : Magnetic shear, defined as rho_tor/q . dq/drho_tor
    :ivar r_inboard : Radial coordinate (major radius) on the inboard side of the magnetic axis
    :ivar r_outboard : Radial coordinate (major radius) on the outboard side of the magnetic axis
    :ivar rho_tor : Toroidal flux coordinate = sqrt(phi/(pi*b0)), where the toroidal flux, phi, corresponds to time_slice/profiles_1d/phi, the toroidal magnetic field, b0, corresponds to that stored in vacuum_toroidal_field/b0 and pi can be found in the IMAS constants
    :ivar rho_tor_norm : Normalized toroidal flux coordinate. The normalizing value for rho_tor_norm, is the toroidal flux coordinate at the equilibrium boundary (LCFS or 99.x % of the LCFS in case of a fixed boundary equilibium calculation). Namely (rho_tor(rho)-rho_tor(magnetic_axis)) / (rho_tor(boundary)-rho_tor(magnetic_axis))
    :ivar dpsi_drho_tor : Derivative of Psi with respect to Rho_Tor
    :ivar geometric_axis : RZ position of the geometric axis of the magnetic surfaces (defined as (Rmin+Rmax) / 2 and (Zmin+Zmax) / 2 of the surface)
    :ivar elongation : Elongation
    :ivar triangularity_upper : Upper triangularity w.r.t. magnetic axis
    :ivar triangularity_lower : Lower triangularity w.r.t. magnetic axis
    :ivar squareness_upper_inner : Upper inner squareness (definition from T. Luce, Plasma Phys. Control. Fusion 55 (2013) 095009)
    :ivar squareness_upper_outer : Upper outer squareness (definition from T. Luce, Plasma Phys. Control. Fusion 55 (2013) 095009)
    :ivar squareness_lower_inner : Lower inner squareness (definition from T. Luce, Plasma Phys. Control. Fusion 55 (2013) 095009)
    :ivar squareness_lower_outer : Lower outer squareness (definition from T. Luce, Plasma Phys. Control. Fusion 55 (2013) 095009)
    :ivar volume : Volume enclosed in the flux surface
    :ivar rho_volume_norm : Normalized square root of enclosed volume (radial coordinate). The normalizing value is the enclosed volume at the equilibrium boundary (LCFS or 99.x % of the LCFS in case of a fixed boundary equilibium calculation)
    :ivar dvolume_dpsi : Radial derivative of the volume enclosed in the flux surface with respect to Psi
    :ivar dvolume_drho_tor : Radial derivative of the volume enclosed in the flux surface with respect to Rho_Tor
    :ivar area : Cross-sectional area of the flux surface
    :ivar darea_dpsi : Radial derivative of the cross-sectional area of the flux surface with respect to psi
    :ivar darea_drho_tor : Radial derivative of the cross-sectional area of the flux surface with respect to rho_tor
    :ivar surface : Surface area of the toroidal flux surface
    :ivar trapped_fraction : Trapped particle fraction
    :ivar gm1 : Flux surface averaged 1/R^2
    :ivar gm2 : Flux surface averaged |grad_rho_tor|^2/R^2
    :ivar gm3 : Flux surface averaged |grad_rho_tor|^2
    :ivar gm4 : Flux surface averaged 1/B^2
    :ivar gm5 : Flux surface averaged B^2
    :ivar gm6 : Flux surface averaged |grad_rho_tor|^2/B^2
    :ivar gm7 : Flux surface averaged |grad_rho_tor|
    :ivar gm8 : Flux surface averaged R
    :ivar gm9 : Flux surface averaged 1/R
    :ivar b_field_average : Flux surface averaged modulus of B (always positive, irrespective of the sign convention for the B-field direction).
    :ivar b_field_min : Minimum(modulus(B)) on the flux surface (always positive, irrespective of the sign convention for the B-field direction)
    :ivar b_field_max : Maximum(modulus(B)) on the flux surface (always positive, irrespective of the sign convention for the B-field direction)
    :ivar beta_pol : Poloidal beta profile. Defined as betap = 4 int(p dV) / [R_0 * mu_0 * Ip^2]
    :ivar mass_density : Mass density
    """

    class Meta:
        name = "equilibrium_profiles_1d"
        is_root_ids = False

    psi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    psi_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../psi"},
            "field_type": np.ndarray,
        },
    )
    phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../psi"},
            "field_type": np.ndarray,
        },
    )
    pressure: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../psi"},
            "field_type": np.ndarray,
        },
    )
    f: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../psi"},
            "field_type": np.ndarray,
        },
    )
    dpressure_dpsi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../psi"},
            "field_type": np.ndarray,
        },
    )
    f_df_dpsi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../psi"},
            "field_type": np.ndarray,
        },
    )
    j_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../psi"},
            "field_type": np.ndarray,
        },
    )
    j_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../psi"},
            "field_type": np.ndarray,
        },
    )
    q: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../psi"},
            "field_type": np.ndarray,
        },
    )
    magnetic_shear: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../psi"},
            "field_type": np.ndarray,
        },
    )
    r_inboard: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../psi"},
            "field_type": np.ndarray,
        },
    )
    r_outboard: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../psi"},
            "field_type": np.ndarray,
        },
    )
    rho_tor: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../psi"},
            "field_type": np.ndarray,
        },
    )
    rho_tor_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../psi"},
            "field_type": np.ndarray,
        },
    )
    dpsi_drho_tor: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../psi"},
            "field_type": np.ndarray,
        },
    )
    geometric_axis: Optional[EquilibriumProfiles1DRz1DDynamicAos] = field(
        default=None,
        metadata={
            "imas_type": "equilibrium_profiles_1d_rz1d_dynamic_aos",
            "field_type": EquilibriumProfiles1DRz1DDynamicAos,
        },
    )
    elongation: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../psi"},
            "field_type": np.ndarray,
        },
    )
    triangularity_upper: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../psi"},
            "field_type": np.ndarray,
        },
    )
    triangularity_lower: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../psi"},
            "field_type": np.ndarray,
        },
    )
    squareness_upper_inner: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../psi"},
            "field_type": np.ndarray,
        },
    )
    squareness_upper_outer: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../psi"},
            "field_type": np.ndarray,
        },
    )
    squareness_lower_inner: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../psi"},
            "field_type": np.ndarray,
        },
    )
    squareness_lower_outer: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../psi"},
            "field_type": np.ndarray,
        },
    )
    volume: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../psi"},
            "field_type": np.ndarray,
        },
    )
    rho_volume_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../psi"},
            "field_type": np.ndarray,
        },
    )
    dvolume_dpsi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../psi"},
            "field_type": np.ndarray,
        },
    )
    dvolume_drho_tor: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../psi"},
            "field_type": np.ndarray,
        },
    )
    area: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../psi"},
            "field_type": np.ndarray,
        },
    )
    darea_dpsi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../psi"},
            "field_type": np.ndarray,
        },
    )
    darea_drho_tor: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../psi"},
            "field_type": np.ndarray,
        },
    )
    surface: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../psi"},
            "field_type": np.ndarray,
        },
    )
    trapped_fraction: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../psi"},
            "field_type": np.ndarray,
        },
    )
    gm1: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../psi"},
            "field_type": np.ndarray,
        },
    )
    gm2: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../psi"},
            "field_type": np.ndarray,
        },
    )
    gm3: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../psi"},
            "field_type": np.ndarray,
        },
    )
    gm4: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../psi"},
            "field_type": np.ndarray,
        },
    )
    gm5: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../psi"},
            "field_type": np.ndarray,
        },
    )
    gm6: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../psi"},
            "field_type": np.ndarray,
        },
    )
    gm7: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../psi"},
            "field_type": np.ndarray,
        },
    )
    gm8: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../psi"},
            "field_type": np.ndarray,
        },
    )
    gm9: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../psi"},
            "field_type": np.ndarray,
        },
    )
    b_field_average: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../psi"},
            "field_type": np.ndarray,
        },
    )
    b_field_min: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../psi"},
            "field_type": np.ndarray,
        },
    )
    b_field_max: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../psi"},
            "field_type": np.ndarray,
        },
    )
    beta_pol: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../psi"},
            "field_type": np.ndarray,
        },
    )
    mass_density: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../psi"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class EquilibriumProfiles2D(IdsBaseClass):
    """

    :ivar type : Type of profiles (distinguishes contribution from plasma, vaccum fields and total fields)
    :ivar grid_type : Selection of one of a set of grid types
    :ivar grid : Definition of the 2D grid (the content of dim1 and dim2 is defined by the selected grid_type)
    :ivar r : Values of the major radius on the grid
    :ivar z : Values of the Height on the grid
    :ivar psi : Values of the poloidal flux at the grid in the poloidal plane. The poloidal flux is integral of magnetic field passing through a contour defined by the intersection of a flux surface passing through the point of interest and a Z=constant plane. If the integration surface is flat, the surface normal vector is in the increasing vertical coordinate direction, Z, namely upwards.
    :ivar theta : Values of poloidal angle on the grid. The poloidal angle is centered on the magnetic axis and oriented such that (grad rho_tor_norm, grad theta, grad phi) form a right-handed set where grad rho_tor_norm points away from the magnetic axis.
    :ivar phi : Toroidal flux
    :ivar j_phi : Toroidal plasma current density
    :ivar j_parallel : Defined as (j.B)/B0 where j and B are the current density and magnetic field vectors and B0 is the (signed) vacuum toroidal magnetic field strength at the geometric reference point (R0,Z0). It is formally not the component of the plasma current density parallel to the magnetic field
    :ivar b_field_r : R component of the poloidal magnetic field
    :ivar b_field_phi : Toroidal component of the magnetic field
    :ivar b_field_z : Z component of the magnetic field
    """

    class Meta:
        name = "equilibrium_profiles_2d"
        is_root_ids = False

    type: Optional[IdentifierDynamicAos3] = field(
        default=None,
        metadata={
            "imas_type": "identifier_dynamic_aos3",
            "field_type": IdentifierDynamicAos3,
        },
    )
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
    psi: Optional[np.ndarray] = field(
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
    theta: Optional[np.ndarray] = field(
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
    phi: Optional[np.ndarray] = field(
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
    j_phi: Optional[np.ndarray] = field(
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
    j_parallel: Optional[np.ndarray] = field(
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
    b_field_r: Optional[np.ndarray] = field(
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
    b_field_phi: Optional[np.ndarray] = field(
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
    b_field_z: Optional[np.ndarray] = field(
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


@idspy_dataclass(repr=False, slots=True)
class EquilibriumGgd(IdsBaseClass):
    """

    :ivar r : Values of the major radius on various grid subsets
    :ivar z : Values of the Height on various grid subsets
    :ivar psi : Values of the poloidal flux, given on various grid subsets
    :ivar phi : Values of the toroidal flux, given on various grid subsets
    :ivar theta : Values of the poloidal angle, given on various grid subsets. The poloidal angle is centered on the magnetic axis and oriented such that (grad rho_tor_norm, grad theta, grad phi) form a right-handed set where grad rho_tor_norm points away from the magnetic axis.
    :ivar j_phi : Toroidal plasma current density, given on various grid subsets
    :ivar j_parallel : Parallel (to magnetic field) plasma current density, given on various grid subsets
    :ivar b_field_r : R component of the poloidal magnetic field, given on various grid subsets
    :ivar b_field_phi : Toroidal component of the magnetic field, given on various grid subsets
    :ivar b_field_z : Z component of the magnetic field, given on various grid subsets
    """

    class Meta:
        name = "equilibrium_ggd"
        is_root_ids = False

    r: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    z: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
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
    phi: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    theta: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    j_phi: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
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
    b_field_r: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    b_field_phi: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    b_field_z: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class EquilibriumGgdArray(IdsBaseClass):
    """

    :ivar grid : Set of GGD grids for describing the equilibrium, at a given time slice
    :ivar time : Time
    """

    class Meta:
        name = "equilibrium_ggd_array"
        is_root_ids = False

    grid: Optional[GenericGridDynamic] = field(
        default_factory=lambda: StructArray(type_input=GenericGridDynamic),
        metadata={
            "imas_type": "generic_grid_dynamic",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridDynamic,
        },
    )
    time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class EquilibriumTimeSlice(IdsBaseClass):
    """

    :ivar boundary : Description of the plasma boundary. The boundary can be either the real separatrix (provided by a free boundary equilibrium solver) or the 0.99x psi_norm flux surface provided by a fixed boundary equilibrium
    :ivar contour_tree : Description of the topological connectivity of the poloidal flux map critical points as an undirected graph. Critical points are ether local extremum (o-points) or saddle points (x-points) of the poloidal flux map. X-points have zero gradients in orthogonal directions but are not local extremum of the poloidal flux map whilst O-points are.
    :ivar constraints : In case of equilibrium reconstruction under constraints, measurements used to constrain the equilibrium, reconstructed values and accuracy of the fit. The names of the child nodes correspond to the following definition: the solver aims at minimizing a cost function defined as : J=1/2*sum_i [ weight_i^2 (reconstructed_i - measured_i)^2 / sigma_i^2 ]. in which sigma_i is the standard deviation of the measurement error (to be found in the IDS of the measurement)
    :ivar global_quantities : 0D parameters of the equilibrium
    :ivar profiles_1d : Equilibrium profiles (1D radial grid) as a function of the poloidal flux
    :ivar profiles_2d : Equilibrium 2D profiles in the poloidal plane. Multiple 2D representations of the equilibrium can be stored here.
    :ivar ggd : Set of equilibrium representations using the generic grid description
    :ivar coordinate_system : Flux surface coordinate system on a square grid of flux and poloidal angle
    :ivar convergence : Convergence details
    :ivar time : Time
    """

    class Meta:
        name = "equilibrium_time_slice"
        is_root_ids = False

    boundary: Optional[EquilibriumBoundary] = field(
        default=None,
        metadata={
            "imas_type": "equilibrium_boundary",
            "field_type": EquilibriumBoundary,
        },
    )
    contour_tree: Optional[EquilibriumContourTree] = field(
        default=None,
        metadata={
            "imas_type": "equilibrium_contour_tree",
            "field_type": EquilibriumContourTree,
        },
    )
    constraints: Optional[EquilibriumConstraints] = field(
        default=None,
        metadata={
            "imas_type": "equilibrium_constraints",
            "field_type": EquilibriumConstraints,
        },
    )
    global_quantities: Optional[EqulibriumGlobalQuantities] = field(
        default=None,
        metadata={
            "imas_type": "equlibrium_global_quantities",
            "field_type": EqulibriumGlobalQuantities,
        },
    )
    profiles_1d: Optional[EquilibriumProfiles1D] = field(
        default=None,
        metadata={
            "imas_type": "equilibrium_profiles_1d",
            "field_type": EquilibriumProfiles1D,
        },
    )
    profiles_2d: Optional[EquilibriumProfiles2D] = field(
        default_factory=lambda: StructArray(type_input=EquilibriumProfiles2D),
        metadata={
            "imas_type": "equilibrium_profiles_2d",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": EquilibriumProfiles2D,
        },
    )
    ggd: Optional[EquilibriumGgd] = field(
        default_factory=lambda: StructArray(type_input=EquilibriumGgd),
        metadata={
            "imas_type": "equilibrium_ggd",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grids_ggd(itime)/grid"},
            "field_type": EquilibriumGgd,
        },
    )
    coordinate_system: Optional[EquilibriumCoordinateSystem] = field(
        default=None,
        metadata={
            "imas_type": "equilibrium_coordinate_system",
            "field_type": EquilibriumCoordinateSystem,
        },
    )
    convergence: Optional[EquilibriumConvergence] = field(
        default=None,
        metadata={
            "imas_type": "equilibrium_convergence",
            "field_type": EquilibriumConvergence,
        },
    )
    time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class Equilibrium(IdsBaseClass):
    """

    :ivar ids_properties :
    :ivar vacuum_toroidal_field : Characteristics of the vacuum toroidal field (used in rho_tor definition and in the normalization of current densities)
    :ivar grids_ggd : Grids (using the Generic Grid Description), for various time slices. The timebase of this array of structure must be a subset of the time_slice timebase
    :ivar time_slice : Set of equilibria at various time slices
    :ivar code :
    :ivar time : Generic time
    """

    class Meta:
        name = "equilibrium"
        is_root_ids = True

    ids_properties: Optional[IdsProperties] = field(
        default=None,
        metadata={"imas_type": "ids_properties", "field_type": IdsProperties},
    )
    vacuum_toroidal_field: Optional[BTorVacuum1] = field(
        default=None,
        metadata={"imas_type": "b_tor_vacuum_1", "field_type": BTorVacuum1},
    )
    grids_ggd: Optional[EquilibriumGgdArray] = field(
        default_factory=lambda: StructArray(type_input=EquilibriumGgdArray),
        metadata={
            "imas_type": "equilibrium_ggd_array",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": EquilibriumGgdArray,
        },
    )
    time_slice: Optional[EquilibriumTimeSlice] = field(
        default_factory=lambda: StructArray(type_input=EquilibriumTimeSlice),
        metadata={
            "imas_type": "equilibrium_time_slice",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": EquilibriumTimeSlice,
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
