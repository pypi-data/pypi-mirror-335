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
class CurvedSurface(IdsBaseClass):
    """

    :ivar curvature_type : Curvature of the surface
    :ivar x1_curvature : Radius of curvature in the X1 direction, to be filled only for curvature_type/index = 2, 4 or 5
    :ivar x2_curvature : Radius of curvature in the X2 direction, to be filled only for curvature_type/index = 3 or 5
    """

    class Meta:
        name = "curved_surface"
        is_root_ids = False

    curvature_type: Optional[IdentifierStatic] = field(
        default=None,
        metadata={
            "imas_type": "identifier_static",
            "field_type": IdentifierStatic,
        },
    )
    x1_curvature: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    x2_curvature: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class OpticalElementMaterial(IdsBaseClass):
    """

    :ivar type : Type of optical element material. In case of &#39;metal&#39; refractive_index and extinction_coefficient are used. In case of &#39;dielectric&#39; refractive_index and transmission_coefficient are used.
    :ivar wavelengths : Wavelengths array for refractive_index, extinction_coefficient and transmission_coefficient
    :ivar refractive_index : Refractive index (for metal and dielectric)
    :ivar extinction_coefficient : Extinction coefficient (for metal)
    :ivar transmission_coefficient : Transmission coefficient (for dielectric)
    :ivar roughness : Roughness parameter of the material. Varies in range [0, 1]. 0 is perfectly specular, 1 is perfectly rough
    """

    class Meta:
        name = "optical_element_material"
        is_root_ids = False

    type: Optional[IdentifierStatic] = field(
        default=None,
        metadata={
            "imas_type": "identifier_static",
            "field_type": IdentifierStatic,
        },
    )
    wavelengths: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    refractive_index: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../wavelengths"},
            "field_type": np.ndarray,
        },
    )
    extinction_coefficient: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../wavelengths"},
            "field_type": np.ndarray,
        },
    )
    transmission_coefficient: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../wavelengths"},
            "field_type": np.ndarray,
        },
    )
    roughness: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../wavelengths"},
            "field_type": np.ndarray,
        },
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
class OpticalElement(IdsBaseClass):
    """

    :ivar type : Type of optical element. In case of &#39;mirror&#39; and &#39;diaphragm&#39;, the element is described by one &#39;front_surface&#39;. In case of &#39;lens&#39;, the element is described by &#39;front_surface&#39; and &#39;back_surface&#39;.
    :ivar front_surface : Curvature of the front surface
    :ivar back_surface : Curvature of the front surface
    :ivar thickness : Distance between front_surface and back_surface along the X3 vector
    :ivar material_properties : Material properties of the optical element
    :ivar geometry : Further geometrical description of the element
    """

    class Meta:
        name = "optical_element"
        is_root_ids = False

    type: Optional[IdentifierStatic] = field(
        default=None,
        metadata={
            "imas_type": "identifier_static",
            "field_type": IdentifierStatic,
        },
    )
    front_surface: Optional[CurvedSurface] = field(
        default=None,
        metadata={"imas_type": "curved_surface", "field_type": CurvedSurface},
    )
    back_surface: Optional[CurvedSurface] = field(
        default=None,
        metadata={"imas_type": "curved_surface", "field_type": CurvedSurface},
    )
    thickness: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    material_properties: Optional[OpticalElementMaterial] = field(
        default=None,
        metadata={
            "imas_type": "optical_element_material",
            "field_type": OpticalElementMaterial,
        },
    )
    geometry: Optional[DetectorAperture] = field(
        default=None,
        metadata={
            "imas_type": "detector_aperture",
            "field_type": DetectorAperture,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class FibreBundle(IdsBaseClass):
    """

    :ivar geometry : Geometry of the fibre bundle entrance
    :ivar fibre_radius : Radius of a single fibre
    :ivar fibre_positions : Individual fibres centres positions in the (X1, X2) coordinate system
    """

    class Meta:
        name = "fibre_bundle"
        is_root_ids = False

    geometry: Optional[DetectorAperture] = field(
        default=None,
        metadata={
            "imas_type": "detector_aperture",
            "field_type": DetectorAperture,
        },
    )
    fibre_radius: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    fibre_positions: Optional[X1X21DStatic] = field(
        default=None,
        metadata={"imas_type": "x1x21d_static", "field_type": X1X21DStatic},
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
class CameraIrCalibration(IdsBaseClass):
    """

    :ivar luminance_to_temperature : Luminance to temperature conversion table
    :ivar transmission_barrel : Transmission of the optical barrel
    :ivar transmission_mirror : Transmission of the mirror
    :ivar transmission_window : Transmission of the window
    :ivar optical_temperature : Temperature of the optical components (digital levels)
    """

    class Meta:
        name = "camera_ir_calibration"
        is_root_ids = False

    luminance_to_temperature: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=int),
        metadata={
            "imas_type": "INT_2D",
            "ndims": 2,
            "coordinates": {"coordinate1": "1...N", "coordinate2": "1...2"},
            "field_type": np.ndarray,
        },
    )
    transmission_barrel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 4, dtype=int),
        metadata={
            "imas_type": "INT_2D",
            "ndims": 4,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate1_same_as": "../../frame(itime)/surface_temperature",
                "coordinate2": "1...N",
                "coordinate2_same_as": "../../frame(itime)/surface_temperature",
            },
            "field_type": np.ndarray,
        },
    )
    transmission_mirror: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 4, dtype=int),
        metadata={
            "imas_type": "INT_2D",
            "ndims": 4,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate1_same_as": "../../frame(itime)/surface_temperature",
                "coordinate2": "1...N",
                "coordinate2_same_as": "../../frame(itime)/surface_temperature",
            },
            "field_type": np.ndarray,
        },
    )
    transmission_window: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 4, dtype=int),
        metadata={
            "imas_type": "INT_2D",
            "ndims": 4,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate1_same_as": "../../frame(itime)/surface_temperature",
                "coordinate2": "1...N",
                "coordinate2_same_as": "../../frame(itime)/surface_temperature",
            },
            "field_type": np.ndarray,
        },
    )
    optical_temperature: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=int),
        metadata={
            "imas_type": "INT_2D",
            "ndims": 2,
            "coordinates": {"coordinate1": "1...N", "coordinate2": "1...N"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class CameraIrFrameAnalysis(IdsBaseClass):
    """

    :ivar sol_heat_decay_length : Heat flux decay length in SOL at divertor entrance, mapped to the mid-plane, this is the lambda_q parameter defined in reference T. Eich et al, Nucl. Fusion 53 (2013) 093031
    :ivar distance_separatrix_midplane : Distance between the measurement position and the separatrix, mapped along flux surfaces to the outboard midplane, in the major radius direction. Positive value means the measurement is outside of the separatrix.
    :ivar power_flux_parallel : Parallel heat flux received by the element monitored by the camera, along the distance_separatrix_midplane coordinate
    :ivar time : Time
    """

    class Meta:
        name = "camera_ir_frame_analysis"
        is_root_ids = False

    sol_heat_decay_length: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    distance_separatrix_midplane: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    power_flux_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../distance_separatrix_midplane"},
            "field_type": np.ndarray,
        },
    )
    time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class CameraIrFrame(IdsBaseClass):
    """

    :ivar surface_temperature : Surface temperature image. First dimension : line index (horizontal axis). Second dimension: column index (vertical axis). The size of this matrix is assumed to be constant over time
    :ivar time : Time
    """

    class Meta:
        name = "camera_ir_frame"
        is_root_ids = False

    surface_temperature: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {"coordinate1": "1...N", "coordinate2": "1...N"},
            "field_type": np.ndarray,
        },
    )
    time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class CameraIr(IdsBaseClass):
    """

    :ivar ids_properties :
    :ivar name : Name of the camera
    :ivar calibration : Calibration data
    :ivar frame : Set of frames
    :ivar midplane : Choice of midplane definition for the mapping of measurements on an equilibrium
    :ivar frame_analysis : Quantities deduced from frame analysis for a set of time slices
    :ivar optical_element : Set of optical elements
    :ivar fibre_bundle : Description of the fibre bundle
    :ivar latency : Upper bound of the delay between physical information received by the detector and data available on the real-time (RT) network.
    :ivar code :
    :ivar time : Generic time
    """

    class Meta:
        name = "camera_ir"
        is_root_ids = True

    ids_properties: Optional[IdsProperties] = field(
        default=None,
        metadata={"imas_type": "ids_properties", "field_type": IdsProperties},
    )
    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    calibration: Optional[CameraIrCalibration] = field(
        default=None,
        metadata={
            "imas_type": "camera_ir_calibration",
            "field_type": CameraIrCalibration,
        },
    )
    frame: Optional[CameraIrFrame] = field(
        default_factory=lambda: StructArray(type_input=CameraIrFrame),
        metadata={
            "imas_type": "camera_ir_frame",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": CameraIrFrame,
        },
    )
    midplane: Optional[IdentifierStatic] = field(
        default=None,
        metadata={
            "imas_type": "identifier_static",
            "field_type": IdentifierStatic,
        },
    )
    frame_analysis: Optional[CameraIrFrameAnalysis] = field(
        default_factory=lambda: StructArray(type_input=CameraIrFrameAnalysis),
        metadata={
            "imas_type": "camera_ir_frame_analysis",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": CameraIrFrameAnalysis,
        },
    )
    optical_element: Optional[OpticalElement] = field(
        default_factory=lambda: StructArray(type_input=OpticalElement),
        metadata={
            "imas_type": "optical_element",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": OpticalElement,
        },
    )
    fibre_bundle: Optional[FibreBundle] = field(
        default=None,
        metadata={"imas_type": "fibre_bundle", "field_type": FibreBundle},
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
