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
class Xyz0DStatic(IdsBaseClass):
    """

    :ivar x : Component along X axis
    :ivar y : Component along Y axis
    :ivar z : Component along Z axis
    """

    class Meta:
        name = "xyz0d_static"
        is_root_ids = False

    x: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    y: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    z: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class X1X21DStatic(IdsBaseClass):
    """

    :ivar x1 : Positions along x1 axis
    :ivar x2 : Positions along x2 axis
    """

    class Meta:
        name = "x1x21d_static"
        is_root_ids = False

    x1: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    x2: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../x1"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SignalFlt2D(IdsBaseClass):
    """

    :ivar data : Data
    :ivar time : Time
    """

    class Meta:
        name = "signal_flt_2d"
        is_root_ids = False

    data: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "as_parent",
                "coordinate2": "../time",
            },
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
class Rphiz0DDynamicAos3(IdsBaseClass):
    """

    :ivar r : Major radius
    :ivar phi : Toroidal angle (oriented counter-clockwise when viewing from above)
    :ivar z : Height
    """

    class Meta:
        name = "rphiz0d_dynamic_aos3"
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
class DetectorAperture(IdsBaseClass):
    """

    :ivar geometry_type : Type of geometry used to describe the surface of the detector or aperture (1:&#39;outline&#39;, 2:&#39;circular&#39;, 3:&#39;rectangle&#39;). In case of &#39;outline&#39;, the surface is described by an outline of point in a local coordinate system defined by a centre and three unit vectors X1, X2, X3. Note that there is some flexibility here and the data provider should choose the most convenient coordinate system for the object, respecting the definitions of (X1,X2,X3) indicated below. In case of &#39;circular&#39;, the surface is a circle defined by its centre, radius, and normal vector oriented towards the plasma X3.  In case of &#39;rectangle&#39;, the surface is a rectangle defined by its centre, widths in the X1 and X2 directions, and normal vector oriented towards the plasma X3.
    :ivar centre : If geometry_type=2, coordinates of the centre of the circle. If geometry_type=1 or 3, coordinates of the origin of the local coordinate system (X1,X2,X3) describing the plane detector/aperture. This origin is located within the detector/aperture area.
    :ivar radius : Radius of the circle, used only if geometry_type = 2
    :ivar x1_unit_vector : Components of the X1 direction unit vector in the (X,Y,Z) coordinate system, where X is the major radius axis for phi = 0, Y is the major radius axis for phi = pi/2, and Z is the height axis. The X1 vector is more horizontal than X2 (has a smaller abs(Z) component) and oriented in the positive phi direction (counter-clockwise when viewing from above).
    :ivar x2_unit_vector : Components of the X2 direction unit vector in the (X,Y,Z) coordinate system, where X is the major radius axis for phi = 0, Y is the major radius axis for phi = pi/2, and Z is the height axis. The X2 axis is orthonormal so that uX2 = uX3 x uX1.
    :ivar x3_unit_vector : Components of the X3 direction unit vector in the (X,Y,Z) coordinate system, where X is the major radius axis for phi = 0, Y is the major radius axis for phi = pi/2, and Z is the height axis. The X3 axis is normal to the detector/aperture plane and oriented towards the plasma.
    :ivar x1_width : Full width of the aperture in the X1 direction, used only if geometry_type = 3
    :ivar x2_width : Full width of the aperture in the X2 direction, used only if geometry_type = 3
    :ivar outline : Irregular outline of the detector/aperture in the (X1, X2) coordinate system. Repeat the first point since this is a closed contour
    :ivar surface : Surface of the detector/aperture, derived from the above geometric data
    """

    class Meta:
        name = "detector_aperture"
        is_root_ids = False

    geometry_type: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    centre: Optional[Rphiz0DStatic] = field(
        default=None,
        metadata={"imas_type": "rphiz0d_static", "field_type": Rphiz0DStatic},
    )
    radius: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    x1_unit_vector: Optional[Xyz0DStatic] = field(
        default=None,
        metadata={"imas_type": "xyz0d_static", "field_type": Xyz0DStatic},
    )
    x2_unit_vector: Optional[Xyz0DStatic] = field(
        default=None,
        metadata={"imas_type": "xyz0d_static", "field_type": Xyz0DStatic},
    )
    x3_unit_vector: Optional[Xyz0DStatic] = field(
        default=None,
        metadata={"imas_type": "xyz0d_static", "field_type": Xyz0DStatic},
    )
    x1_width: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    x2_width: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    outline: Optional[X1X21DStatic] = field(
        default=None,
        metadata={"imas_type": "x1x21d_static", "field_type": X1X21DStatic},
    )
    surface: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class PlasmaCompositionSpecies(IdsBaseClass):
    """

    :ivar a : Mass of atom
    :ivar z_n : Nuclear charge
    :ivar name : String identifying the species (e.g. H, D, T, ...)
    """

    class Meta:
        name = "plasma_composition_species"
        is_root_ids = False

    a: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    z_n: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    name: Optional[str] = field(
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
class NbiUnitBeamletsGroupTilting(IdsBaseClass):
    """

    :ivar delta_position : Variation of the position of the beamlet group centre
    :ivar delta_tangency_radius : Variation of the tangency radius (major radius where the central line of a NBI unit is tangent to a circle around the torus)
    :ivar delta_angle : Variation of the angle of inclination between a beamlet at the centre of the injection unit surface and the horiontal plane
    :ivar time : Time
    """

    class Meta:
        name = "nbi_unit_beamlets_group_tilting"
        is_root_ids = False

    delta_position: Optional[Rphiz0DDynamicAos3] = field(
        default=None,
        metadata={
            "imas_type": "rphiz0d_dynamic_aos3",
            "field_type": Rphiz0DDynamicAos3,
        },
    )
    delta_tangency_radius: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    delta_angle: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class NbiUnitBeamletsGroupBeamlets(IdsBaseClass):
    """

    :ivar positions : Position of each beamlet
    :ivar tangency_radii : Tangency radius (major radius where the central line of a beamlet is tangent to a circle around the torus), for each beamlet
    :ivar angles : Angle of inclination between a line at the centre of a beamlet and the horizontal plane, for each beamlet
    :ivar power_fractions : Fraction of power of a unit injected by each beamlet
    """

    class Meta:
        name = "nbi_unit_beamlets_group_beamlets"
        is_root_ids = False

    positions: Optional[Rphiz1DStatic] = field(
        default=None,
        metadata={"imas_type": "rphiz1d_static", "field_type": Rphiz1DStatic},
    )
    tangency_radii: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../positions/r"},
            "field_type": np.ndarray,
        },
    )
    angles: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../positions/r"},
            "field_type": np.ndarray,
        },
    )
    power_fractions: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../positions/r"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class NbiUnitBeamletsGroupDivergence(IdsBaseClass):
    """

    :ivar particles_fraction : Fraction of injected particles in the component
    :ivar vertical : The vertical beamlet divergence of the component. Here the divergence is defined for Gaussian beams as the angel where the beam density is reduced by a factor 1/e compared to the maximum density. For non-Gaussian beams the divergence is sqrt(2)*mean((x-mean(x))**2), where x is the angle and the mean should be performed over the beam density, P(x): mean(y)=int(y*P(x)*dx).
    :ivar horizontal : The horiztonal beamlet divergence of the component. Here the divergence is defined for Gaussian beams as the angel where the beam density is reduced by a factor 1/e compared to the maximum density. For non-Gaussian beams the divergence is sqrt(2)*mean((x-mean(x))**2), where x is the angle and the mean should be performed over the beam density, P(x): mean(y)=int(y*P(x)*dx).
    """

    class Meta:
        name = "nbi_unit_beamlets_group_divergence"
        is_root_ids = False

    particles_fraction: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    vertical: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    horizontal: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class NbiUnitBeamletsGroupFocus(IdsBaseClass):
    """

    :ivar focal_length_horizontal : Horizontal focal length along the beam line, i.e. the point along the centre of the beamlet-group where the beamlet-group has its minimum horizontal width
    :ivar focal_length_vertical : Vertical focal length along the beam line, i.e. the point along the centre of the beamlet-group where the beamlet-group has its minimum vertical width
    :ivar width_min_horizontal : The horizontal width (Full Width at Half Maximum) of the beamlets group at the horizontal focal point
    :ivar width_min_vertical : The vertical width (Full Width at Half Maximum) of the beamlets group at the vertical focal point
    """

    class Meta:
        name = "nbi_unit_beamlets_group_focus"
        is_root_ids = False

    focal_length_horizontal: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    focal_length_vertical: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    width_min_horizontal: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    width_min_vertical: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class NbiUnitBeamletsGroup(IdsBaseClass):
    """

    :ivar position : R, Z, Phi position of the beamlet group centre
    :ivar tangency_radius : Tangency radius (major radius where the central line of a NBI unit is tangent to a circle around the torus)
    :ivar angle : Angle of inclination between a beamlet at the centre of the injection unit surface and the horiontal plane
    :ivar tilting : In case of dynamic beam tilting (i.e. during the pulse), e.g. for some Beam Emission Spectroscopy use cases, variations of position, tangency radius and angle with respect to their static value, for various time slices
    :ivar direction : Direction of the beam seen from above the torus: -1 = clockwise; 1 = counter clockwise
    :ivar width_horizontal : Horizontal width (dimensions of the smallest rectangle that surrounds the outer dimensions of the beamlets) of the beamlet group at the injection unit surface (or grounded grid)
    :ivar width_vertical : Vertical width (dimensions of the smallest rectangle that surrounds the outer dimensions of the beamlets) of the beamlet group at the injection unit surface (or grounded grid)
    :ivar focus : Describes how the beamlet group is focused. Calculations of width_min_horizontal and width_min_vertical are on a plane defined by the average normal vector of the two constituent accelerator nbi target planes.
    :ivar divergence_component : Detailed information on beamlet divergence. Divergence is described as a superposition of Gaussian components with amplitide &#34;particles_fraction&#34; and vertical/horizontal divergence. Note that for positive ion NBI the divergence is well described by a single Gaussian
    :ivar beamlets : Detailed information on beamlets
    """

    class Meta:
        name = "nbi_unit_beamlets_group"
        is_root_ids = False

    position: Optional[Rphiz0DStatic] = field(
        default=None,
        metadata={"imas_type": "rphiz0d_static", "field_type": Rphiz0DStatic},
    )
    tangency_radius: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    angle: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    tilting: Optional[NbiUnitBeamletsGroupTilting] = field(
        default_factory=lambda: StructArray(
            type_input=NbiUnitBeamletsGroupTilting
        ),
        metadata={
            "imas_type": "nbi_unit_beamlets_group_tilting",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": NbiUnitBeamletsGroupTilting,
        },
    )
    direction: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    width_horizontal: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    width_vertical: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    focus: Optional[NbiUnitBeamletsGroupFocus] = field(
        default=None,
        metadata={
            "imas_type": "nbi_unit_beamlets_group_focus",
            "field_type": NbiUnitBeamletsGroupFocus,
        },
    )
    divergence_component: Optional[NbiUnitBeamletsGroupDivergence] = field(
        default_factory=lambda: StructArray(
            type_input=NbiUnitBeamletsGroupDivergence
        ),
        metadata={
            "imas_type": "nbi_unit_beamlets_group_divergence",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": NbiUnitBeamletsGroupDivergence,
        },
    )
    beamlets: Optional[NbiUnitBeamletsGroupBeamlets] = field(
        default=None,
        metadata={
            "imas_type": "nbi_unit_beamlets_group_beamlets",
            "field_type": NbiUnitBeamletsGroupBeamlets,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class NbiUnit(IdsBaseClass):
    """

    :ivar name : Short string identifier (unique for a given device)
    :ivar description : Description, e.g. “channel viewing the upper divertor”
    :ivar species : Injected species
    :ivar power_launched : Power launched from this unit into the vacuum vessel
    :ivar energy : Full energy of the injected species (acceleration of a single atom)
    :ivar beam_current_fraction : Fractions of beam current distributed among the different energies, the first index corresponds to the fast neutrals energy (1:full, 2: half, 3: one third)
    :ivar beam_power_fraction : Fractions of beam power distributed among the different energies, the first index corresponds to the fast neutrals energy (1:full, 2: half, 3: one third)
    :ivar beamlets_group : Group of beamlets with common vertical and horizontal focal point. If there are no common focal points, then select small groups of beamlets such that a focal point description of the beamlets group provides a fair description. Beamlet groups are assumed to be Gaussian.
    :ivar source : Description of the surface of the ion source from which the beam is extracted
    :ivar aperture : Description of a set of collimating apertures through which the beam is launched
    """

    class Meta:
        name = "nbi_unit"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    description: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    species: Optional[PlasmaCompositionSpecies] = field(
        default=None,
        metadata={
            "imas_type": "plasma_composition_species",
            "field_type": PlasmaCompositionSpecies,
        },
    )
    power_launched: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )
    energy: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )
    beam_current_fraction: Optional[SignalFlt2D] = field(
        default_factory=lambda: StructArray(type_input=SignalFlt2D),
        metadata={
            "imas_type": "signal_flt_2d",
            "ndims": 2,
            "coordinates": {"coordinate1": "1...3", "coordinate2": "time"},
            "field_type": SignalFlt2D,
        },
    )
    beam_power_fraction: Optional[SignalFlt2D] = field(
        default_factory=lambda: StructArray(type_input=SignalFlt2D),
        metadata={
            "imas_type": "signal_flt_2d",
            "ndims": 2,
            "coordinates": {"coordinate1": "1...3", "coordinate2": "time"},
            "field_type": SignalFlt2D,
        },
    )
    beamlets_group: Optional[NbiUnitBeamletsGroup] = field(
        default_factory=lambda: StructArray(type_input=NbiUnitBeamletsGroup),
        metadata={
            "imas_type": "nbi_unit_beamlets_group",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": NbiUnitBeamletsGroup,
        },
    )
    source: Optional[DetectorAperture] = field(
        default=None,
        metadata={
            "imas_type": "detector_aperture",
            "field_type": DetectorAperture,
        },
    )
    aperture: Optional[DetectorAperture] = field(
        default_factory=lambda: StructArray(type_input=DetectorAperture),
        metadata={
            "imas_type": "detector_aperture",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": DetectorAperture,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class Nbi(IdsBaseClass):
    """

    :ivar ids_properties :
    :ivar unit : The NBI system is described as a set of units of which the power can be controlled individually.
    :ivar latency : Upper bound of the delay between input command received from the RT network and actuator starting to react. Applies globally to the system described by this IDS unless specific latencies (e.g. channel-specific or antenna-specific) are provided at a deeper level in the IDS structure.
    :ivar code :
    :ivar time : Generic time
    """

    class Meta:
        name = "nbi"
        is_root_ids = True

    ids_properties: Optional[IdsProperties] = field(
        default=None,
        metadata={"imas_type": "ids_properties", "field_type": IdsProperties},
    )
    unit: Optional[NbiUnit] = field(
        default_factory=lambda: StructArray(type_input=NbiUnit),
        metadata={
            "imas_type": "nbi_unit",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": NbiUnit,
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
