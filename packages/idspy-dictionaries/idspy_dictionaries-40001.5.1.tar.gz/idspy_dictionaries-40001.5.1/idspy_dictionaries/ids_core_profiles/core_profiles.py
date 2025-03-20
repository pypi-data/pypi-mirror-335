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
class CoreProfilesVectorComponents3(IdsBaseClass):
    """

    :ivar radial : Radial component
    :ivar diamagnetic : Diamagnetic component
    :ivar parallel : Parallel component
    :ivar poloidal : Poloidal component
    :ivar toroidal : Toroidal component
    """

    class Meta:
        name = "core_profiles_vector_components_3"
        is_root_ids = False

    radial: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    diamagnetic: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    poloidal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    toroidal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class CoreProfilesVectorComponents2(IdsBaseClass):
    """

    :ivar radial : Radial component
    :ivar diamagnetic : Diamagnetic component
    :ivar parallel : Parallel component
    :ivar poloidal : Poloidal component
    :ivar toroidal : Toroidal component
    """

    class Meta:
        name = "core_profiles_vector_components_2"
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
class CoreProfilesNeutralState(IdsBaseClass):
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
        name = "core_profiles_neutral_state"
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
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    density: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    density_thermal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    density_fast: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    pressure: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    pressure_thermal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    pressure_fast_perpendicular: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    pressure_fast_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
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
class CoreProfilesIonsChargeStates2(IdsBaseClass):
    """

    :ivar z_min : Minimum Z of the charge state bundle
    :ivar z_max : Maximum Z of the charge state bundle (equal to z_min if no bundle)
    :ivar z_average : Average Z of the charge state bundle, volume averaged over the plasma radius (equal to z_min if no bundle), = sum (Z*x_z) where x_z is the relative concentration of a given charge state in the bundle, i.e. sum(x_z) = 1 over the bundle.
    :ivar z_square_average : Average Z square of the charge state bundle, volume averaged over the plasma radius (equal to z_min squared if no bundle), = sum (Z^2*x_z) where x_z is the relative concentration of a given charge state in the bundle, i.e. sum(x_z) = 1 over the bundle.
    :ivar z_average_1d : Average charge profile of the charge state bundle (equal to z_min if no bundle), = sum (Z*x_z) where x_z is the relative concentration of a given charge state in the bundle, i.e. sum(x_z) = 1 over the bundle.
    :ivar z_average_square_1d : Average square charge profile of the charge state bundle (equal to z_min squared if no bundle), = sum (Z^2*x_z) where x_z is the relative concentration of a given charge state in the bundle, i.e. sum(x_z) = 1 over the bundle.
    :ivar ionization_potential : Cumulative and average ionization potential to reach a given bundle. Defined as sum (x_z* (sum of Epot from z&#39;=0 to z-1)), where Epot is the ionization potential of ion Xz’+, and x_z is the relative concentration of a given charge state in the bundle, i.e. sum(x_z) = 1 over the bundle.
    :ivar name : String identifying state (e.g. C+, C+2 , C+3, C+4, C+5, C+6, ...)
    :ivar electron_configuration : Configuration of atomic orbitals of this state, e.g. 1s2-2s1
    :ivar vibrational_level : Vibrational level (can be bundled)
    :ivar vibrational_mode : Vibrational mode of this state, e.g. &#34;A_g&#34;. Need to define, or adopt a standard nomenclature.
    :ivar rotation_frequency_tor : Toroidal rotation frequency (i.e. toroidal velocity divided by the major radius at which the toroidal velocity is taken)
    :ivar velocity : Velocity at the position of maximum major radius on every flux surface
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
        name = "core_profiles_ions_charge_states2"
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
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    z_average_square_1d: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
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
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    velocity: Optional[CoreProfilesVectorComponents3] = field(
        default=None,
        metadata={
            "imas_type": "core_profiles_vector_components_3",
            "field_type": CoreProfilesVectorComponents3,
        },
    )
    temperature: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    density: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    density_fit: Optional[CoreProfiles1DFit] = field(
        default=None,
        metadata={
            "imas_type": "core_profiles_1D_fit",
            "field_type": CoreProfiles1DFit,
        },
    )
    density_thermal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    density_fast: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    pressure: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    pressure_thermal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    pressure_fast_perpendicular: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    pressure_fast_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class CoreProfileIons(IdsBaseClass):
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
        name = "core_profile_ions"
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
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    z_ion_square_1d: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    temperature: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    temperature_validity: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    temperature_fit: Optional[CoreProfiles1DFit] = field(
        default=None,
        metadata={
            "imas_type": "core_profiles_1D_fit",
            "field_type": CoreProfiles1DFit,
        },
    )
    density: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    density_validity: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    density_fit: Optional[CoreProfiles1DFit] = field(
        default=None,
        metadata={
            "imas_type": "core_profiles_1D_fit",
            "field_type": CoreProfiles1DFit,
        },
    )
    density_thermal: Optional[np.ndarray] = field(
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
    pressure_thermal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    pressure_fast_perpendicular: Optional[np.ndarray] = field(
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
    rotation_frequency_tor: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    velocity: Optional[CoreProfilesVectorComponents2] = field(
        default=None,
        metadata={
            "imas_type": "core_profiles_vector_components_2",
            "field_type": CoreProfilesVectorComponents2,
        },
    )
    multiple_states_flag: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    state: Optional[CoreProfilesIonsChargeStates2] = field(
        default_factory=lambda: StructArray(
            type_input=CoreProfilesIonsChargeStates2
        ),
        metadata={
            "imas_type": "core_profiles_ions_charge_states2",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": CoreProfilesIonsChargeStates2,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class CoreProfilesProfiles1DElectrons(IdsBaseClass):
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
        name = "core_profiles_profiles_1d_electrons"
        is_root_ids = False

    temperature: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    temperature_validity: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    temperature_fit: Optional[CoreProfiles1DFit] = field(
        default=None,
        metadata={
            "imas_type": "core_profiles_1D_fit",
            "field_type": CoreProfiles1DFit,
        },
    )
    density: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    density_validity: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    density_fit: Optional[CoreProfiles1DFit] = field(
        default=None,
        metadata={
            "imas_type": "core_profiles_1D_fit",
            "field_type": CoreProfiles1DFit,
        },
    )
    density_thermal: Optional[np.ndarray] = field(
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
    pressure_thermal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    pressure_fast_perpendicular: Optional[np.ndarray] = field(
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
    collisionality_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
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
class CoreProfileNeutral(IdsBaseClass):
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
        name = "core_profile_neutral"
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
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    density: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    density_thermal: Optional[np.ndarray] = field(
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
    pressure_thermal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    pressure_fast_perpendicular: Optional[np.ndarray] = field(
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
    multiple_states_flag: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    state: Optional[CoreProfilesNeutralState] = field(
        default_factory=lambda: StructArray(
            type_input=CoreProfilesNeutralState
        ),
        metadata={
            "imas_type": "core_profiles_neutral_state",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": CoreProfilesNeutralState,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class CoreProfilesVectorComponents1(IdsBaseClass):
    """

    :ivar radial : Radial component
    :ivar diamagnetic : Diamagnetic component
    :ivar parallel : Parallel component
    :ivar poloidal : Poloidal component
    :ivar toroidal : Toroidal component
    """

    class Meta:
        name = "core_profiles_vector_components_1"
        is_root_ids = False

    radial: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    diamagnetic: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    poloidal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    toroidal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class CoreProfiles1DFit(IdsBaseClass):
    """

    :ivar measured : Measured values. Units are: as_parent for a local measurement, as_parent.m for a line integrated measurement.
    :ivar source : Path to the source data for each measurement in the IMAS data dictionary, e.g. ece/channel(i)/t_e for the electron temperature on the i-th channel in the ECE IDS
    :ivar time_measurement : Exact time slices used from the time array of the measurement source data. The time slice is indicated for each measurement point considered in the fit since measurements may come from different and thus asynchronous diagnostics. If the time slice does not exist in the time array of the source data, it means linear interpolation has been used
    :ivar time_measurement_slice_method : Method used to slice the data : index = 0 means using exact time slice of the measurement, 1 means linear interpolation, ...
    :ivar time_measurement_width : In case the measurements are averaged over a time interval, this node is the full width of this time interval (empty otherwise). In case the slicing/averaging method doesn&#39;t use a hard time interval cutoff, this width is the characteristic time span of the slicing/averaging method. By convention, the time interval starts at time_measurement-time_width and ends at time_measurement.
    :ivar local : Integer flag : 1 means local measurement, 0 means line-integrated measurement
    :ivar rho_tor_norm : Normalized toroidal flux coordinate of each measurement (local value for a local measurement, minimum value reached by the line of sight for a line measurement)
    :ivar weight : Weight given to each measured value
    :ivar reconstructed : Value reconstructed from the fit. Units are: as_parent for a local measurement, as_parent.m for a line integrated measurement.
    :ivar chi_squared : Squared error normalized by the weighted standard deviation considered in the minimization process : chi_squared = weight^2 *(reconstructed - measured)^2 / sigma^2, where sigma is the standard deviation of the measurement error
    :ivar parameters : List of the fit specific parameters in XML format
    """

    class Meta:
        name = "core_profiles_1D_fit"
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
class CoreProfilesProfiles1D(IdsBaseClass):
    """

    :ivar grid : Radial grid
    :ivar electrons : Quantities related to the electrons
    :ivar ion : Quantities related to the different ion species, in the sense of isonuclear or isomolecular sequences. Ionization states (or other types of states) must be differentiated at the state level below
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
    :ivar j_total : Total parallel current density = average(jtot.B) / B0, where B0 = Core_Profiles/Vacuum_Toroidal_Field/ B0
    :ivar current_parallel_inside : Parallel current driven inside the flux surface. Cumulative surface integral of j_total
    :ivar j_phi : Total toroidal current density = average(J_phi/R) / average(1/R)
    :ivar j_ohmic : Ohmic parallel current density = average(J_Ohmic.B) / B0, where B0 = Core_Profiles/Vacuum_Toroidal_Field/ B0
    :ivar j_non_inductive : Non-inductive (includes bootstrap) parallel current density = average(jni.B) / B0, where B0 = Core_Profiles/Vacuum_Toroidal_Field/ B0
    :ivar j_bootstrap : Bootstrap current density = average(J_Bootstrap.B) / B0, where B0 = Core_Profiles/Vacuum_Toroidal_Field/ B0
    :ivar conductivity_parallel : Parallel conductivity
    :ivar e_field : Electric field, averaged on the magnetic surface. E.g for the parallel component, average(E.B) / B0, using core_profiles/vacuum_toroidal_field/b0
    :ivar phi_potential : Electrostatic potential, averaged on the magnetic flux surface
    :ivar rotation_frequency_tor_sonic : Derivative of the flux surface averaged electrostatic potential with respect to the poloidal flux, multiplied by (1/2pi). This quantity is the toroidal angular rotation frequency due to the ExB drift, introduced in formula (43) of Hinton and Wong, Physics of Fluids 3082 (1985), also referred to as sonic flow in regimes in which the toroidal velocity is dominant over the poloidal velocity
    :ivar q : Safety factor (only positive when toroidal current and magnetic field are in same direction)
    :ivar magnetic_shear : Magnetic shear, defined as rho_tor/q . dq/drho_tor
    :ivar time : Time
    """

    class Meta:
        name = "core_profiles_profiles_1d"
        is_root_ids = False

    grid: Optional[CoreRadialGrid] = field(
        default=None,
        metadata={
            "imas_type": "core_radial_grid",
            "field_type": CoreRadialGrid,
        },
    )
    electrons: Optional[CoreProfilesProfiles1DElectrons] = field(
        default=None,
        metadata={
            "imas_type": "core_profiles_profiles_1d_electrons",
            "field_type": CoreProfilesProfiles1DElectrons,
        },
    )
    ion: Optional[CoreProfileIons] = field(
        default_factory=lambda: StructArray(type_input=CoreProfileIons),
        metadata={
            "imas_type": "core_profile_ions",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": CoreProfileIons,
        },
    )
    neutral: Optional[CoreProfileNeutral] = field(
        default_factory=lambda: StructArray(type_input=CoreProfileNeutral),
        metadata={
            "imas_type": "core_profile_neutral",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": CoreProfileNeutral,
        },
    )
    t_i_average: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    t_i_average_fit: Optional[CoreProfiles1DFit] = field(
        default=None,
        metadata={
            "imas_type": "core_profiles_1D_fit",
            "field_type": CoreProfiles1DFit,
        },
    )
    n_i_total_over_n_e: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    n_i_thermal_total: Optional[np.ndarray] = field(
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
    zeff: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    zeff_fit: Optional[CoreProfiles1DFit] = field(
        default=None,
        metadata={
            "imas_type": "core_profiles_1D_fit",
            "field_type": CoreProfiles1DFit,
        },
    )
    pressure_ion_total: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    pressure_thermal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    pressure_perpendicular: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    pressure_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    j_total: Optional[np.ndarray] = field(
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
    j_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    j_ohmic: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    j_non_inductive: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    j_bootstrap: Optional[np.ndarray] = field(
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
    e_field: Optional[CoreProfilesVectorComponents1] = field(
        default=None,
        metadata={
            "imas_type": "core_profiles_vector_components_1",
            "field_type": CoreProfilesVectorComponents1,
        },
    )
    phi_potential: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    rotation_frequency_tor_sonic: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    q: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    magnetic_shear: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../grid/rho_tor_norm"},
            "field_type": np.ndarray,
        },
    )
    time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class CovarianceMatrix(IdsBaseClass):
    """

    :ivar description : Description of this covariance matrix
    :ivar rows_uri : List of URIs corresponding to the rows (1st dimension) of the covariance matrix. If not all indices of a given node are used, they must be listed explicitly e.g. rows_uri(i) = pf_active:1/coil(i) will refer to a list of indices of the occurrence 1 of the pf_active IDS of this data entry. If the rows correspond to all indices of a given vector it is sufficient to give a single URI where this vector is denoted using the (:) implicit notation, e.g. rows_uri(1) = /grid_ggd(3)/grid_subset(2)/elements(:).
    :ivar data : Covariance matrix
    """

    class Meta:
        name = "covariance_matrix"
        is_root_ids = False

    description: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    rows_uri: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=str),
        metadata={
            "imas_type": "STR_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    data: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../rows_uri",
                "coordinate2": "../rows_uri",
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
class CoreProfilesGlobalQuantitiesIon(IdsBaseClass):
    """

    :ivar t_i_volume_average : Volume averaged temperature of this ion species (averaged over the plasma volume up to the LCFS)
    :ivar n_i_volume_average : Volume averaged density of this ion species (averaged over the plasma volume up to the LCFS)
    """

    class Meta:
        name = "core_profiles_global_quantities_ion"
        is_root_ids = False

    t_i_volume_average: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "/time"},
            "field_type": np.ndarray,
        },
    )
    n_i_volume_average: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "/time"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class CoreProfilesGlobalQuantities(IdsBaseClass):
    """

    :ivar ip : Total plasma current (toroidal component). Positive sign means anti-clockwise when viewed from above.
    :ivar current_non_inductive : Total non-inductive current (toroidal component). Positive sign means anti-clockwise when viewed from above.
    :ivar current_bootstrap : Bootstrap current (toroidal component). Positive sign means anti-clockwise when viewed from above.
    :ivar v_loop : LCFS loop voltage (positive value drives positive ohmic current that flows anti-clockwise when viewed from above)
    :ivar li_3 : Internal inductance. The li_3 definition is used, i.e. li_3 = 2/R0/mu0^2/Ip^2 * int(Bp^2 dV).
    :ivar beta_tor : Toroidal beta, defined as the volume-averaged total perpendicular pressure divided by (B0^2/(2*mu0)), i.e. beta_toroidal = 2 mu0 int(p dV) / V / B0^2
    :ivar beta_tor_norm : Normalized toroidal beta, defined as 100 * beta_tor * a[m] * B0 [T] / ip [MA]
    :ivar beta_pol : Poloidal beta. Defined as betap = 4 int(p dV) / [R_0 * mu_0 * Ip^2]
    :ivar energy_diamagnetic : Plasma energy content = 3/2 * integral over the plasma volume of the total perpendicular pressure
    :ivar z_eff_resistive : Volume average plasma effective charge, estimated from the flux consumption in the ohmic phase
    :ivar t_e_peaking : Electron temperature peaking factor, defined as the Te value at the magnetic axis divided by the volume averaged Te (average over the plasma volume up to the LCFS)
    :ivar t_i_average_peaking : Ion temperature (averaged over ion species and states) peaking factor, defined as the Ti value at the magnetic axis divided by the volume averaged Ti (average over the plasma volume up to the LCFS)
    :ivar resistive_psi_losses : Resistive part of the poloidal flux losses, defined as the volume-averaged scalar product of the electric field and the ohmic current density, normalized by the plasma current and integrated in time from the beginning of the plasma discharge: int ( (int(E_field_tor.j_ohm_tor) dV) / Ip ) dt)
    :ivar ejima : Ejima coefficient : resistive psi losses divided by (mu0*R*Ip). See S. Ejima et al, Nuclear Fusion, Vol.22, No.10 (1982), 1313
    :ivar t_e_volume_average : Volume averaged electron temperature (average over the plasma volume up to the LCFS)
    :ivar n_e_volume_average : Volume averaged electron density (average over the plasma volume up to the LCFS)
    :ivar ion : Quantities related to the different ion species, in the sense of isonuclear or isomolecular sequences. The set of ion species of this array must be the same as the one defined in profiles_1d/ion, at the time slice indicated in ion_time_slice
    :ivar ion_time_slice : Time slice of the profiles_1d array used to define the ion composition of the global_quantities/ion array.
    """

    class Meta:
        name = "core_profiles_global_quantities"
        is_root_ids = False

    ip: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time"},
            "field_type": np.ndarray,
        },
    )
    current_non_inductive: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time"},
            "field_type": np.ndarray,
        },
    )
    current_bootstrap: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time"},
            "field_type": np.ndarray,
        },
    )
    v_loop: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time"},
            "field_type": np.ndarray,
        },
    )
    li_3: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time"},
            "field_type": np.ndarray,
        },
    )
    beta_tor: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time"},
            "field_type": np.ndarray,
        },
    )
    beta_tor_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time"},
            "field_type": np.ndarray,
        },
    )
    beta_pol: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time"},
            "field_type": np.ndarray,
        },
    )
    energy_diamagnetic: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time"},
            "field_type": np.ndarray,
        },
    )
    z_eff_resistive: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time"},
            "field_type": np.ndarray,
        },
    )
    t_e_peaking: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time"},
            "field_type": np.ndarray,
        },
    )
    t_i_average_peaking: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time"},
            "field_type": np.ndarray,
        },
    )
    resistive_psi_losses: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time"},
            "field_type": np.ndarray,
        },
    )
    ejima: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time"},
            "field_type": np.ndarray,
        },
    )
    t_e_volume_average: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time"},
            "field_type": np.ndarray,
        },
    )
    n_e_volume_average: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time"},
            "field_type": np.ndarray,
        },
    )
    ion: Optional[CoreProfilesGlobalQuantitiesIon] = field(
        default_factory=lambda: StructArray(
            type_input=CoreProfilesGlobalQuantitiesIon
        ),
        metadata={
            "imas_type": "core_profiles_global_quantities_ion",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../profiles_1d(itime)/ion"},
            "field_type": CoreProfilesGlobalQuantitiesIon,
        },
    )
    ion_time_slice: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class CoreProfiles2DVectorComponents2(IdsBaseClass):
    """

    :ivar radial : Radial component
    :ivar diamagnetic : Diamagnetic component
    :ivar parallel : Parallel component
    :ivar poloidal : Poloidal component
    :ivar toroidal : Toroidal component
    """

    class Meta:
        name = "core_profiles_2d_vector_components_2"
        is_root_ids = False

    radial: Optional[np.ndarray] = field(
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
    diamagnetic: Optional[np.ndarray] = field(
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
    parallel: Optional[np.ndarray] = field(
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
    poloidal: Optional[np.ndarray] = field(
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
    toroidal: Optional[np.ndarray] = field(
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


@idspy_dataclass(repr=False, slots=True)
class CoreProfiles2DIonsStates(IdsBaseClass):
    """

    :ivar z_min : Minimum Z of the charge state bundle
    :ivar z_max : Maximum Z of the charge state bundle (equal to z_min if no bundle)
    :ivar z_average : Average Z of the charge state bundle, volume averaged over the plasma radius (equal to z_min if no bundle), = sum (Z*x_z) where x_z is the relative concentration of a given charge state in the bundle, i.e. sum(x_z) = 1 over the bundle.
    :ivar z_square_average : Average Z square of the charge state bundle, volume averaged over the plasma radius (equal to z_min squared if no bundle), = sum (Z^2*x_z) where x_z is the relative concentration of a given charge state in the bundle, i.e. sum(x_z) = 1 over the bundle.
    :ivar ionization_potential : Cumulative and average ionization potential to reach a given bundle. Defined as sum (x_z* (sum of Epot from z&#39;=0 to z-1)), where Epot is the ionization potential of ion Xz’+, and x_z is the relative concentration of a given charge state in the bundle, i.e. sum(x_z) = 1 over the bundle.
    :ivar name : String identifying state (e.g. C+, C+2 , C+3, C+4, C+5, C+6, ...)
    :ivar electron_configuration : Configuration of atomic orbitals of this state, e.g. 1s2-2s1
    :ivar vibrational_level : Vibrational level (can be bundled)
    :ivar vibrational_mode : Vibrational mode of this state, e.g. &#34;A_g&#34;. Need to define, or adopt a standard nomenclature.
    :ivar rotation_frequency_tor : Toroidal rotation frequency (i.e. toroidal velocity divided by the major radius at which the toroidal velocity is taken)
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
        name = "core_profiles_2d_ions_states"
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
    temperature: Optional[np.ndarray] = field(
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
    density: Optional[np.ndarray] = field(
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
    density_thermal: Optional[np.ndarray] = field(
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
    density_fast: Optional[np.ndarray] = field(
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
    pressure: Optional[np.ndarray] = field(
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
    pressure_thermal: Optional[np.ndarray] = field(
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
    pressure_fast_perpendicular: Optional[np.ndarray] = field(
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
    pressure_fast_parallel: Optional[np.ndarray] = field(
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


@idspy_dataclass(repr=False, slots=True)
class CoreProfile2DIons(IdsBaseClass):
    """

    :ivar element : List of elements forming the atom or molecule
    :ivar z_ion : Ion charge (of the dominant ionization state; lumped ions are allowed), volume averaged over plasma radius
    :ivar name : String identifying ion (e.g. H, D, T, He, C, D2, ...)
    :ivar ion_index : Index of the corresponding ion species in the ../../../profiles_1d/ion array
    :ivar temperature : Temperature (average over charge states when multiple charge states are considered)
    :ivar density : Density (thermal+non-thermal) (sum over charge states when multiple charge states are considered)
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
        name = "core_profile_2d_ions"
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
    ion_index: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    temperature: Optional[np.ndarray] = field(
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
    density: Optional[np.ndarray] = field(
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
    density_thermal: Optional[np.ndarray] = field(
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
    density_fast: Optional[np.ndarray] = field(
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
    pressure: Optional[np.ndarray] = field(
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
    pressure_thermal: Optional[np.ndarray] = field(
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
    pressure_fast_perpendicular: Optional[np.ndarray] = field(
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
    pressure_fast_parallel: Optional[np.ndarray] = field(
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
    rotation_frequency_tor: Optional[np.ndarray] = field(
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
    velocity: Optional[CoreProfiles2DVectorComponents2] = field(
        default=None,
        metadata={
            "imas_type": "core_profiles_2d_vector_components_2",
            "field_type": CoreProfiles2DVectorComponents2,
        },
    )
    multiple_states_flag: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    state: Optional[CoreProfiles2DIonsStates] = field(
        default_factory=lambda: StructArray(
            type_input=CoreProfiles2DIonsStates
        ),
        metadata={
            "imas_type": "core_profiles_2d_ions_states",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": CoreProfiles2DIonsStates,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class CoreProfilesProfiles2D(IdsBaseClass):
    """

    :ivar grid_type : Selection of one of a set of grid types
    :ivar grid : Definition of the 2D grid (the content of dim1 and dim2 is defined by the selected grid_type)
    :ivar ion : 2D quantities related to the different ion species, in the sense of isonuclear or isomolecular sequences. Ionization states (or other types of states) must be differentiated at the state level below. This array doesn&#39;t necessarily have the same size as the profiles_1d/ion array, since 2D data may be relevant only for a subset of ion species.
    :ivar t_i_average : Ion temperature (averaged on states and ion species)
    :ivar n_i_total_over_n_e : Ratio of total ion density (sum over species and charge states) over electron density. (thermal+non-thermal)
    :ivar n_i_thermal_total : Total ion thermal density (sum over species and charge states)
    :ivar momentum_phi : Total plasma toroidal momentum, summed over ion species and electrons weighted by their density and major radius, i.e. sum_over_species(n*R*m*Vphi)
    :ivar zeff : Effective charge
    :ivar pressure_ion_total : Total (sum over ion species) thermal ion pressure
    :ivar pressure_thermal : Thermal pressure (electrons+ions)
    :ivar pressure_perpendicular : Total perpendicular pressure (electrons+ions, thermal+non-thermal)
    :ivar pressure_parallel : Total parallel pressure (electrons+ions, thermal+non-thermal)
    :ivar time : Time
    """

    class Meta:
        name = "core_profiles_profiles_2d"
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
    ion: Optional[CoreProfile2DIons] = field(
        default_factory=lambda: StructArray(type_input=CoreProfile2DIons),
        metadata={
            "imas_type": "core_profile_2d_ions",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": CoreProfile2DIons,
        },
    )
    t_i_average: Optional[np.ndarray] = field(
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
    n_i_total_over_n_e: Optional[np.ndarray] = field(
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
    n_i_thermal_total: Optional[np.ndarray] = field(
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
    momentum_phi: Optional[np.ndarray] = field(
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
    zeff: Optional[np.ndarray] = field(
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
    pressure_ion_total: Optional[np.ndarray] = field(
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
    pressure_thermal: Optional[np.ndarray] = field(
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
    pressure_perpendicular: Optional[np.ndarray] = field(
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
    pressure_parallel: Optional[np.ndarray] = field(
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
    time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class CoreProfiles(IdsBaseClass):
    """

    :ivar ids_properties :
    :ivar profiles_1d : Core plasma radial profiles for various time slices
    :ivar profiles_2d : Core plasma quantities in a poloidal cross section, for various time slices
    :ivar global_quantities : Various global quantities derived from the profiles
    :ivar vacuum_toroidal_field : Characteristics of the vacuum toroidal field (used in rho_tor definition and in the normalization of current densities)
    :ivar covariance : User defined covariance matrix. The covariance of various quantities can be stored here, these quantities are referred to by giving their IDS path in the rows_uri list
    :ivar statistics : Statistics for various time slices
    :ivar code :
    :ivar time : Generic time
    """

    class Meta:
        name = "core_profiles"
        is_root_ids = True

    ids_properties: Optional[IdsProperties] = field(
        default=None,
        metadata={"imas_type": "ids_properties", "field_type": IdsProperties},
    )
    profiles_1d: Optional[CoreProfilesProfiles1D] = field(
        default_factory=lambda: StructArray(type_input=CoreProfilesProfiles1D),
        metadata={
            "imas_type": "core_profiles_profiles_1d",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": CoreProfilesProfiles1D,
        },
    )
    profiles_2d: Optional[CoreProfilesProfiles2D] = field(
        default_factory=lambda: StructArray(type_input=CoreProfilesProfiles2D),
        metadata={
            "imas_type": "core_profiles_profiles_2d",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": CoreProfilesProfiles2D,
        },
    )
    global_quantities: Optional[CoreProfilesGlobalQuantities] = field(
        default=None,
        metadata={
            "imas_type": "core_profiles_global_quantities",
            "field_type": CoreProfilesGlobalQuantities,
        },
    )
    vacuum_toroidal_field: Optional[BTorVacuum1] = field(
        default=None,
        metadata={"imas_type": "b_tor_vacuum_1", "field_type": BTorVacuum1},
    )
    covariance: Optional[CovarianceMatrix] = field(
        default=None,
        metadata={
            "imas_type": "covariance_matrix",
            "field_type": CovarianceMatrix,
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
