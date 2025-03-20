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
class EntryTag(IdsBaseClass):
    """

    :ivar name : Name of the tag
    :ivar comment : Any comment describing the content of the tagged list of entries
    """

    class Meta:
        name = "entry_tag"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    comment: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
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
class SummaryDynamicFlt1DRootParent2(IdsBaseClass):
    """

    :ivar value : Value
    :ivar source : Source of the data (any comment describing the origin of the data : code, path to diagnostic signals, processing method, ...)
    """

    class Meta:
        name = "summary_dynamic_flt_1d_root_parent_2"
        is_root_ids = False

    value: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "/time"},
            "field_type": np.ndarray,
        },
    )
    source: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryDynamicFlt2DFraction2(IdsBaseClass):
    """

    :ivar value : Value
    :ivar source : Source of the data (any comment describing the origin of the data : code, path to diagnostic signals, processing method, ...)
    """

    class Meta:
        name = "summary_dynamic_flt_2d_fraction_2"
        is_root_ids = False

    value: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {"coordinate1": "1...3", "coordinate2": "/time"},
            "field_type": np.ndarray,
        },
    )
    source: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryDynamicFlt1DRoot(IdsBaseClass):
    """

    :ivar value : Value
    :ivar source : Source of the data (any comment describing the origin of the data : code, path to diagnostic signals, processing method, ...)
    """

    class Meta:
        name = "summary_dynamic_flt_1d_root"
        is_root_ids = False

    value: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "/time"},
            "field_type": np.ndarray,
        },
    )
    source: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryStaticFlt0D(IdsBaseClass):
    """

    :ivar value : Value
    :ivar source : Source of the data (any comment describing the origin of the data : code, path to diagnostic signals, processing method, ...)
    """

    class Meta:
        name = "summary_static_flt_0d"
        is_root_ids = False

    value: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    source: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryStaticInt0D(IdsBaseClass):
    """

    :ivar value : Value
    :ivar source : Source of the data (any comment describing the origin of the data : code, path to diagnostic signals, processing method, ...)
    """

    class Meta:
        name = "summary_static_int_0d"
        is_root_ids = False

    value: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    source: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryStaticStr0D(IdsBaseClass):
    """

    :ivar value : Value
    :ivar source : Source of the data (any comment describing the origin of the data : code, path to diagnostic signals, processing method, ...)
    """

    class Meta:
        name = "summary_static_str_0d"
        is_root_ids = False

    value: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    source: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryConstantInt0D(IdsBaseClass):
    """

    :ivar value : Value
    :ivar source : Source of the data (any comment describing the origin of the data : code, path to diagnostic signals, processing method, ...)
    """

    class Meta:
        name = "summary_constant_int_0d"
        is_root_ids = False

    value: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    source: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryConstantFlt0D(IdsBaseClass):
    """

    :ivar value : Value
    :ivar source : Source of the data (any comment describing the origin of the data : code, path to diagnostic signals, processing method, ...)
    """

    class Meta:
        name = "summary_constant_flt_0d"
        is_root_ids = False

    value: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    source: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryConstantFlt0D2(IdsBaseClass):
    """

    :ivar value : Value
    :ivar source : Source of the data (any comment describing the origin of the data : code, path to diagnostic signals, processing method, ...)
    """

    class Meta:
        name = "summary_constant_flt_0d_2"
        is_root_ids = False

    value: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    source: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryConstantStr0D(IdsBaseClass):
    """

    :ivar value : Value
    :ivar source : Source of the data (any comment describing the origin of the data : code, path to diagnostic signals, processing method, ...)
    """

    class Meta:
        name = "summary_constant_str_0d"
        is_root_ids = False

    value: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    source: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryRphiz0DStatic(IdsBaseClass):
    """

    :ivar r : Major radius
    :ivar z : Height
    :ivar phi : Toroidal angle
    """

    class Meta:
        name = "summary_rphiz0d_static"
        is_root_ids = False

    r: Optional[SummaryStaticFlt0D] = field(
        default=None,
        metadata={
            "imas_type": "summary_static_flt_0d",
            "field_type": SummaryStaticFlt0D,
        },
    )
    z: Optional[SummaryStaticFlt0D] = field(
        default=None,
        metadata={
            "imas_type": "summary_static_flt_0d",
            "field_type": SummaryStaticFlt0D,
        },
    )
    phi: Optional[SummaryStaticFlt0D] = field(
        default=None,
        metadata={
            "imas_type": "summary_static_flt_0d",
            "field_type": SummaryStaticFlt0D,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryRz1DDynamic(IdsBaseClass):
    """

    :ivar r : Major radius
    :ivar z : Height
    :ivar source : Source of the data (any comment describing the origin of the data : code, path to diagnostic signals, processing method, ...)
    """

    class Meta:
        name = "summary_rz1d_dynamic"
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
    source: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryDynamicInt1DRoot(IdsBaseClass):
    """

    :ivar value : Value
    :ivar source : Source of the data (any comment describing the origin of the data : code, path to diagnostic signals, processing method, ...)
    """

    class Meta:
        name = "summary_dynamic_int_1d_root"
        is_root_ids = False

    value: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=int),
        metadata={
            "imas_type": "INT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "/time"},
            "field_type": np.ndarray,
        },
    )
    source: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )


@idspy_dataclass(repr=False, slots=True)
class SummarySpeciesTorAngle(IdsBaseClass):
    """

    :ivar hydrogen : Hydrogen (H)
    :ivar deuterium : Deuterium (D)
    :ivar tritium : Tritium (T)
    :ivar helium_3 : Helium isotope with 3 nucleons (3He)
    :ivar helium_4 : Helium isotope with 4 nucleons (4He)
    :ivar beryllium : Beryllium (Be)
    :ivar lithium : Lithium (Li)
    :ivar carbon : Carbon (C)
    :ivar nitrogen : Nitrogen (N)
    :ivar neon : Neon (Ne)
    :ivar argon : Argon (Ar)
    :ivar xenon : Xenon (Xe)
    :ivar oxygen : Oxygen (O)
    :ivar tungsten : Tungsten (W)
    :ivar iron : Iron (Fe)
    :ivar krypton : Krypton (Kr)
    """

    class Meta:
        name = "summary_species_tor_angle"
        is_root_ids = False

    hydrogen: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    deuterium: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    tritium: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    helium_3: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    helium_4: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    beryllium: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    lithium: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    carbon: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    nitrogen: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    neon: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    argon: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    xenon: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    oxygen: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    tungsten: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    iron: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    krypton: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SummarySpecies(IdsBaseClass):
    """

    :ivar hydrogen : Hydrogen (H)
    :ivar deuterium : Deuterium (D)
    :ivar tritium : Tritium (T)
    :ivar helium_3 : Helium isotope with 3 nucleons (3He)
    :ivar helium_4 : Helium isotope with 4 nucleons (4He)
    :ivar beryllium : Beryllium (Be)
    :ivar boron : Boron (B)
    :ivar lithium : Lithium (Li)
    :ivar carbon : Carbon (C)
    :ivar nitrogen : Nitrogen (N)
    :ivar neon : Neon (Ne)
    :ivar argon : Argon (Ar)
    :ivar xenon : Xenon (Xe)
    :ivar oxygen : Oxygen (O)
    :ivar tungsten : Tungsten (W)
    :ivar iron : Iron (Fe)
    :ivar krypton : Krypton (Kr)
    """

    class Meta:
        name = "summary_species"
        is_root_ids = False

    hydrogen: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    deuterium: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    tritium: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    helium_3: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    helium_4: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    beryllium: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    boron: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    lithium: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    carbon: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    nitrogen: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    neon: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    argon: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    xenon: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    oxygen: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    tungsten: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    iron: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    krypton: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryGasInjectionAccumulated(IdsBaseClass):
    """

    :ivar total : Total accumulated injected gas (sum over species)
    :ivar midplane : Accumulated gas injected from all valves located near the equatorial midplane
    :ivar top : Accumulated gas injected from all valves located near the top of the vacuum chamber
    :ivar bottom : Accumulated gas injected from all valves located near near the bottom of the vacuum chamber
    :ivar hydrogen : Hydrogen
    :ivar deuterium : Deuterium
    :ivar tritium : Tritium
    :ivar helium_3 : Helium isotope with 3 nucleons
    :ivar helium_4 : Helium isotope with 4 nucleons
    :ivar impurity_seeding : Flag set to 1 if any gas other than H, D, T, He is puffed during the pulse, 0 otherwise
    :ivar beryllium : Beryllium
    :ivar lithium : Lithium
    :ivar carbon : Carbon
    :ivar oxygen : Oxygen
    :ivar nitrogen : Nitrogen
    :ivar neon : Neon
    :ivar argon : Argon
    :ivar xenon : Xenon
    :ivar krypton : Krypton
    :ivar methane : Methane (CH4)
    :ivar methane_carbon_13 : Methane (CH4 with carbon 13)
    :ivar methane_deuterated : Deuterated methane (CD4)
    :ivar silane : Silane (SiH4)
    :ivar ethylene : Ethylene (C2H4)
    :ivar ethane : Ethane (C2H6)
    :ivar propane : Propane (C3H8)
    :ivar ammonia : Ammonia (NH3)
    :ivar ammonia_deuterated : Deuterated ammonia (ND3)
    """

    class Meta:
        name = "summary_gas_injection_accumulated"
        is_root_ids = False

    total: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    midplane: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    top: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    bottom: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    hydrogen: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    deuterium: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    tritium: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    helium_3: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    helium_4: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    impurity_seeding: Optional[SummaryConstantInt0D] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_int_0d",
            "field_type": SummaryConstantInt0D,
        },
    )
    beryllium: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    lithium: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    carbon: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    oxygen: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    nitrogen: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    neon: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    argon: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    xenon: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    krypton: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    methane: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    methane_carbon_13: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    methane_deuterated: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    silane: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    ethylene: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    ethane: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    propane: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    ammonia: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    ammonia_deuterated: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryGasInjectionPrefill(IdsBaseClass):
    """

    :ivar total : Total accumulated injected gas (sum over species)
    :ivar midplane : Accumulated gas injected from all valves located near the equatorial midplane
    :ivar top : Accumulated gas injected from all valves located near the top of the vacuum chamber
    :ivar bottom : Accumulated gas injected from all valves located near near the bottom of the vacuum chamber
    :ivar hydrogen : Hydrogen
    :ivar deuterium : Deuterium
    :ivar tritium : Tritium
    :ivar helium_3 : Helium isotope with 3 nucleons
    :ivar helium_4 : Helium isotope with 4 nucleons
    :ivar impurity_seeding : Flag set to 1 if any gas other than H, D, T, He is puffed during the prefill, 0 otherwise
    :ivar beryllium : Beryllium
    :ivar lithium : Lithium
    :ivar carbon : Carbon
    :ivar oxygen : Oxygen
    :ivar nitrogen : Nitrogen
    :ivar neon : Neon
    :ivar argon : Argon
    :ivar xenon : Xenon
    :ivar krypton : Krypton
    :ivar methane : Methane (CH4)
    :ivar methane_carbon_13 : Methane (CH4 with carbon 13)
    :ivar methane_deuterated : Deuterated methane (CD4)
    :ivar silane : Silane (SiH4)
    :ivar ethylene : Ethylene (C2H4)
    :ivar ethane : Ethane (C2H6)
    :ivar propane : Propane (C3H8)
    :ivar ammonia : Ammonia (NH3)
    :ivar ammonia_deuterated : Deuterated ammonia (ND3)
    """

    class Meta:
        name = "summary_gas_injection_prefill"
        is_root_ids = False

    total: Optional[SummaryConstantFlt0D2] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_flt_0d_2",
            "field_type": SummaryConstantFlt0D2,
        },
    )
    midplane: Optional[SummaryConstantFlt0D2] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_flt_0d_2",
            "field_type": SummaryConstantFlt0D2,
        },
    )
    top: Optional[SummaryConstantFlt0D2] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_flt_0d_2",
            "field_type": SummaryConstantFlt0D2,
        },
    )
    bottom: Optional[SummaryConstantFlt0D2] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_flt_0d_2",
            "field_type": SummaryConstantFlt0D2,
        },
    )
    hydrogen: Optional[SummaryConstantFlt0D2] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_flt_0d_2",
            "field_type": SummaryConstantFlt0D2,
        },
    )
    deuterium: Optional[SummaryConstantFlt0D2] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_flt_0d_2",
            "field_type": SummaryConstantFlt0D2,
        },
    )
    tritium: Optional[SummaryConstantFlt0D2] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_flt_0d_2",
            "field_type": SummaryConstantFlt0D2,
        },
    )
    helium_3: Optional[SummaryConstantFlt0D2] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_flt_0d_2",
            "field_type": SummaryConstantFlt0D2,
        },
    )
    helium_4: Optional[SummaryConstantFlt0D2] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_flt_0d_2",
            "field_type": SummaryConstantFlt0D2,
        },
    )
    impurity_seeding: Optional[SummaryConstantInt0D] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_int_0d",
            "field_type": SummaryConstantInt0D,
        },
    )
    beryllium: Optional[SummaryConstantFlt0D2] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_flt_0d_2",
            "field_type": SummaryConstantFlt0D2,
        },
    )
    lithium: Optional[SummaryConstantFlt0D2] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_flt_0d_2",
            "field_type": SummaryConstantFlt0D2,
        },
    )
    carbon: Optional[SummaryConstantFlt0D2] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_flt_0d_2",
            "field_type": SummaryConstantFlt0D2,
        },
    )
    oxygen: Optional[SummaryConstantFlt0D2] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_flt_0d_2",
            "field_type": SummaryConstantFlt0D2,
        },
    )
    nitrogen: Optional[SummaryConstantFlt0D2] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_flt_0d_2",
            "field_type": SummaryConstantFlt0D2,
        },
    )
    neon: Optional[SummaryConstantFlt0D2] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_flt_0d_2",
            "field_type": SummaryConstantFlt0D2,
        },
    )
    argon: Optional[SummaryConstantFlt0D2] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_flt_0d_2",
            "field_type": SummaryConstantFlt0D2,
        },
    )
    xenon: Optional[SummaryConstantFlt0D2] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_flt_0d_2",
            "field_type": SummaryConstantFlt0D2,
        },
    )
    krypton: Optional[SummaryConstantFlt0D2] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_flt_0d_2",
            "field_type": SummaryConstantFlt0D2,
        },
    )
    methane: Optional[SummaryConstantFlt0D2] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_flt_0d_2",
            "field_type": SummaryConstantFlt0D2,
        },
    )
    methane_carbon_13: Optional[SummaryConstantFlt0D2] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_flt_0d_2",
            "field_type": SummaryConstantFlt0D2,
        },
    )
    methane_deuterated: Optional[SummaryConstantFlt0D2] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_flt_0d_2",
            "field_type": SummaryConstantFlt0D2,
        },
    )
    silane: Optional[SummaryConstantFlt0D2] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_flt_0d_2",
            "field_type": SummaryConstantFlt0D2,
        },
    )
    ethylene: Optional[SummaryConstantFlt0D2] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_flt_0d_2",
            "field_type": SummaryConstantFlt0D2,
        },
    )
    ethane: Optional[SummaryConstantFlt0D2] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_flt_0d_2",
            "field_type": SummaryConstantFlt0D2,
        },
    )
    propane: Optional[SummaryConstantFlt0D] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_flt_0d",
            "field_type": SummaryConstantFlt0D,
        },
    )
    ammonia: Optional[SummaryConstantFlt0D2] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_flt_0d_2",
            "field_type": SummaryConstantFlt0D2,
        },
    )
    ammonia_deuterated: Optional[SummaryConstantFlt0D2] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_flt_0d_2",
            "field_type": SummaryConstantFlt0D2,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryGasInjection(IdsBaseClass):
    """

    :ivar total : Total gas injection rate (sum over species)
    :ivar midplane : Gas injection rate from all valves located near the equatorial midplane
    :ivar top : Gas injection rate from all valves located near the top of the vaccuum chamber
    :ivar bottom : Gas injection rate from all valves located near near the bottom of the vaccuum chamber
    :ivar hydrogen : Hydrogen
    :ivar deuterium : Deuterium
    :ivar tritium : Tritium
    :ivar helium_3 : Helium isotope with 3 nucleons
    :ivar helium_4 : Helium isotope with 4 nucleons
    :ivar impurity_seeding : Flag set to 1 if any gas other than H, D, T, He is puffed during the pulse, 0 otherwise
    :ivar beryllium : Beryllium
    :ivar lithium : Lithium
    :ivar carbon : Carbon
    :ivar oxygen : Oxygen
    :ivar nitrogen : Nitrogen
    :ivar neon : Neon
    :ivar argon : Argon
    :ivar xenon : Xenon
    :ivar krypton : Krypton
    :ivar methane : Methane (CH4)
    :ivar methane_carbon_13 : Methane (CH4 with carbon 13)
    :ivar methane_deuterated : Deuterated methane (CD4)
    :ivar silane : Silane (SiH4)
    :ivar ethylene : Ethylene (C2H4)
    :ivar ethane : Ethane (C2H6)
    :ivar propane : Propane (C3H8)
    :ivar ammonia : Ammonia (NH3)
    :ivar ammonia_deuterated : Deuterated ammonia (ND3)
    """

    class Meta:
        name = "summary_gas_injection"
        is_root_ids = False

    total: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    midplane: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    top: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    bottom: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    hydrogen: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    deuterium: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    tritium: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    helium_3: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    helium_4: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    impurity_seeding: Optional[SummaryConstantInt0D] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_int_0d",
            "field_type": SummaryConstantInt0D,
        },
    )
    beryllium: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    lithium: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    carbon: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    oxygen: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    nitrogen: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    neon: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    argon: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    xenon: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    krypton: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    methane: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    methane_carbon_13: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    methane_deuterated: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    silane: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    ethylene: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    ethane: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    propane: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    ammonia: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    ammonia_deuterated: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryPlasmaCompositionSpecies(IdsBaseClass):
    """

    :ivar a : Mass of atom
    :ivar z_n : Nuclear charge
    :ivar name : String identifying the species (e.g. H, D, T, ...)
    """

    class Meta:
        name = "summary_plasma_composition_species"
        is_root_ids = False

    a: Optional[SummaryConstantFlt0D] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_flt_0d",
            "field_type": SummaryConstantFlt0D,
        },
    )
    z_n: Optional[SummaryConstantFlt0D] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_flt_0d",
            "field_type": SummaryConstantFlt0D,
        },
    )
    name: Optional[SummaryConstantStr0D] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_str_0d",
            "field_type": SummaryConstantStr0D,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryLocalPositionRZ(IdsBaseClass):
    """

    :ivar rho_tor_norm : Normalized toroidal flux coordinate. The normalizing value for rho_tor_norm, is the toroidal flux coordinate at the equilibrium boundary (LCFS or 99.x % of the LCFS in case of a fixed boundary equilibium calculation, see time_slice/boundary/b_flux_pol_norm in the equilibrium IDS)
    :ivar rho_tor : Toroidal flux coordinate. rho_tor = sqrt(b_flux_tor/(pi*b0)) ~ sqrt(pi*r^2*b0/(pi*b0)) ~ r [m]. The toroidal field used in its definition is indicated under global_quantities/b0
    :ivar psi : Poloidal magnetic flux
    :ivar r : Major radius
    :ivar z : Height
    """

    class Meta:
        name = "summary_local_position_r_z"
        is_root_ids = False

    rho_tor_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../time"},
            "field_type": np.ndarray,
        },
    )
    rho_tor: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../time"},
            "field_type": np.ndarray,
        },
    )
    psi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../time"},
            "field_type": np.ndarray,
        },
    )
    r: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../time"},
            "field_type": np.ndarray,
        },
    )
    z: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../time"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryLocalPosition(IdsBaseClass):
    """

    :ivar rho_tor_norm : Normalized toroidal flux coordinate. The normalizing value for rho_tor_norm, is the toroidal flux coordinate at the equilibrium boundary (LCFS or 99.x % of the LCFS in case of a fixed boundary equilibium calculation, see time_slice/boundary/b_flux_pol_norm in the equilibrium IDS)
    :ivar rho_tor : Toroidal flux coordinate. rho_tor = sqrt(b_flux_tor/(pi*b0)) ~ sqrt(pi*r^2*b0/(pi*b0)) ~ r [m]. The toroidal field used in its definition is indicated under global_quantities/b0
    :ivar psi : Poloidal magnetic flux
    """

    class Meta:
        name = "summary_local_position"
        is_root_ids = False

    rho_tor_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../time"},
            "field_type": np.ndarray,
        },
    )
    rho_tor: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../time"},
            "field_type": np.ndarray,
        },
    )
    psi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../../time"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryLocalQuantitiesRZ(IdsBaseClass):
    """

    :ivar position : Radial position at which physics quantities are evaluated
    :ivar t_e : Electron temperature
    :ivar t_i_average : Ion temperature (average over ion species)
    :ivar n_e : Electron density
    :ivar n_i : Ion density per species
    :ivar n_i_total : Total ion density (sum over species)
    :ivar zeff : Effective charge
    :ivar momentum_phi : Total plasma toroidal momentum, summed over ion species and electrons
    :ivar velocity_phi : Ion toroidal rotation velocity, per species
    :ivar q : Safety factor (only positive when toroidal current and magnetic field are in same direction)
    :ivar magnetic_shear : Magnetic shear, defined as rho_tor/q . dq/drho_tor
    :ivar b_field_tor : Toroidal magnetic field
    :ivar e_field_parallel : Average on the magnetic surface of (e_field.b_field) / B0, where B0 is global_quantities/b0/value
    """

    class Meta:
        name = "summary_local_quantities_r_z"
        is_root_ids = False

    position: Optional[SummaryLocalPositionRZ] = field(
        default=None,
        metadata={
            "imas_type": "summary_local_position_r_z",
            "field_type": SummaryLocalPositionRZ,
        },
    )
    t_e: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    t_i_average: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    n_e: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    n_i: Optional[SummarySpecies] = field(
        default=None,
        metadata={"imas_type": "summary_species", "field_type": SummarySpecies},
    )
    n_i_total: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    zeff: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    momentum_phi: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    velocity_phi: Optional[SummarySpeciesTorAngle] = field(
        default=None,
        metadata={
            "imas_type": "summary_species_tor_angle",
            "field_type": SummarySpeciesTorAngle,
        },
    )
    q: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    magnetic_shear: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    b_field_tor: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    e_field_parallel: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryLocalQuantitiesNoPositionName(IdsBaseClass):
    """

    :ivar name : Name of the limiter or divertor plate. Standard names are : LI (resp. LO) for lower inner (resp. outer) plates;  UI (resp. UO) for upper inner (resp. outer) plates.
    :ivar t_e : Electron temperature
    :ivar t_i_average : Ion temperature (average over ion species)
    :ivar n_e : Electron density
    :ivar n_i : Ion density per species
    :ivar n_i_total : Total ion density (sum over species)
    :ivar zeff : Effective charge
    :ivar flux_expansion : Magnetic flux expansion as defined by Stangeby : ratio between the poloidal field at the midplane separatrix and the poloidal field at the strike-point see formula attached, where u means upstream (midplane separatrix) and t means at divertor target (downstream).
    :ivar power_flux_peak : Peak power flux on the divertor target or limiter surface
    """

    class Meta:
        name = "summary_local_quantities_no_position_name"
        is_root_ids = False

    name: Optional[SummaryStaticStr0D] = field(
        default=None,
        metadata={
            "imas_type": "summary_static_str_0d",
            "field_type": SummaryStaticStr0D,
        },
    )
    t_e: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    t_i_average: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    n_e: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    n_i: Optional[SummarySpecies] = field(
        default=None,
        metadata={"imas_type": "summary_species", "field_type": SummarySpecies},
    )
    n_i_total: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    zeff: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    flux_expansion: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    power_flux_peak: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryLocalQuantitiesStellerator(IdsBaseClass):
    """

    :ivar effective_helical_ripple : Effective helical ripple for 1/nu neoclassical regime (see [Beidler, C. D., and W. N. G. Hitchon, 1994, Plasma Phys. Control. Fusion 35, 317])
    :ivar plateau_factor : Plateau factor, as defined in equation (25) of reference [Stroth U. et al 1998 Plasma Phys. Control. Fusion 40 1551]
    :ivar iota : Rotational transform (1/q)
    """

    class Meta:
        name = "summary_local_quantities_stellerator"
        is_root_ids = False

    effective_helical_ripple: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    plateau_factor: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    iota: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryLocalQuantities(IdsBaseClass):
    """

    :ivar position : Radial position at which physics quantities are evaluated
    :ivar t_e : Electron temperature
    :ivar t_i_average : Ion temperature (average over ion species)
    :ivar n_e : Electron density
    :ivar n_i : Ion density per species
    :ivar n_i_total : Total ion density (sum over species)
    :ivar zeff : Effective charge
    :ivar momentum_phi : Total plasma toroidal momentum, summed over ion species and electrons
    :ivar velocity_phi : Ion toroidal rotation velocity, per species
    :ivar q : Safety factor
    :ivar magnetic_shear : Magnetic shear, defined as rho_tor/q . dq/drho_tor
    :ivar e_field_parallel : Average on the magnetic surface of (e_field.b_field) / B0, where B0 is global_quantities/b0/value
    """

    class Meta:
        name = "summary_local_quantities"
        is_root_ids = False

    position: Optional[SummaryLocalPosition] = field(
        default=None,
        metadata={
            "imas_type": "summary_local_position",
            "field_type": SummaryLocalPosition,
        },
    )
    t_e: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    t_i_average: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    n_e: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    n_i: Optional[SummarySpecies] = field(
        default=None,
        metadata={"imas_type": "summary_species", "field_type": SummarySpecies},
    )
    n_i_total: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    zeff: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    momentum_phi: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    velocity_phi: Optional[SummarySpeciesTorAngle] = field(
        default=None,
        metadata={
            "imas_type": "summary_species_tor_angle",
            "field_type": SummarySpeciesTorAngle,
        },
    )
    q: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    magnetic_shear: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    e_field_parallel: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryPedestalFitStabilityMethod(IdsBaseClass):
    """

    :ivar alpha_critical : Critical normalized pressure gradient determined with self-consistent runs with an MHD stability code. Details of the method for scanning parameters in the series of runs must be described in the &#39;source&#39; node
    :ivar alpha_ratio : Ratio of alpha_critical over alpha_experimental
    :ivar t_e_pedestal_top_critical : Critical electron temperature at pedestal top determined with self-consistent runs with an MHD stability code. Details of the method for scanning parameters in the series of runs must be described in the &#39;source&#39; node
    """

    class Meta:
        name = "summary_pedestal_fit_stability_method"
        is_root_ids = False

    alpha_critical: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    alpha_ratio: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    t_e_pedestal_top_critical: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryPedestalFitStability(IdsBaseClass):
    """

    :ivar alpha_experimental : Experimental normalized pressure gradient reconstructed by an MHD stability code (with assumptions on the ion pressure). See definition in [Miller PoP 5 (1998),973,Eq. 42]
    :ivar bootstrap_current_sauter : MHD calculations of the critical alpha parameter using the Sauter formula for the calculation of the bootstrap current, from Phys. Plasmas 6 (1999) 2834
    :ivar bootstrap_current_hager : MHD calculations of the critical alpha parameter using the Hager formula for the calculation of the bootstrap current, from Phys. Plasmas 23 (2016) 042503
    """

    class Meta:
        name = "summary_pedestal_fit_stability"
        is_root_ids = False

    alpha_experimental: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    bootstrap_current_sauter: Optional[SummaryPedestalFitStabilityMethod] = (
        field(
            default=None,
            metadata={
                "imas_type": "summary_pedestal_fit_stability_method",
                "field_type": SummaryPedestalFitStabilityMethod,
            },
        )
    )
    bootstrap_current_hager: Optional[SummaryPedestalFitStabilityMethod] = (
        field(
            default=None,
            metadata={
                "imas_type": "summary_pedestal_fit_stability_method",
                "field_type": SummaryPedestalFitStabilityMethod,
            },
        )
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryPedestalFitLinearTe(IdsBaseClass):
    """

    :ivar pedestal_height : Pedestal height
    :ivar pedestal_width : Pedestal full width in normalized poloidal flux
    :ivar pedestal_position : Pedestal position in normalized poloidal flux
    :ivar offset : Offset of the parent quantity in the SOL
    :ivar d_dpsi_norm : Core slope of the parent quantity
    :ivar d_dpsi_norm_max : Maximum gradient of the parent quantity (with respect to the normalized poloidal flux) in the pedestal
    """

    class Meta:
        name = "summary_pedestal_fit_linear_te"
        is_root_ids = False

    pedestal_height: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    pedestal_width: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    pedestal_position: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    offset: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    d_dpsi_norm: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    d_dpsi_norm_max: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryPedestalFitTe(IdsBaseClass):
    """

    :ivar pedestal_height : Pedestal height
    :ivar pedestal_width : Pedestal full width in normalized poloidal flux
    :ivar pedestal_position : Pedestal position in normalized poloidal flux
    :ivar offset : Offset of the parent quantity in the SOL
    :ivar d_dpsi_norm : Core slope of the parent quantity
    :ivar d_dpsi_norm_max : Maximum gradient of the parent quantity (with respect to the normalized poloidal flux) in the pedestal
    :ivar d_dpsi_norm_max_position : Position (in terms of normalized poloidal flux) of the maximum gradient of the parent quantity in the pedestal
    """

    class Meta:
        name = "summary_pedestal_fit_te"
        is_root_ids = False

    pedestal_height: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    pedestal_width: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    pedestal_position: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    offset: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    d_dpsi_norm: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    d_dpsi_norm_max: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    d_dpsi_norm_max_position: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryPedestalFitLinearNe(IdsBaseClass):
    """

    :ivar separatrix : Value at separatrix
    :ivar pedestal_height : Pedestal height
    :ivar pedestal_width : Pedestal full width in normalized poloidal flux
    :ivar pedestal_position : Pedestal position in normalized poloidal flux
    :ivar offset : Offset of the parent quantity in the SOL
    :ivar d_dpsi_norm : Core slope of the parent quantity
    :ivar d_dpsi_norm_max : Maximum gradient of the parent quantity (with respect to the normalized poloidal flux) in the pedestal
    """

    class Meta:
        name = "summary_pedestal_fit_linear_ne"
        is_root_ids = False

    separatrix: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    pedestal_height: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    pedestal_width: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    pedestal_position: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    offset: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    d_dpsi_norm: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    d_dpsi_norm_max: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryPedestalFitNe(IdsBaseClass):
    """

    :ivar separatrix : Value at separatrix
    :ivar pedestal_height : Pedestal height
    :ivar pedestal_width : Pedestal full width in normalized poloidal flux
    :ivar pedestal_position : Pedestal position in normalized poloidal flux
    :ivar offset : Offset of the parent quantity in the SOL
    :ivar d_dpsi_norm : Core slope of the parent quantity
    :ivar d_dpsi_norm_max : Maximum gradient of the parent quantity (with respect to the normalized poloidal flux) in the pedestal
    :ivar d_dpsi_norm_max_position : Position (in terms of normalized poloidal flux) of the maximum gradient of the parent quantity in the pedestal
    """

    class Meta:
        name = "summary_pedestal_fit_ne"
        is_root_ids = False

    separatrix: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    pedestal_height: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    pedestal_width: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    pedestal_position: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    offset: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    d_dpsi_norm: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    d_dpsi_norm_max: Optional[SummaryDynamicFlt1DRootParent2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root_parent_2",
            "field_type": SummaryDynamicFlt1DRootParent2,
        },
    )
    d_dpsi_norm_max_position: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryPedestalFitLinear(IdsBaseClass):
    """

    :ivar n_e : Electron density related quantities
    :ivar t_e : Electron temperature related quantities
    :ivar pressure_electron : Electron pressure related quantities
    :ivar energy_thermal_pedestal_electron : Pedestal stored thermal energy for electrons
    :ivar energy_thermal_pedestal_ion : Pedestal stored thermal energy for ions
    :ivar volume_inside_pedestal : Plasma volume enclosed between the magnetic axis and the top of the pedestal
    :ivar beta_pol_pedestal_top_electron_average : Poloidal beta at pressure pedestal top for electrons using the flux surface average magnetic poloidal field
    :ivar beta_pol_pedestal_top_electron_lfs : Poloidal beta at pressure pedestal top for electrons using the low field side magnetic poloidal field
    :ivar beta_pol_pedestal_top_electron_hfs : Poloidal beta at pressure pedestal top for electrons using the high field side magnetic poloidal field
    :ivar nustar_pedestal_top_electron : Normalized collisionality at pressure pedestal top for electrons
    :ivar rhostar_pedestal_top_electron_lfs : Normalized Larmor radius at pressure pedestal top for electrons using the low field side magnetic field (important for spherical tokamaks)
    :ivar rhostar_pedestal_top_electron_hfs : Normalized Larmor radius at pressure pedestal top for electrons using the high field side magnetic field (important for spherical tokamaks)
    :ivar rhostar_pedestal_top_electron_magnetic_axis : Normalized Larmor radius at pressure pedestal top for electrons using the magnetic field on the magnetic axis (definition used in most tokamak literature)
    :ivar b_field_pol_pedestal_top_average : Poloidal field calculated at the position of the pressure pedestal top (as determined by the fit) and averaged over the flux surface
    :ivar b_field_pol_pedestal_top_hfs : Poloidal field calculated at the position of the pressure pedestal top (as determined by the fit) on the high field side
    :ivar b_field_pol_pedestal_top_lfs : Poloidal field calculated at the position of the pressure pedestal top (as determined by the fit) on the low field side
    :ivar b_field_pedestal_top_hfs : Total magnetic field calculated at the position of the pressure pedestal top (as determined by the fit) on the high field side
    :ivar b_field_pedestal_top_lfs : Total magnetic field calculated at the position of the pressure pedestal top (as determined by the fit) on the low field side
    :ivar b_field_tor_pedestal_top_hfs : Toroidal field calculated at the position of the pressure pedestal top (as determined by the fit) on the high field side
    :ivar b_field_tor_pedestal_top_lfs : Toroidal field calculated at the position of the pressure pedestal top (as determined by the fit) on the low field side
    :ivar coulomb_factor_pedestal_top : Coulomb factor log(lambda) at the position of the pressure pedestal top (as determined by the fit)
    :ivar parameters : Parameters of the fit
    """

    class Meta:
        name = "summary_pedestal_fit_linear"
        is_root_ids = False

    n_e: Optional[SummaryPedestalFitLinearNe] = field(
        default=None,
        metadata={
            "imas_type": "summary_pedestal_fit_linear_ne",
            "field_type": SummaryPedestalFitLinearNe,
        },
    )
    t_e: Optional[SummaryPedestalFitLinearTe] = field(
        default=None,
        metadata={
            "imas_type": "summary_pedestal_fit_linear_te",
            "field_type": SummaryPedestalFitLinearTe,
        },
    )
    pressure_electron: Optional[SummaryPedestalFitNe] = field(
        default=None,
        metadata={
            "imas_type": "summary_pedestal_fit_ne",
            "field_type": SummaryPedestalFitNe,
        },
    )
    energy_thermal_pedestal_electron: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    energy_thermal_pedestal_ion: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    volume_inside_pedestal: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    beta_pol_pedestal_top_electron_average: Optional[
        SummaryDynamicFlt1DRoot
    ] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    beta_pol_pedestal_top_electron_lfs: Optional[SummaryDynamicFlt1DRoot] = (
        field(
            default=None,
            metadata={
                "imas_type": "summary_dynamic_flt_1d_root",
                "field_type": SummaryDynamicFlt1DRoot,
            },
        )
    )
    beta_pol_pedestal_top_electron_hfs: Optional[SummaryDynamicFlt1DRoot] = (
        field(
            default=None,
            metadata={
                "imas_type": "summary_dynamic_flt_1d_root",
                "field_type": SummaryDynamicFlt1DRoot,
            },
        )
    )
    nustar_pedestal_top_electron: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    rhostar_pedestal_top_electron_lfs: Optional[SummaryDynamicFlt1DRoot] = (
        field(
            default=None,
            metadata={
                "imas_type": "summary_dynamic_flt_1d_root",
                "field_type": SummaryDynamicFlt1DRoot,
            },
        )
    )
    rhostar_pedestal_top_electron_hfs: Optional[SummaryDynamicFlt1DRoot] = (
        field(
            default=None,
            metadata={
                "imas_type": "summary_dynamic_flt_1d_root",
                "field_type": SummaryDynamicFlt1DRoot,
            },
        )
    )
    rhostar_pedestal_top_electron_magnetic_axis: Optional[
        SummaryDynamicFlt1DRoot
    ] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    b_field_pol_pedestal_top_average: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    b_field_pol_pedestal_top_hfs: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    b_field_pol_pedestal_top_lfs: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    b_field_pedestal_top_hfs: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    b_field_pedestal_top_lfs: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    b_field_tor_pedestal_top_hfs: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    b_field_tor_pedestal_top_lfs: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    coulomb_factor_pedestal_top: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    parameters: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...5"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryPedestalFit(IdsBaseClass):
    """

    :ivar n_e : Electron density related quantities
    :ivar t_e : Electron temperature related quantities
    :ivar pressure_electron : Electron pressure related quantities
    :ivar energy_thermal_pedestal_electron : Pedestal stored thermal energy for electrons
    :ivar energy_thermal_pedestal_ion : Pedestal stored thermal energy for ions
    :ivar volume_inside_pedestal : Plasma volume enclosed between the magnetic axis and the top of the pedestal
    :ivar alpha_electron_pedestal_max : Maximum value in the pedestal of the alpha parameter for electron pressure (see [Miller PoP 5 (1998),973,Eq. 42])
    :ivar alpha_electron_pedestal_max_position : Position in normalized poloidal flux of the maximum value in the pedestal of the alpha parameter for electron pressure (see [Miller PoP 5 (1998),973,Eq. 42])
    :ivar beta_pol_pedestal_top_electron_average : Poloidal beta at pressure pedestal top for electrons using the flux surface average magnetic poloidal field
    :ivar beta_pol_pedestal_top_electron_lfs : Poloidal beta at pedestal top for electrons using the low field side magnetic poloidal field
    :ivar beta_pol_pedestal_top_electron_hfs : Poloidal beta at pressure pedestal top for electrons using the high field side magnetic poloidal field
    :ivar nustar_pedestal_top_electron : Normalized collisionality at pressure pedestal top for electrons
    :ivar rhostar_pedestal_top_electron_lfs : Normalized Larmor radius at pressure pedestal top for electrons using the low field side magnetic field (important for spherical tokamaks)
    :ivar rhostar_pedestal_top_electron_hfs : Normalized Larmor radius at pressure pedestal top for electrons using the high field side magnetic field (important for spherical tokamaks)
    :ivar rhostar_pedestal_top_electron_magnetic_axis : Normalized Larmor radius at pressure pedestal top for electrons using the magnetic field on the magnetic axis (definition used in most tokamak litterature)
    :ivar b_field_pol_pedestal_top_average : Poloidal field calculated at the position of the pressure pedestal top (as determined by the fit) and averaged over the flux surface
    :ivar b_field_pol_pedestal_top_hfs : Poloidal field calculated at the position of the pressure pedestal top (as determined by the fit) on the high field side
    :ivar b_field_pol_pedestal_top_lfs : Poloidal field calculated at the position of the pressure pedestal top (as determined by the fit) on the low field side
    :ivar b_field_pedestal_top_hfs : Total magnetic field calculated at the position of the pressure pedestal top (as determined by the fit) on the high field side
    :ivar b_field_pedestal_top_lfs : Total magnetic field calculated at the position of the pressure pedestal top (as determined by the fit) on the low field side
    :ivar b_field_tor_pedestal_top_hfs : Toroidal field calculated at the position of the pressure pedestal top (as determined by the fit) on the high field side
    :ivar b_field_tor_pedestal_top_lfs : Toroidal field calculated at the position of the pressure pedestal top (as determined by the fit) on the low field side
    :ivar coulomb_factor_pedestal_top : Coulomb factor log(lambda) at the position of the pressure pedestal top (as determined by the fit)
    :ivar stability : MHD stability analysis of the pedestal (for this fit of the profiles)
    :ivar parameters : Parameters of the fit
    """

    class Meta:
        name = "summary_pedestal_fit"
        is_root_ids = False

    n_e: Optional[SummaryPedestalFitNe] = field(
        default=None,
        metadata={
            "imas_type": "summary_pedestal_fit_ne",
            "field_type": SummaryPedestalFitNe,
        },
    )
    t_e: Optional[SummaryPedestalFitTe] = field(
        default=None,
        metadata={
            "imas_type": "summary_pedestal_fit_te",
            "field_type": SummaryPedestalFitTe,
        },
    )
    pressure_electron: Optional[SummaryPedestalFitNe] = field(
        default=None,
        metadata={
            "imas_type": "summary_pedestal_fit_ne",
            "field_type": SummaryPedestalFitNe,
        },
    )
    energy_thermal_pedestal_electron: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    energy_thermal_pedestal_ion: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    volume_inside_pedestal: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    alpha_electron_pedestal_max: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    alpha_electron_pedestal_max_position: Optional[SummaryDynamicFlt1DRoot] = (
        field(
            default=None,
            metadata={
                "imas_type": "summary_dynamic_flt_1d_root",
                "field_type": SummaryDynamicFlt1DRoot,
            },
        )
    )
    beta_pol_pedestal_top_electron_average: Optional[
        SummaryDynamicFlt1DRoot
    ] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    beta_pol_pedestal_top_electron_lfs: Optional[SummaryDynamicFlt1DRoot] = (
        field(
            default=None,
            metadata={
                "imas_type": "summary_dynamic_flt_1d_root",
                "field_type": SummaryDynamicFlt1DRoot,
            },
        )
    )
    beta_pol_pedestal_top_electron_hfs: Optional[SummaryDynamicFlt1DRoot] = (
        field(
            default=None,
            metadata={
                "imas_type": "summary_dynamic_flt_1d_root",
                "field_type": SummaryDynamicFlt1DRoot,
            },
        )
    )
    nustar_pedestal_top_electron: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    rhostar_pedestal_top_electron_lfs: Optional[SummaryDynamicFlt1DRoot] = (
        field(
            default=None,
            metadata={
                "imas_type": "summary_dynamic_flt_1d_root",
                "field_type": SummaryDynamicFlt1DRoot,
            },
        )
    )
    rhostar_pedestal_top_electron_hfs: Optional[SummaryDynamicFlt1DRoot] = (
        field(
            default=None,
            metadata={
                "imas_type": "summary_dynamic_flt_1d_root",
                "field_type": SummaryDynamicFlt1DRoot,
            },
        )
    )
    rhostar_pedestal_top_electron_magnetic_axis: Optional[
        SummaryDynamicFlt1DRoot
    ] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    b_field_pol_pedestal_top_average: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    b_field_pol_pedestal_top_hfs: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    b_field_pol_pedestal_top_lfs: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    b_field_pedestal_top_hfs: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    b_field_pedestal_top_lfs: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    b_field_tor_pedestal_top_hfs: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    b_field_tor_pedestal_top_lfs: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    coulomb_factor_pedestal_top: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    stability: Optional[SummaryPedestalFitStability] = field(
        default=None,
        metadata={
            "imas_type": "summary_pedestal_fit_stability",
            "field_type": SummaryPedestalFitStability,
        },
    )
    parameters: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...5"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryPedestalFits(IdsBaseClass):
    """

    :ivar mtanh : Quantities related to &#34;mtanh&#34; fit
    :ivar linear : Quantities related to linear fit
    """

    class Meta:
        name = "summary_pedestal_fits"
        is_root_ids = False

    mtanh: Optional[SummaryPedestalFit] = field(
        default=None,
        metadata={
            "imas_type": "summary_pedestal_fit",
            "field_type": SummaryPedestalFit,
        },
    )
    linear: Optional[SummaryPedestalFitLinear] = field(
        default=None,
        metadata={
            "imas_type": "summary_pedestal_fit_linear",
            "field_type": SummaryPedestalFitLinear,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryLocal(IdsBaseClass):
    """

    :ivar magnetic_axis : Parameters at magnetic axis
    :ivar separatrix : Parameters at separatrix (intersection of the separatrix and the outboard midplane)
    :ivar separatrix_average : Flux surface averaged parameters at separatrix (flux-surface average over the entire core-SOL boundary separatrix)
    :ivar pedestal : Parameters at pedestal top
    :ivar itb : Parameters at internal transport barrier
    :ivar limiter : Parameters at the limiter tangency point
    :ivar divertor_target : Parameters at a divertor target
    :ivar r_eff_norm_2_3 : Parameters at r_eff_norm = 2/3, where r_eff_norm is the stellarator effective minor radius normalized to its value at the last closed flux surface
    """

    class Meta:
        name = "summary_local"
        is_root_ids = False

    magnetic_axis: Optional[SummaryLocalQuantitiesRZ] = field(
        default=None,
        metadata={
            "imas_type": "summary_local_quantities_r_z",
            "field_type": SummaryLocalQuantitiesRZ,
        },
    )
    separatrix: Optional[SummaryLocalQuantities] = field(
        default=None,
        metadata={
            "imas_type": "summary_local_quantities",
            "field_type": SummaryLocalQuantities,
        },
    )
    separatrix_average: Optional[SummaryLocalQuantities] = field(
        default=None,
        metadata={
            "imas_type": "summary_local_quantities",
            "field_type": SummaryLocalQuantities,
        },
    )
    pedestal: Optional[SummaryLocalQuantities] = field(
        default=None,
        metadata={
            "imas_type": "summary_local_quantities",
            "field_type": SummaryLocalQuantities,
        },
    )
    itb: Optional[SummaryLocalQuantities] = field(
        default=None,
        metadata={
            "imas_type": "summary_local_quantities",
            "field_type": SummaryLocalQuantities,
        },
    )
    limiter: Optional[SummaryLocalQuantitiesNoPositionName] = field(
        default=None,
        metadata={
            "imas_type": "summary_local_quantities_no_position_name",
            "field_type": SummaryLocalQuantitiesNoPositionName,
        },
    )
    divertor_target: Optional[SummaryLocalQuantitiesNoPositionName] = field(
        default_factory=lambda: StructArray(
            type_input=SummaryLocalQuantitiesNoPositionName
        ),
        metadata={
            "imas_type": "summary_local_quantities_no_position_name",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": SummaryLocalQuantitiesNoPositionName,
        },
    )
    r_eff_norm_2_3: Optional[SummaryLocalQuantitiesStellerator] = field(
        default=None,
        metadata={
            "imas_type": "summary_local_quantities_stellerator",
            "field_type": SummaryLocalQuantitiesStellerator,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SummarySol(IdsBaseClass):
    """

    :ivar t_e_decay_length : Electron temperature radial decay length inv(grad Te/Te)
    :ivar t_i_average_decay_length : Ion temperature (average over ion species) radial decay length inv(grad Ti/Ti)
    :ivar n_e_decay_length : Electron density radial decay length inv(grad ne/ne)
    :ivar n_i_total_decay_length : Ion density radial decay length inv(grad ni/ni)
    :ivar heat_flux_e_decay_length : Electron heat flux radial decay length inv(grad qe/qe)
    :ivar heat_flux_i_decay_length : Ion heat flux radial decay length inv(grad qi/qi)
    :ivar power_radiated : Power radiated from the SOL
    :ivar pressure_neutral : Neutral pressure in the SOL
    """

    class Meta:
        name = "summary_sol"
        is_root_ids = False

    t_e_decay_length: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    t_i_average_decay_length: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    n_e_decay_length: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    n_i_total_decay_length: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    heat_flux_e_decay_length: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    heat_flux_i_decay_length: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    power_radiated: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    pressure_neutral: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryAverageQuantities(IdsBaseClass):
    """

    :ivar t_e : Electron temperature
    :ivar t_i_average : Ion temperature (average over ion species)
    :ivar n_e : Electron density
    :ivar dn_e_dt : Time derivative of the electron density
    :ivar n_i : Ion density per species
    :ivar n_i_total : Total ion density (sum over species)
    :ivar zeff : Effective charge
    :ivar meff_hydrogenic : Effective mass of the hydrogenic species (MH. nH+MD.nD+MT.nT)/(nH+nD+nT)
    :ivar isotope_fraction_hydrogen : Fraction of hydrogen density among the hydrogenic species (nH/(nH+nD+nT))
    """

    class Meta:
        name = "summary_average_quantities"
        is_root_ids = False

    t_e: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    t_i_average: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    n_e: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    dn_e_dt: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    n_i: Optional[SummarySpecies] = field(
        default=None,
        metadata={"imas_type": "summary_species", "field_type": SummarySpecies},
    )
    n_i_total: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    zeff: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    meff_hydrogenic: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    isotope_fraction_hydrogen: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryElms(IdsBaseClass):
    """

    :ivar frequency : ELMs frequency
    :ivar type : ELMs type (I, II, III, ...)
    """

    class Meta:
        name = "summary_elms"
        is_root_ids = False

    frequency: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    type: Optional[SummaryDynamicInt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_int_1d_root",
            "field_type": SummaryDynamicInt1DRoot,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryPellets(IdsBaseClass):
    """

    :ivar occurrence : Flag set to 1 if there is any pellet injected during the pulse, 0 otherwise
    """

    class Meta:
        name = "summary_pellets"
        is_root_ids = False

    occurrence: Optional[SummaryConstantInt0D] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_int_0d",
            "field_type": SummaryConstantInt0D,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryBoundary(IdsBaseClass):
    """

    :ivar type : 0 (limiter), 1 (diverted), 11 (LSN), 12 (USN), 13 (DN), 14 (snowflake)
    :ivar geometric_axis_r : R position of the geometric axis (defined as (Rmax+Rmin) / 2 of the boundary)
    :ivar geometric_axis_z : Z position of the geometric axis (defined as (Zmax+Zmin) / 2 of the boundary)
    :ivar magnetic_axis_r : R position of the magnetic axis
    :ivar magnetic_axis_z : Z position of the magnetic axis
    :ivar minor_radius : Minor radius of the plasma boundary (defined as (Rmax-Rmin) / 2 of the boundary)
    :ivar elongation : Elongation of the plasma boundary
    :ivar triangularity_upper : Upper triangularity of the plasma boundary
    :ivar triangularity_lower : Lower triangularity of the plasma boundary
    :ivar strike_point_inner_r : R position of the inner strike point
    :ivar strike_point_inner_z : Z position of the inner strike point
    :ivar strike_point_outer_r : R position of the outer strike point
    :ivar strike_point_outer_z : Z position of the outer strike point
    :ivar strike_point_configuration : String describing the configuration of the strike points (constant, may need to become dynamic when available)
    :ivar gap_limiter_wall : Distance between the separatrix and the nearest limiter or wall element
    :ivar distance_inner_outer_separatrices : Distance between the inner and outer separatrices, in the major radius direction, at the plasma outboard and at the height corresponding to the maximum R for the inner separatrix.
    :ivar x_point_main : RZ position of the main X-point
    """

    class Meta:
        name = "summary_boundary"
        is_root_ids = False

    type: Optional[SummaryDynamicInt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_int_1d_root",
            "field_type": SummaryDynamicInt1DRoot,
        },
    )
    geometric_axis_r: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    geometric_axis_z: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    magnetic_axis_r: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    magnetic_axis_z: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    minor_radius: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    elongation: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    triangularity_upper: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    triangularity_lower: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    strike_point_inner_r: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    strike_point_inner_z: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    strike_point_outer_r: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    strike_point_outer_z: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    strike_point_configuration: Optional[SummaryConstantStr0D] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_str_0d",
            "field_type": SummaryConstantStr0D,
        },
    )
    gap_limiter_wall: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    distance_inner_outer_separatrices: Optional[SummaryDynamicFlt1DRoot] = (
        field(
            default=None,
            metadata={
                "imas_type": "summary_dynamic_flt_1d_root",
                "field_type": SummaryDynamicFlt1DRoot,
            },
        )
    )
    x_point_main: Optional[SummaryRz1DDynamic] = field(
        default=None,
        metadata={
            "imas_type": "summary_rz1d_dynamic",
            "field_type": SummaryRz1DDynamic,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryRmp(IdsBaseClass):
    """

    :ivar occurrence : Flag set to 1 if resonant magnetic perturbations are used during the pulse, 0 otherwise
    """

    class Meta:
        name = "summary_rmp"
        is_root_ids = False

    occurrence: Optional[SummaryConstantInt0D] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_int_0d",
            "field_type": SummaryConstantInt0D,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryKicks(IdsBaseClass):
    """

    :ivar occurrence : Flag set to 1 if vertical kicks of the plasma position are used during the pulse, 0 otherwise
    """

    class Meta:
        name = "summary_kicks"
        is_root_ids = False

    occurrence: Optional[SummaryConstantInt0D] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_int_0d",
            "field_type": SummaryConstantInt0D,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryGlobalQuantities(IdsBaseClass):
    """

    :ivar ip : Total plasma current (toroidal component). Positive sign means anti-clockwise when viewed from above.
    :ivar current_non_inductive : Total non-inductive current (toroidal component). Positive sign means anti-clockwise when viewed from above.
    :ivar current_bootstrap : Bootstrap current (toroidal component). Positive sign means anti-clockwise when viewed from above.
    :ivar current_ohm : Ohmic current (toroidal component). Positive sign means anti-clockwise when viewed from above.
    :ivar current_alignment : Figure of merit of the alignment of the current profile sources, defined in the following reference: http://iopscience.iop.org/article/10.1088/0029-5515/43/7/318
    :ivar v_loop : LCFS loop voltage (positive value drives positive ohmic current that flows anti-clockwise when viewed from above)
    :ivar li_3 : Internal inductance. The li_3 definition is used, i.e. li_3 = 2/R0/mu0^2/Ip^2 * int(Bp^2 dV).
    :ivar li_3_mhd : Internal inductance as determined by an equilibrium reconstruction code. Use this only when the li node above is used for another estimation method and there is a need to store a second value of li (determined by an equilibrium reconstruction code). The li_3 definition is used, i.e. li_3 = 2/R0/mu0^2/Ip^2 * int(Bp^2 dV).
    :ivar beta_tor : Toroidal beta, defined as the volume-averaged total perpendicular pressure divided by (B0^2/(2*mu0)), i.e. beta_toroidal = 2 mu0 int(p dV) / V / B0^2
    :ivar beta_tor_mhd : Toroidal beta, using the pressure determined by an equilibrium reconstruction code
    :ivar beta_tor_norm : Normalized toroidal beta, defined as 100 * beta_tor * a[m] * B0 [T] / ip [MA]
    :ivar beta_tor_norm_mhd : Normalized toroidal beta, using the pressure determined by an equilibrium reconstruction code
    :ivar beta_tor_thermal_norm : Normalized toroidal beta from thermal pressure only, defined as 100 * beta_tor_thermal * a[m] * B0 [T] / ip [MA]
    :ivar beta_pol : Poloidal beta. Defined as betap = 4 int(p dV) / [R_0 * mu_0 * Ip^2]
    :ivar beta_pol_mhd : Poloidal beta estimated from the pressure determined by an equilibrium reconstruction code. Defined as betap = 4 int(p dV) / [R_0 * mu_0 * Ip^2]
    :ivar energy_diamagnetic : Plasma diamagnetic energy content = 3/2 * integral over the plasma volume of the total perpendicular pressure
    :ivar denergy_diamagnetic_dt : Time derivative of the diamagnetic plasma energy content
    :ivar energy_total : Plasma energy content = 3/2 * integral over the plasma volume of the total kinetic pressure
    :ivar energy_mhd : Plasma energy content = 3/2 * integral over the plasma volume of the total kinetic pressure (pressure determined by an equilibrium reconstruction code)
    :ivar energy_thermal : Thermal plasma energy content = 3/2 * integral over the plasma volume of the thermal pressure
    :ivar energy_ion_total_thermal : Thermal ion plasma energy content (sum over the ion species) = 3/2 * integral over the plasma volume of the thermal ion pressure
    :ivar energy_electrons_thermal : Thermal electron plasma energy content = 3/2 * integral over the plasma volume of the thermal electron pressure
    :ivar denergy_thermal_dt : Time derivative of the thermal plasma energy content
    :ivar energy_b_field_pol : Poloidal magnetic plasma energy content = 1/(2.mu0) * integral over the plasma volume of b_field_pol^2
    :ivar energy_fast_perpendicular : Fast particles perpendicular energy content = 3/2 * integral over the plasma volume of the fast perpendicular pressure
    :ivar energy_fast_parallel : Fast particles parallel energy content = 3/2 * integral over the plasma volume of the fast parallel pressure
    :ivar volume : Volume of the confined plasma
    :ivar h_mode : H-mode flag: 0 when the plasma is in L-mode and 1 when in H-mode
    :ivar r0 : Reference major radius where the vacuum toroidal magnetic field is given (usually a fixed position such as the middle of the vessel at the equatorial midplane)
    :ivar b0 : Vacuum toroidal field at R0. Positive sign means anti-clockwise when viewed from above. The product R0B0 must be consistent with the b_tor_vacuum_r field of the tf IDS.
    :ivar fusion_gain : Fusion gain : ratio of the power provided by fusion reactions to the auxiliary power needed to heat the plasma. Often noted as Q in the litterature.
    :ivar h_98 : Energy confinement time enhancement factor over the IPB98(y,2) scaling
    :ivar tau_energy : Energy confinement time
    :ivar tau_helium : Helium confinement time
    :ivar tau_resistive : Current diffusion characteristic time
    :ivar tau_energy_98 : Energy confinement time estimated from the IPB98(y,2) scaling
    :ivar ratio_tau_helium_fuel : Ratio of Helium confinement time to fuel confinement time
    :ivar resistance : Plasma electric resistance
    :ivar q_95 : q at the 95% poloidal flux surface (only positive when toroidal current and magnetic field are in same direction)
    :ivar power_ohm : Ohmic power
    :ivar power_steady : Total power coupled to the plasma minus dW/dt (correcting from transient energy content)
    :ivar power_radiated : Total radiated power
    :ivar power_radiated_inside_lcfs : Radiated power from the plasma inside the Last Closed Flux Surface
    :ivar power_radiated_outside_lcfs : Radiated power from the plasma outside the Last Closed Flux Surface
    :ivar power_line : Radiated power from line radiation
    :ivar power_bremsstrahlung : Radiated power from Bremsstrahlung
    :ivar power_synchrotron : Radiated power from synchrotron radiation
    :ivar power_loss : Power through separatrix
    :ivar greenwald_fraction : Greenwald fraction =line_average/n_e/value divided by (global_quantities/ip/value *1e6 * pi * minor_radius^2)
    :ivar fusion_fluence : Fusion fluence : power provided by fusion reactions, integrated over time since the beginning of the pulse
    :ivar psi_external_average : Average (over the plasma poloidal cross section) plasma poloidal magnetic flux produced by all toroidal loops (active coils and passive loops) but the plasma, given by the following formula : int(psi_loops.j_tor.dS) / Ip
    """

    class Meta:
        name = "summary_global_quantities"
        is_root_ids = False

    ip: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    current_non_inductive: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    current_bootstrap: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    current_ohm: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    current_alignment: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    v_loop: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    li_3: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    li_3_mhd: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    beta_tor: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    beta_tor_mhd: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    beta_tor_norm: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    beta_tor_norm_mhd: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    beta_tor_thermal_norm: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    beta_pol: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    beta_pol_mhd: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    energy_diamagnetic: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    denergy_diamagnetic_dt: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    energy_total: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    energy_mhd: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    energy_thermal: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    energy_ion_total_thermal: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    energy_electrons_thermal: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    denergy_thermal_dt: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    energy_b_field_pol: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    energy_fast_perpendicular: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    energy_fast_parallel: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    volume: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    h_mode: Optional[SummaryDynamicInt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_int_1d_root",
            "field_type": SummaryDynamicInt1DRoot,
        },
    )
    r0: Optional[SummaryConstantFlt0D] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_flt_0d",
            "field_type": SummaryConstantFlt0D,
        },
    )
    b0: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    fusion_gain: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    h_98: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    tau_energy: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    tau_helium: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    tau_resistive: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    tau_energy_98: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    ratio_tau_helium_fuel: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    resistance: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    q_95: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    power_ohm: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    power_steady: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    power_radiated: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    power_radiated_inside_lcfs: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    power_radiated_outside_lcfs: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    power_line: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    power_bremsstrahlung: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    power_synchrotron: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    power_loss: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    greenwald_fraction: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    fusion_fluence: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    psi_external_average: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryNeutronRatesReaction(IdsBaseClass):
    """

    :ivar total : Total neutron rate coming from this reaction
    :ivar thermal : Neutron rate coming from thermal plasma
    :ivar beam_thermal : Neutron rate coming from NBI beam - plasma reactions
    :ivar beam_beam : Neutron rate coming from NBI beam self reactions
    """

    class Meta:
        name = "summary_neutron_rates_reaction"
        is_root_ids = False

    total: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    thermal: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    beam_thermal: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    beam_beam: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryNeutronRates(IdsBaseClass):
    """

    :ivar total : Total neutron rate from all reactions
    :ivar thermal : Neutron rate from all plasma thermal reactions
    :ivar dd : Neutron rates from DD reactions
    :ivar dt : Neutron rates from DT reactions
    :ivar tt : Neutron rates from TT reactions
    """

    class Meta:
        name = "summary_neutron_rates"
        is_root_ids = False

    total: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    thermal: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    dd: Optional[SummaryNeutronRatesReaction] = field(
        default=None,
        metadata={
            "imas_type": "summary_neutron_rates_reaction",
            "field_type": SummaryNeutronRatesReaction,
        },
    )
    dt: Optional[SummaryNeutronRatesReaction] = field(
        default=None,
        metadata={
            "imas_type": "summary_neutron_rates_reaction",
            "field_type": SummaryNeutronRatesReaction,
        },
    )
    tt: Optional[SummaryNeutronRatesReaction] = field(
        default=None,
        metadata={
            "imas_type": "summary_neutron_rates_reaction",
            "field_type": SummaryNeutronRatesReaction,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryFusion(IdsBaseClass):
    """

    :ivar power : Power coupled to the plasma by fusion reactions
    :ivar current : Parallel current driven by this fusion reactions
    :ivar neutron_rates : Neutron rates from various reactions
    :ivar neutron_power_total : Total neutron power (from all reactions). Sum over each type of reaction (DD, DT, TT for thermal, beam-plasma, beam-beam, etc.) of the neutron production rate times the average neutron birth energy
    """

    class Meta:
        name = "summary_fusion"
        is_root_ids = False

    power: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    current: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    neutron_rates: Optional[SummaryNeutronRates] = field(
        default=None,
        metadata={
            "imas_type": "summary_neutron_rates",
            "field_type": SummaryNeutronRates,
        },
    )
    neutron_power_total: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryRunaways(IdsBaseClass):
    """

    :ivar particles : Number of runaway electrons
    :ivar current : Parallel current driven by the runaway electrons
    """

    class Meta:
        name = "summary_runaways"
        is_root_ids = False

    particles: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    current: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryHCdNbi(IdsBaseClass):
    """

    :ivar species : Injected species
    :ivar power : NBI power coupled to the plasma by this unit (i.e. without shine-through and fast ion losses)
    :ivar power_launched : NBI power launched into the vacuum vessel from this unit
    :ivar current : Parallel current driven by this NBI unit
    :ivar position : R, Z, Phi position of the NBI unit centre
    :ivar tangency_radius : Tangency radius (major radius where the central line of a NBI unit is tangent to a circle around the torus)
    :ivar angle : Angle of inclination between a beamlet at the centre of the injection unit surface and the horizontal plane
    :ivar direction : Direction of the beam seen from above the torus: -1 = clockwise; 1 = counter clockwise
    :ivar energy : Full energy of the injected species (acceleration of a single atom)
    :ivar beam_current_fraction : Fractions of beam current distributed among the different energies, the first index corresponds to the fast neutrals energy (1:full, 2: half, 3: one third)
    :ivar beam_power_fraction : Fractions of beam power distributed among the different energies, the first index corresponds to the fast neutrals energy (1:full, 2: half, 3: one third)
    """

    class Meta:
        name = "summary_h_cd_nbi"
        is_root_ids = False

    species: Optional[SummaryPlasmaCompositionSpecies] = field(
        default=None,
        metadata={
            "imas_type": "summary_plasma_composition_species",
            "field_type": SummaryPlasmaCompositionSpecies,
        },
    )
    power: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    power_launched: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    current: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    position: Optional[SummaryRphiz0DStatic] = field(
        default=None,
        metadata={
            "imas_type": "summary_rphiz0d_static",
            "field_type": SummaryRphiz0DStatic,
        },
    )
    tangency_radius: Optional[SummaryStaticFlt0D] = field(
        default=None,
        metadata={
            "imas_type": "summary_static_flt_0d",
            "field_type": SummaryStaticFlt0D,
        },
    )
    angle: Optional[SummaryStaticFlt0D] = field(
        default=None,
        metadata={
            "imas_type": "summary_static_flt_0d",
            "field_type": SummaryStaticFlt0D,
        },
    )
    direction: Optional[SummaryStaticInt0D] = field(
        default=None,
        metadata={
            "imas_type": "summary_static_int_0d",
            "field_type": SummaryStaticInt0D,
        },
    )
    energy: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    beam_current_fraction: Optional[SummaryDynamicFlt2DFraction2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_2d_fraction_2",
            "field_type": SummaryDynamicFlt2DFraction2,
        },
    )
    beam_power_fraction: Optional[SummaryDynamicFlt2DFraction2] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_2d_fraction_2",
            "field_type": SummaryDynamicFlt2DFraction2,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryHCdEc(IdsBaseClass):
    """

    :ivar frequency : ECRH frequency
    :ivar position : Position of the maximum of the ECRH power deposition, in rho_tor_norm
    :ivar polarization : Polarization of the ECRH waves (0 = O mode, 1 = X mode)
    :ivar harmonic : Harmonic number of the absorbed ECRH waves
    :ivar phi : Toroidal angle of ECRH at resonance
    :ivar angle_pol : Poloidal angle of ECRH at resonance
    :ivar power : Electron cyclotron heating power coupled to the plasma from this launcher
    :ivar power_launched : Electron cyclotron heating power launched into the vacuum vessel from this launcher
    :ivar current : Parallel current driven by EC waves
    :ivar energy_fast : Fast particle energy content driven by EC waves
    """

    class Meta:
        name = "summary_h_cd_ec"
        is_root_ids = False

    frequency: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    position: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    polarization: Optional[SummaryDynamicInt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_int_1d_root",
            "field_type": SummaryDynamicInt1DRoot,
        },
    )
    harmonic: Optional[SummaryDynamicInt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_int_1d_root",
            "field_type": SummaryDynamicInt1DRoot,
        },
    )
    phi: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    angle_pol: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    power: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    power_launched: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    current: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    energy_fast: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryHCdLh(IdsBaseClass):
    """

    :ivar frequency : LH wave frequency
    :ivar position : Position of the maximum of the LH power deposition, in rho_tor_norm
    :ivar n_parallel : Main parallel refractive index of LH waves at launch
    :ivar power : LH heating power coupled to the plasma from this launcher
    :ivar power_launched : LH heating power launched into the vacuum vessel from this launcher
    :ivar current : Parallel current driven by LH waves
    :ivar energy_fast : Fast particle energy content driven by LH waves
    """

    class Meta:
        name = "summary_h_cd_lh"
        is_root_ids = False

    frequency: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    position: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    n_parallel: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    power: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    power_launched: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    current: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    energy_fast: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryHCdIc(IdsBaseClass):
    """

    :ivar frequency : ICRH frequency
    :ivar position : Position of the maximum of the ICRH power deposition, in rho_tor_norm
    :ivar n_phi : Main toroidal mode number of IC waves. The wave vector toroidal component is defined as k_phi = n_phi grad phi where phi is the toroidal angle so that a positive n_tor means a wave propagating in the positive phi direction
    :ivar k_perpendicular : Main perpendicular wave number of IC waves
    :ivar e_field_plus_minus_ratio : Average E+/E- power ratio of IC waves
    :ivar harmonic : Harmonic number of the absorbed ICRH waves
    :ivar phase : Phase between straps
    :ivar power : IC heating power coupled to the plasma from this launcher
    :ivar power_launched : IC heating power launched into the vacuum vessel from this launcher
    :ivar current : Parallel current driven by IC waves
    :ivar energy_fast : Fast particle energy content driven by IC waves
    """

    class Meta:
        name = "summary_h_cd_ic"
        is_root_ids = False

    frequency: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    position: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    n_phi: Optional[SummaryDynamicInt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_int_1d_root",
            "field_type": SummaryDynamicInt1DRoot,
        },
    )
    k_perpendicular: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    e_field_plus_minus_ratio: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    harmonic: Optional[SummaryDynamicInt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_int_1d_root",
            "field_type": SummaryDynamicInt1DRoot,
        },
    )
    phase: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    power: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    power_launched: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    current: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    energy_fast: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryHCd(IdsBaseClass):
    """

    :ivar ec : Set of ECRH/ECCD launchers
    :ivar nbi : Set of NBI units
    :ivar ic : Set of ICRH launchers
    :ivar lh : Set of LHCD launchers
    :ivar power_ec : Total EC power coupled to the plasma
    :ivar power_launched_ec : Total EC power launched from EC launchers into the vacuum vessel
    :ivar power_nbi : Total NBI power coupled to the plasma
    :ivar power_launched_nbi : Total NBI power launched from neutral beam injectors into the vacuum vessel
    :ivar power_launched_nbi_co_injected_ratio : Ratio of co-injected beam launched power to total NBI launched power. Is set to 1 for purely perpendicular injection
    :ivar power_ic : Total IC power coupled to the plasma
    :ivar power_launched_ic : Total IC power launched from IC antennas into the vacuum vessel
    :ivar power_lh : Total LH power coupled to the plasma
    :ivar power_launched_lh : Total LH power launched from LH antennas into the vacuum vessel
    :ivar power_additional : Total additional external power (NBI+EC+IC+LH, without ohmic) coupled to the plasma
    """

    class Meta:
        name = "summary_h_cd"
        is_root_ids = False

    ec: Optional[SummaryHCdEc] = field(
        default_factory=lambda: StructArray(type_input=SummaryHCdEc),
        metadata={
            "imas_type": "summary_h_cd_ec",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": SummaryHCdEc,
        },
    )
    nbi: Optional[SummaryHCdNbi] = field(
        default_factory=lambda: StructArray(type_input=SummaryHCdNbi),
        metadata={
            "imas_type": "summary_h_cd_nbi",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": SummaryHCdNbi,
        },
    )
    ic: Optional[SummaryHCdIc] = field(
        default_factory=lambda: StructArray(type_input=SummaryHCdIc),
        metadata={
            "imas_type": "summary_h_cd_ic",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": SummaryHCdIc,
        },
    )
    lh: Optional[SummaryHCdLh] = field(
        default_factory=lambda: StructArray(type_input=SummaryHCdLh),
        metadata={
            "imas_type": "summary_h_cd_lh",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": SummaryHCdLh,
        },
    )
    power_ec: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    power_launched_ec: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    power_nbi: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    power_launched_nbi: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    power_launched_nbi_co_injected_ratio: Optional[SummaryDynamicFlt1DRoot] = (
        field(
            default=None,
            metadata={
                "imas_type": "summary_dynamic_flt_1d_root",
                "field_type": SummaryDynamicFlt1DRoot,
            },
        )
    )
    power_ic: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    power_launched_ic: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    power_lh: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    power_launched_lh: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )
    power_additional: Optional[SummaryDynamicFlt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_flt_1d_root",
            "field_type": SummaryDynamicFlt1DRoot,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryDisruptionDecayLinear(IdsBaseClass):
    """

    :ivar x1 : User-defined parameter, see description of linear_custom
    :ivar x2 : User-defined value, see description of linear_custom
    :ivar decay_time : Decay time
    """

    class Meta:
        name = "summary_disruption_decay_linear"
        is_root_ids = False

    x1: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    x2: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    decay_time: Optional[SummaryConstantFlt0D] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_flt_0d",
            "field_type": SummaryConstantFlt0D,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryDisruptionDecayTimes(IdsBaseClass):
    """

    :ivar linear_20_80 : Decay time defined as (t(0.2)-t(0.8))/0.6, where t(X) corresponds to the time where this quantity reaches X*100% of its pre-disruptive value
    :ivar linear_custom : Decay time defined as (t(X2)-t(X1))/(X1-X2), where t(Xj) corresponds to the time where this quantity reaches Xj*100% of its pre-disruptive value
    :ivar exponential : Exponential decay time (tau) used when the process is described by an exponential function (exp(-(t-t0)/tau))). Here &#34;t&#34; is time and &#34;t0&#34; is the time where the decay process starts
    """

    class Meta:
        name = "summary_disruption_decay_times"
        is_root_ids = False

    linear_20_80: Optional[SummaryConstantFlt0D] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_flt_0d",
            "field_type": SummaryConstantFlt0D,
        },
    )
    linear_custom: Optional[SummaryDisruptionDecayLinear] = field(
        default=None,
        metadata={
            "imas_type": "summary_disruption_decay_linear",
            "field_type": SummaryDisruptionDecayLinear,
        },
    )
    exponential: Optional[SummaryConstantFlt0D] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_flt_0d",
            "field_type": SummaryConstantFlt0D,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryDisruptionDecay(IdsBaseClass):
    """

    :ivar ip : Total toroidal plasma current (including runaway electrons and halo currents)
    :ivar current_runaways : Total toroidal current carried by runaway electrons
    :ivar t_e_volume_average : Volume average electron temperature
    :ivar t_e_magnetic_axis : Electron temperature at the magnetic axis
    :ivar energy_thermal : Thermal plasma energy content = 3/2 * integral over the plasma volume of the thermal pressure
    """

    class Meta:
        name = "summary_disruption_decay"
        is_root_ids = False

    ip: Optional[SummaryDisruptionDecayTimes] = field(
        default=None,
        metadata={
            "imas_type": "summary_disruption_decay_times",
            "field_type": SummaryDisruptionDecayTimes,
        },
    )
    current_runaways: Optional[SummaryDisruptionDecayTimes] = field(
        default=None,
        metadata={
            "imas_type": "summary_disruption_decay_times",
            "field_type": SummaryDisruptionDecayTimes,
        },
    )
    t_e_volume_average: Optional[SummaryDisruptionDecayTimes] = field(
        default=None,
        metadata={
            "imas_type": "summary_disruption_decay_times",
            "field_type": SummaryDisruptionDecayTimes,
        },
    )
    t_e_magnetic_axis: Optional[SummaryDisruptionDecayTimes] = field(
        default=None,
        metadata={
            "imas_type": "summary_disruption_decay_times",
            "field_type": SummaryDisruptionDecayTimes,
        },
    )
    energy_thermal: Optional[SummaryDisruptionDecayTimes] = field(
        default=None,
        metadata={
            "imas_type": "summary_disruption_decay_times",
            "field_type": SummaryDisruptionDecayTimes,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryDisruption(IdsBaseClass):
    """

    :ivar time : Time of the disruption
    :ivar time_radiated_power_max : Time of maximum radiated power, relative to the time of the disruption
    :ivar time_half_ip : Time at which the plasma current has fallen to half of the initial current at the start of the disruption, relative to the time of the disruption
    :ivar vertical_displacement : Direction of the plasma vertical displacement just before the disruption 1 (upwards) / 0 (no displacement)/ -1 (downwards)
    :ivar mitigation_valve : Flag indicating whether any disruption mitigation valve has been used (1) or none (0)
    :ivar decay_times : Characteristic decay times describing the loss of different quantities during the disruption
    """

    class Meta:
        name = "summary_disruption"
        is_root_ids = False

    time: Optional[SummaryConstantFlt0D] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_flt_0d",
            "field_type": SummaryConstantFlt0D,
        },
    )
    time_radiated_power_max: Optional[SummaryConstantFlt0D] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_flt_0d",
            "field_type": SummaryConstantFlt0D,
        },
    )
    time_half_ip: Optional[SummaryConstantFlt0D] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_flt_0d",
            "field_type": SummaryConstantFlt0D,
        },
    )
    vertical_displacement: Optional[SummaryConstantInt0D] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_int_0d",
            "field_type": SummaryConstantInt0D,
        },
    )
    mitigation_valve: Optional[SummaryConstantInt0D] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_int_0d",
            "field_type": SummaryConstantInt0D,
        },
    )
    decay_times: Optional[SummaryDisruptionDecay] = field(
        default=None,
        metadata={
            "imas_type": "summary_disruption_decay",
            "field_type": SummaryDisruptionDecay,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryWall(IdsBaseClass):
    """

    :ivar material : Wall material
    :ivar evaporation : Chemical formula of the evaporated material or gas used to cover the vaccum vessel wall. NONE for no evaporation.
    """

    class Meta:
        name = "summary_wall"
        is_root_ids = False

    material: Optional[IdentifierStatic] = field(
        default=None,
        metadata={
            "imas_type": "identifier_static",
            "field_type": IdentifierStatic,
        },
    )
    evaporation: Optional[SummaryStaticStr0D] = field(
        default=None,
        metadata={
            "imas_type": "summary_static_str_0d",
            "field_type": SummaryStaticStr0D,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SummaryLimiter(IdsBaseClass):
    """

    :ivar material : Limiter material
    """

    class Meta:
        name = "summary_limiter"
        is_root_ids = False

    material: Optional[IdentifierStatic] = field(
        default=None,
        metadata={
            "imas_type": "identifier_static",
            "field_type": IdentifierStatic,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class Summary(IdsBaseClass):
    """

    :ivar ids_properties :
    :ivar tag : Tag qualifying this data entry (or a list of data entries)
    :ivar configuration : Device configuration (the content may be device-specific)
    :ivar magnetic_shear_flag : Magnetic field shear indicator for stellarators: 0 for shearless stellarators (W7-A, W7-AS, W7-X); 1, otherwise. See [Stroth U. et al 1996 Nucl. Fusion 36 1063]
    :ivar stationary_phase_flag : This flag is set to one if the pulse is in a stationary phase from the point of the of the energy content (if the time derivative of the energy dW/dt can be neglected when calculating tau_E as W/(P_abs-dW/dt).)
    :ivar midplane : Choice of midplane definition (use the lowest index number if more than one value is relevant)
    :ivar global_quantities : Various global quantities derived from the profiles
    :ivar local : Plasma parameter values at different locations
    :ivar boundary : Description of the plasma boundary
    :ivar pedestal_fits : Quantities derived from specific fits of pedestal profiles, typically used in the Pedestal Database.
    :ivar line_average : Line average plasma parameters
    :ivar volume_average : Volume average plasma parameters
    :ivar disruption : Disruption characteristics, if the pulse is terminated by a disruption
    :ivar elms : Edge Localized Modes related quantities
    :ivar fusion : Fusion reactions
    :ivar gas_injection_rates : Gas injection rates in equivalent electrons.s^-1
    :ivar gas_injection_accumulated : Accumulated injected gas since the plasma breakdown in equivalent electrons
    :ivar gas_injection_prefill : Accumulated injected gas during the prefill in equivalent electrons
    :ivar heating_current_drive : Heating and current drive parameters
    :ivar kicks : Vertical kicks of the plasma position
    :ivar pellets : Pellet related quantities
    :ivar rmps : Resonant magnetic perturbations related quantities
    :ivar runaways : Runaway electrons
    :ivar scrape_off_layer : Scrape-Off-Layer (SOL) characteristics
    :ivar wall : Wall characteristics
    :ivar limiter : Limiter characteristics
    :ivar time_breakdown : Time of the plasma breakdown
    :ivar plasma_duration : Duration of existence of a confined plasma during the pulse
    :ivar time_width : In case the time-dependent quantities of this IDS are averaged over a time interval, this node is the width of this time interval (empty otherwise). By convention, the time interval starts at time-time_width and ends at time.
    :ivar code :
    :ivar time : Generic time
    """

    class Meta:
        name = "summary"
        is_root_ids = True

    ids_properties: Optional[IdsProperties] = field(
        default=None,
        metadata={"imas_type": "ids_properties", "field_type": IdsProperties},
    )
    tag: Optional[EntryTag] = field(
        default=None,
        metadata={"imas_type": "entry_tag", "field_type": EntryTag},
    )
    configuration: Optional[SummaryStaticStr0D] = field(
        default=None,
        metadata={
            "imas_type": "summary_static_str_0d",
            "field_type": SummaryStaticStr0D,
        },
    )
    magnetic_shear_flag: Optional[SummaryStaticInt0D] = field(
        default=None,
        metadata={
            "imas_type": "summary_static_int_0d",
            "field_type": SummaryStaticInt0D,
        },
    )
    stationary_phase_flag: Optional[SummaryDynamicInt1DRoot] = field(
        default=None,
        metadata={
            "imas_type": "summary_dynamic_int_1d_root",
            "field_type": SummaryDynamicInt1DRoot,
        },
    )
    midplane: Optional[IdentifierStatic] = field(
        default=None,
        metadata={
            "imas_type": "identifier_static",
            "field_type": IdentifierStatic,
        },
    )
    global_quantities: Optional[SummaryGlobalQuantities] = field(
        default=None,
        metadata={
            "imas_type": "summary_global_quantities",
            "field_type": SummaryGlobalQuantities,
        },
    )
    local: Optional[SummaryLocal] = field(
        default=None,
        metadata={"imas_type": "summary_local", "field_type": SummaryLocal},
    )
    boundary: Optional[SummaryBoundary] = field(
        default=None,
        metadata={
            "imas_type": "summary_boundary",
            "field_type": SummaryBoundary,
        },
    )
    pedestal_fits: Optional[SummaryPedestalFits] = field(
        default=None,
        metadata={
            "imas_type": "summary_pedestal_fits",
            "field_type": SummaryPedestalFits,
        },
    )
    line_average: Optional[SummaryAverageQuantities] = field(
        default=None,
        metadata={
            "imas_type": "summary_average_quantities",
            "field_type": SummaryAverageQuantities,
        },
    )
    volume_average: Optional[SummaryAverageQuantities] = field(
        default=None,
        metadata={
            "imas_type": "summary_average_quantities",
            "field_type": SummaryAverageQuantities,
        },
    )
    disruption: Optional[SummaryDisruption] = field(
        default=None,
        metadata={
            "imas_type": "summary_disruption",
            "field_type": SummaryDisruption,
        },
    )
    elms: Optional[SummaryElms] = field(
        default=None,
        metadata={"imas_type": "summary_elms", "field_type": SummaryElms},
    )
    fusion: Optional[SummaryFusion] = field(
        default=None,
        metadata={"imas_type": "summary_fusion", "field_type": SummaryFusion},
    )
    gas_injection_rates: Optional[SummaryGasInjection] = field(
        default=None,
        metadata={
            "imas_type": "summary_gas_injection",
            "field_type": SummaryGasInjection,
        },
    )
    gas_injection_accumulated: Optional[SummaryGasInjectionAccumulated] = field(
        default=None,
        metadata={
            "imas_type": "summary_gas_injection_accumulated",
            "field_type": SummaryGasInjectionAccumulated,
        },
    )
    gas_injection_prefill: Optional[SummaryGasInjectionPrefill] = field(
        default=None,
        metadata={
            "imas_type": "summary_gas_injection_prefill",
            "field_type": SummaryGasInjectionPrefill,
        },
    )
    heating_current_drive: Optional[SummaryHCd] = field(
        default=None,
        metadata={"imas_type": "summary_h_cd", "field_type": SummaryHCd},
    )
    kicks: Optional[SummaryKicks] = field(
        default=None,
        metadata={"imas_type": "summary_kicks", "field_type": SummaryKicks},
    )
    pellets: Optional[SummaryPellets] = field(
        default=None,
        metadata={"imas_type": "summary_pellets", "field_type": SummaryPellets},
    )
    rmps: Optional[SummaryRmp] = field(
        default=None,
        metadata={"imas_type": "summary_rmp", "field_type": SummaryRmp},
    )
    runaways: Optional[SummaryRunaways] = field(
        default=None,
        metadata={
            "imas_type": "summary_runaways",
            "field_type": SummaryRunaways,
        },
    )
    scrape_off_layer: Optional[SummarySol] = field(
        default=None,
        metadata={"imas_type": "summary_sol", "field_type": SummarySol},
    )
    wall: Optional[SummaryWall] = field(
        default=None,
        metadata={"imas_type": "summary_wall", "field_type": SummaryWall},
    )
    limiter: Optional[SummaryLimiter] = field(
        default=None,
        metadata={"imas_type": "summary_limiter", "field_type": SummaryLimiter},
    )
    time_breakdown: Optional[SummaryConstantFlt0D] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_flt_0d",
            "field_type": SummaryConstantFlt0D,
        },
    )
    plasma_duration: Optional[SummaryConstantFlt0D] = field(
        default=None,
        metadata={
            "imas_type": "summary_constant_flt_0d",
            "field_type": SummaryConstantFlt0D,
        },
    )
    time_width: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../time"},
            "field_type": np.ndarray,
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
