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
class PlasmaSourcesSourceGgdNeutralState(IdsBaseClass):
    """

    :ivar name : String identifying ion (e.g. H+, D+, T+, He+2, C+, ...)
    :ivar vibrational_level : Vibrational level (can be bundled)
    :ivar vibrational_mode : Vibrational mode of this state, e.g. &#34;A_g&#34;. Need to define, or adopt a standard nomenclature.
    :ivar electron_configuration : Configuration of atomic orbitals of this state, e.g. 1s2-2s1
    :ivar neutral_type : Neutral type, in terms of energy. ID =1: cold; 2: thermal; 3: fast; 4: NBI
    :ivar particles : Source term for the state density transport equation
    :ivar energy : Source terms for the state energy transport equation
    :ivar momentum : Source term for momentum equations, on various grid subsets
    """

    class Meta:
        name = "plasma_sources_source_ggd_neutral_state"
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
    electron_configuration: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    neutral_type: Optional[IdentifierDynamicAos3] = field(
        default=None,
        metadata={
            "imas_type": "identifier_dynamic_aos3",
            "field_type": IdentifierDynamicAos3,
        },
    )
    particles: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    energy: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    momentum: Optional[GenericGridVectorComponents] = field(
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


@idspy_dataclass(repr=False, slots=True)
class PlasmaSourcesSourceGgdIonState(IdsBaseClass):
    """

    :ivar z_min : Minimum Z of the state bundle
    :ivar z_max : Maximum Z of the state bundle
    :ivar name : String identifying state (e.g. C+, C+2 , C+3, C+4, C+5, C+6, ...)
    :ivar vibrational_level : Vibrational level (can be bundled)
    :ivar vibrational_mode : Vibrational mode of this state, e.g. &#34;A_g&#34;. Need to define, or adopt a standard nomenclature.
    :ivar electron_configuration : Configuration of atomic orbitals of this state, e.g. 1s2-2s1
    :ivar particles : Source term for the state density transport equation
    :ivar energy : Source terms for the state energy transport equation
    :ivar momentum : Source term for momentum equations, on various grid subsets
    """

    class Meta:
        name = "plasma_sources_source_ggd_ion_state"
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
    particles: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    energy: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    momentum: Optional[GenericGridVectorComponents] = field(
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
class PlasmaSourcesSourceGgdNeutral(IdsBaseClass):
    """

    :ivar element : List of elements forming the atom or molecule
    :ivar name : String identifying neutral (e.g. H, D, T, He, C, ...)
    :ivar ion_index : Index of the corresponding ion species in the ../../ion array
    :ivar particles : Source term for ion density equation, on various grid subsets
    :ivar energy : Source term for the ion energy transport equation, on various grid subsets
    :ivar momentum : Source term for momentum equations (sum over states when multiple states are considered), on various grid subsets
    :ivar multiple_states_flag : Multiple states calculation flag : 0-Only one state is considered; 1-Multiple states are considered and are described in the state structure
    :ivar state : Source terms related to the different states of the species (energy, excitation, ...)
    """

    class Meta:
        name = "plasma_sources_source_ggd_neutral"
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
    particles: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    energy: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    momentum: Optional[GenericGridVectorComponents] = field(
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
    multiple_states_flag: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    state: Optional[PlasmaSourcesSourceGgdNeutralState] = field(
        default_factory=lambda: StructArray(
            type_input=PlasmaSourcesSourceGgdNeutralState
        ),
        metadata={
            "imas_type": "plasma_sources_source_ggd_neutral_state",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": PlasmaSourcesSourceGgdNeutralState,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class PlasmaSourcesSourceGgdFastIon(IdsBaseClass):
    """

    :ivar element : List of elements forming the atom or molecule
    :ivar z_ion : Ion charge (of the dominant ionization state; lumped ions are allowed)
    :ivar name : String identifying ion (e.g. H+, D+, T+, He+2, C+, ...)
    :ivar neutral_index : Index of the corresponding neutral species in the ../../neutral array
    :ivar power : Total power source or sink related to this ion species, integrated over the volume of the grid subset, for various grid subsets.
    """

    class Meta:
        name = "plasma_sources_source_ggd_fast_ion"
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
class PlasmaSourcesSourceGgdIon(IdsBaseClass):
    """

    :ivar element : List of elements forming the atom or molecule
    :ivar z_ion : Ion charge (of the dominant ionization state; lumped ions are allowed)
    :ivar name : String identifying ion (e.g. H, D, T, He, C, D2, ...)
    :ivar neutral_index : Index of the corresponding neutral species in the ../../neutral array
    :ivar particles : Source term for ion density equation, on various grid subsets
    :ivar energy : Source term for the ion energy transport equation, on various grid subsets
    :ivar momentum : Source term for momentum equations (sum over states when multiple states are considered), on various grid subsets
    :ivar multiple_states_flag : Multiple states calculation flag : 0-Only the &#39;ion&#39; level is considered and the &#39;state&#39; array of structure is empty; 1-Ion states are considered and are described in the &#39;state&#39; array of structure
    :ivar state : Source terms related to the different states of the species (ionization, energy, excitation, ...)
    """

    class Meta:
        name = "plasma_sources_source_ggd_ion"
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
    particles: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    energy: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    momentum: Optional[GenericGridVectorComponents] = field(
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
    multiple_states_flag: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    state: Optional[PlasmaSourcesSourceGgdIonState] = field(
        default_factory=lambda: StructArray(
            type_input=PlasmaSourcesSourceGgdIonState
        ),
        metadata={
            "imas_type": "plasma_sources_source_ggd_ion_state",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": PlasmaSourcesSourceGgdIonState,
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
class PlasmaSourcesSourceGgdElectrons(IdsBaseClass):
    """

    :ivar particles : Source term for electron density equation, given on various grid subsets
    :ivar energy : Source term for the electron energy equation, given on various grid subsets
    """

    class Meta:
        name = "plasma_sources_source_ggd_electrons"
        is_root_ids = False

    particles: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    energy: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
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
class PlasmaSourcesSourceGgdFast(IdsBaseClass):
    """

    :ivar ion : Source term integrals related to the various ion species
    :ivar time : Time
    """

    class Meta:
        name = "plasma_sources_source_ggd_fast"
        is_root_ids = False

    ion: Optional[PlasmaSourcesSourceGgdFastIon] = field(
        default_factory=lambda: StructArray(
            type_input=PlasmaSourcesSourceGgdFastIon
        ),
        metadata={
            "imas_type": "plasma_sources_source_ggd_fast_ion",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": PlasmaSourcesSourceGgdFastIon,
        },
    )
    time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
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
class PlasmaSourcesSourceGgd(IdsBaseClass):
    """

    :ivar electrons : Sources for electrons
    :ivar ion : Source terms related to the different ion species, in the sense of isonuclear or isomolecular sequences. ionization states (and other types of states) must be differentiated at the state level below
    :ivar neutral : Source terms related to the different neutral species
    :ivar total_ion_energy : Source term for the total (summed over ion  species) energy equation, on various grid subsets
    :ivar momentum : Source term for total momentum equations, on various grid subsets
    :ivar current : Current density source
    :ivar time : Time
    """

    class Meta:
        name = "plasma_sources_source_ggd"
        is_root_ids = False

    electrons: Optional[PlasmaSourcesSourceGgdElectrons] = field(
        default=None,
        metadata={
            "imas_type": "plasma_sources_source_ggd_electrons",
            "field_type": PlasmaSourcesSourceGgdElectrons,
        },
    )
    ion: Optional[PlasmaSourcesSourceGgdIon] = field(
        default_factory=lambda: StructArray(
            type_input=PlasmaSourcesSourceGgdIon
        ),
        metadata={
            "imas_type": "plasma_sources_source_ggd_ion",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": PlasmaSourcesSourceGgdIon,
        },
    )
    neutral: Optional[PlasmaSourcesSourceGgdNeutral] = field(
        default_factory=lambda: StructArray(
            type_input=PlasmaSourcesSourceGgdNeutral
        ),
        metadata={
            "imas_type": "plasma_sources_source_ggd_neutral",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": PlasmaSourcesSourceGgdNeutral,
        },
    )
    total_ion_energy: Optional[GenericGridScalar] = field(
        default_factory=lambda: StructArray(type_input=GenericGridScalar),
        metadata={
            "imas_type": "generic_grid_scalar",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": GenericGridScalar,
        },
    )
    momentum: Optional[GenericGridVectorComponents] = field(
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
    current: Optional[GenericGridScalar] = field(
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
class PlasmaSourcesSourceProfiles1DParticlesDecomposed2(IdsBaseClass):
    """

    :ivar implicit_part : Implicit part of the source term, i.e. to be multiplied by the equation&#39;s primary quantity
    :ivar explicit_part : Explicit part of the source term
    """

    class Meta:
        name = "plasma_sources_source_profiles_1d_particles_decomposed_2"
        is_root_ids = False

    implicit_part: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    explicit_part: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class PlasmaSourcesSourceProfiles1DParticlesDecomposed3(IdsBaseClass):
    """

    :ivar implicit_part : Implicit part of the source term, i.e. to be multiplied by the equation&#39;s primary quantity
    :ivar explicit_part : Explicit part of the source term
    """

    class Meta:
        name = "plasma_sources_source_profiles_1d_particles_decomposed_3"
        is_root_ids = False

    implicit_part: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    explicit_part: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class PlasmaSourcesSourceProfiles1DParticlesDecomposed4(IdsBaseClass):
    """

    :ivar implicit_part : Implicit part of the source term, i.e. to be multiplied by the equation&#39;s primary quantity
    :ivar explicit_part : Explicit part of the source term
    """

    class Meta:
        name = "plasma_sources_source_profiles_1d_particles_decomposed_4"
        is_root_ids = False

    implicit_part: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    explicit_part: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class PlasmaSourcesSourceProfiles1DMomentumDecomposed4(IdsBaseClass):
    """

    :ivar implicit_part : Implicit part of the source term, i.e. to be multiplied by the equation&#39;s primary quantity
    :ivar explicit_part : Explicit part of the source term
    """

    class Meta:
        name = "plasma_sources_source_profiles_1d_momentum_decomposed_4"
        is_root_ids = False

    implicit_part: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    explicit_part: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class PlasmaSourcesSourceProfiles1DEnergyDecomposed4(IdsBaseClass):
    """

    :ivar implicit_part : Implicit part of the source term, i.e. to be multiplied by the equation&#39;s primary quantity
    :ivar explicit_part : Explicit part of the source term
    """

    class Meta:
        name = "plasma_sources_source_profiles_1d_energy_decomposed_4"
        is_root_ids = False

    implicit_part: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    explicit_part: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class PlasmaSourcesSourceProfiles1DEnergyDecomposed3(IdsBaseClass):
    """

    :ivar implicit_part : Implicit part of the source term, i.e. to be multiplied by the equation&#39;s primary quantity
    :ivar explicit_part : Explicit part of the source term
    """

    class Meta:
        name = "plasma_sources_source_profiles_1d_energy_decomposed_3"
        is_root_ids = False

    implicit_part: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    explicit_part: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class PlasmaSourcesSourceProfiles1DEnergyDecomposed2(IdsBaseClass):
    """

    :ivar implicit_part : Implicit part of the source term, i.e. to be multiplied by the equation&#39;s primary quantity
    :ivar explicit_part : Explicit part of the source term
    """

    class Meta:
        name = "plasma_sources_source_profiles_1d_energy_decomposed_2"
        is_root_ids = False

    implicit_part: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    explicit_part: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class PlasmaSourcesSourceProfiles1DNeutralState(IdsBaseClass):
    """

    :ivar name : String identifying state
    :ivar vibrational_level : Vibrational level (can be bundled)
    :ivar vibrational_mode : Vibrational mode of this state, e.g. &#34;A_g&#34;. Need to define, or adopt a standard nomenclature.
    :ivar neutral_type : Neutral type (if the considered state is a neutral), in terms of energy. ID =1: cold; 2: thermal; 3: fast; 4: NBI
    :ivar electron_configuration : Configuration of atomic orbitals of this state, e.g. 1s2-2s1
    :ivar particles : Source term for the state density transport equation
    :ivar energy : Source terms for the state energy transport equation
    """

    class Meta:
        name = "plasma_sources_source_profiles_1d_neutral_state"
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


@idspy_dataclass(repr=False, slots=True)
class PlasmaSourcesSourceProfiles1DNeutral(IdsBaseClass):
    """

    :ivar element : List of elements forming the atom or molecule
    :ivar name : String identifying the neutral species (e.g. H, D, T, He, C, ...)
    :ivar ion_index : Index of the corresponding ion species in the ../../ion array
    :ivar particles : Source term for neutral density equation
    :ivar energy : Source term for the neutral energy transport equation.
    :ivar multiple_states_flag : Multiple states calculation flag : 0-Only one state is considered; 1-Multiple states are considered and are described in the state structure
    :ivar state : Source terms related to the different charge states of the species (energy, excitation, ...)
    """

    class Meta:
        name = "plasma_sources_source_profiles_1d_neutral"
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
    multiple_states_flag: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    state: Optional[PlasmaSourcesSourceProfiles1DNeutralState] = field(
        default_factory=lambda: StructArray(
            type_input=PlasmaSourcesSourceProfiles1DNeutralState
        ),
        metadata={
            "imas_type": "plasma_sources_source_profiles_1d_neutral_state",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": PlasmaSourcesSourceProfiles1DNeutralState,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class PlasmaSourcesSourceProfiles1DComponents2(IdsBaseClass):
    """

    :ivar radial : Radial component
    :ivar diamagnetic : Diamagnetic component
    :ivar parallel : Parallel component
    :ivar poloidal : Poloidal component
    :ivar toroidal : Toroidal component
    :ivar toroidal_decomposed : Decomposition of the source term for ion toroidal momentum equation into implicit and explicit parts
    """

    class Meta:
        name = "plasma_sources_source_profiles_1d_components_2"
        is_root_ids = False

    radial: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    diamagnetic: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    poloidal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    toroidal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    toroidal_decomposed: Optional[
        PlasmaSourcesSourceProfiles1DMomentumDecomposed4
    ] = field(
        default=None,
        metadata={
            "imas_type": "plasma_sources_source_profiles_1d_momentum_decomposed_4",
            "field_type": PlasmaSourcesSourceProfiles1DMomentumDecomposed4,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class PlasmaSourcesSourceProfiles1DIonsChargeStates(IdsBaseClass):
    """

    :ivar z_min : Minimum Z of the charge state bundle
    :ivar z_max : Maximum Z of the charge state bundle
    :ivar name : String identifying charge state (e.g. C+, C+2 , C+3, C+4, C+5, C+6, ...)
    :ivar vibrational_level : Vibrational level (can be bundled)
    :ivar vibrational_mode : Vibrational mode of this state, e.g. &#34;A_g&#34;. Need to define, or adopt a standard nomenclature.
    :ivar electron_configuration : Configuration of atomic orbitals of this state, e.g. 1s2-2s1
    :ivar particles : Source term for the charge state density transport equation
    :ivar particles_inside : State source inside the flux surface. Cumulative volume integral of the source term for the electron density equation.
    :ivar particles_decomposed : Decomposition of the source term for state density equation into implicit and explicit parts
    :ivar energy : Source terms for the charge state energy transport equation
    :ivar power_inside : Power coupled to the state inside the flux surface. Cumulative volume integral of the source term for the electron energy equation
    :ivar energy_decomposed : Decomposition of the source term for state energy equation into implicit and explicit parts
    """

    class Meta:
        name = "plasma_sources_source_profiles_1d_ions_charge_states"
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
    particles: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    particles_inside: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    particles_decomposed: Optional[
        PlasmaSourcesSourceProfiles1DParticlesDecomposed4
    ] = field(
        default=None,
        metadata={
            "imas_type": "plasma_sources_source_profiles_1d_particles_decomposed_4",
            "field_type": PlasmaSourcesSourceProfiles1DParticlesDecomposed4,
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
    power_inside: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    energy_decomposed: Optional[
        PlasmaSourcesSourceProfiles1DEnergyDecomposed4
    ] = field(
        default=None,
        metadata={
            "imas_type": "plasma_sources_source_profiles_1d_energy_decomposed_4",
            "field_type": PlasmaSourcesSourceProfiles1DEnergyDecomposed4,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class PlasmaSourcesSourceProfiles1DIons(IdsBaseClass):
    """

    :ivar element : List of elements forming the atom or molecule
    :ivar z_ion : Ion charge (of the dominant ionization state; lumped ions are allowed)
    :ivar name : String identifying ion (e.g. H, D, T, He, C, D2, ...)
    :ivar neutral_index : Index of the corresponding neutral species in the ../../neutral array
    :ivar particles : Source term for ion density equation
    :ivar particles_inside : Ion source inside the flux surface. Cumulative volume integral of the source term for the electron density equation.
    :ivar particles_decomposed : Decomposition of the source term for ion density equation into implicit and explicit parts
    :ivar energy : Source term for the ion energy transport equation.
    :ivar power_inside : Power coupled to the ion species inside the flux surface. Cumulative volume integral of the source term for the electron energy equation
    :ivar energy_decomposed : Decomposition of the source term for ion energy equation into implicit and explicit parts
    :ivar momentum : Source term for the ion momentum transport equations along various components (directions)
    :ivar multiple_states_flag : Multiple states calculation flag : 0-Only the &#39;ion&#39; level is considered and the &#39;state&#39; array of structure is empty; 1-Ion states are considered and are described in the &#39;state&#39; array of structure
    :ivar state : Source terms related to the different charge states of the species (ionization, energy, excitation, ...)
    """

    class Meta:
        name = "plasma_sources_source_profiles_1d_ions"
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
    particles: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    particles_inside: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    particles_decomposed: Optional[
        PlasmaSourcesSourceProfiles1DParticlesDecomposed3
    ] = field(
        default=None,
        metadata={
            "imas_type": "plasma_sources_source_profiles_1d_particles_decomposed_3",
            "field_type": PlasmaSourcesSourceProfiles1DParticlesDecomposed3,
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
    power_inside: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    energy_decomposed: Optional[
        PlasmaSourcesSourceProfiles1DEnergyDecomposed3
    ] = field(
        default=None,
        metadata={
            "imas_type": "plasma_sources_source_profiles_1d_energy_decomposed_3",
            "field_type": PlasmaSourcesSourceProfiles1DEnergyDecomposed3,
        },
    )
    momentum: Optional[PlasmaSourcesSourceProfiles1DComponents2] = field(
        default=None,
        metadata={
            "imas_type": "plasma_sources_source_profiles_1d_components_2",
            "field_type": PlasmaSourcesSourceProfiles1DComponents2,
        },
    )
    multiple_states_flag: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    state: Optional[PlasmaSourcesSourceProfiles1DIonsChargeStates] = field(
        default_factory=lambda: StructArray(
            type_input=PlasmaSourcesSourceProfiles1DIonsChargeStates
        ),
        metadata={
            "imas_type": "plasma_sources_source_profiles_1d_ions_charge_states",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": PlasmaSourcesSourceProfiles1DIonsChargeStates,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class PlasmaSourcesSourceProfiles1DElectrons(IdsBaseClass):
    """

    :ivar particles : Source term for electron density equation
    :ivar particles_decomposed : Decomposition of the source term for electron density equation into implicit and explicit parts
    :ivar particles_inside : Electron source inside the flux surface. Cumulative volume integral of the source term for the electron density equation.
    :ivar energy : Source term for the electron energy equation
    :ivar energy_decomposed : Decomposition of the source term for electron energy equation into implicit and explicit parts
    :ivar power_inside : Power coupled to electrons inside the flux surface. Cumulative volume integral of the source term for the electron energy equation
    """

    class Meta:
        name = "plasma_sources_source_profiles_1d_electrons"
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
    particles_decomposed: Optional[
        PlasmaSourcesSourceProfiles1DParticlesDecomposed3
    ] = field(
        default=None,
        metadata={
            "imas_type": "plasma_sources_source_profiles_1d_particles_decomposed_3",
            "field_type": PlasmaSourcesSourceProfiles1DParticlesDecomposed3,
        },
    )
    particles_inside: Optional[np.ndarray] = field(
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
    energy_decomposed: Optional[
        PlasmaSourcesSourceProfiles1DEnergyDecomposed3
    ] = field(
        default=None,
        metadata={
            "imas_type": "plasma_sources_source_profiles_1d_energy_decomposed_3",
            "field_type": PlasmaSourcesSourceProfiles1DEnergyDecomposed3,
        },
    )
    power_inside: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class PlasmaSourcesSourceProfiles1D(IdsBaseClass):
    """

    :ivar grid : Radial grid. Note that some of the radial coordinates listed above are undefined outside the last closed flux surface, thus they must be filled with EMPTY_FLOAT values in such locations
    :ivar electrons : Sources for electrons
    :ivar total_ion_energy : Source term for the total (summed over ion  species) energy equation
    :ivar total_ion_energy_decomposed : Decomposition of the source term for total ion energy equation into implicit and explicit parts
    :ivar total_ion_power_inside : Total power coupled to ion species (summed over ion  species) inside the flux surface. Cumulative volume integral of the source term for the total ion energy equation
    :ivar total_ion_particles : Source term for the total (summed over ion  species) density equation
    :ivar total_ion_particles_decomposed : Decomposition of the source term for total ion density equation into implicit and explicit parts
    :ivar total_ion_particles_inside : Total ion particle source (summed over ion  species) inside the flux surface. Cumulative volume integral of the source term for the total ion density equation
    :ivar momentum_phi : Source term for total toroidal momentum equation
    :ivar torque_phi_inside : Toroidal torque inside the flux surface. Cumulative volume integral of the source term for the total toroidal momentum equation
    :ivar momentum_phi_j_cross_b_field : Contribution to the toroidal momentum source term (already included in the momentum_tor node) corresponding to the toroidal torques onto the thermal plasma due to Lorentz force associated with radial currents. These currents appear as return-currents (enforcing quasi-neutrality, div(J)=0) balancing radial currents of non-thermal particles, e.g. radial currents of fast and trapped neutral-beam-ions.
    :ivar j_parallel : Parallel current density source, average(J.B) / B0, where B0 = plasma_sources/vacuum_toroidal_field/b0
    :ivar current_parallel_inside : Parallel current driven inside the flux surface. Cumulative surface integral of j_parallel
    :ivar conductivity_parallel : Parallel conductivity due to this source
    :ivar ion : Source terms related to the different ions species, in the sense of isonuclear or isomolecular sequences. ionization states (and other types of states) must be differentiated at the state level below
    :ivar neutral : Source terms related to the different neutral species
    :ivar time : Time
    """

    class Meta:
        name = "plasma_sources_source_profiles_1d"
        is_root_ids = False

    grid: Optional[PlasmaRadialGrid] = field(
        default=None,
        metadata={
            "imas_type": "plasma_radial_grid",
            "field_type": PlasmaRadialGrid,
        },
    )
    electrons: Optional[PlasmaSourcesSourceProfiles1DElectrons] = field(
        default=None,
        metadata={
            "imas_type": "plasma_sources_source_profiles_1d_electrons",
            "field_type": PlasmaSourcesSourceProfiles1DElectrons,
        },
    )
    total_ion_energy: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    total_ion_energy_decomposed: Optional[
        PlasmaSourcesSourceProfiles1DEnergyDecomposed2
    ] = field(
        default=None,
        metadata={
            "imas_type": "plasma_sources_source_profiles_1d_energy_decomposed_2",
            "field_type": PlasmaSourcesSourceProfiles1DEnergyDecomposed2,
        },
    )
    total_ion_power_inside: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    total_ion_particles: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    total_ion_particles_decomposed: Optional[
        PlasmaSourcesSourceProfiles1DParticlesDecomposed2
    ] = field(
        default=None,
        metadata={
            "imas_type": "plasma_sources_source_profiles_1d_particles_decomposed_2",
            "field_type": PlasmaSourcesSourceProfiles1DParticlesDecomposed2,
        },
    )
    total_ion_particles_inside: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    momentum_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    torque_phi_inside: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    momentum_phi_j_cross_b_field: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    j_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    current_parallel_inside: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    conductivity_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    ion: Optional[PlasmaSourcesSourceProfiles1DIons] = field(
        default_factory=lambda: StructArray(
            type_input=PlasmaSourcesSourceProfiles1DIons
        ),
        metadata={
            "imas_type": "plasma_sources_source_profiles_1d_ions",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": PlasmaSourcesSourceProfiles1DIons,
        },
    )
    neutral: Optional[PlasmaSourcesSourceProfiles1DNeutral] = field(
        default_factory=lambda: StructArray(
            type_input=PlasmaSourcesSourceProfiles1DNeutral
        ),
        metadata={
            "imas_type": "plasma_sources_source_profiles_1d_neutral",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": PlasmaSourcesSourceProfiles1DNeutral,
        },
    )
    time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class PlasmaSourcesSourceGlobalElectrons(IdsBaseClass):
    """

    :ivar particles : Electron particle source
    :ivar power : Power coupled to electrons
    """

    class Meta:
        name = "plasma_sources_source_global_electrons"
        is_root_ids = False

    particles: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    power: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class PlasmaSourcesSourceGlobal(IdsBaseClass):
    """

    :ivar power : Total power coupled to the plasma
    :ivar total_ion_particles : Total ion particle source (summed over ion  species)
    :ivar total_ion_power : Total power coupled to ion species (summed over ion  species)
    :ivar electrons : Sources for electrons
    :ivar torque_phi : Toroidal torque
    :ivar current_parallel : Parallel current driven
    :ivar time : Time
    """

    class Meta:
        name = "plasma_sources_source_global"
        is_root_ids = False

    power: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    total_ion_particles: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    total_ion_power: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    electrons: Optional[PlasmaSourcesSourceGlobalElectrons] = field(
        default=None,
        metadata={
            "imas_type": "plasma_sources_source_global_electrons",
            "field_type": PlasmaSourcesSourceGlobalElectrons,
        },
    )
    torque_phi: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    current_parallel: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class PlasmaSourcesSource(IdsBaseClass):
    """

    :ivar species : Species causing this source term (if relevant, e.g. a particular ion or neutral state in case of line radiation)
    :ivar global_quantities : Total source quantities integrated over the plasma volume or surface
    :ivar profiles_1d : Source profiles for various time slices. Source terms are positive (resp. negative) when there is a gain (resp. a loss) to the considered channel.
    :ivar ggd : Source terms represented using the general grid description, for various time slices
    :ivar ggd_fast : Quantities provided at a faster sampling rate than the full ggd quantities. These are either integrated quantities or local quantities provided on a reduced set of positions. Positions and integration domains are described by a set of grid_subsets (of size 1 for a position).
    :ivar code : Code-specific parameters used for this source
    """

    class Meta:
        name = "plasma_sources_source"
        is_root_ids = False

    species: Optional[DistributionSpecies] = field(
        default=None,
        metadata={
            "imas_type": "distribution_species",
            "field_type": DistributionSpecies,
        },
    )
    global_quantities: Optional[PlasmaSourcesSourceGlobal] = field(
        default_factory=lambda: StructArray(
            type_input=PlasmaSourcesSourceGlobal
        ),
        metadata={
            "imas_type": "plasma_sources_source_global",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": PlasmaSourcesSourceGlobal,
        },
    )
    profiles_1d: Optional[PlasmaSourcesSourceProfiles1D] = field(
        default_factory=lambda: StructArray(
            type_input=PlasmaSourcesSourceProfiles1D
        ),
        metadata={
            "imas_type": "plasma_sources_source_profiles_1d",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": PlasmaSourcesSourceProfiles1D,
        },
    )
    ggd: Optional[PlasmaSourcesSourceGgd] = field(
        default_factory=lambda: StructArray(type_input=PlasmaSourcesSourceGgd),
        metadata={
            "imas_type": "plasma_sources_source_ggd",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": PlasmaSourcesSourceGgd,
        },
    )
    ggd_fast: Optional[PlasmaSourcesSourceGgdFast] = field(
        default_factory=lambda: StructArray(
            type_input=PlasmaSourcesSourceGgdFast
        ),
        metadata={
            "imas_type": "plasma_sources_source_ggd_fast",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": PlasmaSourcesSourceGgdFast,
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
class PlasmaSources(IdsBaseClass):
    """

    :ivar ids_properties :
    :ivar midplane : Choice of midplane definition (use the lowest index number if more than one value is relevant)
    :ivar vacuum_toroidal_field : Characteristics of the vacuum toroidal field (used in rho_Tor definition and in the normalization of current densities)
    :ivar grid_ggd : Grid (using the Generic Grid Description), for various time slices. The timebase of this array of structure must be a subset of the ggd timebases
    :ivar source : Set of source terms
    :ivar code :
    :ivar time : Generic time
    """

    class Meta:
        name = "plasma_sources"
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
    source: Optional[PlasmaSourcesSource] = field(
        default_factory=lambda: StructArray(type_input=PlasmaSourcesSource),
        metadata={
            "imas_type": "plasma_sources_source",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": PlasmaSourcesSource,
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
