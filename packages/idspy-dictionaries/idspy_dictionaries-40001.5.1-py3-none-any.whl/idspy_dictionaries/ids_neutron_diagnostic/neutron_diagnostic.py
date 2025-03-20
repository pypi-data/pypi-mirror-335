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
class Rphiz1DGrid(IdsBaseClass):
    """

    :ivar r : Major radius
    :ivar phi : Toroidal angle (oriented counter-clockwise when viewing from above)
    :ivar z : Height
    """

    class Meta:
        name = "rphiz1d_grid"
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
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    z: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
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
class DetectorEnergyBand(IdsBaseClass):
    """

    :ivar lower_bound : Lower bound of the energy band
    :ivar upper_bound : Upper bound of the energy band
    :ivar energies : Array of discrete energy values inside the band
    :ivar detection_efficiency : Probability of detection of a photon impacting the detector as a function of its energy
    """

    class Meta:
        name = "detector_energy_band"
        is_root_ids = False

    lower_bound: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    upper_bound: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    energies: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    detection_efficiency: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../energies"},
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
class Xyz3DStatic(IdsBaseClass):
    """

    :ivar x : Components along X axis for each voxel
    :ivar y : Component along Y axis  for each voxel
    :ivar z : Component along Z axis  for each voxel
    """

    class Meta:
        name = "xyz3d_static"
        is_root_ids = False

    x: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "../../emission_grid/r",
                "coordinate2": "../../emission_grid/z",
                "coordinate3": "../../emission_grid/phi",
            },
            "field_type": np.ndarray,
        },
    )
    y: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "../../emission_grid/r",
                "coordinate2": "../../emission_grid/z",
                "coordinate3": "../../emission_grid/phi",
            },
            "field_type": np.ndarray,
        },
    )
    z: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "../../emission_grid/r",
                "coordinate2": "../../emission_grid/z",
                "coordinate3": "../../emission_grid/phi",
            },
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class NeutronDiagnosticEvent(IdsBaseClass):
    """

    :ivar type : Type of the event
    :ivar values : Array of values for the event
    """

    class Meta:
        name = "neutron_diagnostic_event"
        is_root_ids = False

    type: Optional[IdentifierStatic] = field(
        default=None,
        metadata={
            "imas_type": "identifier_static",
            "field_type": IdentifierStatic,
        },
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


@idspy_dataclass(repr=False, slots=True)
class NeutronDiagnosticFieldOfView(IdsBaseClass):
    """

    :ivar solid_angle : Average solid angle that the detector covers within the voxel
    :ivar emission_grid : Grid defining the neutron emission cells in the plasma
    :ivar direction_to_detector : Vector that points from the centre of the voxel to the centre of the detector, described in the (X,Y,Z) coordinate system, where X is the major radius axis for phi = 0, Y is the major radius axis for phi = pi/2, and Z is the height axis.
    """

    class Meta:
        name = "neutron_diagnostic_field_of_view"
        is_root_ids = False

    solid_angle: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "../emission_grid/r",
                "coordinate2": "../emission_grid/z",
                "coordinate3": "../emission_grid/phi",
            },
            "field_type": np.ndarray,
        },
    )
    emission_grid: Optional[Rphiz1DGrid] = field(
        default=None,
        metadata={"imas_type": "rphiz1d_grid", "field_type": Rphiz1DGrid},
    )
    direction_to_detector: Optional[Xyz3DStatic] = field(
        default=None,
        metadata={"imas_type": "xyz3d_static", "field_type": Xyz3DStatic},
    )


