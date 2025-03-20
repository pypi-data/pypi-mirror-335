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
class SignalFlt1DUnitsLevel2(IdsBaseClass):
    """

    :ivar data : Data
    :ivar time : Time
    """

    class Meta:
        name = "signal_flt_1d_units_level_2"
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
class Rz0DConstant(IdsBaseClass):
    """

    :ivar r : Major radius
    :ivar z : Height
    """

    class Meta:
        name = "rz0d_constant"
        is_root_ids = False

    r: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    z: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
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
class Rphiz1DStatic(IdsBaseClass):
    """

    :ivar r : Major radius
    :ivar phi : Toroidal angle (oriented counter-clockwise when viewing from above)
    :ivar z : Height
    """

    class Meta:
        name = "rphiz1d_static"
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
    phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../r"},
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
class IcAntennasMatchingElement(IdsBaseClass):
    """

    :ivar name : Short string identifier (unique for a given device)
    :ivar type : Type of the matching element. Index = 1 : capacitor (fill capacitance); Index = 2 : stub (fill phase)
    :ivar capacitance : Capacitance of the macthing element
    :ivar phase : Phase delay induced by the stub
    :ivar description : Description, e.g. “channel viewing the upper divertor”
    """

    class Meta:
        name = "ic_antennas_matching_element"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    type: Optional[IdentifierStatic] = field(
        default=None,
        metadata={
            "imas_type": "identifier_static",
            "field_type": IdentifierStatic,
        },
    )
    capacitance: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )
    phase: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )
    description: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )


@idspy_dataclass(repr=False, slots=True)
class IcAntennasMeasurement(IdsBaseClass):
    """

    :ivar name : Short string identifier (unique for a given device)
    :ivar description : Description, e.g. “channel viewing the upper divertor”
    :ivar position : Position of the measurement
    :ivar amplitude : Amplitude of the measurement
    :ivar phase : Phase of the measurement
    """

    class Meta:
        name = "ic_antennas_measurement"
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
    amplitude: Optional[SignalFlt1DUnitsLevel2] = field(
        default=None,
        metadata={
            "imas_type": "signal_flt_1d_units_level_2",
            "field_type": SignalFlt1DUnitsLevel2,
        },
    )
    phase: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )


@idspy_dataclass(repr=False, slots=True)
class IcAntennasStrap(IdsBaseClass):
    """

    :ivar outline : Strap outline
    :ivar width_phi : Width of strap in the toroidal direction
    :ivar distance_to_conductor : Distance to conducting wall or other conductor behind the antenna strap
    :ivar geometry : Cross-sectional shape of the strap
    :ivar current : Root mean square current flowing along the strap
    :ivar phase : Phase of the strap current
    """

    class Meta:
        name = "ic_antennas_strap"
        is_root_ids = False

    outline: Optional[Rphiz1DStatic] = field(
        default=None,
        metadata={"imas_type": "rphiz1d_static", "field_type": Rphiz1DStatic},
    )
    width_phi: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    distance_to_conductor: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    geometry: Optional[Outline2DGeometryStatic] = field(
        default=None,
        metadata={
            "imas_type": "outline_2d_geometry_static",
            "field_type": Outline2DGeometryStatic,
        },
    )
    current: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )
    phase: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )


