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
class CodeConstant(IdsBaseClass):
    """

    :ivar name : Name of software used
    :ivar description : Short description of the software (type, purpose)
    :ivar commit : Unique commit reference of software
    :ivar version : Unique version (tag) of software
    :ivar repository : URL of software repository
    :ivar parameters : List of the code specific parameters in XML format
    :ivar library : List of external libraries used by the code that has produced this IDS
    """

    class Meta:
        name = "code_constant"
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
class AmnsDataDataEntry(IdsBaseClass):
    """

    :ivar description : Description of this data entry
    :ivar shot : Shot number = Mass*1000+Nuclear_charge
    :ivar run : Which run number is the active run number for this version
    """

    class Meta:
        name = "amns_data_data_entry"
        is_root_ids = False

    description: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    shot: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    run: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )


@idspy_dataclass(repr=False, slots=True)
class AmnsDataRelease(IdsBaseClass):
    """

    :ivar description : Description of this release
    :ivar date : Date of this release
    :ivar data_entry : For this release, list of each data item (i.e. shot/run pair containing the actual data) included in this release
    """

    class Meta:
        name = "amns_data_release"
        is_root_ids = False

    description: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    date: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    data_entry: Optional[AmnsDataDataEntry] = field(
        default_factory=lambda: StructArray(type_input=AmnsDataDataEntry),
        metadata={
            "imas_type": "amns_data_data_entry",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": AmnsDataDataEntry,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class AmnsDataProcessReactant(IdsBaseClass):
    """

    :ivar name : String identifying reaction participant (e.g. &#34;D&#34;, &#34;e&#34;, &#34;W&#34;, &#34;CD4&#34;, &#34;photon&#34;, &#34;n&#34;)
    :ivar element : List of elements forming the atom (in such case, this array should be of size 1) or molecule. Mass of atom and nuclear charge should be set to 0 for photons and electrons. The mass of atom shouldn&#39;t be set for an atomic process that is not isotope dependent.
    :ivar mass : Mass of the participant
    :ivar charge : Charge number of the participant
    :ivar relative_charge : This is a flag indicating that charges are absolute (if set to 0), relative (if 1) or irrelevant (-1); relative would be used to categorize the ionization reactions from i to i+1 for all charge states; in the case of bundles, the +1 relative indicates the next bundle
    :ivar multiplicity : Multiplicity in the reaction
    :ivar metastable : An array identifying the metastable; if zero-length, then not a metastable; if of length 1, then the value indicates the electronic level for the metastable (mostly used for atoms/ions); if of length 2, then the 1st would indicate the electronic level and the second the vibrational level for the metastable (mostly used for molecules and molecular ions); if of length 3, then the 1st would indicate the electronic level, the second the vibrational level and the third the rotational level for the metastable (mostly used for molecules and molecular ions)
    :ivar metastable_label : Label identifying in text form the metastable
    """

    class Meta:
        name = "amns_data_process_reactant"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
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
    mass: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    charge: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    relative_charge: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    multiplicity: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    metastable: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=int),
        metadata={
            "imas_type": "INT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    metastable_label: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )


@idspy_dataclass(repr=False, slots=True)
class AmnsDataProcessChargeState(IdsBaseClass):
    """

    :ivar name : String identifying charge state (e.g. C+, C+2 , C+3, C+4, C+5, C+6, ...)
    :ivar z_min : Minimum Z of the charge state bundle
    :ivar z_max : Maximum Z of the charge state bundle (equal to z_min if no bundle)
    :ivar table_0d : 0D table describing the process data
    :ivar table_1d : 1D table describing the process data
    :ivar table_2d : 2D table describing the process data
    :ivar table_3d : 3D table describing the process data
    :ivar table_4d : 4D table describing the process data
    :ivar table_5d : 5D table describing the process data
    :ivar table_6d : 6D table describing the process data
    """

    class Meta:
        name = "amns_data_process_charge_state"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    z_min: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    z_max: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    table_0d: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    table_1d: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    table_2d: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {"coordinate1": "1...N", "coordinate2": "1...N"},
            "field_type": np.ndarray,
        },
    )
    table_3d: Optional[np.ndarray] = field(
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
    table_4d: Optional[np.ndarray] = field(
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
    table_5d: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 5, dtype=float),
        metadata={
            "imas_type": "FLT_5D",
            "ndims": 5,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate2": "1...N",
                "coordinate3": "1...N",
                "coordinate4": "1...N",
                "coordinate5": "1...N",
            },
            "field_type": np.ndarray,
        },
    )
    table_6d: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 6, dtype=float),
        metadata={
            "imas_type": "FLT_6D",
            "ndims": 6,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate2": "1...N",
                "coordinate3": "1...N",
                "coordinate4": "1...N",
                "coordinate5": "1...N",
                "coordinate6": "1...N",
            },
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class AmnsDataProcess(IdsBaseClass):
    """

    :ivar source : Filename or subroutine name used to provide this data
    :ivar provider : Name of the person in charge of producing this data
    :ivar citation : Reference to publication(s)
    :ivar name : String identifying the process (e.g. EI, RC, ...)
    :ivar reactants : Set of reactants involved in this process
    :ivar products : Set of products resulting of this process
    :ivar table_dimension : Table dimensionality of the process (1 to 6), valid for all charge states. Indicates which of the tables is filled (below the charge_state node)
    :ivar coordinate_index : Index in tables_coord, specifying what coordinate systems to use for this process (valid for all tables)
    :ivar result_label : Description of the process result (rate, cross section, sputtering yield, ...)
    :ivar result_units : Units of the process result
    :ivar result_transformation : Transformation of the process result. Integer flag: 0=no transformation; 1=10^; 2=exp()
    :ivar charge_state : Process tables for a set of charge states. Only one table is used for that process, defined by process(:)/table_dimension. If the data in the table_Nd array are used as parameters for a function, then no coordinates are needed, and coordinate_index should be set to -1, and result_transformation should contain the integer identifier to the internally provided functions. If the results will come from an interpolation in the table_Nd data, then coordinates must be provided in coordinate_system(process(i1)/coordinate_index), and the shape of the table should match the cartesian product of the coordinates
    """

    class Meta:
        name = "amns_data_process"
        is_root_ids = False

    source: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    provider: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    citation: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    reactants: Optional[AmnsDataProcessReactant] = field(
        default_factory=lambda: StructArray(type_input=AmnsDataProcessReactant),
        metadata={
            "imas_type": "amns_data_process_reactant",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": AmnsDataProcessReactant,
        },
    )
    products: Optional[AmnsDataProcessReactant] = field(
        default_factory=lambda: StructArray(type_input=AmnsDataProcessReactant),
        metadata={
            "imas_type": "amns_data_process_reactant",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": AmnsDataProcessReactant,
        },
    )
    table_dimension: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    coordinate_index: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    result_label: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    result_units: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    result_transformation: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    charge_state: Optional[AmnsDataProcessChargeState] = field(
        default_factory=lambda: StructArray(
            type_input=AmnsDataProcessChargeState
        ),
        metadata={
            "imas_type": "amns_data_process_charge_state",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": AmnsDataProcessChargeState,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class AmnsDataCoordinateSystemCoordinate(IdsBaseClass):
    """

    :ivar name : Name of coordinate (e.g. &#34;Electron temperature&#34;)
    :ivar values : Coordinate values
    :ivar interpolation_type : Interpolation strategy in this coordinate direction. Integer flag: 0=discrete (no interpolation); 1=linear; ...
    :ivar extrapolation_type : Extrapolation strategy when leaving the domain. The first value of the vector describes the behaviour at lower bound, the second describes the at upper bound. Possible values: 0=none, report error; 1=boundary value; 2=linear extrapolation
    :ivar value_labels : String description of discrete coordinate values (if interpolation_type=0). E.g., for spectroscopic lines, the spectroscopic description of the transition.
    :ivar units : Units of coordinate (e.g. eV)
    :ivar transformation : Coordinate transformation applied to coordinate values stored in coord. Integer flag: 0=none; 1=log10; 2=ln
    :ivar spacing : Flag for specific coordinate spacing (for optimization purposes). Integer flag: 0=undefined; 1=uniform; ...
    """

    class Meta:
        name = "amns_data_coordinate_system_coordinate"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
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
    interpolation_type: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    extrapolation_type: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=int),
        metadata={
            "imas_type": "INT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...2"},
            "field_type": np.ndarray,
        },
    )
    value_labels: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=str),
        metadata={
            "imas_type": "STR_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../values"},
            "field_type": np.ndarray,
        },
    )
    units: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    transformation: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    spacing: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )


@idspy_dataclass(repr=False, slots=True)
class AmnsDataCoordinateSystem(IdsBaseClass):
    """

    :ivar coordinate : Set of coordinates for that coordinate system. A coordinate an be either a range of real values or a set of discrete values (if interpolation_type=0)
    """

    class Meta:
        name = "amns_data_coordinate_system"
        is_root_ids = False

    coordinate: Optional[AmnsDataCoordinateSystemCoordinate] = field(
        default_factory=lambda: StructArray(
            type_input=AmnsDataCoordinateSystemCoordinate
        ),
        metadata={
            "imas_type": "amns_data_coordinate_system_coordinate",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": AmnsDataCoordinateSystemCoordinate,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class AmnsData(IdsBaseClass):
    """

    :ivar ids_properties :
    :ivar z_n : Nuclear charge
    :ivar a : Mass of atom
    :ivar process : Description and data for a set of physical processes.
    :ivar coordinate_system : Array of possible coordinate systems for process tables
    :ivar release : List of available releases of the AMNS data; each element contains information about the AMNS data that is included in the release. This part of the IDS is filled and stored only into shot/run=0/1, playing the role of a catalogue.
    :ivar code : Generic decription of the code-specific parameters for the code that has produced this IDS
    """

    class Meta:
        name = "amns_data"
        is_root_ids = True

    ids_properties: Optional[IdsProperties] = field(
        default=None,
        metadata={"imas_type": "ids_properties", "field_type": IdsProperties},
    )
    z_n: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    a: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    process: Optional[AmnsDataProcess] = field(
        default_factory=lambda: StructArray(type_input=AmnsDataProcess),
        metadata={
            "imas_type": "amns_data_process",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": AmnsDataProcess,
        },
    )
    coordinate_system: Optional[AmnsDataCoordinateSystem] = field(
        default_factory=lambda: StructArray(
            type_input=AmnsDataCoordinateSystem
        ),
        metadata={
            "imas_type": "amns_data_coordinate_system",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": AmnsDataCoordinateSystem,
        },
    )
    release: Optional[AmnsDataRelease] = field(
        default_factory=lambda: StructArray(type_input=AmnsDataRelease),
        metadata={
            "imas_type": "amns_data_release",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": AmnsDataRelease,
        },
    )
    code: Optional[CodeConstant] = field(
        default=None,
        metadata={"imas_type": "code_constant", "field_type": CodeConstant},
    )