@idspy_dataclass(repr=False, slots=True)
class NeutronDiagnosticGreen(IdsBaseClass):
    """

    :ivar source_neutron_energies : Array of source neutron energy bins
    :ivar event_in_detector_neutron_flux : 5th dimension for the neutron_flux Green function representing values of events measured in the detector. The type of events monitored depends on the detector and can be defined by the user. It can be energy of neutrons, or electrical signal, or time of flight ... (defined by type below)
    :ivar neutron_flux_integrated_flags : Array of flags telling, for each coordinate of the neutron_flux, whether the neutron_flux has been integrated over this coordinate (1) or not (0). If it has been integrated over a coordinate, the size related to this coordinate must be equal to 1
    :ivar neutron_flux : Grouped neutron flux in the detector from one neutron energy bin emitted by the current plasma voxel towards the detector
    :ivar event_in_detector_response_function : 5th dimension for the response_function Green function representing values of events measured in the detector. The type of events monitored depends on the detector and can be defined by the user. It can be energy of neutrons, or electrical signal, or time of flight ... (defined by type below)
    :ivar response_function_integrated_flags : Array of flags telling, for each coordinate of the response_function, whether the response_function has been integrated over this coordinate (1) or not (0). If it has been integrated over a coordinate, the size related to this coordinate must be equal to 1
    :ivar response_function : Number of events occurring in the detector from one neutron energy bin emitted by the current plasma voxel towards the detector
    """

    class Meta:
        name = "neutron_diagnostic_green"
        is_root_ids = False

    source_neutron_energies: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    event_in_detector_neutron_flux: Optional[NeutronDiagnosticEvent] = field(
        default=None,
        metadata={
            "imas_type": "neutron_diagnostic_event",
            "field_type": NeutronDiagnosticEvent,
        },
    )
    neutron_flux_integrated_flags: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=int),
        metadata={
            "imas_type": "INT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...5"},
            "field_type": np.ndarray,
        },
    )
    neutron_flux: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 5, dtype=float),
        metadata={
            "imas_type": "FLT_5D",
            "ndims": 5,
            "coordinates": {
                "coordinate1": "../../field_of_view/emission_grid/r",
                "coordinate2": "../../field_of_view/emission_grid/z",
                "coordinate3": "../../field_of_view/emission_grid/phi",
                "coordinate4": "../source_neutron_energies",
                "coordinate5": "../event_in_detector_neutron_flux/values",
            },
            "field_type": np.ndarray,
        },
    )
    event_in_detector_response_function: Optional[NeutronDiagnosticEvent] = (
        field(
            default=None,
            metadata={
                "imas_type": "neutron_diagnostic_event",
                "field_type": NeutronDiagnosticEvent,
            },
        )
    )
    response_function_integrated_flags: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=int),
        metadata={
            "imas_type": "INT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...5"},
            "field_type": np.ndarray,
        },
    )
    response_function: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 5, dtype=float),
        metadata={
            "imas_type": "FLT_5D",
            "ndims": 5,
            "coordinates": {
                "coordinate1": "../../field_of_view/emission_grid/r",
                "coordinate2": "../../field_of_view/emission_grid/z",
                "coordinate3": "../../field_of_view/emission_grid/phi",
                "coordinate4": "../source_neutron_energies",
                "coordinate5": "../event_in_detector_response_function/values",
            },
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class NeutronDiagnosticTemperatureSensor(IdsBaseClass):
    """

    :ivar power_switch : Power switch (1=on, 0=off)
    :ivar temperature : Temperature measured by the sensor
    """

    class Meta:
        name = "neutron_diagnostic_temperature_sensor"
        is_root_ids = False

    power_switch: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    temperature: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )


@idspy_dataclass(repr=False, slots=True)
class NeutronDiagnosticBFieldSensor(IdsBaseClass):
    """

    :ivar power_switch : Power switch (1=on, 0=off)
    :ivar b_field : Magnetic field measured by the sensor
    """

    class Meta:
        name = "neutron_diagnostic_b_field_sensor"
        is_root_ids = False

    power_switch: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    b_field: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )


