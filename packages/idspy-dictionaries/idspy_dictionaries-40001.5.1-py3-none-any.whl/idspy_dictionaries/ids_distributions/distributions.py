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
class PlasmaCompositionNeutralStateConstant(IdsBaseClass):
    """

    :ivar name : String identifying neutral state
    :ivar electron_configuration : Configuration of atomic orbitals of this state, e.g. 1s2-2s1
    :ivar vibrational_level : Vibrational level (can be bundled)
    :ivar vibrational_mode : Vibrational mode of this state, e.g. &#34;A_g&#34;. Need to define, or adopt a standard nomenclature.
    """

    class Meta:
        name = "plasma_composition_neutral_state_constant"
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


@idspy_dataclass(repr=False, slots=True)
class PlasmaCompositionIonStateConstant(IdsBaseClass):
    """

    :ivar z_min : Minimum Z of the charge state bundle (z_min = z_max = 0 for a neutral)
    :ivar z_max : Maximum Z of the charge state bundle (equal to z_min if no bundle)
    :ivar name : String identifying ion state (e.g. C+, C+2 , C+3, C+4, C+5, C+6, ...)
    :ivar electron_configuration : Configuration of atomic orbitals of this state, e.g. 1s2-2s1
    :ivar vibrational_level : Vibrational level (can be bundled)
    :ivar vibrational_mode : Vibrational mode of this state, e.g. &#34;A_g&#34;. Need to define, or adopt a standard nomenclature.
    """

    class Meta:
        name = "plasma_composition_ion_state_constant"
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
class PlasmaCompositionIonsConstant(IdsBaseClass):
    """

    :ivar element : List of elements forming the atom or molecule
    :ivar z_ion : Ion charge (of the dominant ionization state; lumped ions are allowed)
    :ivar name : String identifying ion (e.g. H+, D+, T+, He+2, C+, ...)
    :ivar state : Quantities related to the different states of the species (ionization, energy, excitation, ...)
    """

    class Meta:
        name = "plasma_composition_ions_constant"
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
    z_ion: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    state: Optional[PlasmaCompositionIonStateConstant] = field(
        default=None,
        metadata={
            "imas_type": "plasma_composition_ion_state_constant",
            "field_type": PlasmaCompositionIonStateConstant,
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
class PlasmaCompositionNeutralConstant(IdsBaseClass):
    """

    :ivar element : List of elements forming the atom or molecule
    :ivar name : String identifying neutral (e.g. H, D, T, He, C, ...)
    :ivar state : State of the species (energy, excitation, ...)
    """

    class Meta:
        name = "plasma_composition_neutral_constant"
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
    state: Optional[PlasmaCompositionNeutralStateConstant] = field(
        default=None,
        metadata={
            "imas_type": "plasma_composition_neutral_state_constant",
            "field_type": PlasmaCompositionNeutralStateConstant,
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
class GenericGridMatrix(IdsBaseClass):
    """

    :ivar grid_index : Index of the grid used to represent this quantity
    :ivar grid_subset_index : Index of the grid subset the data is provided on. Corresponds to the index used in the grid subset definition: grid_subset(:)/identifier/index
    :ivar values : List of matrix components, one list per element in the grid subset. First dimension: element index. Second dimension: first matrix index. Third dimension: second matrix index.
    :ivar coefficients : Interpolation coefficients, to be used for a high precision evaluation of the physical quantity with finite elements, provided per element in the grid subset (first dimension). Second dimension: first matrix index. Third dimension: second matrix index. Fourth dimension: coefficient index
    """

    class Meta:
        name = "generic_grid_matrix"
        is_root_ids = False

    grid_index: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    grid_subset_index: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    values: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate2": "1...N",
                "coordinate3": "1...N",
            },
            "field_type": np.ndarray,
        },
    )
    coefficients: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 4, dtype=float),
        metadata={
            "imas_type": "FLT_4D",
            "ndims": 4,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate2": "1...N",
                "coordinate3": "1...N",
                "coordinate4": "1...N",
            },
            "field_type": np.ndarray,
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
class GenericGridInteger(IdsBaseClass):
    """

    :ivar grid_index : Index of the grid used to represent this quantity
    :ivar grid_subset_index : Index of the grid subset the data is provided on. Corresponds to the index used in the grid subset definition: grid_subset(:)/identifier/index
    :ivar values : One integer value is provided per element in the grid subset.
    """

    class Meta:
        name = "generic_grid_integer"
        is_root_ids = False

    grid_index: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    grid_subset_index: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    values: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=int),
        metadata={
            "imas_type": "INT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
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
class DistributionsDGgd(IdsBaseClass):
    """

    :ivar grid : Grid description
    :ivar temperature : Reference temperature profile used to define the local thermal energy and the thermal velocity (for normalization of the grid coordinates)
    :ivar orbit_frequency_pol : Poloidal orbit frequency (transit or bounce) at the grid location (in phase space)
    :ivar orbit_frequency_tor : Toroidal orbit frequency (transit or precession) at the grid location (in phase space)
    :ivar expansion : Distribution function expanded into a vector of successive approximations. The first element in the vector (expansion(1)) is the zeroth order distribution function, while the K:th element in the vector (expansion(K)) is the K:th correction, such that the total distribution function is a sum over all elements in the expansion vector.
    :ivar expansion_fd3v : Distribution function multiplied by the volume of the local velocity cell d3v, expanded into a vector of successive approximations. The first element in the vector (expansion(1)) is the zeroth order distribution function, while the K:th element in the vector (expansion(K)) is the K:th correction, such that the total distribution function is a sum over all elements in the expansion vector.
    :ivar amplitude : Value of the distribution function at the grid position in phase space. The interpolation coefficients refer to a C-2 spline.
    :ivar orbit : Orbit description of the particle at this position in phase space. First dimension is the element index. Second dimension is the time along the orbit. Third dimension contains the particle phase space coordinates.
    :ivar orbit_type : Orbit type identifier
    :ivar time : Time
    """

    class Meta:
        name = "distributions_d_ggd"
        is_root_ids = False

    grid: Optional[GenericGridDynamic] = field(
        default=None,
        metadata={
            "imas_type": "generic_grid_dynamic",
            "field_type": GenericGridDynamic,
        },
    )
    temperature: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {
                "coordinate1": "../../profiles_1d(itime)/grid/rho_tor_norm"
            },
            "field_type": np.ndarray,
        },
    )
    orbit_frequency_pol: Optional[GenericGridScalar] = field(
        default=None,
        metadata={
            "imas_type": "generic_grid_scalar",
            "field_type": GenericGridScalar,
        },
    )
    orbit_frequency_tor: Optional[GenericGridScalar] = field(
        default=None,
        metadata={
            "imas_type": "generic_grid_scalar",
            "field_type": GenericGridScalar,
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
    amplitude: Optional[GenericGridScalar] = field(
        default=None,
        metadata={
            "imas_type": "generic_grid_scalar",
            "field_type": GenericGridScalar,
        },
    )
    orbit: Optional[GenericGridMatrix] = field(
        default=None,
        metadata={
            "imas_type": "generic_grid_matrix",
            "field_type": GenericGridMatrix,
        },
    )
    orbit_type: Optional[GenericGridInteger] = field(
        default=None,
        metadata={
            "imas_type": "generic_grid_integer",
            "field_type": GenericGridInteger,
        },
    )
    time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class DistributionProcessIdentifier(IdsBaseClass):
    """

    :ivar nbi_unit : Index of the NBI unit considered. Refers to the &#34;unit&#34; array of the NBI IDS. 0 means sum over all NBI units.
    :ivar nbi_beamlets_group : Index of the NBI beamlets group considered. Refers to the &#34;unit/beamlets_group&#34; array of the NBI IDS. 0 means sum over all beamlets groups.
    """

    class Meta:
        name = "distribution_process_identifier"
        is_root_ids = False

    nbi_unit: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    nbi_beamlets_group: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
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
class DistributionSpecies(IdsBaseClass):
    """

    :ivar ion : Description of the ion or neutral species, used if type/index = 2 or 3
    :ivar neutral : Description of the neutral species, used if type/index = 4 or 5
    """

    class Meta:
        name = "distribution_species"
        is_root_ids = False

    ion: Optional[PlasmaCompositionIonsConstant] = field(
        default=None,
        metadata={
            "imas_type": "plasma_composition_ions_constant",
            "field_type": PlasmaCompositionIonsConstant,
        },
    )
    neutral: Optional[PlasmaCompositionNeutralConstant] = field(
        default=None,
        metadata={
            "imas_type": "plasma_composition_neutral_constant",
            "field_type": PlasmaCompositionNeutralConstant,
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
class DistributionsDSourceIdentifier(IdsBaseClass):
    """

    :ivar type : Type of the source term. Index  = 1 for a wave, index = 2 for a particle source process
    :ivar wave_index : Index into distribution/wave
    :ivar process_index : Index into distribution/process
    """

    class Meta:
        name = "distributions_d_source_identifier"
        is_root_ids = False

    type: Optional[IdentifierDynamicAos3] = field(
        default=None,
        metadata={
            "imas_type": "identifier_dynamic_aos3",
            "field_type": IdentifierDynamicAos3,
        },
    )
    wave_index: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    process_index: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )


@idspy_dataclass(repr=False, slots=True)
class DistributionsDGlobalQuantitiesThermalized(IdsBaseClass):
    """

    :ivar particles : Source rate of thermal particles due to the thermalization of fast particles
    :ivar power : Power input to the thermal particle population due to the thermalization of fast particles
    :ivar torque : Torque input to the thermal particle population due to the thermalization of fast particles
    """

    class Meta:
        name = "distributions_d_global_quantities_thermalized"
        is_root_ids = False

    particles: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    power: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    torque: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class DistributionsDGlobalQuantitiesSource(IdsBaseClass):
    """

    :ivar identifier : Identifier of the wave or particle source process, defined respectively in distribution/wave or distribution/process
    :ivar particles : Particle source rate
    :ivar power : Total power of the source
    :ivar torque_phi : Total toroidal torque of the source
    """

    class Meta:
        name = "distributions_d_global_quantities_source"
        is_root_ids = False

    identifier: Optional[DistributionsDSourceIdentifier] = field(
        default=None,
        metadata={
            "imas_type": "distributions_d_source_identifier",
            "field_type": DistributionsDSourceIdentifier,
        },
    )
    particles: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    power: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    torque_phi: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class DistributionsDGlobalQuantitiesCollisionsIonState(IdsBaseClass):
    """

    :ivar z_min : Minimum Z of the charge state bundle (z_min = z_max = 0 for a neutral)
    :ivar z_max : Maximum Z of the charge state bundle (equal to z_min if no bundle)
    :ivar name : String identifying charge state (e.g. C+, C+2 , C+3, C+4, C+5, C+6, ...)
    :ivar electron_configuration : Configuration of atomic orbitals of this state, e.g. 1s2-2s1
    :ivar vibrational_level : Vibrational level (can be bundled)
    :ivar vibrational_mode : Vibrational mode of this state, e.g. &#34;A_g&#34;. Need to define, or adopt a standard nomenclature.
    :ivar power_thermal : Collisional power to the thermal particle population
    :ivar power_fast : Collisional power to the fast particle population
    :ivar torque_thermal_phi : Collisional toroidal torque to the thermal particle population
    :ivar torque_fast_phi : Collisional toroidal torque to the fast particle population
    """

    class Meta:
        name = "distributions_d_global_quantities_collisions_ion_state"
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
    power_fast: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    torque_thermal_phi: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    torque_fast_phi: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class DistributionsDGlobalQuantitiesCollisionsIon(IdsBaseClass):
    """

    :ivar element : List of elements forming the atom or molecule
    :ivar z_ion : Ion charge (of the dominant ionization state; lumped ions are allowed).
    :ivar name : String identifying the species (e.g. H+, D+, T+, He+2, C+, D2, DT, CD4, ...)
    :ivar neutral_index : Index of the corresponding neutral species in the ../../neutral array
    :ivar power_thermal : Collisional power to the thermal particle population
    :ivar power_fast : Collisional power to the fast particle population
    :ivar torque_thermal_phi : Collisional toroidal torque to the thermal particle population
    :ivar torque_fast_phi : Collisional toroidal torque to the fast particle population
    :ivar multiple_states_flag : Multiple state calculation flag : 0-Only one state is considered; 1-Multiple states are considered and are described in the state structure
    :ivar state : Collisional exchange with the various states of the ion species (ionization, energy, excitation, ...)
    """

    class Meta:
        name = "distributions_d_global_quantities_collisions_ion"
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
    power_thermal: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    power_fast: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    torque_thermal_phi: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    torque_fast_phi: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    multiple_states_flag: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    state: Optional[DistributionsDGlobalQuantitiesCollisionsIonState] = field(
        default_factory=lambda: StructArray(
            type_input=DistributionsDGlobalQuantitiesCollisionsIonState
        ),
        metadata={
            "imas_type": "distributions_d_global_quantities_collisions_ion_state",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": DistributionsDGlobalQuantitiesCollisionsIonState,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class DistributionsDGlobalQuantitiesCollisionsElectrons(IdsBaseClass):
    """

    :ivar power_thermal : Collisional power to the thermal particle population
    :ivar power_fast : Collisional power to the fast particle population
    :ivar torque_thermal_phi : Collisional toroidal torque to the thermal particle population
    :ivar torque_fast_phi : Collisional toroidal torque to the fast particle population
    """

    class Meta:
        name = "distributions_d_global_quantities_collisions_electrons"
        is_root_ids = False

    power_thermal: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    power_fast: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    torque_thermal_phi: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    torque_fast_phi: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class DistributionsDGlobalQuantitiesCollisions(IdsBaseClass):
    """

    :ivar electrons : Collisional exchange with electrons
    :ivar ion : Collisional exchange with the various ion species
    """

    class Meta:
        name = "distributions_d_global_quantities_collisions"
        is_root_ids = False

    electrons: Optional[DistributionsDGlobalQuantitiesCollisionsElectrons] = (
        field(
            default=None,
            metadata={
                "imas_type": "distributions_d_global_quantities_collisions_electrons",
                "field_type": DistributionsDGlobalQuantitiesCollisionsElectrons,
            },
        )
    )
    ion: Optional[DistributionsDGlobalQuantitiesCollisionsIon] = field(
        default_factory=lambda: StructArray(
            type_input=DistributionsDGlobalQuantitiesCollisionsIon
        ),
        metadata={
            "imas_type": "distributions_d_global_quantities_collisions_ion",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": DistributionsDGlobalQuantitiesCollisionsIon,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class DistributionsDGlobalQuantities(IdsBaseClass):
    """

    :ivar particles_n : Number of particles in the distribution, i.e. the volume integral of the density (note: this is the number of real particles and not markers)
    :ivar particles_fast_n : Number of fast particles in the distribution, i.e. the volume integral of the density (note: this is the number of real particles and not markers)
    :ivar energy : Total energy in the distribution
    :ivar energy_fast : Total energy of the fast particles in the distribution
    :ivar energy_fast_parallel : Parallel energy of the fast particles in the distribution
    :ivar torque_tor_j_radial : Toroidal torque due to radial currents
    :ivar current_phi : Toroidal current driven by the distribution
    :ivar power_first_orbit : Power loss due to first orbit losses
    :ivar power_rotation : Power going to plasma rotation. This power goes into sustaining the plasma rotation rather than heating the plasma. This is given because the injection energy in the rotating plasma frame is (assuming rotation in the same direction of the NB injection) lower than in the lab-frame.
    :ivar power_charge_exchange : Power loss due to Charge Exchange loss of fast ions
    :ivar collisions : Power and torque exchanged between the species described by the distribution and the different plasma species through collisions
    :ivar thermalization : Volume integrated source of thermal particles, momentum and energy due to thermalization. Here thermalization refers to non-thermal particles, sufficiently assimilated to the thermal background to be re-categorized as thermal particles. Note that this source may also be negative if thermal particles are being accelerated such that they form a distinct non-thermal contribution, e.g. due run-away of RF interactions.
    :ivar source : Set of volume integrated sources and sinks of particles, momentum and energy included in the Fokker-Planck modelling, related to the various waves or particle source processes affecting the distribution
    :ivar time : Time
    """

    class Meta:
        name = "distributions_d_global_quantities"
        is_root_ids = False

    particles_n: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    particles_fast_n: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    energy: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    energy_fast: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    energy_fast_parallel: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    torque_tor_j_radial: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    current_phi: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    power_first_orbit: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    power_rotation: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    power_charge_exchange: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    collisions: Optional[DistributionsDGlobalQuantitiesCollisions] = field(
        default=None,
        metadata={
            "imas_type": "distributions_d_global_quantities_collisions",
            "field_type": DistributionsDGlobalQuantitiesCollisions,
        },
    )
    thermalization: Optional[DistributionsDGlobalQuantitiesThermalized] = field(
        default=None,
        metadata={
            "imas_type": "distributions_d_global_quantities_thermalized",
            "field_type": DistributionsDGlobalQuantitiesThermalized,
        },
    )
    source: Optional[DistributionsDGlobalQuantitiesSource] = field(
        default_factory=lambda: StructArray(
            type_input=DistributionsDGlobalQuantitiesSource
        ),
        metadata={
            "imas_type": "distributions_d_global_quantities_source",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": DistributionsDGlobalQuantitiesSource,
        },
    )
    time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class DistributionsDProfiles1DThermalized(IdsBaseClass):
    """

    :ivar particles : Source rate of thermal particle density due to the thermalization of fast particles
    :ivar energy : Source rate of energy density within the thermal particle population due to the thermalization of fast particles
    :ivar momentum_phi : Source rate of toroidal angular momentum density within the thermal particle population due to the thermalisation of fast particles
    """

    class Meta:
        name = "distributions_d_profiles_1d_thermalized"
        is_root_ids = False

    particles: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    energy: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    momentum_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class DistributionsDProfiles1DSource(IdsBaseClass):
    """

    :ivar identifier : Identifier of the wave or particle source process, defined respectively in distribution/wave or distribution/process
    :ivar particles : Source rate of thermal particle density
    :ivar energy : Source rate of energy density
    :ivar momentum_phi : Source rate of toroidal angular momentum density
    """

    class Meta:
        name = "distributions_d_profiles_1d_source"
        is_root_ids = False

    identifier: Optional[DistributionsDSourceIdentifier] = field(
        default=None,
        metadata={
            "imas_type": "distributions_d_source_identifier",
            "field_type": DistributionsDSourceIdentifier,
        },
    )
    particles: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    energy: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    momentum_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class DistributionsDProfiles1DPartialSource(IdsBaseClass):
    """

    :ivar identifier : Identifier of the wave or particle source process, defined respectively in distribution/wave or distribution/process
    :ivar particles : Source rate of thermal particle density
    :ivar energy : Source rate of energy density
    :ivar momentum_phi : Source rate of toroidal angular momentum density
    """

    class Meta:
        name = "distributions_d_profiles_1d_partial_source"
        is_root_ids = False

    identifier: Optional[DistributionsDSourceIdentifier] = field(
        default=None,
        metadata={
            "imas_type": "distributions_d_source_identifier",
            "field_type": DistributionsDSourceIdentifier,
        },
    )
    particles: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    energy: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    momentum_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class DistributionsDProfiles2DCollisionsIon(IdsBaseClass):
    """

    :ivar element : List of elements forming the atom or molecule
    :ivar z_ion : Ion charge (of the dominant ionization state; lumped ions are allowed).
    :ivar name : String identifying the species (e.g. H+, D+, T+, He+2, C+, D2, DT, CD4, ...)
    :ivar neutral_index : Index of the corresponding neutral species in the ../../neutral array
    :ivar power_thermal : Collisional power density to the thermal particle population
    :ivar power_fast : Collisional power density to the fast particle population
    :ivar torque_thermal_phi : Collisional toroidal torque density to the thermal particle population
    :ivar torque_fast_phi : Collisional toroidal torque density to the fast particle population
    :ivar multiple_states_flag : Multiple state calculation flag : 0-Only one state is considered; 1-Multiple states are considered and are described in the state structure
    :ivar state : Collisional exchange with the various states of the ion species (ionization, energy, excitation, ...)
    """

    class Meta:
        name = "distributions_d_profiles_2d_collisions_ion"
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
    power_thermal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../../grid/r OR ../../../grid/rho_tor_norm",
                "coordinate2": "../../../grid/z OR ../../../grid/theta_geometric OR ../../../grid/theta_straight",
            },
            "field_type": np.ndarray,
        },
    )
    power_fast: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../../grid/r OR ../../../grid/rho_tor_norm",
                "coordinate2": "../../../grid/z OR ../../../grid/theta_geometric OR ../../../grid/theta_straight",
            },
            "field_type": np.ndarray,
        },
    )
    torque_thermal_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../../grid/r OR ../../../grid/rho_tor_norm",
                "coordinate2": "../../../grid/z OR ../../../grid/theta_geometric OR ../../../grid/theta_straight",
            },
            "field_type": np.ndarray,
        },
    )
    torque_fast_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../../grid/r OR ../../../grid/rho_tor_norm",
                "coordinate2": "../../../grid/z OR ../../../grid/theta_geometric OR ../../../grid/theta_straight",
            },
            "field_type": np.ndarray,
        },
    )
    multiple_states_flag: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    state: Optional[DistributionsDProfiles2DCollisionsIonState] = field(
        default_factory=lambda: StructArray(
            type_input=DistributionsDProfiles2DCollisionsIonState
        ),
        metadata={
            "imas_type": "distributions_d_profiles_2d_collisions_ion_state",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": DistributionsDProfiles2DCollisionsIonState,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class DistributionsDProfiles2DPartialCollisionsIon(IdsBaseClass):
    """

    :ivar element : List of elements forming the atom or molecule
    :ivar z_ion : Ion charge (of the dominant ionization state; lumped ions are allowed).
    :ivar name : String identifying the species (e.g. H+, D+, T+, He+2, C+, D2, DT, CD4, ...)
    :ivar neutral_index : Index of the corresponding neutral species in the ../../neutral array
    :ivar power_thermal : Collisional power density to the thermal particle population
    :ivar power_fast : Collisional power density to the fast particle population
    :ivar torque_thermal_phi : Collisional toroidal torque density to the thermal particle population
    :ivar torque_fast_phi : Collisional toroidal torque density to the fast particle population
    :ivar multiple_states_flag : Multiple state calculation flag : 0-Only one state is considered; 1-Multiple states are considered and are described in the state structure
    :ivar state : Collisional exchange with the various states of the ion species (ionization, energy, excitation, ...)
    """

    class Meta:
        name = "distributions_d_profiles_2d_partial_collisions_ion"
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
    power_thermal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../../../grid/r OR ../../../../grid/rho_tor_norm",
                "coordinate2": "../../../../grid/z OR ../../../../grid/theta_geometric OR ../../../../grid/theta_straight",
            },
            "field_type": np.ndarray,
        },
    )
    power_fast: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../../../grid/r OR ../../../../grid/rho_tor_norm",
                "coordinate2": "../../../../grid/z OR ../../../../grid/theta_geometric OR ../../../../grid/theta_straight",
            },
            "field_type": np.ndarray,
        },
    )
    torque_thermal_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../../../grid/r OR ../../../../grid/rho_tor_norm",
                "coordinate2": "../../../../grid/z OR ../../../../grid/theta_geometric OR ../../../../grid/theta_straight",
            },
            "field_type": np.ndarray,
        },
    )
    torque_fast_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../../../grid/r OR ../../../../grid/rho_tor_norm",
                "coordinate2": "../../../../grid/z OR ../../../../grid/theta_geometric OR ../../../../grid/theta_straight",
            },
            "field_type": np.ndarray,
        },
    )
    multiple_states_flag: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    state: Optional[DistributionsDProfiles2DPartialCollisionsIonState] = field(
        default_factory=lambda: StructArray(
            type_input=DistributionsDProfiles2DPartialCollisionsIonState
        ),
        metadata={
            "imas_type": "distributions_d_profiles_2d_partial_collisions_ion_state",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": DistributionsDProfiles2DPartialCollisionsIonState,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class DistributionsDProfiles2DCollisionsIonState(IdsBaseClass):
    """

    :ivar z_min : Minimum Z of the charge state bundle (z_min = z_max = 0 for a neutral)
    :ivar z_max : Maximum Z of the charge state bundle (equal to z_min if no bundle)
    :ivar name : String identifying charge state (e.g. C+, C+2 , C+3, C+4, C+5, C+6, ...)
    :ivar electron_configuration : Configuration of atomic orbitals of this state, e.g. 1s2-2s1
    :ivar vibrational_level : Vibrational level (can be bundled)
    :ivar vibrational_mode : Vibrational mode of this state, e.g. &#34;A_g&#34;. Need to define, or adopt a standard nomenclature.
    :ivar power_thermal : Collisional power density to the thermal particle population
    :ivar power_fast : Collisional power density to the fast particle population
    :ivar torque_thermal_phi : Collisional toroidal torque density to the thermal particle population
    :ivar torque_fast_phi : Collisional toroidal torque density to the fast particle population
    """

    class Meta:
        name = "distributions_d_profiles_2d_collisions_ion_state"
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
    power_thermal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../../../grid/r OR ../../../../grid/rho_tor_norm",
                "coordinate2": "../../../../grid/z OR ../../../../grid/theta_geometric OR ../../../../grid/theta_straight",
            },
            "field_type": np.ndarray,
        },
    )
    power_fast: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../../../grid/r OR ../../../../grid/rho_tor_norm",
                "coordinate2": "../../../../grid/z OR ../../../../grid/theta_geometric OR ../../../../grid/theta_straight",
            },
            "field_type": np.ndarray,
        },
    )
    torque_thermal_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../../../grid/r OR ../../../../grid/rho_tor_norm",
                "coordinate2": "../../../../grid/z OR ../../../../grid/theta_geometric OR ../../../../grid/theta_straight",
            },
            "field_type": np.ndarray,
        },
    )
    torque_fast_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../../../grid/r OR ../../../../grid/rho_tor_norm",
                "coordinate2": "../../../../grid/z OR ../../../../grid/theta_geometric OR ../../../../grid/theta_straight",
            },
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class DistributionsDProfiles2DPartialCollisionsIonState(IdsBaseClass):
    """

    :ivar z_min : Minimum Z of the charge state bundle (z_min = z_max = 0 for a neutral)
    :ivar z_max : Maximum Z of the charge state bundle (equal to z_min if no bundle)
    :ivar name : String identifying charge state (e.g. C+, C+2 , C+3, C+4, C+5, C+6, ...)
    :ivar electron_configuration : Configuration of atomic orbitals of this state, e.g. 1s2-2s1
    :ivar vibrational_level : Vibrational level (can be bundled)
    :ivar vibrational_mode : Vibrational mode of this state, e.g. &#34;A_g&#34;. Need to define, or adopt a standard nomenclature.
    :ivar power_thermal : Collisional power density to the thermal particle population
    :ivar power_fast : Collisional power density to the fast particle population
    :ivar torque_thermal_phi : Collisional toroidal torque density to the thermal particle population
    :ivar torque_fast_tor : Collisional toroidal torque density to the fast particle population
    :ivar torque_fast_phi : Collisional toroidal torque density to the fast particle population
    """

    class Meta:
        name = "distributions_d_profiles_2d_partial_collisions_ion_state"
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
    power_thermal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../../../../grid/r OR ../../../../../grid/rho_tor_norm",
                "coordinate2": "../../../../../grid/z OR ../../../../../grid/theta_geometric OR ../../../../../grid/theta_straight",
            },
            "field_type": np.ndarray,
        },
    )
    power_fast: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../../../../grid/r OR ../../../../../grid/rho_tor_norm",
                "coordinate2": "../../../../../grid/z OR ../../../../../grid/theta_geometric OR ../../../../../grid/theta_straight",
            },
            "field_type": np.ndarray,
        },
    )
    torque_thermal_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../../../../grid/r OR ../../../../../grid/rho_tor_norm",
                "coordinate2": "../../../../../grid/z OR ../../../../../grid/theta_geometric OR ../../../../../grid/theta_straight",
            },
            "field_type": np.ndarray,
        },
    )
    torque_fast_tor: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../../../../grid/r OR ../../../../../grid/rho_tor_norm",
                "coordinate2": "../../../../../grid/z OR ../../../../../grid/theta_geometric OR ../../../../../grid/theta_straight",
            },
            "field_type": np.ndarray,
        },
    )
    torque_fast_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../../../../grid/r OR ../../../../../grid/rho_tor_norm",
                "coordinate2": "../../../../../grid/z OR ../../../../../grid/theta_geometric OR ../../../../../grid/theta_straight",
            },
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class DistributionsDProfiles2DCollisionsElectrons(IdsBaseClass):
    """

    :ivar power_thermal : Collisional power density to the thermal particle population
    :ivar power_fast : Collisional power density to the fast particle population
    :ivar torque_thermal_phi : Collisional toroidal torque density to the thermal particle population
    :ivar torque_fast_phi : Collisional toroidal torque density to the fast particle population
    """

    class Meta:
        name = "distributions_d_profiles_2d_collisions_electrons"
        is_root_ids = False

    power_thermal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../../grid/r OR ../../../grid/rho_tor_norm",
                "coordinate2": "../../../grid/z OR ../../../grid/theta_geometric OR ../../../grid/theta_straight",
            },
            "field_type": np.ndarray,
        },
    )
    power_fast: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../../grid/r OR ../../../grid/rho_tor_norm",
                "coordinate2": "../../../grid/z OR ../../../grid/theta_geometric OR ../../../grid/theta_straight",
            },
            "field_type": np.ndarray,
        },
    )
    torque_thermal_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../../grid/r OR ../../../grid/rho_tor_norm",
                "coordinate2": "../../../grid/z OR ../../../grid/theta_geometric OR ../../../grid/theta_straight",
            },
            "field_type": np.ndarray,
        },
    )
    torque_fast_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../../grid/r OR ../../../grid/rho_tor_norm",
                "coordinate2": "../../../grid/z OR ../../../grid/theta_geometric OR ../../../grid/theta_straight",
            },
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class DistributionsDProfiles2DPartialCollisionsElectrons(IdsBaseClass):
    """

    :ivar power_thermal : Collisional power density to the thermal particle population
    :ivar power_fast : Collisional power density to the fast particle population
    :ivar torque_thermal_phi : Collisional toroidal torque density to the thermal particle population
    :ivar torque_fast_phi : Collisional toroidal torque density to the fast particle population
    """

    class Meta:
        name = "distributions_d_profiles_2d_partial_collisions_electrons"
        is_root_ids = False

    power_thermal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../../../grid/r OR ../../../../grid/rho_tor_norm",
                "coordinate2": "../../../../grid/z OR ../../../../grid/theta_geometric OR ../../../../grid/theta_straight",
            },
            "field_type": np.ndarray,
        },
    )
    power_fast: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../../../grid/r OR ../../../../grid/rho_tor_norm",
                "coordinate2": "../../../../grid/z OR ../../../../grid/theta_geometric OR ../../../../grid/theta_straight",
            },
            "field_type": np.ndarray,
        },
    )
    torque_thermal_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../../../grid/r OR ../../../../grid/rho_tor_norm",
                "coordinate2": "../../../../grid/z OR ../../../../grid/theta_geometric OR ../../../../grid/theta_straight",
            },
            "field_type": np.ndarray,
        },
    )
    torque_fast_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../../../grid/r OR ../../../../grid/rho_tor_norm",
                "coordinate2": "../../../../grid/z OR ../../../../grid/theta_geometric OR ../../../../grid/theta_straight",
            },
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class DistributionsDProfiles2DCollisions(IdsBaseClass):
    """

    :ivar electrons : Collisional exchange with electrons
    :ivar ion : Collisional exchange with the various ion species
    """

    class Meta:
        name = "distributions_d_profiles_2d_collisions"
        is_root_ids = False

    electrons: Optional[DistributionsDProfiles2DCollisionsElectrons] = field(
        default=None,
        metadata={
            "imas_type": "distributions_d_profiles_2d_collisions_electrons",
            "field_type": DistributionsDProfiles2DCollisionsElectrons,
        },
    )
    ion: Optional[DistributionsDProfiles2DCollisionsIon] = field(
        default_factory=lambda: StructArray(
            type_input=DistributionsDProfiles2DCollisionsIon
        ),
        metadata={
            "imas_type": "distributions_d_profiles_2d_collisions_ion",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": DistributionsDProfiles2DCollisionsIon,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class DistributionsDProfiles2DPartialCollisions(IdsBaseClass):
    """

    :ivar electrons : Collisional exchange with electrons
    :ivar ion : Collisional exchange with the various ion species
    """

    class Meta:
        name = "distributions_d_profiles_2d_partial_collisions"
        is_root_ids = False

    electrons: Optional[DistributionsDProfiles2DPartialCollisionsElectrons] = (
        field(
            default=None,
            metadata={
                "imas_type": "distributions_d_profiles_2d_partial_collisions_electrons",
                "field_type": DistributionsDProfiles2DPartialCollisionsElectrons,
            },
        )
    )
    ion: Optional[DistributionsDProfiles2DPartialCollisionsIon] = field(
        default_factory=lambda: StructArray(
            type_input=DistributionsDProfiles2DPartialCollisionsIon
        ),
        metadata={
            "imas_type": "distributions_d_profiles_2d_partial_collisions_ion",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": DistributionsDProfiles2DPartialCollisionsIon,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class DistributionsDProfiles2DPartial(IdsBaseClass):
    """

    :ivar density : Density (thermal+non-thermal)
    :ivar density_fast : Density of fast particles
    :ivar pressure : Pressure (thermal+non-thermal)
    :ivar pressure_fast : Pressure of fast particles
    :ivar pressure_fast_parallel : Pressure of fast particles in the parallel direction
    :ivar current_phi : Total toroidal driven current density (including electron and thermal ion back-current, or drag-current)
    :ivar current_fast_phi : Total toroidal driven current density of fast (non-thermal) particles (excluding electron and thermal ion back-current, or drag-current)
    :ivar torque_phi_j_radial : Toroidal torque due to radial currents
    :ivar collisions : Power and torque exchanged between the species described by the distribution and the different plasma species through collisions
    """

    class Meta:
        name = "distributions_d_profiles_2d_partial"
        is_root_ids = False

    density: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../grid/r OR ../../grid/rho_tor_norm",
                "coordinate2": "../../grid/z OR ../../grid/theta_geometric OR ../../grid/theta_straight",
            },
            "field_type": np.ndarray,
        },
    )
    density_fast: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../grid/r OR ../../grid/rho_tor_norm",
                "coordinate2": "../../grid/z OR ../../grid/theta_geometric OR ../../grid/theta_straight",
            },
            "field_type": np.ndarray,
        },
    )
    pressure: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../grid/r OR ../../grid/rho_tor_norm",
                "coordinate2": "../../grid/z OR ../../grid/theta_geometric OR ../../grid/theta_straight",
            },
            "field_type": np.ndarray,
        },
    )
    pressure_fast: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../grid/r OR ../../grid/rho_tor_norm",
                "coordinate2": "../../grid/z OR ../../grid/theta_geometric OR ../../grid/theta_straight",
            },
            "field_type": np.ndarray,
        },
    )
    pressure_fast_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../grid/r OR ../../grid/rho_tor_norm",
                "coordinate2": "../../grid/z OR ../../grid/theta_geometric OR ../../grid/theta_straight",
            },
            "field_type": np.ndarray,
        },
    )
    current_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../grid/r OR ../../grid/rho_tor_norm",
                "coordinate2": "../../grid/z OR ../../grid/theta_geometric OR ../../grid/theta_straight",
            },
            "field_type": np.ndarray,
        },
    )
    current_fast_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../grid/r OR ../../grid/rho_tor_norm",
                "coordinate2": "../../grid/z OR ../../grid/theta_geometric OR ../../grid/theta_straight",
            },
            "field_type": np.ndarray,
        },
    )
    torque_phi_j_radial: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../grid/r OR ../../grid/rho_tor_norm",
                "coordinate2": "../../grid/z OR ../../grid/theta_geometric OR ../../grid/theta_straight",
            },
            "field_type": np.ndarray,
        },
    )
    collisions: Optional[DistributionsDProfiles2DPartialCollisions] = field(
        default=None,
        metadata={
            "imas_type": "distributions_d_profiles_2d_partial_collisions",
            "field_type": DistributionsDProfiles2DPartialCollisions,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class DistributionsDProfiles1DCollisionsIon(IdsBaseClass):
    """

    :ivar element : List of elements forming the atom or molecule
    :ivar z_ion : Ion charge (of the dominant ionization state; lumped ions are allowed).
    :ivar name : String identifying the species (e.g. H+, D+, T+, He+2, C+, D2, DT, CD4, ...)
    :ivar neutral_index : Index of the corresponding neutral species in the ../../neutral array
    :ivar power_thermal : Collisional power density to the thermal particle population
    :ivar power_fast : Collisional power density to the fast particle population
    :ivar torque_thermal_phi : Collisional toroidal torque density to the thermal particle population
    :ivar torque_fast_phi : Collisional toroidal torque density to the fast particle population
    :ivar multiple_states_flag : Multiple state calculation flag : 0-Only one state is considered; 1-Multiple states are considered and are described in the state structure
    :ivar state : Collisional exchange with the various states of the ion species (ionization, energy, excitation, ...)
    """

    class Meta:
        name = "distributions_d_profiles_1d_collisions_ion"
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
    power_thermal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    power_fast: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    torque_thermal_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    torque_fast_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    multiple_states_flag: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    state: Optional[DistributionsDProfiles1DCollisionsIonState] = field(
        default_factory=lambda: StructArray(
            type_input=DistributionsDProfiles1DCollisionsIonState
        ),
        metadata={
            "imas_type": "distributions_d_profiles_1d_collisions_ion_state",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": DistributionsDProfiles1DCollisionsIonState,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class DistributionsDProfiles1DPartialCollisionsIon(IdsBaseClass):
    """

    :ivar element : List of elements forming the atom or molecule
    :ivar z_ion : Ion charge (of the dominant ionization state; lumped ions are allowed).
    :ivar name : String identifying the species (e.g. H+, D+, T+, He+2, C+, D2, DT, CD4, ...)
    :ivar neutral_index : Index of the corresponding neutral species in the ../../neutral array
    :ivar power_thermal : Collisional power density to the thermal particle population
    :ivar power_fast : Collisional power density to the fast particle population
    :ivar torque_thermal_phi : Collisional toroidal torque density to the thermal particle population
    :ivar torque_fast_phi : Collisional toroidal torque density to the fast particle population
    :ivar multiple_states_flag : Multiple state calculation flag : 0-Only one state is considered; 1-Multiple states are considered and are described in the state structure
    :ivar state : Collisional exchange with the various states of the ion species (ionization, energy, excitation, ...)
    """

    class Meta:
        name = "distributions_d_profiles_1d_partial_collisions_ion"
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
    power_thermal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    power_fast: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    torque_thermal_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    torque_fast_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    multiple_states_flag: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    state: Optional[DistributionsDProfiles1DPartialCollisionsIonState] = field(
        default_factory=lambda: StructArray(
            type_input=DistributionsDProfiles1DPartialCollisionsIonState
        ),
        metadata={
            "imas_type": "distributions_d_profiles_1d_partial_collisions_ion_state",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": DistributionsDProfiles1DPartialCollisionsIonState,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class DistributionsDProfiles1DCollisionsIonState(IdsBaseClass):
    """

    :ivar z_min : Minimum Z of the charge state bundle (z_min = z_max = 0 for a neutral)
    :ivar z_max : Maximum Z of the charge state bundle (equal to z_min if no bundle)
    :ivar name : String identifying charge state (e.g. C+, C+2 , C+3, C+4, C+5, C+6, ...)
    :ivar electron_configuration : Configuration of atomic orbitals of this state, e.g. 1s2-2s1
    :ivar vibrational_level : Vibrational level (can be bundled)
    :ivar vibrational_mode : Vibrational mode of this state, e.g. &#34;A_g&#34;. Need to define, or adopt a standard nomenclature.
    :ivar power_thermal : Collisional power density to the thermal particle population
    :ivar power_fast : Collisional power density to the fast particle population
    :ivar torque_thermal_phi : Collisional toroidal torque density to the thermal particle population
    :ivar torque_fast_phi : Collisional toroidal torque density to the fast particle population
    """

    class Meta:
        name = "distributions_d_profiles_1d_collisions_ion_state"
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
    power_thermal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    power_fast: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    torque_thermal_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    torque_fast_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class DistributionsDProfiles1DPartialCollisionsIonState(IdsBaseClass):
    """

    :ivar z_min : Minimum Z of the charge state bundle (z_min = z_max = 0 for a neutral)
    :ivar z_max : Maximum Z of the charge state bundle (equal to z_min if no bundle)
    :ivar name : String identifying charge state (e.g. C+, C+2 , C+3, C+4, C+5, C+6, ...)
    :ivar electron_configuration : Configuration of atomic orbitals of this state, e.g. 1s2-2s1
    :ivar vibrational_level : Vibrational level (can be bundled)
    :ivar vibrational_mode : Vibrational mode of this state, e.g. &#34;A_g&#34;. Need to define, or adopt a standard nomenclature.
    :ivar power_thermal : Collisional power density to the thermal particle population
    :ivar power_fast : Collisional power density to the fast particle population
    :ivar torque_thermal_phi : Collisional toroidal torque density to the thermal particle population
    :ivar torque_fast_phi : Collisional toroidal torque density to the fast particle population
    """

    class Meta:
        name = "distributions_d_profiles_1d_partial_collisions_ion_state"
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
    power_thermal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    power_fast: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    torque_thermal_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    torque_fast_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class DistributionsDProfiles1DCollisionsElectrons(IdsBaseClass):
    """

    :ivar power_thermal : Collisional power density to the thermal particle population
    :ivar power_fast : Collisional power density to the fast particle population
    :ivar torque_thermal_phi : Collisional toroidal torque density to the thermal particle population
    :ivar torque_fast_phi : Collisional toroidal torque density to the fast particle population
    """

    class Meta:
        name = "distributions_d_profiles_1d_collisions_electrons"
        is_root_ids = False

    power_thermal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    power_fast: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    torque_thermal_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    torque_fast_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class DistributionsDProfiles1DPartialCollisionsElectrons(IdsBaseClass):
    """

    :ivar power_thermal : Collisional power density to the thermal particle population
    :ivar power_fast : Collisional power density to the fast particle population
    :ivar torque_thermal_phi : Collisional toroidal torque density to the thermal particle population
    :ivar torque_fast_phi : Collisional toroidal torque density to the fast particle population
    """

    class Meta:
        name = "distributions_d_profiles_1d_partial_collisions_electrons"
        is_root_ids = False

    power_thermal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    power_fast: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    torque_thermal_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    torque_fast_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class DistributionsDProfiles1DCollisions(IdsBaseClass):
    """

    :ivar electrons : Collisional exchange with electrons
    :ivar ion : Collisional exchange with the various ion species
    """

    class Meta:
        name = "distributions_d_profiles_1d_collisions"
        is_root_ids = False

    electrons: Optional[DistributionsDProfiles1DCollisionsElectrons] = field(
        default=None,
        metadata={
            "imas_type": "distributions_d_profiles_1d_collisions_electrons",
            "field_type": DistributionsDProfiles1DCollisionsElectrons,
        },
    )
    ion: Optional[DistributionsDProfiles1DCollisionsIon] = field(
        default_factory=lambda: StructArray(
            type_input=DistributionsDProfiles1DCollisionsIon
        ),
        metadata={
            "imas_type": "distributions_d_profiles_1d_collisions_ion",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": DistributionsDProfiles1DCollisionsIon,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class DistributionsDProfiles1DPartialCollisions(IdsBaseClass):
    """

    :ivar electrons : Collisional exchange with electrons
    :ivar ion : Collisional exchange with the various ion species
    """

    class Meta:
        name = "distributions_d_profiles_1d_partial_collisions"
        is_root_ids = False

    electrons: Optional[DistributionsDProfiles1DPartialCollisionsElectrons] = (
        field(
            default=None,
            metadata={
                "imas_type": "distributions_d_profiles_1d_partial_collisions_electrons",
                "field_type": DistributionsDProfiles1DPartialCollisionsElectrons,
            },
        )
    )
    ion: Optional[DistributionsDProfiles1DPartialCollisionsIon] = field(
        default_factory=lambda: StructArray(
            type_input=DistributionsDProfiles1DPartialCollisionsIon
        ),
        metadata={
            "imas_type": "distributions_d_profiles_1d_partial_collisions_ion",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": DistributionsDProfiles1DPartialCollisionsIon,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class DistributionsDProfiles1DPartial(IdsBaseClass):
    """

    :ivar density : Density (thermal+non-thermal)
    :ivar density_fast : Density of fast particles
    :ivar pressure : Pressure (thermal+non-thermal)
    :ivar pressure_fast : Pressure of fast particles
    :ivar pressure_fast_parallel : Pressure of fast particles in the parallel direction
    :ivar current_phi : Total toroidal driven current density (including electron and thermal ion back-current, or drag-current)
    :ivar current_fast_phi : Total toroidal driven current density of fast (non-thermal) particles (excluding electron and thermal ion back-current, or drag-current)
    :ivar torque_phi_j_radial : Toroidal torque due to radial currents
    :ivar collisions : Power and torque exchanged between the species described by the distribution and the different plasma species through collisions
    :ivar source : Set of flux averaged sources and sinks of particles, momentum and energy included in the Fokker-Planck modelling, related to the various waves or particle source processes affecting the distribution
    """

    class Meta:
        name = "distributions_d_profiles_1d_partial"
        is_root_ids = False

    density: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    density_fast: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    pressure: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    pressure_fast: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    pressure_fast_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    current_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    current_fast_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    torque_phi_j_radial: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    collisions: Optional[DistributionsDProfiles1DPartialCollisions] = field(
        default=None,
        metadata={
            "imas_type": "distributions_d_profiles_1d_partial_collisions",
            "field_type": DistributionsDProfiles1DPartialCollisions,
        },
    )
    source: Optional[DistributionsDProfiles1DPartialSource] = field(
        default_factory=lambda: StructArray(
            type_input=DistributionsDProfiles1DPartialSource
        ),
        metadata={
            "imas_type": "distributions_d_profiles_1d_partial_source",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": DistributionsDProfiles1DPartialSource,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class DistributionsDFastFilter(IdsBaseClass):
    """

    :ivar method : Method used to separate the fast and thermal particle population (indices TBD)
    :ivar energy : Energy at which the fast and thermal particle populations were separated, as a function of radius
    """

    class Meta:
        name = "distributions_d_fast_filter"
        is_root_ids = False

    method: Optional[IdentifierDynamicAos3] = field(
        default=None,
        metadata={
            "imas_type": "identifier_dynamic_aos3",
            "field_type": IdentifierDynamicAos3,
        },
    )
    energy: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class DistributionsDProfiles1D(IdsBaseClass):
    """

    :ivar grid : Radial grid
    :ivar fast_filter : Description of how the fast and the thermal particle populations are separated
    :ivar density : Density (thermal+non-thermal)
    :ivar density_fast : Density of fast particles
    :ivar pressure : Pressure (thermal+non-thermal)
    :ivar pressure_fast : Pressure of fast particles
    :ivar pressure_fast_parallel : Pressure of fast particles in the parallel direction
    :ivar current_phi : Total toroidal driven current density (including electron and thermal ion back-current, or drag-current)
    :ivar current_fast_phi : Total toroidal driven current density of fast (non-thermal) particles (excluding electron and thermal ion back-current, or drag-current)
    :ivar torque_phi_j_radial : Toroidal torque due to radial currents
    :ivar collisions : Power and torque exchanged between the species described by the distribution and the different plasma species through collisions
    :ivar thermalization : Flux surface averaged source of thermal particles, momentum and energy due to thermalization. Here thermalization refers to non-thermal particles, sufficiently assimilated to the thermal background to be re-categorized as thermal particles. Note that this source may also be negative if thermal particles are being accelerated such that they form a distinct non-thermal contribution, e.g. due run-away of RF interactions.
    :ivar source : Set of flux averaged sources and sinks of particles, momentum and energy included in the Fokker-Planck modelling, related to the various waves or particle source processes affecting the distribution
    :ivar trapped : Flux surface averaged profile evaluated using the trapped particle part of the distribution.
    :ivar co_passing : Flux surface averaged profile evaluated using the co-passing particle part of the distribution.
    :ivar counter_passing : Flux surface averaged profile evaluated using the counter-passing particle part of the distribution.
    :ivar time : Time
    """

    class Meta:
        name = "distributions_d_profiles_1d"
        is_root_ids = False

    grid: Optional[CoreRadialGrid] = field(
        default=None,
        metadata={
            "imas_type": "core_radial_grid",
            "field_type": CoreRadialGrid,
        },
    )
    fast_filter: Optional[DistributionsDFastFilter] = field(
        default=None,
        metadata={
            "imas_type": "distributions_d_fast_filter",
            "field_type": DistributionsDFastFilter,
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
    density_fast: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    pressure: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    pressure_fast: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    pressure_fast_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    current_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    current_fast_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    torque_phi_j_radial: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    collisions: Optional[DistributionsDProfiles1DCollisions] = field(
        default=None,
        metadata={
            "imas_type": "distributions_d_profiles_1d_collisions",
            "field_type": DistributionsDProfiles1DCollisions,
        },
    )
    thermalization: Optional[DistributionsDProfiles1DThermalized] = field(
        default=None,
        metadata={
            "imas_type": "distributions_d_profiles_1d_thermalized",
            "field_type": DistributionsDProfiles1DThermalized,
        },
    )
    source: Optional[DistributionsDProfiles1DSource] = field(
        default_factory=lambda: StructArray(
            type_input=DistributionsDProfiles1DSource
        ),
        metadata={
            "imas_type": "distributions_d_profiles_1d_source",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": DistributionsDProfiles1DSource,
        },
    )
    trapped: Optional[DistributionsDProfiles1DPartial] = field(
        default=None,
        metadata={
            "imas_type": "distributions_d_profiles_1d_partial",
            "field_type": DistributionsDProfiles1DPartial,
        },
    )
    co_passing: Optional[DistributionsDProfiles1DPartial] = field(
        default=None,
        metadata={
            "imas_type": "distributions_d_profiles_1d_partial",
            "field_type": DistributionsDProfiles1DPartial,
        },
    )
    counter_passing: Optional[DistributionsDProfiles1DPartial] = field(
        default=None,
        metadata={
            "imas_type": "distributions_d_profiles_1d_partial",
            "field_type": DistributionsDProfiles1DPartial,
        },
    )
    time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class DistributionsDProfiles2DGrid(IdsBaseClass):
    """

    :ivar type : Grid type: index=0: Rectangular grid in the (R,Z) coordinates; index=1: Rectangular grid in the (radial, theta_geometric) coordinates; index=2: Rectangular grid in the (radial, theta_straight) coordinates.
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
        name = "distributions_d_profiles_2d_grid"
        is_root_ids = False

    type: Optional[IdentifierDynamicAos3] = field(
        default=None,
        metadata={
            "imas_type": "identifier_dynamic_aos3",
            "field_type": IdentifierDynamicAos3,
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
    z: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    theta_straight: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    theta_geometric: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
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


@idspy_dataclass(repr=False, slots=True)
class DistributionsDProfiles2D(IdsBaseClass):
    """

    :ivar grid : Grid. The grid has to be rectangular in a pair of coordinates, as specified in type
    :ivar density : Density (thermal+non-thermal)
    :ivar density_fast : Density of fast particles
    :ivar pressure : Pressure (thermal+non-thermal)
    :ivar pressure_fast : Pressure of fast particles
    :ivar pressure_fast_parallel : Pressure of fast particles in the parallel direction
    :ivar current_phi : Total toroidal driven current density (including electron and thermal ion back-current, or drag-current)
    :ivar current_fast_phi : Total toroidal driven current density of fast (non-thermal) particles (excluding electron and thermal ion back-current, or drag-current)
    :ivar torque_phi_j_radial : Toroidal torque due to radial currents
    :ivar collisions : Power and torque exchanged between the species described by the distribution and the different plasma species through collisions
    :ivar trapped : Flux surface averaged profile evaluated using the trapped particle part of the distribution.
    :ivar co_passing : Flux surface averaged profile evaluated using the co-passing particle part of the distribution.
    :ivar counter_passing : Flux surface averaged profile evaluated using the counter-passing particle part of the distribution.
    :ivar time : Time
    """

    class Meta:
        name = "distributions_d_profiles_2d"
        is_root_ids = False

    grid: Optional[DistributionsDProfiles2DGrid] = field(
        default=None,
        metadata={
            "imas_type": "distributions_d_profiles_2d_grid",
            "field_type": DistributionsDProfiles2DGrid,
        },
    )
    density: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../grid/r OR ../grid/rho_tor_norm",
                "coordinate2": "../grid/z OR ../grid/theta_geometric OR ../grid/theta_straight",
            },
            "field_type": np.ndarray,
        },
    )
    density_fast: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../grid/r OR ../grid/rho_tor_norm",
                "coordinate2": "../grid/z OR ../grid/theta_geometric OR ../grid/theta_straight",
            },
            "field_type": np.ndarray,
        },
    )
    pressure: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../grid/r OR ../grid/rho_tor_norm",
                "coordinate2": "../grid/z OR ../grid/theta_geometric OR ../grid/theta_straight",
            },
            "field_type": np.ndarray,
        },
    )
    pressure_fast: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../grid/r OR ../grid/rho_tor_norm",
                "coordinate2": "../grid/z OR ../grid/theta_geometric OR ../grid/theta_straight",
            },
            "field_type": np.ndarray,
        },
    )
    pressure_fast_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../grid/r OR ../grid/rho_tor_norm",
                "coordinate2": "../grid/z OR ../grid/theta_geometric OR ../grid/theta_straight",
            },
            "field_type": np.ndarray,
        },
    )
    current_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../grid/r OR ../grid/rho_tor_norm",
                "coordinate2": "../grid/z OR ../grid/theta_geometric OR ../grid/theta_straight",
            },
            "field_type": np.ndarray,
        },
    )
    current_fast_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../grid/r OR ../grid/rho_tor_norm",
                "coordinate2": "../grid/z OR ../grid/theta_geometric OR ../grid/theta_straight",
            },
            "field_type": np.ndarray,
        },
    )
    torque_phi_j_radial: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../grid/r OR ../grid/rho_tor_norm",
                "coordinate2": "../grid/z OR ../grid/theta_geometric OR ../grid/theta_straight",
            },
            "field_type": np.ndarray,
        },
    )
    collisions: Optional[DistributionsDProfiles2DCollisions] = field(
        default=None,
        metadata={
            "imas_type": "distributions_d_profiles_2d_collisions",
            "field_type": DistributionsDProfiles2DCollisions,
        },
    )
    trapped: Optional[DistributionsDProfiles2DPartial] = field(
        default=None,
        metadata={
            "imas_type": "distributions_d_profiles_2d_partial",
            "field_type": DistributionsDProfiles2DPartial,
        },
    )
    co_passing: Optional[DistributionsDProfiles2DPartial] = field(
        default=None,
        metadata={
            "imas_type": "distributions_d_profiles_2d_partial",
            "field_type": DistributionsDProfiles2DPartial,
        },
    )
    counter_passing: Optional[DistributionsDProfiles2DPartial] = field(
        default=None,
        metadata={
            "imas_type": "distributions_d_profiles_2d_partial",
            "field_type": DistributionsDProfiles2DPartial,
        },
    )
    time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class DistributionsD(IdsBaseClass):
    """

    :ivar wave : List all waves affecting the distribution, identified as in waves/coherent_wave(i)/identifier in the waves IDS
    :ivar process : List all processes (NBI units, fusion reactions, ...) affecting the distribution, identified as in distribution_sources/source(i)/process in the DISTRIBUTION_SOURCES IDS
    :ivar gyro_type : Defines how to interpret the spatial coordinates: 1 = given at the actual particle birth point; 2 =given at the gyro centre of the birth point
    :ivar species : Species described by this distribution
    :ivar global_quantities : Global quantities (integrated over plasma volume for moments of the distribution, collisional exchange and source terms), for various time slices
    :ivar profiles_1d : Radial profiles (flux surface averaged quantities) for various time slices
    :ivar profiles_2d : 2D profiles in the poloidal plane for various time slices
    :ivar is_delta_f : If is_delta_f=1, then the distribution represents the deviation from a Maxwellian; is_delta_f=0, then the distribution represents all particles, i.e. the full-f solution
    :ivar ggd : Distribution represented using the ggd, for various time slices
    :ivar markers : Distribution represented by a set of markers (test particles)
    """

    class Meta:
        name = "distributions_d"
        is_root_ids = False

    wave: Optional[WavesCoherentWaveIdentifier] = field(
        default_factory=lambda: StructArray(
            type_input=WavesCoherentWaveIdentifier
        ),
        metadata={
            "imas_type": "waves_coherent_wave_identifier",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": WavesCoherentWaveIdentifier,
        },
    )
    process: Optional[DistributionProcessIdentifier] = field(
        default_factory=lambda: StructArray(
            type_input=DistributionProcessIdentifier
        ),
        metadata={
            "imas_type": "distribution_process_identifier",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": DistributionProcessIdentifier,
        },
    )
    gyro_type: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    species: Optional[DistributionSpecies] = field(
        default=None,
        metadata={
            "imas_type": "distribution_species",
            "field_type": DistributionSpecies,
        },
    )
    global_quantities: Optional[DistributionsDGlobalQuantities] = field(
        default_factory=lambda: StructArray(
            type_input=DistributionsDGlobalQuantities
        ),
        metadata={
            "imas_type": "distributions_d_global_quantities",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": DistributionsDGlobalQuantities,
        },
    )
    profiles_1d: Optional[DistributionsDProfiles1D] = field(
        default_factory=lambda: StructArray(
            type_input=DistributionsDProfiles1D
        ),
        metadata={
            "imas_type": "distributions_d_profiles_1d",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": DistributionsDProfiles1D,
        },
    )
    profiles_2d: Optional[DistributionsDProfiles2D] = field(
        default_factory=lambda: StructArray(
            type_input=DistributionsDProfiles2D
        ),
        metadata={
            "imas_type": "distributions_d_profiles_2d",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": DistributionsDProfiles2D,
        },
    )
    is_delta_f: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    ggd: Optional[DistributionsDGgd] = field(
        default_factory=lambda: StructArray(type_input=DistributionsDGgd),
        metadata={
            "imas_type": "distributions_d_ggd",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": DistributionsDGgd,
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
class Distributions(IdsBaseClass):
    """

    :ivar ids_properties :
    :ivar distribution : Set of distribution functions. Every distribution function has to be associated with only one particle species, specified in distri_vec/species/, but there could be multiple distribution function for each species. In this case, the fast particle populations should be superposed
    :ivar vacuum_toroidal_field : Characteristics of the vacuum toroidal field (used in rho_tor definition and in the normalization of current densities)
    :ivar magnetic_axis : Magnetic axis position (used to define a poloidal angle for the 2D profiles)
    :ivar code :
    :ivar time : Generic time
    """

    class Meta:
        name = "distributions"
        is_root_ids = True

    ids_properties: Optional[IdsProperties] = field(
        default=None,
        metadata={"imas_type": "ids_properties", "field_type": IdsProperties},
    )
    distribution: Optional[DistributionsD] = field(
        default_factory=lambda: StructArray(type_input=DistributionsD),
        metadata={
            "imas_type": "distributions_d",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": DistributionsD,
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