@idspy_dataclass(repr=False, slots=True)
class IcAntennasAntennaModule(IdsBaseClass):
    """

    :ivar name : Short string identifier (unique for a given device)
    :ivar description : Description, e.g. “channel viewing the upper divertor”
    :ivar frequency : Frequency
    :ivar power_launched : Power launched from this module into the vacuum vessel
    :ivar power_forward : Forward power arriving to the back of the module
    :ivar power_reflected : Reflected power
    :ivar coupling_resistance : Coupling resistance
    :ivar phase_forward : Phase of the forward power with respect to the first module
    :ivar phase_reflected : Phase of the reflected power with respect to the forward power of this module
    :ivar voltage : Set of voltage measurements
    :ivar current : Set of current measurements
    :ivar pressure : Set of pressure measurements
    :ivar matching_element : Set of matching elements
    :ivar strap : Set of IC antenna straps
    """

    class Meta:
        name = "ic_antennas_antenna_module"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    description: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    frequency: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )
    power_launched: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )
    power_forward: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )
    power_reflected: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )
    coupling_resistance: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )
    phase_forward: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )
    phase_reflected: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )
    voltage: Optional[IcAntennasMeasurement] = field(
        default_factory=lambda: StructArray(type_input=IcAntennasMeasurement),
        metadata={
            "imas_type": "ic_antennas_measurement",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": IcAntennasMeasurement,
        },
    )
    current: Optional[IcAntennasMeasurement] = field(
        default_factory=lambda: StructArray(type_input=IcAntennasMeasurement),
        metadata={
            "imas_type": "ic_antennas_measurement",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": IcAntennasMeasurement,
        },
    )
    pressure: Optional[IcAntennasMeasurement] = field(
        default_factory=lambda: StructArray(type_input=IcAntennasMeasurement),
        metadata={
            "imas_type": "ic_antennas_measurement",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": IcAntennasMeasurement,
        },
    )
    matching_element: Optional[IcAntennasMatchingElement] = field(
        default_factory=lambda: StructArray(
            type_input=IcAntennasMatchingElement
        ),
        metadata={
            "imas_type": "ic_antennas_matching_element",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": IcAntennasMatchingElement,
        },
    )
    strap: Optional[IcAntennasStrap] = field(
        default_factory=lambda: StructArray(type_input=IcAntennasStrap),
        metadata={
            "imas_type": "ic_antennas_strap",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": IcAntennasStrap,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class IcAntennasSurfaceCurrent(IdsBaseClass):
    """

    :ivar m_pol : Poloidal mode numbers, used to describe the spectrum of the antenna current. The poloidal angle is defined from the reference point; the angle at a point (R,Z) is given by atan((Z-Zref)/(R-Rref)), where Rref=reference_point/r and Zref=reference_point/z
    :ivar n_phi : Toroidal mode numbers, used to describe the spectrum of the antenna current. The wave vector toroidal component is defined as k_phi = n_phi grad phi where phi is the toroidal angle so that a positive n_phi means a wave propagating in the positive phi direction
    :ivar spectrum : Spectrum of the total surface current on the antenna strap and passive components expressed in poloidal and toroidal modes
    :ivar time : Time
    """

    class Meta:
        name = "ic_antennas_surface_current"
        is_root_ids = False

    m_pol: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=int),
        metadata={
            "imas_type": "INT_1D",
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
    spectrum: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../m_pol",
                "coordinate2": "../n_phi",
            },
            "field_type": np.ndarray,
        },
    )
    time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class IcAntennasAntenna(IdsBaseClass):
    """

    :ivar name : Short string identifier (unique for a given device)
    :ivar description : Description, e.g. “channel viewing the upper divertor”
    :ivar frequency : Frequency (average over modules)
    :ivar power_launched : Power launched from this antenna into the vacuum vessel
    :ivar power_forward : Forward power arriving to the back of the antenna
    :ivar power_reflected : Reflected power
    :ivar module : Set of antenna modules (each module is fed by a single transmission line)
    :ivar surface_current : Description of the IC surface current on the antenna straps and on passive components, for every time slice
    """

    class Meta:
        name = "ic_antennas_antenna"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    description: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    frequency: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )
    power_launched: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )
    power_forward: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )
    power_reflected: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )
    module: Optional[IcAntennasAntennaModule] = field(
        default_factory=lambda: StructArray(type_input=IcAntennasAntennaModule),
        metadata={
            "imas_type": "ic_antennas_antenna_module",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": IcAntennasAntennaModule,
        },
    )
    surface_current: Optional[IcAntennasSurfaceCurrent] = field(
        default_factory=lambda: StructArray(
            type_input=IcAntennasSurfaceCurrent
        ),
        metadata={
            "imas_type": "ic_antennas_surface_current",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": IcAntennasSurfaceCurrent,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class IcAntennas(IdsBaseClass):
    """

    :ivar ids_properties :
    :ivar reference_point : Reference point used to define the poloidal angle, e.g. the geometrical centre of the vacuum vessel. Used to define the poloidal mode numbers under antenna/surface_current
    :ivar antenna : Set of Ion Cyclotron antennas
    :ivar power_launched : Power launched into the vacuum vessel by the whole ICRH system (sum over antennas)
    :ivar latency : Upper bound of the delay between input command received from the RT network and actuator starting to react. Applies globally to the system described by this IDS unless specific latencies (e.g. channel-specific or antenna-specific) are provided at a deeper level in the IDS structure.
    :ivar code :
    :ivar time : Generic time
    """

    class Meta:
        name = "ic_antennas"
        is_root_ids = True

    ids_properties: Optional[IdsProperties] = field(
        default=None,
        metadata={"imas_type": "ids_properties", "field_type": IdsProperties},
    )
    reference_point: Optional[Rz0DConstant] = field(
        default=None,
        metadata={"imas_type": "rz0d_constant", "field_type": Rz0DConstant},
    )
    antenna: Optional[IcAntennasAntenna] = field(
        default_factory=lambda: StructArray(type_input=IcAntennasAntenna),
        metadata={
            "imas_type": "ic_antennas_antenna",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": IcAntennasAntenna,
        },
    )
    power_launched: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
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
