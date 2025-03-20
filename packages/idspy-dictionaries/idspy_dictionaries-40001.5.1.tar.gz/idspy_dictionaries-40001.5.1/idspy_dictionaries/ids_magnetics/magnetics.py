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
class SignalFlt1DValidity(IdsBaseClass):
    """

    :ivar data : Data
    :ivar validity_timed : Indicator of the validity of the data for each time slice. 0: valid from automated processing, 1: valid and certified by the diagnostic RO; - 1 means problem identified in the data processing (request verification by the diagnostic RO), -2: invalid data, should not be used (values lower than -2 have a code-specific meaning detailing the origin of their invalidity)
    :ivar validity : Indicator of the validity of the data for the whole acquisition period. 0: valid from automated processing, 1: valid and certified by the diagnostic RO; - 1 means problem identified in the data processing (request verification by the diagnostic RO), -2: invalid data, should not be used (values lower than -2 have a code-specific meaning detailing the origin of their invalidity)
    :ivar time : Time
    """

    class Meta:
        name = "signal_flt_1d_validity"
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
    validity_timed: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=int),
        metadata={
            "imas_type": "INT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../time"},
            "field_type": np.ndarray,
        },
    )
    validity: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
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
class LineOfSight2PointsRz(IdsBaseClass):
    """

    :ivar first_point : Position of the first point
    :ivar second_point : Position of the second point
    """

    class Meta:
        name = "line_of_sight_2points_rz"
        is_root_ids = False

    first_point: Optional[Rz0DStatic] = field(
        default=None,
        metadata={"imas_type": "rz0d_static", "field_type": Rz0DStatic},
    )
    second_point: Optional[Rz0DStatic] = field(
        default=None,
        metadata={"imas_type": "rz0d_static", "field_type": Rz0DStatic},
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
class MagneticsRogowski(IdsBaseClass):
    """

    :ivar name : Short string identifier (unique for a given device)
    :ivar description : Description, e.g. “channel viewing the upper divertor”
    :ivar measured_quantity : Quantity measured by the sensor
    :ivar position : List of (R,Z,phi) points defining the position of the coil guiding centre. Values defining a single segment must be entered in contiguous order
    :ivar indices_compound : Indices (from the rogowski_coil array of structure) of the partial Rogowskis used to build the coumpound signal (sum of the partial Rogowski signals). Can be set to any unique integer value for each section of a compound Rogowski coil. Use only if ../measure_quantity/index = 5, leave empty otherwise
    :ivar area : Effective area of the loop wrapped around the guiding centre. In case of multiple layers, sum of the areas of each layer
    :ivar turns_per_metre : Number of turns per unit length. In case of multiple layers, turns are counted for a single layer
    :ivar current : Measured current inside the Rogowski coil contour. The normal direction to the Rogowski coil is defined by the order of points in the list of guiding centre positions. The current is positive when oriented in the same direction as the normal.
    """

    class Meta:
        name = "magnetics_rogowski"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    description: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    measured_quantity: Optional[IdentifierStatic] = field(
        default=None,
        metadata={
            "imas_type": "identifier_static",
            "field_type": IdentifierStatic,
        },
    )
    position: Optional[Rphiz0DStatic] = field(
        default_factory=lambda: StructArray(type_input=Rphiz0DStatic),
        metadata={
            "imas_type": "rphiz0d_static",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": Rphiz0DStatic,
        },
    )
    indices_compound: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=int),
        metadata={
            "imas_type": "INT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    area: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    turns_per_metre: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    current: Optional[SignalFlt1DValidity] = field(
        default=None,
        metadata={
            "imas_type": "signal_flt_1d_validity",
            "field_type": SignalFlt1DValidity,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class MagneticsFluxLoop(IdsBaseClass):
    """

    :ivar name : Short string identifier (unique for a given device)
    :ivar description : Description, e.g. “channel viewing the upper divertor”
    :ivar type : Flux loop type
    :ivar position : List of (R,Z,phi) points defining the position of the loop (see data structure documentation FLUXLOOPposition.pdf)
    :ivar indices_differential : Indices (from the flux_loop array of structure) of the two flux loops used to build the flux difference flux(second index) - flux(first index). Use only if ../type/index = 6, leave empty otherwise
    :ivar area : Effective area (ratio between flux and average magnetic field over the loop)
    :ivar gm9 : Integral of 1/R over the loop area (ratio between flux and magnetic rigidity R0.B0). Use only if ../type/index = 3 to 6, leave empty otherwise.
    :ivar flux : Measured magnetic flux through loop with normal to enclosed surface determined by order of points
    :ivar voltage : Measured voltage between the loop terminals
    """

    class Meta:
        name = "magnetics_flux_loop"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    description: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    type: Optional[IdentifierStatic] = field(
        default=None,
        metadata={
            "imas_type": "identifier_static",
            "field_type": IdentifierStatic,
        },
    )
    position: Optional[Rphiz0DStatic] = field(
        default_factory=lambda: StructArray(type_input=Rphiz0DStatic),
        metadata={
            "imas_type": "rphiz0d_static",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": Rphiz0DStatic,
        },
    )
    indices_differential: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=int),
        metadata={
            "imas_type": "INT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...2"},
            "field_type": np.ndarray,
        },
    )
    area: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    gm9: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    flux: Optional[SignalFlt1DValidity] = field(
        default=None,
        metadata={
            "imas_type": "signal_flt_1d_validity",
            "field_type": SignalFlt1DValidity,
        },
    )
    voltage: Optional[SignalFlt1DValidity] = field(
        default=None,
        metadata={
            "imas_type": "signal_flt_1d_validity",
            "field_type": SignalFlt1DValidity,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class MagneticsBpolProbeNonLinear(IdsBaseClass):
    """

    :ivar b_field_linear : Array of magnetic field values (corresponding to the assumption of a linear relation between magnetic field and probe coil current), for each of which the probe non-linear response is given in ../b_field_non_linear
    :ivar b_field_non_linear : Magnetic field value taking into account the non-linear response of the probe
    """

    class Meta:
        name = "magnetics_bpol_probe_non_linear"
        is_root_ids = False

    b_field_linear: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    b_field_non_linear: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../b_field_linear"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class MagneticsBpolProbe(IdsBaseClass):
    """

    :ivar name : Short string identifier (unique for a given device)
    :ivar description : Description, e.g. “channel viewing the upper divertor”
    :ivar type : Probe type
    :ivar position : R, Z, Phi position of the coil centre
    :ivar poloidal_angle : Angle of the sensor normal vector (vector parallel to the the axis of the coil, n on the diagram) with respect to horizontal plane (clockwise theta-like angle). Zero if sensor normal vector fully in the horizontal plane and oriented towards increasing major radius. Values in [0 , 2Pi]
    :ivar toroidal_angle : Angle of the projection of the sensor normal vector (n) in the horizontal plane with the increasing R direction (i.e. grad(R)) (angle is counter-clockwise from above). Values should be taken modulo pi with values within (-pi/2,pi/2]. Zero if projected sensor normal is parallel to grad(R), pi/2 if it is parallel to grad(phi).
    :ivar indices_differential : Indices (from the b_field_pol_probe array of structure) of the two probes used to build the field difference field(second index) - field(first index). Use only if ../type/index = 6, leave empty otherwise
    :ivar bandwidth_3db : 3dB bandwith (first index : lower frequency bound, second index : upper frequency bound)
    :ivar area : Area of each turn of the sensor; becomes effective area when multiplied by the turns
    :ivar length : Length of the sensor along it&#39;s normal vector (n)
    :ivar turns : Turns in the coil, including sign
    :ivar field : Magnetic field component in direction of sensor normal axis (n) averaged over sensor volume defined by area and length, where n = cos(poloidal_angle)*cos(toroidal_angle)*grad(R) - sin(poloidal_angle)*grad(Z) + cos(poloidal_angle)*sin(toroidal_angle)*grad(Phi)/norm(grad(Phi))
    :ivar voltage : Voltage on the coil terminals
    :ivar non_linear_response : Non-linear response of the probe (typically in case of a Hall probe)
    """

    class Meta:
        name = "magnetics_bpol_probe"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    description: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    type: Optional[IdentifierStatic] = field(
        default=None,
        metadata={
            "imas_type": "identifier_static",
            "field_type": IdentifierStatic,
        },
    )
    position: Optional[Rphiz0DStatic] = field(
        default=None,
        metadata={"imas_type": "rphiz0d_static", "field_type": Rphiz0DStatic},
    )
    poloidal_angle: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    toroidal_angle: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    indices_differential: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=int),
        metadata={
            "imas_type": "INT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...2"},
            "field_type": np.ndarray,
        },
    )
    bandwidth_3db: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...2"},
            "field_type": np.ndarray,
        },
    )
    area: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    length: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    turns: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    field: Optional[SignalFlt1DValidity] = field(
        default=None,
        metadata={
            "imas_type": "signal_flt_1d_validity",
            "field_type": SignalFlt1DValidity,
        },
    )
    voltage: Optional[SignalFlt1DValidity] = field(
        default=None,
        metadata={
            "imas_type": "signal_flt_1d_validity",
            "field_type": SignalFlt1DValidity,
        },
    )
    non_linear_response: Optional[MagneticsBpolProbeNonLinear] = field(
        default=None,
        metadata={
            "imas_type": "magnetics_bpol_probe_non_linear",
            "field_type": MagneticsBpolProbeNonLinear,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class MagneticsMethod(IdsBaseClass):
    """

    :ivar name : Name of the data processing method
    :ivar ip : Plasma current. Positive sign means anti-clockwise when viewed from above.
    """

    class Meta:
        name = "magnetics_method"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    ip: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )


@idspy_dataclass(repr=False, slots=True)
class MagneticsMethodDistinct(IdsBaseClass):
    """

    :ivar method_name : Name of the calculation method
    :ivar data : Data
    :ivar time : Time
    """

    class Meta:
        name = "magnetics_method_distinct"
        is_root_ids = False

    method_name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
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
class MagneticsShunt(IdsBaseClass):
    """

    :ivar name : Short string identifier (unique for a given device)
    :ivar description : Description, e.g. “channel viewing the upper divertor”
    :ivar position : Position of shunt terminals
    :ivar resistance : Shunt resistance
    :ivar voltage : Voltage on the shunt terminals (Vfirst_point-Vsecond_point)
    :ivar divertor_index : If the shunt is located on a given divertor, index of that divertor in the divertors IDS
    :ivar target_index : If the shunt is located on a divertor target, index of that target in the divertors IDS
    :ivar tile_index : If the shunt is located on a divertor tile, index of that tile in the divertors IDS
    """

    class Meta:
        name = "magnetics_shunt"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    description: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    position: Optional[LineOfSight2PointsRz] = field(
        default=None,
        metadata={
            "imas_type": "line_of_sight_2points_rz",
            "field_type": LineOfSight2PointsRz,
        },
    )
    resistance: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    voltage: Optional[SignalFlt1DValidity] = field(
        default=None,
        metadata={
            "imas_type": "signal_flt_1d_validity",
            "field_type": SignalFlt1DValidity,
        },
    )
    divertor_index: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    target_index: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    tile_index: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )


@idspy_dataclass(repr=False, slots=True)
class Magnetics(IdsBaseClass):
    """

    :ivar ids_properties :
    :ivar flux_loop : Flux loops; partial flux loops can be described
    :ivar b_field_pol_probe : Poloidal field probes
    :ivar b_field_phi_probe : Toroidal field probes
    :ivar rogowski_coil : Set of Rogowski coils. If some of the coils form a compound Rogowski sensor, they must be entered in contiguous order
    :ivar shunt : Set of shunt resistances through which currents in the divertor structure are measured. Shunts are modelled as piecewise straight line segments in the poloidal plane.
    :ivar ip : Plasma current. Positive sign means anti-clockwise when viewed from above. The array of structure corresponds to a set of calculation methods (starting with the generally recommended method).
    :ivar diamagnetic_flux : Diamagnetic flux. The array of structure corresponds to a set of calculation methods (starting with the generally recommended method).
    :ivar latency : Upper bound of the delay between physical information received by the detector and data available on the real-time (RT) network.
    :ivar code :
    :ivar time : Generic time
    """

    class Meta:
        name = "magnetics"
        is_root_ids = True

    ids_properties: Optional[IdsProperties] = field(
        default=None,
        metadata={"imas_type": "ids_properties", "field_type": IdsProperties},
    )
    flux_loop: Optional[MagneticsFluxLoop] = field(
        default_factory=lambda: StructArray(type_input=MagneticsFluxLoop),
        metadata={
            "imas_type": "magnetics_flux_loop",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": MagneticsFluxLoop,
        },
    )
    b_field_pol_probe: Optional[MagneticsBpolProbe] = field(
        default_factory=lambda: StructArray(type_input=MagneticsBpolProbe),
        metadata={
            "imas_type": "magnetics_bpol_probe",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": MagneticsBpolProbe,
        },
    )
    b_field_phi_probe: Optional[MagneticsBpolProbe] = field(
        default_factory=lambda: StructArray(type_input=MagneticsBpolProbe),
        metadata={
            "imas_type": "magnetics_bpol_probe",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": MagneticsBpolProbe,
        },
    )
    rogowski_coil: Optional[MagneticsRogowski] = field(
        default_factory=lambda: StructArray(type_input=MagneticsRogowski),
        metadata={
            "imas_type": "magnetics_rogowski",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": MagneticsRogowski,
        },
    )
    shunt: Optional[MagneticsShunt] = field(
        default_factory=lambda: StructArray(type_input=MagneticsShunt),
        metadata={
            "imas_type": "magnetics_shunt",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": MagneticsShunt,
        },
    )
    ip: Optional[MagneticsMethodDistinct] = field(
        default_factory=lambda: StructArray(type_input=MagneticsMethodDistinct),
        metadata={
            "imas_type": "magnetics_method_distinct",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": MagneticsMethodDistinct,
        },
    )
    diamagnetic_flux: Optional[MagneticsMethodDistinct] = field(
        default_factory=lambda: StructArray(type_input=MagneticsMethodDistinct),
        metadata={
            "imas_type": "magnetics_method_distinct",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": MagneticsMethodDistinct,
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
