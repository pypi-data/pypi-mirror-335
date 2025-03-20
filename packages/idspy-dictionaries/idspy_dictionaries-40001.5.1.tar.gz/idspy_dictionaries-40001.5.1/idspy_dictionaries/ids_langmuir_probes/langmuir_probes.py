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
class Rphiz0DStatic(IdsBaseClass):
    """

    :ivar r : Major radius
    :ivar phi : Toroidal angle (oriented counter-clockwise when viewing from above)
    :ivar z : Height
    """

    class Meta:
        name = "rphiz0d_static"
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


@idspy_dataclass(repr=False, slots=True)
class PhysicalQuantityFlt1DTime1(IdsBaseClass):
    """

    :ivar data : Data
    :ivar validity_timed : Indicator of the validity of the data for each time slice. 0: valid from automated processing, 1: valid and certified by the diagnostic RO; - 1 means problem identified in the data processing (request verification by the diagnostic RO), -2: invalid data, should not be used (values lower than -2 have a code-specific meaning detailing the origin of their invalidity)
    :ivar validity : Indicator of the validity of the data for the whole acquisition period. 0: valid from automated processing, 1: valid and certified by the diagnostic RO; - 1 means problem identified in the data processing (request verification by the diagnostic RO), -2: invalid data, should not be used (values lower than -2 have a code-specific meaning detailing the origin of their invalidity)
    """

    class Meta:
        name = "physical_quantity_flt_1d_time_1"
        is_root_ids = False

    data: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time"},
            "field_type": np.ndarray,
        },
    )
    validity_timed: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=int),
        metadata={
            "imas_type": "INT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time"},
            "field_type": np.ndarray,
        },
    )
    validity: Optional[int] = field(
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
class LangmuirProbesPlungePhysicalQuantity2(IdsBaseClass):
    """

    :ivar data : Data
    :ivar validity_timed : Indicator of the validity of the data for each time slice. 0: valid from automated processing, 1: valid and certified by the diagnostic RO; - 1 means problem identified in the data processing (request verification by the diagnostic RO), -2: invalid data, should not be used (values lower than -2 have a code-specific meaning detailing the origin of their invalidity)
    :ivar validity : Indicator of the validity of the data for the whole plunge. 0: valid from automated processing, 1: valid and certified by the diagnostic RO; - 1 means problem identified in the data processing (request verification by the diagnostic RO), -2: invalid data, should not be used (values lower than -2 have a code-specific meaning detailing the origin of their invalidity)
    """

    class Meta:
        name = "langmuir_probes_plunge_physical_quantity_2"
        is_root_ids = False

    data: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../time_within_plunge"},
            "field_type": np.ndarray,
        },
    )
    validity_timed: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=int),
        metadata={
            "imas_type": "INT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../time_within_plunge"},
            "field_type": np.ndarray,
        },
    )
    validity: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )


@idspy_dataclass(repr=False, slots=True)
class LangmuirProbesPlungePhysicalQuantity(IdsBaseClass):
    """

    :ivar data : Data
    :ivar validity_timed : Indicator of the validity of the data for each time slice. 0: valid from automated processing, 1: valid and certified by the diagnostic RO; - 1 means problem identified in the data processing (request verification by the diagnostic RO), -2: invalid data, should not be used (values lower than -2 have a code-specific meaning detailing the origin of their invalidity)
    :ivar validity : Indicator of the validity of the data for the whole plunge. 0: valid from automated processing, 1: valid and certified by the diagnostic RO; - 1 means problem identified in the data processing (request verification by the diagnostic RO), -2: invalid data, should not be used (values lower than -2 have a code-specific meaning detailing the origin of their invalidity)
    """

    class Meta:
        name = "langmuir_probes_plunge_physical_quantity"
        is_root_ids = False

    data: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time_within_plunge"},
            "field_type": np.ndarray,
        },
    )
    validity_timed: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=int),
        metadata={
            "imas_type": "INT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time_within_plunge"},
            "field_type": np.ndarray,
        },
    )
    validity: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )


@idspy_dataclass(repr=False, slots=True)
class LangmuirProbesPlungeCollector(IdsBaseClass):
    """

    :ivar position : Position of the collector
    :ivar v_floating : Floating potential
    :ivar v_floating_sigma : Standard deviation of the floating potential, corresponding to the fluctuations of the quantity over time
    :ivar t_e : Electron temperature
    :ivar t_i : Ion temperature
    :ivar j_i_parallel : Ion parallel current density at the probe position
    :ivar ion_saturation_current : Ion saturation current measured by the probe
    :ivar j_i_saturation : Ion saturation current density
    :ivar j_i_skew : Skew of the ion saturation current density
    :ivar j_i_kurtosis : Pearson kurtosis of the ion saturation current density
    :ivar j_i_sigma : Standard deviation of the ion saturation current density, corresponding to the fluctuations of the quantity over time
    :ivar heat_flux_parallel : Parallel heat flux at the probe position
    """

    class Meta:
        name = "langmuir_probes_plunge_collector"
        is_root_ids = False

    position: Optional[LangmuirProbesPositionReciprocating2] = field(
        default=None,
        metadata={
            "imas_type": "langmuir_probes_position_reciprocating_2",
            "field_type": LangmuirProbesPositionReciprocating2,
        },
    )
    v_floating: Optional[LangmuirProbesPlungePhysicalQuantity2] = field(
        default=None,
        metadata={
            "imas_type": "langmuir_probes_plunge_physical_quantity_2",
            "field_type": LangmuirProbesPlungePhysicalQuantity2,
        },
    )
    v_floating_sigma: Optional[LangmuirProbesPlungePhysicalQuantity2] = field(
        default=None,
        metadata={
            "imas_type": "langmuir_probes_plunge_physical_quantity_2",
            "field_type": LangmuirProbesPlungePhysicalQuantity2,
        },
    )
    t_e: Optional[LangmuirProbesPlungePhysicalQuantity2] = field(
        default=None,
        metadata={
            "imas_type": "langmuir_probes_plunge_physical_quantity_2",
            "field_type": LangmuirProbesPlungePhysicalQuantity2,
        },
    )
    t_i: Optional[LangmuirProbesPlungePhysicalQuantity2] = field(
        default=None,
        metadata={
            "imas_type": "langmuir_probes_plunge_physical_quantity_2",
            "field_type": LangmuirProbesPlungePhysicalQuantity2,
        },
    )
    j_i_parallel: Optional[LangmuirProbesPlungePhysicalQuantity2] = field(
        default=None,
        metadata={
            "imas_type": "langmuir_probes_plunge_physical_quantity_2",
            "field_type": LangmuirProbesPlungePhysicalQuantity2,
        },
    )
    ion_saturation_current: Optional[LangmuirProbesPlungePhysicalQuantity2] = (
        field(
            default=None,
            metadata={
                "imas_type": "langmuir_probes_plunge_physical_quantity_2",
                "field_type": LangmuirProbesPlungePhysicalQuantity2,
            },
        )
    )
    j_i_saturation: Optional[LangmuirProbesPlungePhysicalQuantity2] = field(
        default=None,
        metadata={
            "imas_type": "langmuir_probes_plunge_physical_quantity_2",
            "field_type": LangmuirProbesPlungePhysicalQuantity2,
        },
    )
    j_i_skew: Optional[LangmuirProbesPlungePhysicalQuantity2] = field(
        default=None,
        metadata={
            "imas_type": "langmuir_probes_plunge_physical_quantity_2",
            "field_type": LangmuirProbesPlungePhysicalQuantity2,
        },
    )
    j_i_kurtosis: Optional[LangmuirProbesPlungePhysicalQuantity2] = field(
        default=None,
        metadata={
            "imas_type": "langmuir_probes_plunge_physical_quantity_2",
            "field_type": LangmuirProbesPlungePhysicalQuantity2,
        },
    )
    j_i_sigma: Optional[LangmuirProbesPlungePhysicalQuantity2] = field(
        default=None,
        metadata={
            "imas_type": "langmuir_probes_plunge_physical_quantity_2",
            "field_type": LangmuirProbesPlungePhysicalQuantity2,
        },
    )
    heat_flux_parallel: Optional[LangmuirProbesPlungePhysicalQuantity2] = field(
        default=None,
        metadata={
            "imas_type": "langmuir_probes_plunge_physical_quantity_2",
            "field_type": LangmuirProbesPlungePhysicalQuantity2,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class LangmuirProbesPositionReciprocating2(IdsBaseClass):
    """

    :ivar r : Major radius
    :ivar z : Height
    :ivar phi : Toroidal angle
    :ivar validity_timed : Indicator of the validity of the position data for each time slice. 0: valid from automated processing, 1: valid and certified by the diagnostic RO; - 1 means problem identified in the data processing (request verification by the diagnostic RO), -2: invalid data, should not be used (values lower than -2 have a code-specific meaning detailing the origin of their invalidity)
    :ivar validity : Indicator of the validity of the position data for the whole plunge. 0: valid from automated processing, 1: valid and certified by the diagnostic RO; - 1 means problem identified in the data processing (request verification by the diagnostic RO), -2: invalid data, should not be used (values lower than -2 have a code-specific meaning detailing the origin of their invalidity)
    """

    class Meta:
        name = "langmuir_probes_position_reciprocating_2"
        is_root_ids = False

    r: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../time_within_plunge"},
            "field_type": np.ndarray,
        },
    )
    z: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../time_within_plunge"},
            "field_type": np.ndarray,
        },
    )
    phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../time_within_plunge"},
            "field_type": np.ndarray,
        },
    )
    validity_timed: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=int),
        metadata={
            "imas_type": "INT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../time_within_plunge"},
            "field_type": np.ndarray,
        },
    )
    validity: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )


@idspy_dataclass(repr=False, slots=True)
class LangmuirProbesPositionReciprocating(IdsBaseClass):
    """

    :ivar r : Major radius
    :ivar z : Height
    :ivar phi : Toroidal angle
    :ivar validity_timed : Indicator of the validity of the position data for each time slice. 0: valid from automated processing, 1: valid and certified by the diagnostic RO; - 1 means problem identified in the data processing (request verification by the diagnostic RO), -2: invalid data, should not be used (values lower than -2 have a code-specific meaning detailing the origin of their invalidity)
    :ivar validity : Indicator of the validity of the position data for the whole plunge. 0: valid from automated processing, 1: valid and certified by the diagnostic RO; - 1 means problem identified in the data processing (request verification by the diagnostic RO), -2: invalid data, should not be used (values lower than -2 have a code-specific meaning detailing the origin of their invalidity)
    """

    class Meta:
        name = "langmuir_probes_position_reciprocating"
        is_root_ids = False

    r: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time_within_plunge"},
            "field_type": np.ndarray,
        },
    )
    z: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time_within_plunge"},
            "field_type": np.ndarray,
        },
    )
    phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time_within_plunge"},
            "field_type": np.ndarray,
        },
    )
    validity_timed: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=int),
        metadata={
            "imas_type": "INT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time_within_plunge"},
            "field_type": np.ndarray,
        },
    )
    validity: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )


@idspy_dataclass(repr=False, slots=True)
class LangmuirProbesMultiTemperature(IdsBaseClass):
    """

    :ivar t_e : Electron temperature
    :ivar t_i : Ion temperature
    :ivar time : Timebase for the dynamic nodes of this probe located at this level of the IDS structure
    """

    class Meta:
        name = "langmuir_probes_multi_temperature"
        is_root_ids = False

    t_e: Optional[PhysicalQuantityFlt1DTime1] = field(
        default=None,
        metadata={
            "imas_type": "physical_quantity_flt_1d_time_1",
            "field_type": PhysicalQuantityFlt1DTime1,
        },
    )
    t_i: Optional[PhysicalQuantityFlt1DTime1] = field(
        default=None,
        metadata={
            "imas_type": "physical_quantity_flt_1d_time_1",
            "field_type": PhysicalQuantityFlt1DTime1,
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
class LangmuirProbesEmbedded(IdsBaseClass):
    """

    :ivar name : Short string identifier (unique for a given device)
    :ivar description : Description, e.g. “channel viewing the upper divertor”
    :ivar position : Position of the measurements
    :ivar surface_area : Area of the probe surface exposed to the plasma (use when assuming constant effective collection area)
    :ivar surface_area_effective : Effective collection area of the probe surface, varying with time due to e.g. changes in the magnetic field line incidence angle
    :ivar v_floating : Floating potential
    :ivar v_floating_sigma : Standard deviation of the floating potential, corresponding to the fluctuations of the quantity over time
    :ivar v_plasma : Plasma potential
    :ivar t_e : Electron temperature
    :ivar n_e : Electron density
    :ivar t_i : Ion temperature
    :ivar j_i_parallel : Ion parallel current density at the probe position
    :ivar j_i_parallel_sigma : Standard deviation of ion parallel current density at the probe position
    :ivar ion_saturation_current : Ion saturation current measured by the probe
    :ivar j_i_saturation : Ion saturation current density
    :ivar j_i_saturation_skew : Skew of the ion saturation current density
    :ivar j_i_saturation_kurtosis : Pearson kurtosis of the ion saturation current density
    :ivar j_i_saturation_sigma : Standard deviation of the ion saturation current density, corresponding to the fluctuations of the quantity over time
    :ivar heat_flux_parallel : Parallel heat flux at the probe position
    :ivar fluence : Positive charge fluence normal to an ideal axisymmetric surface of the divertor (assuming no shaping), estimated at the probe location.
    :ivar b_field_angle : Incident angle of the magnetic field with respect to PFC surface
    :ivar distance_separatrix_midplane : Distance between the measurement position and the separatrix, mapped along flux surfaces to the outboard midplane, in the major radius direction. Positive value means the measurement is outside of the separatrix.
    :ivar multi_temperature_fits : Set of temperatures describing the electron and ion distribution functions in case of multi-temperature fits
    :ivar time : Timebase for the dynamic nodes of this probe located at this level of the IDS structure
    """

    class Meta:
        name = "langmuir_probes_embedded"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    description: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    position: Optional[Rphiz0DStatic] = field(
        default=None,
        metadata={"imas_type": "rphiz0d_static", "field_type": Rphiz0DStatic},
    )
    surface_area: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    surface_area_effective: Optional[PhysicalQuantityFlt1DTime1] = field(
        default=None,
        metadata={
            "imas_type": "physical_quantity_flt_1d_time_1",
            "field_type": PhysicalQuantityFlt1DTime1,
        },
    )
    v_floating: Optional[PhysicalQuantityFlt1DTime1] = field(
        default=None,
        metadata={
            "imas_type": "physical_quantity_flt_1d_time_1",
            "field_type": PhysicalQuantityFlt1DTime1,
        },
    )
    v_floating_sigma: Optional[PhysicalQuantityFlt1DTime1] = field(
        default=None,
        metadata={
            "imas_type": "physical_quantity_flt_1d_time_1",
            "field_type": PhysicalQuantityFlt1DTime1,
        },
    )
    v_plasma: Optional[PhysicalQuantityFlt1DTime1] = field(
        default=None,
        metadata={
            "imas_type": "physical_quantity_flt_1d_time_1",
            "field_type": PhysicalQuantityFlt1DTime1,
        },
    )
    t_e: Optional[PhysicalQuantityFlt1DTime1] = field(
        default=None,
        metadata={
            "imas_type": "physical_quantity_flt_1d_time_1",
            "field_type": PhysicalQuantityFlt1DTime1,
        },
    )
    n_e: Optional[PhysicalQuantityFlt1DTime1] = field(
        default=None,
        metadata={
            "imas_type": "physical_quantity_flt_1d_time_1",
            "field_type": PhysicalQuantityFlt1DTime1,
        },
    )
    t_i: Optional[PhysicalQuantityFlt1DTime1] = field(
        default=None,
        metadata={
            "imas_type": "physical_quantity_flt_1d_time_1",
            "field_type": PhysicalQuantityFlt1DTime1,
        },
    )
    j_i_parallel: Optional[PhysicalQuantityFlt1DTime1] = field(
        default=None,
        metadata={
            "imas_type": "physical_quantity_flt_1d_time_1",
            "field_type": PhysicalQuantityFlt1DTime1,
        },
    )
    j_i_parallel_sigma: Optional[PhysicalQuantityFlt1DTime1] = field(
        default=None,
        metadata={
            "imas_type": "physical_quantity_flt_1d_time_1",
            "field_type": PhysicalQuantityFlt1DTime1,
        },
    )
    ion_saturation_current: Optional[PhysicalQuantityFlt1DTime1] = field(
        default=None,
        metadata={
            "imas_type": "physical_quantity_flt_1d_time_1",
            "field_type": PhysicalQuantityFlt1DTime1,
        },
    )
    j_i_saturation: Optional[PhysicalQuantityFlt1DTime1] = field(
        default=None,
        metadata={
            "imas_type": "physical_quantity_flt_1d_time_1",
            "field_type": PhysicalQuantityFlt1DTime1,
        },
    )
    j_i_saturation_skew: Optional[PhysicalQuantityFlt1DTime1] = field(
        default=None,
        metadata={
            "imas_type": "physical_quantity_flt_1d_time_1",
            "field_type": PhysicalQuantityFlt1DTime1,
        },
    )
    j_i_saturation_kurtosis: Optional[PhysicalQuantityFlt1DTime1] = field(
        default=None,
        metadata={
            "imas_type": "physical_quantity_flt_1d_time_1",
            "field_type": PhysicalQuantityFlt1DTime1,
        },
    )
    j_i_saturation_sigma: Optional[PhysicalQuantityFlt1DTime1] = field(
        default=None,
        metadata={
            "imas_type": "physical_quantity_flt_1d_time_1",
            "field_type": PhysicalQuantityFlt1DTime1,
        },
    )
    heat_flux_parallel: Optional[PhysicalQuantityFlt1DTime1] = field(
        default=None,
        metadata={
            "imas_type": "physical_quantity_flt_1d_time_1",
            "field_type": PhysicalQuantityFlt1DTime1,
        },
    )
    fluence: Optional[PhysicalQuantityFlt1DTime1] = field(
        default=None,
        metadata={
            "imas_type": "physical_quantity_flt_1d_time_1",
            "field_type": PhysicalQuantityFlt1DTime1,
        },
    )
    b_field_angle: Optional[PhysicalQuantityFlt1DTime1] = field(
        default=None,
        metadata={
            "imas_type": "physical_quantity_flt_1d_time_1",
            "field_type": PhysicalQuantityFlt1DTime1,
        },
    )
    distance_separatrix_midplane: Optional[PhysicalQuantityFlt1DTime1] = field(
        default=None,
        metadata={
            "imas_type": "physical_quantity_flt_1d_time_1",
            "field_type": PhysicalQuantityFlt1DTime1,
        },
    )
    multi_temperature_fits: Optional[LangmuirProbesMultiTemperature] = field(
        default_factory=lambda: StructArray(
            type_input=LangmuirProbesMultiTemperature
        ),
        metadata={
            "imas_type": "langmuir_probes_multi_temperature",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": LangmuirProbesMultiTemperature,
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
class LangmuirProbesPlunge(IdsBaseClass):
    """

    :ivar position_average : Average position of the measurements derived from multiple collectors
    :ivar collector : Set of probe collectors including measurements specific to each collector. The number of collectors (size of this array of structure) is assumed to remain constant for all plunges
    :ivar v_plasma : Plasma potential
    :ivar t_e_average : Electron temperature (upstream to downstream average)
    :ivar t_i_average : Ion temperature (upstream to downstream average)
    :ivar n_e : Electron density
    :ivar b_field_angle : Incident angle of the magnetic field with respect to PFC surface
    :ivar distance_separatrix_midplane : Distance between the measurement position and the separatrix, mapped along flux surfaces to the outboard midplane, in the major radius direction. Positive value means the measurement is outside of the separatrix.
    :ivar distance_x_point_z : Distance in the z direction of the measurement position to the closest X-point (Zmeasurement-Zx_point)
    :ivar mach_number_parallel : Parallel Mach number
    :ivar time_within_plunge : Time vector for describing the dynamics within the plunge
    :ivar time : Time of maximum penetration of the probe during a given plunge
    """

    class Meta:
        name = "langmuir_probes_plunge"
        is_root_ids = False

    position_average: Optional[LangmuirProbesPositionReciprocating] = field(
        default=None,
        metadata={
            "imas_type": "langmuir_probes_position_reciprocating",
            "field_type": LangmuirProbesPositionReciprocating,
        },
    )
    collector: Optional[LangmuirProbesPlungeCollector] = field(
        default_factory=lambda: StructArray(
            type_input=LangmuirProbesPlungeCollector
        ),
        metadata={
            "imas_type": "langmuir_probes_plunge_collector",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": LangmuirProbesPlungeCollector,
        },
    )
    v_plasma: Optional[LangmuirProbesPlungePhysicalQuantity] = field(
        default=None,
        metadata={
            "imas_type": "langmuir_probes_plunge_physical_quantity",
            "field_type": LangmuirProbesPlungePhysicalQuantity,
        },
    )
    t_e_average: Optional[LangmuirProbesPlungePhysicalQuantity] = field(
        default=None,
        metadata={
            "imas_type": "langmuir_probes_plunge_physical_quantity",
            "field_type": LangmuirProbesPlungePhysicalQuantity,
        },
    )
    t_i_average: Optional[LangmuirProbesPlungePhysicalQuantity] = field(
        default=None,
        metadata={
            "imas_type": "langmuir_probes_plunge_physical_quantity",
            "field_type": LangmuirProbesPlungePhysicalQuantity,
        },
    )
    n_e: Optional[LangmuirProbesPlungePhysicalQuantity] = field(
        default=None,
        metadata={
            "imas_type": "langmuir_probes_plunge_physical_quantity",
            "field_type": LangmuirProbesPlungePhysicalQuantity,
        },
    )
    b_field_angle: Optional[LangmuirProbesPlungePhysicalQuantity] = field(
        default=None,
        metadata={
            "imas_type": "langmuir_probes_plunge_physical_quantity",
            "field_type": LangmuirProbesPlungePhysicalQuantity,
        },
    )
    distance_separatrix_midplane: Optional[
        LangmuirProbesPlungePhysicalQuantity
    ] = field(
        default=None,
        metadata={
            "imas_type": "langmuir_probes_plunge_physical_quantity",
            "field_type": LangmuirProbesPlungePhysicalQuantity,
        },
    )
    distance_x_point_z: Optional[LangmuirProbesPlungePhysicalQuantity] = field(
        default=None,
        metadata={
            "imas_type": "langmuir_probes_plunge_physical_quantity",
            "field_type": LangmuirProbesPlungePhysicalQuantity,
        },
    )
    mach_number_parallel: Optional[LangmuirProbesPlungePhysicalQuantity] = (
        field(
            default=None,
            metadata={
                "imas_type": "langmuir_probes_plunge_physical_quantity",
                "field_type": LangmuirProbesPlungePhysicalQuantity,
            },
        )
    )
    time_within_plunge: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class LangmuirProbesReciprocating(IdsBaseClass):
    """

    :ivar name : Short string identifier (unique for a given device)
    :ivar description : Description, e.g. “channel viewing the upper divertor”
    :ivar surface_area : Area of the surface exposed to the plasma of each collector (constant assuming negligible dependence on e.g. the magnetic field line angle)
    :ivar plunge : Set of plunges of this probe during the pulse, each plunge being recorded as a time slice from the Access Layer point of view. The time child node corresponds to the time of maximum penetration of the probe during a given plunge. The dynamics of physical quantities within the plunge are described via the time_within_plunge vector.
    """

    class Meta:
        name = "langmuir_probes_reciprocating"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    description: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    surface_area: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../plunge(itime)/collector"},
            "field_type": np.ndarray,
        },
    )
    plunge: Optional[LangmuirProbesPlunge] = field(
        default_factory=lambda: StructArray(type_input=LangmuirProbesPlunge),
        metadata={
            "imas_type": "langmuir_probes_plunge",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": LangmuirProbesPlunge,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class LangmuirProbes(IdsBaseClass):
    """

    :ivar ids_properties :
    :ivar midplane : Choice of midplane definition for the mapping of measurements on an equilibrium (use the lowest index number if more than one value is relevant). Indicate the IMAS URI of the used equilibrium IDS in the ids_properties/provenance structure.
    :ivar embedded : Set of embedded (in a plasma facing component) probes
    :ivar reciprocating : Set of reciprocating probes
    :ivar latency : Upper bound of the delay between physical information received by the detector and data available on the real-time (RT) network.
    :ivar code :
    :ivar time : Generic time
    """

    class Meta:
        name = "langmuir_probes"
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
    embedded: Optional[LangmuirProbesEmbedded] = field(
        default_factory=lambda: StructArray(type_input=LangmuirProbesEmbedded),
        metadata={
            "imas_type": "langmuir_probes_embedded",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": LangmuirProbesEmbedded,
        },
    )
    reciprocating: Optional[LangmuirProbesReciprocating] = field(
        default_factory=lambda: StructArray(
            type_input=LangmuirProbesReciprocating
        ),
        metadata={
            "imas_type": "langmuir_probes_reciprocating",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": LangmuirProbesReciprocating,
        },
    )
    latency: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
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