@idspy_dataclass(repr=False, slots=True)
class NeutronDiagnosticTestGenerator(IdsBaseClass):
    """

    :ivar power_switch : Power switch (1=on, 0=off)
    :ivar rise_time : Peak rise time
    :ivar fall_time : Peak fall time
    :ivar frequency : Generated signal frequency
    :ivar amplitude : Generated signal amplitude
    """

    class Meta:
        name = "neutron_diagnostic_test_generator"
        is_root_ids = False

    power_switch: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    rise_time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    fall_time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    frequency: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )
    amplitude: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )


@idspy_dataclass(repr=False, slots=True)
class NeutronDiagnosticSupply(IdsBaseClass):
    """

    :ivar power_switch : Power switch (1=on, 0=off)
    :ivar voltage_set : Voltage set
    :ivar voltage_out : Voltage at the supply output
    """

    class Meta:
        name = "neutron_diagnostic_supply"
        is_root_ids = False

    power_switch: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    voltage_set: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )
    voltage_out: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )


@idspy_dataclass(repr=False, slots=True)
class NeutronDiagnosticAdc(IdsBaseClass):
    """

    :ivar power_switch : Power switch (1=on, 0=off)
    :ivar discriminator_level_lower : Lower level discriminator of ADC
    :ivar discriminator_level_upper : Upper level discriminator of ADC
    :ivar sampling_rate : Number of samples recorded per second
    :ivar bias : ADC signal bias
    :ivar input_range : ADC input range
    :ivar impedance : ADC impedance
    """

    class Meta:
        name = "neutron_diagnostic_adc"
        is_root_ids = False

    power_switch: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    discriminator_level_lower: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    discriminator_level_upper: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    sampling_rate: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    bias: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    input_range: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    impedance: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class NeutronDiagnosticDetectorMode(IdsBaseClass):
    """

    :ivar identifier : Identifier of the measuring mode
    :ivar counting : Detected counts per second as a function of time
    :ivar count_limit_max : Maximum count limit under which the detector response is linear
    :ivar count_limit_min : Minimum count limit above which the detector response is linear
    :ivar spectrum : Detected counts per second per energy channel as a function of time (in case of spectroscopic measurement mode)
    """

    class Meta:
        name = "neutron_diagnostic_detector_mode"
        is_root_ids = False

    identifier: Optional[IdentifierStatic] = field(
        default=None,
        metadata={
            "imas_type": "identifier_static",
            "field_type": IdentifierStatic,
        },
    )
    counting: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )
    count_limit_max: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    count_limit_min: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    spectrum: Optional[SignalFlt2D] = field(
        default_factory=lambda: StructArray(type_input=SignalFlt2D),
        metadata={
            "imas_type": "signal_flt_2d",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../energy_band"},
            "field_type": SignalFlt2D,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class NeutronDiagnosticDetectors(IdsBaseClass):
    """

    :ivar name : Name of the detector
    :ivar geometry : Detector geometry
    :ivar material : Name of detector&#39;s converter for resent particle
    :ivar nuclei_n : Number of target nuclei in the dectector
    :ivar temperature : Temperature of the detector
    :ivar aperture : Description of a set of collimating apertures
    :ivar mode : Set of Measuring Modes simultaneously used by the detector
    :ivar energy_band : Set of energy bands in which neutrons are counted by the detector
    :ivar exposure_time : Exposure time
    :ivar adc : Description of analogic-digital converter
    :ivar supply_high_voltage : Description of high voltage power supply
    :ivar supply_low_voltage : Description of low voltage power supply
    :ivar test_generator : Test generator characteristics
    :ivar b_field_sensor : Magnetic field sensor
    :ivar temperature_sensor : Temperature sensor
    :ivar field_of_view : Field of view associated to this detector. The field of view is described by a voxelized plasma volume. Each voxel, with indexes i_R, i_Z, and i_phi, has an associated solid angle scalar and a detector direction vector.
    :ivar green_functions : Green function coefficients used to represent the detector response based on its field of view
    """

    class Meta:
        name = "neutron_diagnostic_detectors"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    geometry: Optional[DetectorAperture] = field(
        default=None,
        metadata={
            "imas_type": "detector_aperture",
            "field_type": DetectorAperture,
        },
    )
    material: Optional[IdentifierStatic] = field(
        default=None,
        metadata={
            "imas_type": "identifier_static",
            "field_type": IdentifierStatic,
        },
    )
    nuclei_n: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    temperature: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "/time"},
            "field_type": np.ndarray,
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
    mode: Optional[NeutronDiagnosticDetectorMode] = field(
        default_factory=lambda: StructArray(
            type_input=NeutronDiagnosticDetectorMode
        ),
        metadata={
            "imas_type": "neutron_diagnostic_detector_mode",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": NeutronDiagnosticDetectorMode,
        },
    )
    energy_band: Optional[DetectorEnergyBand] = field(
        default_factory=lambda: StructArray(type_input=DetectorEnergyBand),
        metadata={
            "imas_type": "detector_energy_band",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": DetectorEnergyBand,
        },
    )
    exposure_time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    adc: Optional[NeutronDiagnosticAdc] = field(
        default=None,
        metadata={
            "imas_type": "neutron_diagnostic_adc",
            "field_type": NeutronDiagnosticAdc,
        },
    )
    supply_high_voltage: Optional[NeutronDiagnosticSupply] = field(
        default=None,
        metadata={
            "imas_type": "neutron_diagnostic_supply",
            "field_type": NeutronDiagnosticSupply,
        },
    )
    supply_low_voltage: Optional[NeutronDiagnosticSupply] = field(
        default=None,
        metadata={
            "imas_type": "neutron_diagnostic_supply",
            "field_type": NeutronDiagnosticSupply,
        },
    )
    test_generator: Optional[NeutronDiagnosticTestGenerator] = field(
        default=None,
        metadata={
            "imas_type": "neutron_diagnostic_test_generator",
            "field_type": NeutronDiagnosticTestGenerator,
        },
    )
    b_field_sensor: Optional[NeutronDiagnosticTestGenerator] = field(
        default=None,
        metadata={
            "imas_type": "neutron_diagnostic_test_generator",
            "field_type": NeutronDiagnosticTestGenerator,
        },
    )
    temperature_sensor: Optional[NeutronDiagnosticTestGenerator] = field(
        default=None,
        metadata={
            "imas_type": "neutron_diagnostic_test_generator",
            "field_type": NeutronDiagnosticTestGenerator,
        },
    )
    field_of_view: Optional[NeutronDiagnosticFieldOfView] = field(
        default=None,
        metadata={
            "imas_type": "neutron_diagnostic_field_of_view",
            "field_type": NeutronDiagnosticFieldOfView,
        },
    )
    green_functions: Optional[NeutronDiagnosticGreen] = field(
        default=None,
        metadata={
            "imas_type": "neutron_diagnostic_green",
            "field_type": NeutronDiagnosticGreen,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class NeutronDiagnostic(IdsBaseClass):
    """

    :ivar ids_properties :
    :ivar detector : Set of neutron detection systems
    :ivar neutron_flux_total : Total Neutron Flux reconstructed from the detectors signals
    :ivar fusion_power : Fusion power reconstructed from the detectors signals
    :ivar latency : Upper bound of the delay between physical information received by the detector and data available on the real-time (RT) network.
    :ivar code :
    :ivar time : Generic time
    """

    class Meta:
        name = "neutron_diagnostic"
        is_root_ids = True

    ids_properties: Optional[IdsProperties] = field(
        default=None,
        metadata={"imas_type": "ids_properties", "field_type": IdsProperties},
    )
    detector: Optional[NeutronDiagnosticDetectors] = field(
        default_factory=lambda: StructArray(
            type_input=NeutronDiagnosticDetectors
        ),
        metadata={
            "imas_type": "neutron_diagnostic_detectors",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": NeutronDiagnosticDetectors,
        },
    )
    neutron_flux_total: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../time"},
            "field_type": np.ndarray,
        },
    )
    fusion_power: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../time"},
            "field_type": np.ndarray,
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
