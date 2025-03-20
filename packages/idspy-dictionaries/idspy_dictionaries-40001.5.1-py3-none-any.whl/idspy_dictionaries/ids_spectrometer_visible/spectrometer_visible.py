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
class LineOfSight2Points(IdsBaseClass):
    """

    :ivar first_point : Position of the first point
    :ivar second_point : Position of the second point
    """

    class Meta:
        name = "line_of_sight_2points"
        is_root_ids = False

    first_point: Optional[Rphiz0DStatic] = field(
        default=None,
        metadata={"imas_type": "rphiz0d_static", "field_type": Rphiz0DStatic},
    )
    second_point: Optional[Rphiz0DStatic] = field(
        default=None,
        metadata={"imas_type": "rphiz0d_static", "field_type": Rphiz0DStatic},
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
class GeometryMatrixEmission(IdsBaseClass):
    """

    :ivar grid_type : Grid type
    :ivar dim1 : First dimension values
    :ivar dim2 : Second dimension values
    :ivar dim3 : Third dimension values
    """

    class Meta:
        name = "geometry_matrix_emission"
        is_root_ids = False

    grid_type: Optional[IdentifierStatic] = field(
        default=None,
        metadata={
            "imas_type": "identifier_static",
            "field_type": IdentifierStatic,
        },
    )
    dim1: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    dim2: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    dim3: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
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
class SignalInt1D(IdsBaseClass):
    """

    :ivar data : Data
    :ivar time : Time
    """

    class Meta:
        name = "signal_int_1d"
        is_root_ids = False

    data: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=int),
        metadata={
            "imas_type": "INT_1D",
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
class PlasmaCompositionNeutralElementConstant(IdsBaseClass):
    """

    :ivar a : Mass of atom
    :ivar z_n : Nuclear charge
    :ivar atoms_n : Number of atoms of this element in the molecule
    """

    class Meta:
        name = "plasma_composition_neutral_element_constant"
        is_root_ids = False

    a: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    z_n: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    atoms_n: Optional[int] = field(
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
class SpectroVisGeometryMatrixInterpolated(IdsBaseClass):
    """

    :ivar r : Major radius of interpolation knots
    :ivar z : Height of interpolation knots
    :ivar phi : Toroidal angle (oriented counter-clockwise when viewing from above) of interpolation knots
    :ivar data : Interpolated Ray Transfer Matrix (RTM, or geometry matrix), which provides transformation of the reflected light from each interpolation knot to the receiver (detector or head of an optic fibre). When convolving with an emission profile, the values must be interpolated to the emission grid and multiplied by the volume of the grid cells. The interpolated matrix is given on an array of interpolation knots of coordinates r, z and phi
    """

    class Meta:
        name = "spectro_vis_geometry_matrix_interpolated"
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
    phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../r"},
            "field_type": np.ndarray,
        },
    )
    data: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../r"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SpectroVisGeometryMatrixStep2(IdsBaseClass):
    """

    :ivar data : The Ray Transfer Matrix (RTM, or geometry matrix) here provides transformation of the signal from each individual unit light source (voxel) to the receiver (detector or head of an optic fibre). The emission profile has [photons.m^-3.s^-1.sr^-1] units and radiance signal has [photons.m^-2.s^-1.sr^-1] units. So the RTM has [m] units. This data is stored in a sparse form, i.e. the array contains only the non-zero element of the Ray transfer matrix. The voxel index corresponding to an element of this array can be found in voxel_indices
    :ivar voxel_indices : List of voxel indices (defined in the voxel map) used in the sparse data array
    """

    class Meta:
        name = "spectro_vis_geometry_matrix_step2"
        is_root_ids = False

    data: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    voxel_indices: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=int),
        metadata={
            "imas_type": "INT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../data"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SpectroVisGeometryMatrix(IdsBaseClass):
    """

    :ivar with_reflections : Geometry matrix with reflections
    :ivar without_reflections : Geometry matrix without reflections
    :ivar interpolated : Interpolated geometry matrix for reflected light
    :ivar voxel_map : Voxel map for geometry matrix. The cells with same number are merged in the computation into a single emission source meta-cell (the voxel). Cells with number -1 are excluded. Voxel count starts from 0.
    :ivar voxels_n : Number of voxels defined in the voxel_map.
    :ivar emission_grid : Grid defining the light emission cells
    """

    class Meta:
        name = "spectro_vis_geometry_matrix"
        is_root_ids = False

    with_reflections: Optional[SpectroVisGeometryMatrixStep2] = field(
        default=None,
        metadata={
            "imas_type": "spectro_vis_geometry_matrix_step2",
            "field_type": SpectroVisGeometryMatrixStep2,
        },
    )
    without_reflections: Optional[SpectroVisGeometryMatrixStep2] = field(
        default=None,
        metadata={
            "imas_type": "spectro_vis_geometry_matrix_step2",
            "field_type": SpectroVisGeometryMatrixStep2,
        },
    )
    interpolated: Optional[SpectroVisGeometryMatrixInterpolated] = field(
        default=None,
        metadata={
            "imas_type": "spectro_vis_geometry_matrix_interpolated",
            "field_type": SpectroVisGeometryMatrixInterpolated,
        },
    )
    voxel_map: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=int),
        metadata={
            "imas_type": "INT_3D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "../emission_grid/dim1",
                "coordinate2": "../emission_grid/dim2",
                "coordinate3": "../emission_grid/dim3",
            },
            "field_type": np.ndarray,
        },
    )
    voxels_n: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    emission_grid: Optional[GeometryMatrixEmission] = field(
        default=None,
        metadata={
            "imas_type": "geometry_matrix_emission",
            "field_type": GeometryMatrixEmission,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SpectroVisChannelWavelengthCalibration(IdsBaseClass):
    """

    :ivar offset : Offset
    :ivar gain : Gain
    """

    class Meta:
        name = "spectro_vis_channel_wavelength_calibration"
        is_root_ids = False

    offset: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    gain: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class SpectroVisChannelProcessedLineFilter(IdsBaseClass):
    """

    :ivar name : String identifying the processed line. To avoid ambiguities, the following syntax is used : element with ionization state_wavelength in Angstrom (e.g. WI_4000)
    :ivar wavelength_central : Central wavelength of the processed line
    """

    class Meta:
        name = "spectro_vis_channel_processed_line_filter"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    wavelength_central: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class SpectroVisChannelProcessedLine(IdsBaseClass):
    """

    :ivar name : String identifying the processed line. To avoid ambiguities, the following syntax is used : element with ionization state_wavelength in Angstrom (e.g. WI_4000)
    :ivar wavelength_central : Central wavelength of the processed line
    :ivar radiance : Calibrated, background subtracted radiance (integrated over the spectrum for this line)
    :ivar intensity : Non-calibrated intensity (integrated over the spectrum for this line)
    """

    class Meta:
        name = "spectro_vis_channel_processed_line"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    wavelength_central: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    radiance: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )
    intensity: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )


