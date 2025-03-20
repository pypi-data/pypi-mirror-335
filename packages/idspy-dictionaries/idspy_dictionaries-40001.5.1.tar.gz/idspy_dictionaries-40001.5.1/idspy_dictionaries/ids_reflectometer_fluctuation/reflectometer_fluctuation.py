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
class Xyz0DDynamicAos3(IdsBaseClass):
    """

    :ivar x : Component along X axis
    :ivar y : Component along Y axis
    :ivar z : Component along Z axis
    """

    class Meta:
        name = "xyz0d_dynamic_aos3"
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
class LineOfSight2PointsDynamicAos3(IdsBaseClass):
    """

    :ivar first_point : Position of the first point
    :ivar second_point : Position of the second point
    """

    class Meta:
        name = "line_of_sight_2points_dynamic_aos3"
        is_root_ids = False

    first_point: Optional[Rphiz0DDynamicAos3] = field(
        default=None,
        metadata={
            "imas_type": "rphiz0d_dynamic_aos3",
            "field_type": Rphiz0DDynamicAos3,
        },
    )
    second_point: Optional[Rphiz0DDynamicAos3] = field(
        default=None,
        metadata={
            "imas_type": "rphiz0d_dynamic_aos3",
            "field_type": Rphiz0DDynamicAos3,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class FlatObjectStatic(IdsBaseClass):
    """

    :ivar geometry_type : Type of geometry used to describe the surface of the detector or aperture (1:&#39;outline&#39;, 2:&#39;circular&#39;, 3:&#39;rectangle&#39;). In case of &#39;outline&#39;, the surface is described by an outline of point in a local coordinate system defined by a centre and three unit vectors X1, X2, X3. Note that there is some flexibility here and the data provider should choose the most convenient coordinate system for the object, respecting the definitions of (X1,X2,X3) indicated below. In case of &#39;circular&#39;, the surface is a circle defined by its centre, radius, and normal vector oriented towards the plasma X3.  In case of &#39;rectangle&#39;, the surface is a rectangle defined by its centre, widths in the X1 and X2 directions, and normal vector oriented towards the plasma X3.
    :ivar centre : If geometry_type=2, coordinates of the centre of the circle. If geometry_type=1 or 3, coordinates of the origin of the local coordinate system (X1,X2,X3) describing the plane detector/aperture. This origin is located within the detector/aperture area.
    :ivar radius : Radius of the circle, used only if geometry_type = 2
    :ivar x1_width : Full width of the aperture in the X1 direction, used only if geometry_type = 3
    :ivar x2_width : Full width of the aperture in the X2 direction, used only if geometry_type = 3
    :ivar outline : Irregular outline of the detector/aperture in the (X1, X2) coordinate system. Repeat the first point since this is a closed contour
    :ivar surface : Surface of the detector/aperture, derived from the above geometric data
    """

    class Meta:
        name = "flat_object_static"
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
class FlatObjectOrientationAos3(IdsBaseClass):
    """

    :ivar x1_unit_vector : Components of the X1 direction unit vector in the (X,Y,Z) coordinate system, where X is the major radius axis for phi = 0, Y is the major radius axis for phi = pi/2, and Z is the height axis. The X1 vector is more horizontal than X2 (has a smaller abs(Z) component) and oriented in the positive phi direction (counter-clockwise when viewing from above).
    :ivar x2_unit_vector : Components of the X2 direction unit vector in the (X,Y,Z) coordinate system, where X is the major radius axis for phi = 0, Y is the major radius axis for phi = pi/2, and Z is the height axis. The X2 axis is orthonormal so that uX2 = uX3 x uX1.
    :ivar x3_unit_vector : Components of the X3 direction unit vector in the (X,Y,Z) coordinate system, where X is the major radius axis for phi = 0, Y is the major radius axis for phi = pi/2, and Z is the height axis. The X3 axis is normal to the detector/aperture plane and oriented towards the plasma.
    """

    class Meta:
        name = "flat_object_orientation_aos3"
        is_root_ids = False

    x1_unit_vector: Optional[Xyz0DDynamicAos3] = field(
        default=None,
        metadata={
            "imas_type": "xyz0d_dynamic_aos3",
            "field_type": Xyz0DDynamicAos3,
        },
    )
    x2_unit_vector: Optional[Xyz0DDynamicAos3] = field(
        default=None,
        metadata={
            "imas_type": "xyz0d_dynamic_aos3",
            "field_type": Xyz0DDynamicAos3,
        },
    )
    x3_unit_vector: Optional[Xyz0DDynamicAos3] = field(
        default=None,
        metadata={
            "imas_type": "xyz0d_dynamic_aos3",
            "field_type": Xyz0DDynamicAos3,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class PsiNormalization(IdsBaseClass):
    """

    :ivar psi_magnetic_axis : Value of the poloidal magnetic flux at the magnetic axis
    :ivar psi_boundary : Value of the poloidal magnetic flux at the plasma boundary
    :ivar time : Time for the R,Z,phi coordinates
    """

    class Meta:
        name = "psi_normalization"
        is_root_ids = False

    psi_magnetic_axis: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../time"},
            "field_type": np.ndarray,
        },
    )
    psi_boundary: Optional[np.ndarray] = field(
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
class ReflectometerAntennas(IdsBaseClass):
    """

    :ivar line_of_sight_emission : Description of the line of sight of the emission antenna. The first point corresponds to the centre of the antenna mouth. The second point correspond to the interception of the line of sight with the reflection surface on the inner wall.
    :ivar line_of_sight_detection : Description of the line of sight of the detection antenna, to be filled only if its position is distinct from the emission antenna. The first point corresponds to the centre of the antenna mouth. The second point correspond to the interception of the line of sight with the reflection surface on the inner wall.
    :ivar antenna_emission : Dynamic emission antenna orientation
    :ivar antenna_detection : Dynamic detection antenna orientation, to be filled only if it is distinct from the emission antenna.
    :ivar time : Time
    """

    class Meta:
        name = "reflectometer_antennas"
        is_root_ids = False

    line_of_sight_emission: Optional[LineOfSight2PointsDynamicAos3] = field(
        default=None,
        metadata={
            "imas_type": "line_of_sight_2points_dynamic_aos3",
            "field_type": LineOfSight2PointsDynamicAos3,
        },
    )
    line_of_sight_detection: Optional[LineOfSight2PointsDynamicAos3] = field(
        default=None,
        metadata={
            "imas_type": "line_of_sight_2points_dynamic_aos3",
            "field_type": LineOfSight2PointsDynamicAos3,
        },
    )
    antenna_emission: Optional[FlatObjectOrientationAos3] = field(
        default=None,
        metadata={
            "imas_type": "flat_object_orientation_aos3",
            "field_type": FlatObjectOrientationAos3,
        },
    )
    antenna_detection: Optional[FlatObjectOrientationAos3] = field(
        default=None,
        metadata={
            "imas_type": "flat_object_orientation_aos3",
            "field_type": FlatObjectOrientationAos3,
        },
    )
    time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class ReflectometerDopplerPosition1D(IdsBaseClass):
    """

    :ivar r : Major radius
    :ivar z : Height
    :ivar phi : Toroidal angle (oriented counter-clockwise when viewing from above)
    :ivar psi : Poloidal flux
    :ivar rho_tor_norm : Normalized toroidal flux coordinate
    :ivar rho_pol_norm : Normalized poloidal flux coordinate = sqrt((psi(rho)-psi(magnetic_axis)) / (psi(LCFS)-psi(magnetic_axis)))
    :ivar theta : Poloidal angle (oriented clockwise when viewing the poloidal cross section on the right hand side of the tokamak axis of symmetry, with the origin placed on the plasma magnetic axis)
    """

    class Meta:
        name = "reflectometer_doppler_position_1d"
        is_root_ids = False

    r: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time"},
            "field_type": np.ndarray,
        },
    )
    z: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time"},
            "field_type": np.ndarray,
        },
    )
    phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time"},
            "field_type": np.ndarray,
        },
    )
    psi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time"},
            "field_type": np.ndarray,
        },
    )
    rho_tor_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time"},
            "field_type": np.ndarray,
        },
    )
    rho_pol_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time"},
            "field_type": np.ndarray,
        },
    )
    theta: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class ReflectometerFluctuationLevelPosition2D(IdsBaseClass):
    """

    :ivar r : Major radius
    :ivar z : Height
    :ivar phi : Toroidal angle (oriented counter-clockwise when viewing from above)
    :ivar psi : Poloidal flux
    :ivar rho_tor_norm : Normalized toroidal flux coordinate
    :ivar rho_pol_norm : Normalized poloidal flux coordinate = sqrt((psi(rho)-psi(magnetic_axis)) / (psi(LCFS)-psi(magnetic_axis)))
    :ivar theta : Poloidal angle (oriented clockwise when viewing the poloidal cross section on the right hand side of the tokamak axis of symmetry, with the origin placed on the plasma magnetic axis)
    """

    class Meta:
        name = "reflectometer_fluctuation_level_position_2d"
        is_root_ids = False

    r: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate1_same_as": "../../dn_e_over_n_e",
                "coordinate2": "../../time",
            },
            "field_type": np.ndarray,
        },
    )
    z: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate1_same_as": "../../dn_e_over_n_e",
                "coordinate2": "../../time",
            },
            "field_type": np.ndarray,
        },
    )
    phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate1_same_as": "../../dn_e_over_n_e",
                "coordinate2": "../../time",
            },
            "field_type": np.ndarray,
        },
    )
    psi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate1_same_as": "../../dn_e_over_n_e",
                "coordinate2": "../../time",
            },
            "field_type": np.ndarray,
        },
    )
    rho_tor_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate1_same_as": "../../dn_e_over_n_e",
                "coordinate2": "../../time",
            },
            "field_type": np.ndarray,
        },
    )
    rho_pol_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate1_same_as": "../../dn_e_over_n_e",
                "coordinate2": "../../time",
            },
            "field_type": np.ndarray,
        },
    )
    theta: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate1_same_as": "../../dn_e_over_n_e",
                "coordinate2": "../../time",
            },
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class ReflectometerFluctuationLevel(IdsBaseClass):
    """

    :ivar dn_e_over_n_e : Relative amplitude of the density fluctuations post-processed for swept and fixed frequency (profile/one point)
    :ivar position : Array of positions at which the fluctuation level is computed
    :ivar time_width : Width of the time interval over which fluctuating profiles are processed. By convention, the time interval starts at time-time_width and ends at time.
    :ivar radial_width : Width in the radial direction over which fluctuating profiles are processed
    :ivar time : Time
    """

    class Meta:
        name = "reflectometer_fluctuation_level"
        is_root_ids = False

    dn_e_over_n_e: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {"coordinate1": "1...N", "coordinate2": "../time"},
            "field_type": np.ndarray,
        },
    )
    position: Optional[ReflectometerFluctuationLevelPosition2D] = field(
        default=None,
        metadata={
            "imas_type": "reflectometer_fluctuation_level_position_2d",
            "field_type": ReflectometerFluctuationLevelPosition2D,
        },
    )
    time_width: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    radial_width: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
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
class ReflectometerFluctuationDoppler(IdsBaseClass):
    """

    :ivar wavenumber : Wavenumber probed by the diagnostic
    :ivar shift : Doppler frequency shift (for the main peak of the power spectrum)
    :ivar velocity_pol : Poloidal velocity
    :ivar e_field_radial : Radial electric field
    :ivar position : Measurement position
    :ivar time_width : Width of the time interval over which fluctuating profiles are processed. By convention, the time interval starts at time-time_width and ends at time.
    :ivar radial_width : Width in the radial direction over which fluctuating profiles are processed
    :ivar time : Time
    """

    class Meta:
        name = "reflectometer_fluctuation_doppler"
        is_root_ids = False

    wavenumber: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../time"},
            "field_type": np.ndarray,
        },
    )
    shift: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../time"},
            "field_type": np.ndarray,
        },
    )
    velocity_pol: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../time"},
            "field_type": np.ndarray,
        },
    )
    e_field_radial: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../time"},
            "field_type": np.ndarray,
        },
    )
    position: Optional[ReflectometerDopplerPosition1D] = field(
        default=None,
        metadata={
            "imas_type": "reflectometer_doppler_position_1d",
            "field_type": ReflectometerDopplerPosition1D,
        },
    )
    time_width: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    radial_width: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
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
class ReflectometerFluctuationSpectrum(IdsBaseClass):
    """

    :ivar power_log : Power spectrum in log scale
    :ivar frequencies_fourier : Array of frequencies used for the Fourier transform
    :ivar time_width : Width of the time interval over which the spectrum is processed. By convention, the time interval starts at time-time_width and ends at time.
    :ivar time : Time
    """

    class Meta:
        name = "reflectometer_fluctuation_spectrum"
        is_root_ids = False

    power_log: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 4, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 4,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate1_same_as": "../../frequencies/data",
                "coordinate2": "../frequencies_fourier",
                "coordinate3": "../time",
            },
            "field_type": np.ndarray,
        },
    )
    frequencies_fourier: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    time_width: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
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
class ReflectometerFluctuationRaw(IdsBaseClass):
    """

    :ivar i_component : I component of the IQ detector used to retrieve the phase of signal&#39;s envelope
    :ivar q_component : Q component of the IQ detector used to retrieve the phase of signal&#39;s envelope
    :ivar time : Time
    """

    class Meta:
        name = "reflectometer_fluctuation_raw"
        is_root_ids = False

    i_component: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate1_same_as": "../../frequencies/data",
                "coordinate2": "../time",
            },
            "field_type": np.ndarray,
        },
    )
    q_component: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate1_same_as": "../../frequencies/data",
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
class ReflectometerFluctuationChannel(IdsBaseClass):
    """

    :ivar name : Short string identifier (unique for a given device)
    :ivar description : Description, e.g. “channel viewing the upper divertor”
    :ivar mode : Detection mode &#34;X&#34; or &#34;O&#34;
    :ivar antennas_orientation : Description of lines of sight and antenna orientation as a function of time
    :ivar antenna_emission_static : Static part of the geometry of the emission antenna
    :ivar antenna_detection_static : Static part of the geometry of the detection antenna, to be filled only if it is distinct from the emission antenna.
    :ivar sweep_time : Duration of a sweep
    :ivar frequencies : Array of frequencies scanned during a sweep
    :ivar raw_signal : Raw data from IQ detector
    :ivar phase : Measured phase of the probing wave for each frequency and time slice (corresponding to the begin time of a sweep), relative to the phase at launch
    :ivar amplitude : Measured amplitude of the detected probing wave for each frequency and time slice (corresponding to the begin time of a sweep)
    :ivar fluctuations_level : Reconstruction of the amplitude of the fluctuations
    :ivar fluctuations_spectrum : Spectrum of the fluctuations, obtained by Fourier transform
    :ivar doppler : Processed data for Doppler reflectometers
    """

    class Meta:
        name = "reflectometer_fluctuation_channel"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    description: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    mode: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    antennas_orientation: Optional[ReflectometerAntennas] = field(
        default_factory=lambda: StructArray(type_input=ReflectometerAntennas),
        metadata={
            "imas_type": "reflectometer_antennas",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": ReflectometerAntennas,
        },
    )
    antenna_emission_static: Optional[FlatObjectStatic] = field(
        default=None,
        metadata={
            "imas_type": "flat_object_static",
            "field_type": FlatObjectStatic,
        },
    )
    antenna_detection_static: Optional[FlatObjectStatic] = field(
        default=None,
        metadata={
            "imas_type": "flat_object_static",
            "field_type": FlatObjectStatic,
        },
    )
    sweep_time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    frequencies: Optional[SignalFlt2D] = field(
        default_factory=lambda: StructArray(type_input=SignalFlt2D),
        metadata={
            "imas_type": "signal_flt_2d",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": SignalFlt2D,
        },
    )
    raw_signal: Optional[ReflectometerFluctuationRaw] = field(
        default=None,
        metadata={
            "imas_type": "reflectometer_fluctuation_raw",
            "field_type": ReflectometerFluctuationRaw,
        },
    )
    phase: Optional[SignalFlt2D] = field(
        default_factory=lambda: StructArray(type_input=SignalFlt2D),
        metadata={
            "imas_type": "signal_flt_2d",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate1_same_as": "../frequencies/data",
            },
            "field_type": SignalFlt2D,
        },
    )
    amplitude: Optional[SignalFlt2D] = field(
        default_factory=lambda: StructArray(type_input=SignalFlt2D),
        metadata={
            "imas_type": "signal_flt_2d",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate1_same_as": "../frequencies/data",
            },
            "field_type": SignalFlt2D,
        },
    )
    fluctuations_level: Optional[ReflectometerFluctuationLevel] = field(
        default=None,
        metadata={
            "imas_type": "reflectometer_fluctuation_level",
            "field_type": ReflectometerFluctuationLevel,
        },
    )
    fluctuations_spectrum: Optional[ReflectometerFluctuationSpectrum] = field(
        default=None,
        metadata={
            "imas_type": "reflectometer_fluctuation_spectrum",
            "field_type": ReflectometerFluctuationSpectrum,
        },
    )
    doppler: Optional[ReflectometerFluctuationDoppler] = field(
        default=None,
        metadata={
            "imas_type": "reflectometer_fluctuation_doppler",
            "field_type": ReflectometerFluctuationDoppler,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class ReflectometerFluctuation(IdsBaseClass):
    """

    :ivar ids_properties :
    :ivar type : Type of reflectometer (frequency_swept, radar, ...)
    :ivar channel : Set of channels, e.g. different reception antennas or frequency bandwidths of the reflectometer
    :ivar psi_normalization : Quantities to use to normalize psi, as a function of time
    :ivar latency : Upper bound of the delay between physical information received by the detector and data available on the real-time (RT) network.
    :ivar code :
    :ivar time : Generic time
    """

    class Meta:
        name = "reflectometer_fluctuation"
        is_root_ids = True

    ids_properties: Optional[IdsProperties] = field(
        default=None,
        metadata={"imas_type": "ids_properties", "field_type": IdsProperties},
    )
    type: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    channel: Optional[ReflectometerFluctuationChannel] = field(
        default_factory=lambda: StructArray(
            type_input=ReflectometerFluctuationChannel
        ),
        metadata={
            "imas_type": "reflectometer_fluctuation_channel",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": ReflectometerFluctuationChannel,
        },
    )
    psi_normalization: Optional[PsiNormalization] = field(
        default=None,
        metadata={
            "imas_type": "psi_normalization",
            "field_type": PsiNormalization,
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
