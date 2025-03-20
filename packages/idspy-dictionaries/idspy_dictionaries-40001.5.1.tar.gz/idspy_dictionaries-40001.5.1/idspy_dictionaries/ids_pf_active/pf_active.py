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
class PfCoilsElements(IdsBaseClass):
    """

    :ivar name : Short string identifier (unique for a given device)
    :ivar description : Description, e.g. “channel viewing the upper divertor”
    :ivar turns_with_sign : Number of effective turns in the element for calculating the magnetic field from the coil/loop. Should be positive, unless the coil has elements going in opposite directions.
    :ivar area : Cross-sectional areas of the element
    :ivar geometry : Cross-sectional shape of the element
    """

    class Meta:
        name = "pf_coils_elements"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    description: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    turns_with_sign: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    area: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    geometry: Optional[Outline2DGeometryStatic] = field(
        default=None,
        metadata={
            "imas_type": "outline_2d_geometry_static",
            "field_type": Outline2DGeometryStatic,
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
class PfSupplies(IdsBaseClass):
    """

    :ivar name : Short string identifier (unique for a given device)
    :ivar description : Description, e.g. “channel viewing the upper divertor”
    :ivar type : Type of the supply; TBD add free description of non-linear power supplies
    :ivar resistance : Power supply internal resistance
    :ivar delay : Pure delay in the supply
    :ivar filter_numerator : Coefficients of the numerator, in increasing order : a0 + a1*s + ... + an*s^n; used for a linear supply description
    :ivar filter_denominator : Coefficients of the denominator, in increasing order : b0 + b1*s + ... + bm*s^m; used for a linear supply description
    :ivar current_limit_max : Maximum current in the supply
    :ivar current_limit_min : Minimum current in the supply
    :ivar voltage_limit_max : Maximum voltage from the supply
    :ivar voltage_limit_min : Minimum voltage from the supply
    :ivar current_limiter_gain : Gain to prevent overcurrent in a linear model of the supply
    :ivar energy_limit_max : Maximum energy to be dissipated in the supply during a pulse
    :ivar nonlinear_model : Description of the nonlinear transfer function of the supply
    :ivar voltage : Voltage at the supply output (Vside1-Vside2)
    :ivar current : Current at the supply output, defined positive if it flows from point 1 to point 2 in the circuit connected to the supply (outside the supply)
    """

    class Meta:
        name = "pf_supplies"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    description: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    type: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    resistance: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    delay: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    filter_numerator: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    filter_denominator: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    current_limit_max: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    current_limit_min: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    voltage_limit_max: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    voltage_limit_min: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    current_limiter_gain: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    energy_limit_max: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    nonlinear_model: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    voltage: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )
    current: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )


@idspy_dataclass(repr=False, slots=True)
class PfCircuits(IdsBaseClass):
    """

    :ivar name : Short string identifier (unique for a given device)
    :ivar description : Description, e.g. “channel viewing the upper divertor”
    :ivar type : Type of the circuit
    :ivar connections : Description of the supplies and coils connections (nodes) across the circuit. Nodes of the circuit are listed as the first dimension of the matrix. Supplies (listed first) and coils (listed second) are listed as the second dimension. Thus the second dimension has a size equal to (N_supplies+N_coils). N_supplies (resp. N_coils) is the total number of supplies (resp. coils) listed in the supply (resp.coil) array of structure, i.e. including also supplies/coils that are not part of the actual circuit. The (i,j) matrix elements are 1 if the j-th supply or coil side is connected to the i-th node by its positive side, -1 if connected by its negative side, or 0 if not connected.
    :ivar voltage : Voltage on the circuit between the sides of the group of supplies (only for circuits with a single supply or in which supplies are grouped)
    :ivar current : Current in the circuit between the sides of the group of supplies (only for circuits with a single supply or in which supplies are grouped)
    """

    class Meta:
        name = "pf_circuits"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    description: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    type: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    connections: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=int),
        metadata={
            "imas_type": "INT_2D",
            "ndims": 2,
            "coordinates": {"coordinate1": "1...N", "coordinate2": "1...N"},
            "field_type": np.ndarray,
        },
    )
    voltage: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )
    current: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )


@idspy_dataclass(repr=False, slots=True)
class PfCoils(IdsBaseClass):
    """

    :ivar name : Short string identifier (unique for a given device)
    :ivar description : Description, e.g. “channel viewing the upper divertor”
    :ivar function : Set of functions for which this coil may be used
    :ivar resistance : Coil resistance
    :ivar resistance_additional : Additional resistance due to e.g. dynamically switchable resistors. The coil effective resistance is obtained by adding this dynamic quantity to the static resistance of the coil.
    :ivar energy_limit_max : Maximum Energy to be dissipated in the coil
    :ivar current_limit_max : Maximum tolerable current in the conductor
    :ivar b_field_max : List of values of the maximum magnetic field on the conductor surface (coordinate for current_limit_max)
    :ivar temperature : List of values of the conductor temperature (coordinate for current_limit_max)
    :ivar b_field_max_timed : Maximum absolute value of the magnetic field on the conductor surface
    :ivar element : Each PF coil is comprised of a number of cross-section elements described  individually and connected serially
    :ivar current : Current fed in the coil (for 1 turn, to be multiplied by the number of turns to obtain the generated magnetic field), positive when the current is counter-clockwise when seen from above.
    :ivar voltage : Voltage on the coil terminals (Vside1-Vside2) - including additional resistors if any
    :ivar force_radial : Radial force applied on this coil (positive when outwards)
    :ivar force_vertical : Vertical force applied on this coil (positive when upwards)
    :ivar force_radial_crushing : Radial crushing force applied on this coil (positive when compressive)
    :ivar force_vertical_crushing : Vertical crushing force applied on this coil (positive when compressive)
    """

    class Meta:
        name = "pf_coils"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    description: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    function: Optional[IdentifierStatic] = field(
        default_factory=lambda: StructArray(type_input=IdentifierStatic),
        metadata={
            "imas_type": "identifier_static",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": IdentifierStatic,
        },
    )
    resistance: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    resistance_additional: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )
    energy_limit_max: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    current_limit_max: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../b_field_max",
                "coordinate2": "../temperature",
            },
            "field_type": np.ndarray,
        },
    )
    b_field_max: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    temperature: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    b_field_max_timed: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )
    element: Optional[PfCoilsElements] = field(
        default_factory=lambda: StructArray(type_input=PfCoilsElements),
        metadata={
            "imas_type": "pf_coils_elements",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": PfCoilsElements,
        },
    )
    current: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )
    voltage: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )
    force_radial: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )
    force_vertical: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )
    force_radial_crushing: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )
    force_vertical_crushing: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )


@idspy_dataclass(repr=False, slots=True)
class PfForceLimits(IdsBaseClass):
    """

    :ivar combination_matrix : Force limits are expressed as a linear combination of the forces on each individual coil. The weights of the linear combination are given by this matrix, while the limits are given by the sibling nodes limit_min and limit_max. Each row of this matrix corresponds to a force limit. The columns represent, for each coil, the 4 types of forces on the coil namely [coil1_radial, coil1_vertical, coil1_radial_crush, coil1_vertical_crush, coil2_radial, coil2_vertical, coil2_radial_crush, coil2_vertical_crush, ...]. There are therefore 4*coils_n columns.
    :ivar limit_max : Maximum force limit, for each limit (line of the combination matrix). EMPTY_FLT value means unbounded
    :ivar limit_min : Minimum force limit, for each limit (line of the combination matrix). EMPTY_FLT value means unbounded
    :ivar force : Force (positive when upwards for a vertical force, positive when outwards for a radial force)
    """

    class Meta:
        name = "pf_force_limits"
        is_root_ids = False

    combination_matrix: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../limit_max",
                "coordinate2": "1...N",
            },
            "field_type": np.ndarray,
        },
    )
    limit_max: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    limit_min: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../limit_max"},
            "field_type": np.ndarray,
        },
    )
    force: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )


@idspy_dataclass(repr=False, slots=True)
class PfActive(IdsBaseClass):
    """

    :ivar ids_properties :
    :ivar coil : Active PF coils
    :ivar force_limits : Description of force limits on the axisymmetric PF coil system
    :ivar circuit : Circuits, connecting multiple PF coils to multiple supplies, defining the current and voltage relationships in the system
    :ivar supply : PF power supplies
    :ivar latency : Upper bound of the delay between input command received from the RT network and actuator starting to react. Applies globally to the system described by this IDS unless specific latencies (e.g. channel-specific or antenna-specific) are provided at a deeper level in the IDS structure.
    :ivar code :
    :ivar time : Generic time
    """

    class Meta:
        name = "pf_active"
        is_root_ids = True

    ids_properties: Optional[IdsProperties] = field(
        default=None,
        metadata={"imas_type": "ids_properties", "field_type": IdsProperties},
    )
    coil: Optional[PfCoils] = field(
        default_factory=lambda: StructArray(type_input=PfCoils),
        metadata={
            "imas_type": "pf_coils",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": PfCoils,
        },
    )
    force_limits: Optional[PfForceLimits] = field(
        default=None,
        metadata={"imas_type": "pf_force_limits", "field_type": PfForceLimits},
    )
    circuit: Optional[PfCircuits] = field(
        default_factory=lambda: StructArray(type_input=PfCircuits),
        metadata={
            "imas_type": "pf_circuits",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": PfCircuits,
        },
    )
    supply: Optional[PfSupplies] = field(
        default_factory=lambda: StructArray(type_input=PfSupplies),
        metadata={
            "imas_type": "pf_supplies",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": PfSupplies,
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
