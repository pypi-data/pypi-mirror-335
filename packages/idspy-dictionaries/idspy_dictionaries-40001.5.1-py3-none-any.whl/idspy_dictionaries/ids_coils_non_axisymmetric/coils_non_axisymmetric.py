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
class NormalBinormalStatic(IdsBaseClass):
    """

    :ivar normal : Coordinate along the normal axis
    :ivar binormal : Coordinates along the binormal axis
    """

    class Meta:
        name = "normal_binormal_static"
        is_root_ids = False

    normal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    binormal: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../normal"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class CoilNaRphiz1DStatic(IdsBaseClass):
    """

    :ivar r : Major radius
    :ivar phi : Toroidal angle (oriented counter-clockwise when viewing from above)
    :ivar z : Height
    """

    class Meta:
        name = "coil_na_rphiz1d_static"
        is_root_ids = False

    r: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../types"},
            "field_type": np.ndarray,
        },
    )
    phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../types"},
            "field_type": np.ndarray,
        },
    )
    z: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../types"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class CoilCrossSection(IdsBaseClass):
    """

    :ivar geometry_type : Geometry type used to describe the cross section of this element. The conductor centre is given by the ../../elements description.
    :ivar width : Full width of the rectangle or square in the normal direction, when geometry_type/index = 3 or 4. Diameter of the circle when geometry_type/index = 2. Outer diameter of the annulus in case geometry_type/index = 5
    :ivar height : Full height of the rectangle in the binormal direction, used only if geometry_type/index = 3
    :ivar radius_inner : Inner radius of the annulus, used only if geometry_type/index = 5
    :ivar outline : Polygonal outline of the cross section in the (normal, binormal) coordinate system. Do NOT repeat the first point.
    :ivar area : Area of the conductor cross-section, derived from the above geometric data
    """

    class Meta:
        name = "coil_cross_section"
        is_root_ids = False

    geometry_type: Optional[IdentifierStatic] = field(
        default=None,
        metadata={
            "imas_type": "identifier_static",
            "field_type": IdentifierStatic,
        },
    )
    width: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    height: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    radius_inner: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    outline: Optional[NormalBinormalStatic] = field(
        default=None,
        metadata={
            "imas_type": "normal_binormal_static",
            "field_type": NormalBinormalStatic,
        },
    )
    area: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class CoilConductorElements(IdsBaseClass):
    """

    :ivar types : Type of every element: 1: line segment, its ends are given by the start and end points; index = 2: arc of a circle; index = 3: full circle
    :ivar start_points : Position of the start point of every element
    :ivar intermediate_points : Position of an intermediate point along the circle or arc of circle, for every element, providing the orientation of the element (must define with the corresponding start point an aperture angle strictly inferior to PI). In the case of a line segment (../types/index=1), fill this node with a point such that the vector intermediate_point - start_point defines the direction of the element&#39;s normal axis (see documentation of ../elements)
    :ivar end_points : Position of the end point of every element. Meaningful only if type/index = 1 or 2, fill with default/empty value otherwise
    :ivar centres : Position of the centre of the arc of a circle of every element (meaningful only if type/index = 2 or 3, fill with default/empty value otherwise)
    """

    class Meta:
        name = "coil_conductor_elements"
        is_root_ids = False

    types: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=int),
        metadata={
            "imas_type": "INT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    start_points: Optional[CoilNaRphiz1DStatic] = field(
        default=None,
        metadata={
            "imas_type": "coil_na_rphiz1d_static",
            "field_type": CoilNaRphiz1DStatic,
        },
    )
    intermediate_points: Optional[CoilNaRphiz1DStatic] = field(
        default=None,
        metadata={
            "imas_type": "coil_na_rphiz1d_static",
            "field_type": CoilNaRphiz1DStatic,
        },
    )
    end_points: Optional[CoilNaRphiz1DStatic] = field(
        default=None,
        metadata={
            "imas_type": "coil_na_rphiz1d_static",
            "field_type": CoilNaRphiz1DStatic,
        },
    )
    centres: Optional[CoilNaRphiz1DStatic] = field(
        default=None,
        metadata={
            "imas_type": "coil_na_rphiz1d_static",
            "field_type": CoilNaRphiz1DStatic,
        },
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
class CoilConductor(IdsBaseClass):
    """

    :ivar elements : Set of geometrical elements (line segments and/or arcs of a circle) describing the contour of the conductor centre. We define a coordinate system associated to each element as follows: for the arc and circle elements: binormal = (start point - center) x (intermediate point - center). This vector points in the direction of the circle / arc axis. normal = (center - point on curve). The normal vector will rotate as the point moves around the curve. Tangent = normal x binormal. For the line element we require an extra point, using the currently redundant intermediate point to define the line element&#39;s normal axis. The local coordinates for the line element then become: tangent = end point - start point; normal = intermediate point - start point; binormal = tangent x normal. It is assumed that all the axes above are normalized such that they have a unit length.
    :ivar cross_section : The cross-section perpendicular to the conductor contour is described by a series of contour points, given by their relative position with respect to the start point of each element. If the size of this array of structure is equal to 1, then the cross-section is given only for the first element and translated along the conductor elements. Otherwise, it&#39;s given explictly for each element, allowing to describe changes of the cross section shape
    :ivar resistance : conductor resistance
    :ivar voltage : Voltage on the conductor terminals. Sign convention : positive when the current flows in the direction in which conductor elements are ordered (from start to end for a positive polarity coil)
    """

    class Meta:
        name = "coil_conductor"
        is_root_ids = False

    elements: Optional[CoilConductorElements] = field(
        default=None,
        metadata={
            "imas_type": "coil_conductor_elements",
            "field_type": CoilConductorElements,
        },
    )
    cross_section: Optional[CoilCrossSection] = field(
        default_factory=lambda: StructArray(type_input=CoilCrossSection),
        metadata={
            "imas_type": "coil_cross_section",
            "ndims": 1,
            "coordinates": {"coordinate1": "../elements/types OR 1...1"},
            "field_type": CoilCrossSection,
        },
    )
    resistance: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    voltage: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )


@idspy_dataclass(repr=False, slots=True)
class Coil(IdsBaseClass):
    """

    :ivar name : Name of the coil
    :ivar identifier : Alphanumeric identifier of coil
    :ivar conductor : Set of conductors inside the coil. The structure can be used with size 1 for a simplified description as a single conductor. A conductor is composed of several elements, serially connected, i.e. transporting the same current.
    :ivar turns : Number of total turns in the coil. May be a fraction when describing the coil connections.
    :ivar resistance : Coil resistance
    :ivar current : Current in one turn of the coil (to be multiplied by the number of turns to calculate the magnetic field generated). Sign convention : a positive current flows in the direction in which conductor elements are ordered (from start to end for a positive polarity coil)
    :ivar voltage : Voltage on the coil terminals. Sign convention : positive when the current flows in the direction in which conductor elements are ordered (from start to end for a positive polarity coil)
    """

    class Meta:
        name = "coil"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    identifier: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    conductor: Optional[CoilConductor] = field(
        default_factory=lambda: StructArray(type_input=CoilConductor),
        metadata={
            "imas_type": "coil_conductor",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": CoilConductor,
        },
    )
    turns: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    resistance: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    current: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )
    voltage: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
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
class CoilsNonAxisymmetric(IdsBaseClass):
    """

    :ivar ids_properties :
    :ivar coil : Set of coils
    :ivar latency : Upper bound of the delay between input command received from the RT network and actuator starting to react. Applies globally to the system described by this IDS unless specific latencies (e.g. channel-specific or antenna-specific) are provided at a deeper level in the IDS structure.
    :ivar code :
    :ivar time : Generic time
    """

    class Meta:
        name = "coils_non_axisymmetric"
        is_root_ids = True

    ids_properties: Optional[IdsProperties] = field(
        default=None,
        metadata={"imas_type": "ids_properties", "field_type": IdsProperties},
    )
    coil: Optional[Coil] = field(
        default_factory=lambda: StructArray(type_input=Coil),
        metadata={
            "imas_type": "coil",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": Coil,
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