@idspy_dataclass(repr=False, slots=True)
class SpectroVisChannelLightCollection(IdsBaseClass):
    """

    :ivar values : Values of the light collection efficiencies
    :ivar positions : List of positions for which the light collection efficiencies are provided
    """

    class Meta:
        name = "spectro_vis_channel_light_collection"
        is_root_ids = False

    values: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../positions/r"},
            "field_type": np.ndarray,
        },
    )
    positions: Optional[Rphiz1DStatic] = field(
        default=None,
        metadata={"imas_type": "rphiz1d_static", "field_type": Rphiz1DStatic},
    )


@idspy_dataclass(repr=False, slots=True)
class DetectorImageCircular(IdsBaseClass):
    """

    :ivar radius : Radius of the circle
    :ivar ellipticity : Ellipticity
    """

    class Meta:
        name = "detector_image_circular"
        is_root_ids = False

    radius: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    ellipticity: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class DetectorImage(IdsBaseClass):
    """

    :ivar geometry_type : Type of geometry used to describe the image (1:&#39;outline&#39;, 2:&#39;circular&#39;)
    :ivar outline : Coordinates of the points shaping the polygon of the image
    :ivar circular : Description of circular or elliptic image
    """

    class Meta:
        name = "detector_image"
        is_root_ids = False

    geometry_type: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    outline: Optional[Rphiz1DStatic] = field(
        default=None,
        metadata={"imas_type": "rphiz1d_static", "field_type": Rphiz1DStatic},
    )
    circular: Optional[DetectorImageCircular] = field(
        default=None,
        metadata={
            "imas_type": "detector_image_circular",
            "field_type": DetectorImageCircular,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SpectroVisChannelIsotopesIsotope(IdsBaseClass):
    """

    :ivar element : List of elements forming the atom or molecule
    :ivar name : String identifying the species (H, D, T, He3, He4)
    :ivar density_ratio : Ratio of the density of neutrals of this isotope over the summed neutral densities of all other isotopes described in the ../isotope array
    :ivar cold_neutrals_fraction : Fraction of cold neutrals for this isotope (n_cold_neutrals/(n_cold_neutrals+n_hot_neutrals))
    :ivar hot_neutrals_fraction : Fraction of hot neutrals for this isotope (n_hot_neutrals/(n_cold_neutrals+n_hot_neutrals))
    :ivar cold_neutrals_temperature : Temperature of cold neutrals for this isotope
    :ivar hot_neutrals_temperature : Temperature of hot neutrals for this isotope
    :ivar time : Timebase for dynamic quantities at this level of the data structure
    """

    class Meta:
        name = "spectro_vis_channel_isotopes_isotope"
        is_root_ids = False

    element: Optional[PlasmaCompositionNeutralElementConstant] = field(
        default_factory=lambda: StructArray(
            type_input=PlasmaCompositionNeutralElementConstant
        ),
        metadata={
            "imas_type": "plasma_composition_neutral_element_constant",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": PlasmaCompositionNeutralElementConstant,
        },
    )
    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    density_ratio: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../time"},
            "field_type": np.ndarray,
        },
    )
    cold_neutrals_fraction: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../time"},
            "field_type": np.ndarray,
        },
    )
    hot_neutrals_fraction: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../time"},
            "field_type": np.ndarray,
        },
    )
    cold_neutrals_temperature: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../time"},
            "field_type": np.ndarray,
        },
    )
    hot_neutrals_temperature: Optional[np.ndarray] = field(
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
class SpectroVisChannelIsotopes(IdsBaseClass):
    """

    :ivar validity_timed : Indicator of the validity of the isotope ratios as a function of time (0 means valid, negative values mean non-valid)
    :ivar validity : Indicator of the validity of the isotope ratios for the whole acquisition period (0 means valid, negative values mean non-valid)
    :ivar signal_to_noise : Log10 of the ratio of the powers in two bands, one with the spectral lines of interest (signal) the other without spectral lines (noise).
    :ivar isotope : Set of isotopes
    :ivar time : Timebase for dynamic quantities at this level of the data structure
    """

    class Meta:
        name = "spectro_vis_channel_isotopes"
        is_root_ids = False

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
    signal_to_noise: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../time"},
            "field_type": np.ndarray,
        },
    )
    isotope: Optional[SpectroVisChannelIsotopesIsotope] = field(
        default_factory=lambda: StructArray(
            type_input=SpectroVisChannelIsotopesIsotope
        ),
        metadata={
            "imas_type": "spectro_vis_channel_isotopes_isotope",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": SpectroVisChannelIsotopesIsotope,
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
class SpectroVisChannelPolarization(IdsBaseClass):
    """

    :ivar e_field_lh_r : Lower Hybrid electric field component in the major radius direction
    :ivar e_field_lh_z : Lower Hybrid electric field component in the vertical direction
    :ivar e_field_lh_phi : Lower Hybrid electric field component in the toroidal direction
    :ivar b_field_modulus : Modulus of the magnetic field (always positive, irrespective of the sign convention for the B-field direction), obtained from Zeeman effect fit
    :ivar n_e : Electron density, obtained from Stark broadening fit
    :ivar temperature_cold_neutrals : Fit of cold neutrals temperature
    :ivar temperature_hot_neutrals : Fit of hot neutrals temperature
    :ivar velocity_cold_neutrals : Projection of the cold neutral velocity along the line of sight, positive when going from first point to second point of the line of sight
    :ivar velocity_hot_neutrals : Projection of the hot neutral velocity along the line of sight, positive when going from first point to second point of the line of sight
    :ivar time : Timebase for dynamic quantities at this level of the data structure
    """

    class Meta:
        name = "spectro_vis_channel_polarization"
        is_root_ids = False

    e_field_lh_r: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../time"},
            "field_type": np.ndarray,
        },
    )
    e_field_lh_z: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../time"},
            "field_type": np.ndarray,
        },
    )
    e_field_lh_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../time"},
            "field_type": np.ndarray,
        },
    )
    b_field_modulus: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../time"},
            "field_type": np.ndarray,
        },
    )
    n_e: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../time"},
            "field_type": np.ndarray,
        },
    )
    temperature_cold_neutrals: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../time"},
            "field_type": np.ndarray,
        },
    )
    temperature_hot_neutrals: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../time"},
            "field_type": np.ndarray,
        },
    )
    velocity_cold_neutrals: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../time"},
            "field_type": np.ndarray,
        },
    )
    velocity_hot_neutrals: Optional[np.ndarray] = field(
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
class SpectroVisChannelResolution(IdsBaseClass):
    """

    :ivar centre : Position of the centre of the spatially resolved zone
    :ivar width : Full width of the spatially resolved zone in the R, Z and phi directions
    :ivar time : Time
    """

    class Meta:
        name = "spectro_vis_channel_resolution"
        is_root_ids = False

    centre: Optional[Rphiz0DDynamicAos3] = field(
        default=None,
        metadata={
            "imas_type": "rphiz0d_dynamic_aos3",
            "field_type": Rphiz0DDynamicAos3,
        },
    )
    width: Optional[Rphiz0DDynamicAos3] = field(
        default=None,
        metadata={
            "imas_type": "rphiz0d_dynamic_aos3",
            "field_type": Rphiz0DDynamicAos3,
        },
    )
    time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class SpectroVisChannelFilterFilter(IdsBaseClass):
    """

    :ivar wavelength_central : Central wavelength of the filter
    :ivar wavelength_width : Filter transmission function width (at 90% level)
    """

    class Meta:
        name = "spectro_vis_channel_filter_filter"
        is_root_ids = False

    wavelength_central: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    wavelength_width: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class SpectroVisChannelFilter(IdsBaseClass):
    """

    :ivar filter : Filter description
    :ivar processed_line : Set of processed spectral lines (normally a single line is filtered out, but it may happen in some cases that several lines go through the filter).
    :ivar output_voltage : Raw voltage output of the whole acquisition chain
    :ivar photoelectric_voltage : Gain corrected and background subtracted voltage
    :ivar photon_count : Detected photon count
    :ivar exposure_time : Exposure time
    :ivar wavelengths : Array of wavelengths for radiance calibration
    :ivar radiance_calibration : Radiance calibration
    :ivar radiance_calibration_date : Date of the radiance calibration (yyyy_mm_dd)
    :ivar sensitivity : Photoelectric sensitivity of the detector. This is the conversion factor from the received power on the detector into electric voltage depending on the wavelength
    """

    class Meta:
        name = "spectro_vis_channel_filter"
        is_root_ids = False

    filter: Optional[SpectroVisChannelFilterFilter] = field(
        default=None,
        metadata={
            "imas_type": "spectro_vis_channel_filter_filter",
            "field_type": SpectroVisChannelFilterFilter,
        },
    )
    processed_line: Optional[SpectroVisChannelProcessedLineFilter] = field(
        default_factory=lambda: StructArray(
            type_input=SpectroVisChannelProcessedLineFilter
        ),
        metadata={
            "imas_type": "spectro_vis_channel_processed_line_filter",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": SpectroVisChannelProcessedLineFilter,
        },
    )
    output_voltage: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )
    photoelectric_voltage: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )
    photon_count: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )
    exposure_time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
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
    radiance_calibration: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../wavelengths"},
            "field_type": np.ndarray,
        },
    )
    radiance_calibration_date: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    sensitivity: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../wavelengths"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SpectroVisChannelGrating(IdsBaseClass):
    """

    :ivar grating : Number of grating lines per unit length
    :ivar slit_width : Width of the slit (placed in the object focal plane)
    :ivar wavelengths : Measured wavelengths
    :ivar radiance_spectral : Calibrated spectral radiance (radiance per unit wavelength)
    :ivar intensity_spectrum : Intensity spectrum (not calibrated), i.e. number of photoelectrons detected by unit time by a wavelength pixel of the channel, taking into account electronic gain compensation and channels relative calibration
    :ivar exposure_time : Exposure time
    :ivar processed_line : Set of processed spectral lines
    :ivar radiance_calibration : Radiance calibration
    :ivar radiance_calibration_date : Date of the radiance calibration (yyyy_mm_dd)
    :ivar wavelength_calibration : Wavelength calibration data. The wavelength is obtained from the pixel index k by: wavelength =  k * gain + offset. k is starting from 1.
    :ivar wavelength_calibration_date : Date of the wavelength calibration (yyyy_mm_dd)
    :ivar instrument_function : Array of Gaussian widths and amplitudes which as a sum make up the instrument function. The instrument function is the shape that would be measured by a grating spectrometer if perfectly monochromatic line emission would be used as input. F(lambda) = 1 / sqrt (2*pi) * sum( instrument_function(1,i) / instrument_function(2,i)  ) * exp( -lambda^2 / (2 * instrument_function(2,i)^2) )  ), whereby sum( instrument_function(1,i) ) = 1
    """

    class Meta:
        name = "spectro_vis_channel_grating"
        is_root_ids = False

    grating: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    slit_width: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
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
    radiance_spectral: Optional[SignalFlt2D] = field(
        default_factory=lambda: StructArray(type_input=SignalFlt2D),
        metadata={
            "imas_type": "signal_flt_2d",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../wavelengths",
                "coordinate2": "time",
            },
            "field_type": SignalFlt2D,
        },
    )
    intensity_spectrum: Optional[SignalFlt2D] = field(
        default_factory=lambda: StructArray(type_input=SignalFlt2D),
        metadata={
            "imas_type": "signal_flt_2d",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../wavelengths",
                "coordinate2": "time",
            },
            "field_type": SignalFlt2D,
        },
    )
    exposure_time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    processed_line: Optional[SpectroVisChannelProcessedLine] = field(
        default_factory=lambda: StructArray(
            type_input=SpectroVisChannelProcessedLine
        ),
        metadata={
            "imas_type": "spectro_vis_channel_processed_line",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": SpectroVisChannelProcessedLine,
        },
    )
    radiance_calibration: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../wavelengths"},
            "field_type": np.ndarray,
        },
    )
    radiance_calibration_date: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    wavelength_calibration: Optional[SpectroVisChannelWavelengthCalibration] = (
        field(
            default=None,
            metadata={
                "imas_type": "spectro_vis_channel_wavelength_calibration",
                "field_type": SpectroVisChannelWavelengthCalibration,
            },
        )
    )
    wavelength_calibration_date: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    instrument_function: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {"coordinate1": "1...2", "coordinate2": "1...N"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SpectroVisChannel(IdsBaseClass):
    """

    :ivar name : Name of the channel
    :ivar object_observed : Main object observed by the channel
    :ivar type : Type of spectrometer the channel is connected to (index=1: grating, 2: filter)
    :ivar detector : Detector description
    :ivar aperture : Description of a set of collimating apertures
    :ivar etendue : Etendue (geometric extent) of the channel&#39;s optical system
    :ivar etendue_method : Method used to calculate the etendue. Index = 0 : exact calculation with a 4D integral; 1 : approximation with first order formula (detector surface times solid angle subtended by the apertures); 2 : other methods
    :ivar line_of_sight : Description of the line of sight of the channel, given by 2 points
    :ivar detector_image : Image of the detector or pixel on the focal plane of the optical system
    :ivar fibre_image : Image of the optical fibre on the focal plane of the optical system
    :ivar light_collection_efficiencies : Light collection efficiencies (fraction of the local emission detected by the optical system) for a list of points defining regions of interest. To be used for non-pinhole optics.
    :ivar active_spatial_resolution : In case of active spectroscopy, describes the spatial resolution of the measurement, calculated as a convolution of the atomic smearing, magnetic and beam geometry smearing and detector projection, for a set of time slices
    :ivar polarizer : Polarizer description
    :ivar polarizer_active : Indicator of whether a polarizer is present and active in the optical system (set to 1 in this case, set to 0 or leave empty ottherwise)
    :ivar grating_spectrometer : Quantities measured by the channel if connected to a grating spectrometer
    :ivar filter_spectrometer : Quantities measured by the channel if connected to a filter spectrometer
    :ivar validity_timed : Indicator of the validity of the channel as a function of time (0 means valid, negative values mean non-valid)
    :ivar validity : Indicator of the validity of the channel for the whole acquisition period (0 means valid, negative values mean non-valid)
    :ivar isotope_ratios : Isotope ratios and related information
    :ivar polarization_spectroscopy : Physics quantities measured from polarized light spectroscopy
    :ivar geometry_matrix : Description of geometry matrix (ray transfer matrix)
    :ivar optical_element : Set of optical elements
    :ivar fibre_bundle : Description of the fibre bundle
    """

    class Meta:
        name = "spectro_vis_channel"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    object_observed: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    type: Optional[IdentifierStatic] = field(
        default=None,
        metadata={
            "imas_type": "identifier_static",
            "field_type": IdentifierStatic,
        },
    )
    detector: Optional[DetectorAperture] = field(
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
    etendue: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    etendue_method: Optional[IdentifierStatic] = field(
        default=None,
        metadata={
            "imas_type": "identifier_static",
            "field_type": IdentifierStatic,
        },
    )
    line_of_sight: Optional[LineOfSight2Points] = field(
        default=None,
        metadata={
            "imas_type": "line_of_sight_2points",
            "field_type": LineOfSight2Points,
        },
    )
    detector_image: Optional[DetectorImage] = field(
        default=None,
        metadata={"imas_type": "detector_image", "field_type": DetectorImage},
    )
    fibre_image: Optional[DetectorImage] = field(
        default=None,
        metadata={"imas_type": "detector_image", "field_type": DetectorImage},
    )
    light_collection_efficiencies: Optional[
        SpectroVisChannelLightCollection
    ] = field(
        default=None,
        metadata={
            "imas_type": "spectro_vis_channel_light_collection",
            "field_type": SpectroVisChannelLightCollection,
        },
    )
    active_spatial_resolution: Optional[SpectroVisChannelResolution] = field(
        default_factory=lambda: StructArray(
            type_input=SpectroVisChannelResolution
        ),
        metadata={
            "imas_type": "spectro_vis_channel_resolution",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": SpectroVisChannelResolution,
        },
    )
    polarizer: Optional[DetectorAperture] = field(
        default=None,
        metadata={
            "imas_type": "detector_aperture",
            "field_type": DetectorAperture,
        },
    )
    polarizer_active: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    grating_spectrometer: Optional[SpectroVisChannelGrating] = field(
        default=None,
        metadata={
            "imas_type": "spectro_vis_channel_grating",
            "field_type": SpectroVisChannelGrating,
        },
    )
    filter_spectrometer: Optional[SpectroVisChannelFilter] = field(
        default=None,
        metadata={
            "imas_type": "spectro_vis_channel_filter",
            "field_type": SpectroVisChannelFilter,
        },
    )
    validity_timed: Optional[SignalInt1D] = field(
        default=None,
        metadata={"imas_type": "signal_int_1d", "field_type": SignalInt1D},
    )
    validity: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )
    isotope_ratios: Optional[SpectroVisChannelIsotopes] = field(
        default=None,
        metadata={
            "imas_type": "spectro_vis_channel_isotopes",
            "field_type": SpectroVisChannelIsotopes,
        },
    )
    polarization_spectroscopy: Optional[SpectroVisChannelPolarization] = field(
        default=None,
        metadata={
            "imas_type": "spectro_vis_channel_polarization",
            "field_type": SpectroVisChannelPolarization,
        },
    )
    geometry_matrix: Optional[SpectroVisGeometryMatrix] = field(
        default=None,
        metadata={
            "imas_type": "spectro_vis_geometry_matrix",
            "field_type": SpectroVisGeometryMatrix,
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


@idspy_dataclass(repr=False, slots=True)
class SpectrometerVisible(IdsBaseClass):
    """

    :ivar ids_properties :
    :ivar detector_layout : Layout of the detector grid employed. Ex: &#39;4x16&#39;, &#39;4x32&#39;, &#39;1x18&#39;
    :ivar channel : Set of channels (detector or pixel of a camera)
    :ivar latency : Upper bound of the delay between physical information received by the detector and data available on the real-time (RT) network.
    :ivar code :
    :ivar time : Generic time
    """

    class Meta:
        name = "spectrometer_visible"
        is_root_ids = True

    ids_properties: Optional[IdsProperties] = field(
        default=None,
        metadata={"imas_type": "ids_properties", "field_type": IdsProperties},
    )
    detector_layout: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    channel: Optional[SpectroVisChannel] = field(
        default_factory=lambda: StructArray(type_input=SpectroVisChannel),
        metadata={
            "imas_type": "spectro_vis_channel",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": SpectroVisChannel,
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
