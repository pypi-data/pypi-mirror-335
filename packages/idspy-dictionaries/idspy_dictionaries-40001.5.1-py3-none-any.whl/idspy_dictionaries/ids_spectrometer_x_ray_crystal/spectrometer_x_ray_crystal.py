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
class Rphiz2DStatic(IdsBaseClass):
    """

    :ivar r : Major radius
    :ivar phi : Toroidal angle (oriented counter-clockwise when viewing from above)
    :ivar z : Height
    """

    class Meta:
        name = "rphiz2d_static"
        is_root_ids = False

    r: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {"coordinate1": "1...N", "coordinate2": "1...N"},
            "field_type": np.ndarray,
        },
    )
    phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 4, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 4,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate1_same_as": "../r",
                "coordinate2": "1...N",
                "coordinate2_same_as": "../r",
            },
            "field_type": np.ndarray,
        },
    )
    z: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 4, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 4,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate1_same_as": "../r",
                "coordinate2": "1...N",
                "coordinate2_same_as": "../r",
            },
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class LineOfSight2PointsRphiz2D(IdsBaseClass):
    """

    :ivar first_point : Position of the first point
    :ivar second_point : Position of the second point
    """

    class Meta:
        name = "line_of_sight_2points_rphiz_2d"
        is_root_ids = False

    first_point: Optional[Rphiz2DStatic] = field(
        default=None,
        metadata={"imas_type": "rphiz2d_static", "field_type": Rphiz2DStatic},
    )
    second_point: Optional[Rphiz2DStatic] = field(
        default=None,
        metadata={"imas_type": "rphiz2d_static", "field_type": Rphiz2DStatic},
    )


@idspy_dataclass(repr=False, slots=True)
class FilterWindow(IdsBaseClass):
    """

    :ivar name : Short string identifier (unique for a given device)
    :ivar description : Description, e.g. “channel viewing the upper divertor”
    :ivar geometry_type : Geometry of the filter contour. Note that there is some flexibility in the choice of the local coordinate system (X1,X2,X3). The data provider should choose the most convenient coordinate system for the filter, respecting the definitions of (X1,X2,X3) indicated below.
    :ivar curvature_type : Curvature of the filter.
    :ivar centre : Coordinates of the origin of the local coordinate system (X1,X2,X3) describing the filter. This origin is located within the filter area and should be the middle point of the filter surface. If geometry_type=2, it&#39;s the centre of the circular filter. If geometry_type=3, it&#39;s the centre of the rectangular filter.
    :ivar radius : Radius of the circle, used only if geometry_type/index = 2
    :ivar x1_unit_vector : Components of the X1 direction unit vector in the (X,Y,Z) coordinate system, where X is the major radius axis for phi = 0, Y is the major radius axis for phi = pi/2, and Z is the height axis. The X1 vector is more horizontal than X2 (has a smaller abs(Z) component) and oriented in the positive phi direction (counter-clockwise when viewing from above).
    :ivar x2_unit_vector : Components of the X2 direction unit vector in the (X,Y,Z) coordinate system, where X is the major radius axis for phi = 0, Y is the major radius axis for phi = pi/2, and Z is the height axis. The X2 axis is orthonormal so that uX2 = uX3 x uX1.
    :ivar x3_unit_vector : Components of the X3 direction unit vector in the (X,Y,Z) coordinate system, where X is the major radius axis for phi = 0, Y is the major radius axis for phi = pi/2, and Z is the height axis. The X3 axis is normal to the filter surface and oriented towards the plasma.
    :ivar x1_width : Full width of the filter in the X1 direction, used only if geometry_type/index = 3
    :ivar x2_width : Full width of the filter in the X2 direction, used only if geometry_type/index = 3
    :ivar outline : Irregular outline of the filter in the (X1, X2) coordinate system, used only if geometry_type/index=1. Repeat the first point since this is a closed contour
    :ivar x1_curvature : Radius of curvature in the X1 direction, to be filled only for curvature_type/index = 2, 4 or 5
    :ivar x2_curvature : Radius of curvature in the X2 direction, to be filled only for curvature_type/index = 3 or 5
    :ivar surface : Surface of the filter, derived from the above geometric data
    :ivar material : Material of the filter window
    :ivar thickness : Thickness of the filter window
    :ivar wavelength_lower : Lower bound of the filter wavelength range
    :ivar wavelength_upper : Upper bound of the filter wavelength range
    :ivar wavelengths : Array of wavelength values
    :ivar photon_absorption : Probability of absorbing a photon passing through the filter as a function of its wavelength
    """

    class Meta:
        name = "filter_window"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    description: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    geometry_type: Optional[IdentifierStatic] = field(
        default=None,
        metadata={
            "imas_type": "identifier_static",
            "field_type": IdentifierStatic,
        },
    )
    curvature_type: Optional[IdentifierStatic] = field(
        default=None,
        metadata={
            "imas_type": "identifier_static",
            "field_type": IdentifierStatic,
        },
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
    x1_curvature: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    x2_curvature: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    surface: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    material: Optional[IdentifierStatic] = field(
        default=None,
        metadata={
            "imas_type": "identifier_static",
            "field_type": IdentifierStatic,
        },
    )
    thickness: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    wavelength_lower: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    wavelength_upper: Optional[float] = field(
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
    photon_absorption: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../wavelengths"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class CurvedObject(IdsBaseClass):
    """

    :ivar name : Short string identifier (unique for a given device)
    :ivar description : Description, e.g. “channel viewing the upper divertor”
    :ivar geometry_type : Geometry of the object contour. Note that there is some flexibility in the choice of the local coordinate system (X1,X2,X3). The data provider should choose the most convenient coordinate system for the object, respecting the definitions of (X1,X2,X3) indicated below.
    :ivar curvature_type : Curvature of the object.
    :ivar material : Material of the object
    :ivar centre : Coordinates of the origin of the local coordinate system (X1,X2,X3) describing the object. This origin is located within the object area and should be the middle point of the object surface. If geometry_type=2, it&#39;s the centre of the circular object. If geometry_type=3, it&#39;s the centre of the rectangular object.
    :ivar radius : Radius of the circle, used only if geometry_type/index = 2
    :ivar x1_unit_vector : Components of the X1 direction unit vector in the (X,Y,Z) coordinate system, where X is the major radius axis for phi = 0, Y is the major radius axis for phi = pi/2, and Z is the height axis. The X1 vector is more horizontal than X2 (has a smaller abs(Z) component) and oriented in the positive phi direction (counter-clockwise when viewing from above).
    :ivar x2_unit_vector : Components of the X2 direction unit vector in the (X,Y,Z) coordinate system, where X is the major radius axis for phi = 0, Y is the major radius axis for phi = pi/2, and Z is the height axis. The X2 axis is orthonormal so that uX2 = uX3 x uX1.
    :ivar x3_unit_vector : Components of the X3 direction unit vector in the (X,Y,Z) coordinate system, where X is the major radius axis for phi = 0, Y is the major radius axis for phi = pi/2, and Z is the height axis. The X3 axis is normal to the object surface and oriented towards the plasma.
    :ivar x1_width : Full width of the object in the X1 direction, used only if geometry_type/index = 3
    :ivar x2_width : Full width of the object in the X2 direction, used only if geometry_type/index = 3
    :ivar outline : Irregular outline of the object in the (X1, X2) coordinate system, used only if geometry_type/index=1. Repeat the first point since this is a closed contour
    :ivar x1_curvature : Radius of curvature in the X1 direction, to be filled only for curvature_type/index = 2, 4 or 5
    :ivar x2_curvature : Radius of curvature in the X2 direction, to be filled only for curvature_type/index = 3 or 5
    :ivar surface : Surface of the object, derived from the above geometric data
    """

    class Meta:
        name = "curved_object"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    description: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    geometry_type: Optional[IdentifierStatic] = field(
        default=None,
        metadata={
            "imas_type": "identifier_static",
            "field_type": IdentifierStatic,
        },
    )
    curvature_type: Optional[IdentifierStatic] = field(
        default=None,
        metadata={
            "imas_type": "identifier_static",
            "field_type": IdentifierStatic,
        },
    )
    material: Optional[IdentifierStatic] = field(
        default=None,
        metadata={
            "imas_type": "identifier_static",
            "field_type": IdentifierStatic,
        },
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
    x1_curvature: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    x2_curvature: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    surface: Optional[float] = field(
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
class CameraGeometry(IdsBaseClass):
    """

    :ivar pixel_dimensions : Pixel dimension in each direction (x1, x2)
    :ivar pixels_n : Number of pixels in each direction (x1, x2)
    :ivar pixel_position : Position of the centre of each pixel. First dimension : line index (x1 axis). Second dimension: column index (x2 axis).
    :ivar camera_dimensions : Total camera dimension in each direction (x1, x2)
    :ivar centre : Position of the camera centre
    :ivar x1_unit_vector : Components of the X1 direction unit vector in the (X,Y,Z) coordinate system, where X is the major radius axis for phi = 0, Y is the major radius axis for phi = pi/2, and Z is the height axis. The X1 vector is more horizontal than X2 (has a smaller abs(Z) component) and oriented in the positive phi direction (counter-clockwise when viewing from above).
    :ivar x2_unit_vector : Components of the X2 direction unit vector in the (X,Y,Z) coordinate system, where X is the major radius axis for phi = 0, Y is the major radius axis for phi = pi/2, and Z is the height axis. The X2 axis is orthonormal so that uX2 = uX3 x uX1.
    :ivar x3_unit_vector : Components of the X3 direction unit vector in the (X,Y,Z) coordinate system, where X is the major radius axis for phi = 0, Y is the major radius axis for phi = pi/2, and Z is the height axis. The X3 axis is normal to the camera plane and oriented towards the plasma.
    :ivar line_of_sight : Description of the line of sight for each pixel, given by 2 points. For each coordinate : first dimension : line index (x1 axis); second dimension: column index (x2 axis).
    """

    class Meta:
        name = "camera_geometry"
        is_root_ids = False

    pixel_dimensions: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...2"},
            "field_type": np.ndarray,
        },
    )
    pixels_n: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=int),
        metadata={
            "imas_type": "INT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...2"},
            "field_type": np.ndarray,
        },
    )
    pixel_position: Optional[Rphiz2DStatic] = field(
        default=None,
        metadata={"imas_type": "rphiz2d_static", "field_type": Rphiz2DStatic},
    )
    camera_dimensions: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...2"},
            "field_type": np.ndarray,
        },
    )
    centre: Optional[Rphiz0DStatic] = field(
        default=None,
        metadata={"imas_type": "rphiz0d_static", "field_type": Rphiz0DStatic},
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
    line_of_sight: Optional[LineOfSight2PointsRphiz2D] = field(
        default=None,
        metadata={
            "imas_type": "line_of_sight_2points_rphiz_2d",
            "field_type": LineOfSight2PointsRphiz2D,
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
class SpectrometerXRayCrystalFlt2DTime1(IdsBaseClass):
    """

    :ivar data : Data
    :ivar validity_timed : Indicator of the validity of the data for each time slice. 0: valid from automated processing, 1: valid and certified by the diagnostic RO; - 1 means problem identified in the data processing (request verification by the diagnostic RO), -2: invalid data, should not be used (values lower than -2 have a code-specific meaning detailing the origin of their invalidity)
    :ivar validity : Indicator of the validity of the data for the whole acquisition period. 0: valid from automated processing, 1: valid and certified by the diagnostic RO; - 1 means problem identified in the data processing (request verification by the diagnostic RO), -2: invalid data, should not be used (values lower than -2 have a code-specific meaning detailing the origin of their invalidity)
    """

    class Meta:
        name = "spectrometer_x_ray_crystal_flt_2d_time_1"
        is_root_ids = False

    data: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "as_parent",
                "coordinate2": "../../time",
            },
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
class SpectrometerXRayCrystalInstrumentFuncBin(IdsBaseClass):
    """

    :ivar wavelengths : Array of wavelengths on which the instrument function is defined
    :ivar values : Explicit instrument function values for the detector. When multiplied by the line-integrated emission spectrum in photons/second/sr/m/m^2 received on a binned pixel of the detector, gives the detector pixel output in counts/seconds.
    :ivar type : Instrument function type
    :ivar intensity : Scaling factor for the instrument function such that convolving the instrument function with an emission spectrum gives the counts per second on the detector
    :ivar centre : Centre (in terms of absolute wavelength) of instrument function
    :ivar sigma : Standard deviation of Gaussian instrument function
    :ivar scale : Scale of Lorentzian instrument function (full width at half height)
    """

    class Meta:
        name = "spectrometer_x_ray_crystal_instrument_func_bin"
        is_root_ids = False

    wavelengths: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    values: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate1_same_as": "../../../wavelength_frames",
                "coordinate2": "../wavelengths",
            },
            "field_type": np.ndarray,
        },
    )
    type: Optional[IdentifierStatic] = field(
        default=None,
        metadata={
            "imas_type": "identifier_static",
            "field_type": IdentifierStatic,
        },
    )
    intensity: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../wavelengths"},
            "field_type": np.ndarray,
        },
    )
    centre: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../wavelengths"},
            "field_type": np.ndarray,
        },
    )
    sigma: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../wavelengths"},
            "field_type": np.ndarray,
        },
    )
    scale: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../wavelengths"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SpectrometerXRayCrystalInstrumentFunction(IdsBaseClass):
    """

    :ivar wavelengths : Array of wavelengths on which the instrument function is defined
    :ivar values : Explicit instrument function values for the detector. When multiplied by the line-integrated emission spectrum in photons/second/sr/m/m^2 received on a pixel of the detector, gives the detector pixel output in counts/seconds.
    :ivar type : Instrument function type
    :ivar intensity : Scaling factor for the instrument function such that convolving the instrument function with an emission spectrum gives the counts per second on the detector
    :ivar centre : Centre (in terms of absolute wavelength) of instrument function
    :ivar sigma : Standard deviation of Gaussian instrument function
    :ivar scale : Scale of Lorentzian instrument function (full width at half height)
    """

    class Meta:
        name = "spectrometer_x_ray_crystal_instrument_function"
        is_root_ids = False

    wavelengths: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    values: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 4, dtype=float),
        metadata={
            "imas_type": "FLT_3D",
            "ndims": 4,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate1_same_as": "../../wavelength_frames",
                "coordinate2": "../../z_frames",
                "coordinate3": "../wavelengths",
            },
            "field_type": np.ndarray,
        },
    )
    type: Optional[IdentifierStatic] = field(
        default=None,
        metadata={
            "imas_type": "identifier_static",
            "field_type": IdentifierStatic,
        },
    )
    intensity: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../z_frames",
                "coordinate2": "../wavelengths",
            },
            "field_type": np.ndarray,
        },
    )
    centre: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../z_frames",
                "coordinate2": "../wavelengths",
            },
            "field_type": np.ndarray,
        },
    )
    sigma: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../z_frames",
                "coordinate2": "../wavelengths",
            },
            "field_type": np.ndarray,
        },
    )
    scale: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "../../z_frames",
                "coordinate2": "../wavelengths",
            },
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SpectrometerXRayCrystalCrystal(IdsBaseClass):
    """

    :ivar name : Short string identifier (unique for a given device)
    :ivar description : Description, e.g. “channel viewing the upper divertor”
    :ivar geometry_type : Geometry of the object contour. Note that there is some flexibility in the choice of the local coordinate system (X1,X2,X3). The data provider should choose the most convenient coordinate system for the object, respecting the definitions of (X1,X2,X3) indicated below.
    :ivar curvature_type : Curvature of the object.
    :ivar material : Material of the object
    :ivar centre : Coordinates of the origin of the local coordinate system (X1,X2,X3) describing the object. This origin is located within the object area and should be the middle point of the object surface. If geometry_type=2, it&#39;s the centre of the circular object. If geometry_type=3, it&#39;s the centre of the rectangular object.
    :ivar radius : Radius of the circle, used only if geometry_type/index = 2
    :ivar x1_unit_vector : Components of the X1 direction unit vector in the (X,Y,Z) coordinate system, where X is the major radius axis for phi = 0, Y is the major radius axis for phi = pi/2, and Z is the height axis. The X1 vector is more horizontal than X2 (has a smaller abs(Z) component) and oriented in the positive phi direction (counter-clockwise when viewing from above).
    :ivar x2_unit_vector : Components of the X2 direction unit vector in the (X,Y,Z) coordinate system, where X is the major radius axis for phi = 0, Y is the major radius axis for phi = pi/2, and Z is the height axis. The X2 axis is orthonormal so that uX2 = uX3 x uX1.
    :ivar x3_unit_vector : Components of the X3 direction unit vector in the (X,Y,Z) coordinate system, where X is the major radius axis for phi = 0, Y is the major radius axis for phi = pi/2, and Z is the height axis. The X3 axis is normal to the object surface and oriented towards the plasma.
    :ivar x1_width : Full width of the object in the X1 direction, used only if geometry_type/index = 3
    :ivar x2_width : Full width of the object in the X2 direction, used only if geometry_type/index = 3
    :ivar outline : Irregular outline of the object in the (X1, X2) coordinate system, used only if geometry_type/index=1. Repeat the first point since this is a closed contour
    :ivar x1_curvature : Radius of curvature in the X1 direction, to be filled only for curvature_type/index = 2, 4 or 5
    :ivar x2_curvature : Radius of curvature in the X2 direction, to be filled only for curvature_type/index = 3 or 5
    :ivar surface : Surface of the object, derived from the above geometric data
    :ivar wavelength_bragg : Bragg wavelength of the crystal
    :ivar angle_bragg : Bragg angle of the crystal
    :ivar thickness : Thickness of the crystal
    :ivar cut : Miller indices characterizing the cut of the crystal (can be of length 3 or 4)
    :ivar mesh_type : Crystal mesh type
    """

    class Meta:
        name = "spectrometer_x_ray_crystal_crystal"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    description: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    geometry_type: Optional[IdentifierStatic] = field(
        default=None,
        metadata={
            "imas_type": "identifier_static",
            "field_type": IdentifierStatic,
        },
    )
    curvature_type: Optional[IdentifierStatic] = field(
        default=None,
        metadata={
            "imas_type": "identifier_static",
            "field_type": IdentifierStatic,
        },
    )
    material: Optional[IdentifierStatic] = field(
        default=None,
        metadata={
            "imas_type": "identifier_static",
            "field_type": IdentifierStatic,
        },
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
    x1_curvature: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    x2_curvature: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    surface: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    wavelength_bragg: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    angle_bragg: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    thickness: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    cut: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=int),
        metadata={
            "imas_type": "INT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    mesh_type: Optional[IdentifierStatic] = field(
        default=None,
        metadata={
            "imas_type": "identifier_static",
            "field_type": IdentifierStatic,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class SpectrometerXRayCrystalBin(IdsBaseClass):
    """

    :ivar z_pixel_range : Vertical pixel index range indicating the corresponding binned detector area
    :ivar wavelength : Wavelength of incoming photons on each horizontal pixel of this bin.
    :ivar line_of_sight : Description of the line of sight from the crystal to the plasma for this bin, defined by two points
    :ivar instrument_function : Instrument function for this bin (replaces the ../../instrument function in case vertical binning is used), i.e. response of the detector to a monochromatic emission passing through the spectrometer. The resulting image on the detector will be a 2-D distribution of pixel values, for each wavelength. It can be given as explicit values for each detector pixel (values node) or as a parametric function of wavelength (described by the other nodes)
    """

    class Meta:
        name = "spectrometer_x_ray_crystal_bin"
        is_root_ids = False

    z_pixel_range: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=int),
        metadata={
            "imas_type": "INT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...2"},
            "field_type": np.ndarray,
        },
    )
    wavelength: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate1_same_as": "../../wavelength_frames",
            },
            "field_type": np.ndarray,
        },
    )
    line_of_sight: Optional[LineOfSight2Points] = field(
        default=None,
        metadata={
            "imas_type": "line_of_sight_2points",
            "field_type": LineOfSight2Points,
        },
    )
    instrument_function: Optional[SpectrometerXRayCrystalInstrumentFuncBin] = (
        field(
            default=None,
            metadata={
                "imas_type": "spectrometer_x_ray_crystal_instrument_func_bin",
                "field_type": SpectrometerXRayCrystalInstrumentFuncBin,
            },
        )
    )


@idspy_dataclass(repr=False, slots=True)
class SpectrometerXRayCrystalFrame(IdsBaseClass):
    """

    :ivar counts_n : Number of counts detected on each pixel of the frame during one exposure time
    :ivar counts_bin_n : Number of counts detected on each pixel/bin of the binned frame during one exposure time
    :ivar time : Time
    """

    class Meta:
        name = "spectrometer_x_ray_crystal_frame"
        is_root_ids = False

    counts_n: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate1_same_as": "../../wavelength_frames",
                "coordinate2": "../../z_frames",
            },
            "field_type": np.ndarray,
        },
    )
    counts_bin_n: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate1_same_as": "../../wavelength_frames",
                "coordinate2": "../../bin",
            },
            "field_type": np.ndarray,
        },
    )
    time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class SpectrometerXRayCrystalProxy(IdsBaseClass):
    """

    :ivar lines_of_sight_second_point : For each profile point, a line of sight is defined by a first point given by the centre of the crystal and a second point described here.
    :ivar lines_of_sight_rho_tor_norm : Shortest distance in rho_tor_norm between lines of sight and magnetic axis, signed with following convention : positive (resp. negative) means the point of shortest distance is above (resp. below) the magnetic axis
    :ivar t_i : Ion temperature (estimated from a spectral fit directly on the output line-integrated signal, without tomographic inversion)
    :ivar t_e : Electron temperature (estimated from a spectral fit directly on the output line-integrated signal, without tomographic inversion)
    :ivar velocity_tor : Toroidal velocity (estimated from a spectral fit directly on the output line-integrated signal, without tomographic inversion)
    :ivar time : Timebase for the dynamic nodes of this probe located at this level of the IDS structure
    """

    class Meta:
        name = "spectrometer_x_ray_crystal_proxy"
        is_root_ids = False

    lines_of_sight_second_point: Optional[Rphiz1DStatic] = field(
        default=None,
        metadata={"imas_type": "rphiz1d_static", "field_type": Rphiz1DStatic},
    )
    lines_of_sight_rho_tor_norm: Optional[SpectrometerXRayCrystalFlt2DTime1] = (
        field(
            default_factory=lambda: StructArray(
                type_input=SpectrometerXRayCrystalFlt2DTime1
            ),
            metadata={
                "imas_type": "spectrometer_x_ray_crystal_flt_2d_time_1",
                "ndims": 1,
                "coordinates": {
                    "coordinate1": "../lines_of_sight_second_point/r"
                },
                "field_type": SpectrometerXRayCrystalFlt2DTime1,
            },
        )
    )
    t_i: Optional[SpectrometerXRayCrystalFlt2DTime1] = field(
        default_factory=lambda: StructArray(
            type_input=SpectrometerXRayCrystalFlt2DTime1
        ),
        metadata={
            "imas_type": "spectrometer_x_ray_crystal_flt_2d_time_1",
            "ndims": 1,
            "coordinates": {"coordinate1": "../lines_of_sight_second_point/r"},
            "field_type": SpectrometerXRayCrystalFlt2DTime1,
        },
    )
    t_e: Optional[SpectrometerXRayCrystalFlt2DTime1] = field(
        default_factory=lambda: StructArray(
            type_input=SpectrometerXRayCrystalFlt2DTime1
        ),
        metadata={
            "imas_type": "spectrometer_x_ray_crystal_flt_2d_time_1",
            "ndims": 1,
            "coordinates": {"coordinate1": "../lines_of_sight_second_point/r"},
            "field_type": SpectrometerXRayCrystalFlt2DTime1,
        },
    )
    velocity_tor: Optional[SpectrometerXRayCrystalFlt2DTime1] = field(
        default_factory=lambda: StructArray(
            type_input=SpectrometerXRayCrystalFlt2DTime1
        ),
        metadata={
            "imas_type": "spectrometer_x_ray_crystal_flt_2d_time_1",
            "ndims": 1,
            "coordinates": {"coordinate1": "../lines_of_sight_second_point/r"},
            "field_type": SpectrometerXRayCrystalFlt2DTime1,
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
class SpectrometerXRayCrystalChannel(IdsBaseClass):
    """

    :ivar exposure_time : Exposure time of the measurement
    :ivar energy_bound_lower : Lower energy bound for the photon detection, for each pixel (horizontal, vertical)
    :ivar energy_bound_upper : Upper energy bound for the photon detection, for each pixel (horizontal, vertical)
    :ivar aperture : Collimating aperture
    :ivar reflector : Set of reflectors (optional) reflecting the light coming from the plasma towards the crystal. If empty, means that the plasma light directly arrives on the crystal.
    :ivar crystal : Characteristics of the crystal used
    :ivar filter_window : Set of filter windows
    :ivar camera : Characteristics of the camera used
    :ivar z_frames : Height of the observed zone at the focal plane in the plasma, corresponding to the vertical dimension of the frame
    :ivar wavelength_frames : Wavelength of incoming photons on each pixel of the frames, mainly varying accross the horizontal dimension of the frame. However a 2D map of the wavelength is given since it is not constant vertically due to the elliptical curvature of the photon iso-surfaces
    :ivar bin : Set of bins (binning in the vertical dimension) defined to increase the signal to noise ratio of the spectra
    :ivar frame : Set of frames
    :ivar energies : Array of energy values for tabulation of the detection efficiency
    :ivar detection_efficiency : Probability of detection of a photon impacting the detector as a function of its energy
    :ivar profiles_line_integrated : Profiles proxies are given in the vertical direction of the detector. They are estimated directly from the camera, without tomographic inversion. Binning is allowed so the number of profile points may be lower than the length of z_frames. Physical quantities deduced from the measured spectra are given for each profile point. They correspond to the spectra integrated along lines of sight, defined by a first point given by the centre of the crystal and a second point (depending on the profile point) described below.
    :ivar instrument_function : Instrument function (to be used in case vertical binning is not used), i.e. response of the detector to a monochromatic emission passing through the spectrometer. The resulting image on the detector will be a 2-D distribution of pixel values, for each wavelength. It can be given as explicit values for each detector pixel (values node) or as a parametric function of wavelength (described by the other nodes)
    """

    class Meta:
        name = "spectrometer_x_ray_crystal_channel"
        is_root_ids = False

    exposure_time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    energy_bound_lower: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate1_same_as": "../wavelength_frames",
                "coordinate2": "../z_frames",
            },
            "field_type": np.ndarray,
        },
    )
    energy_bound_upper: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 3, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 3,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate1_same_as": "../wavelength_frames",
                "coordinate2": "../z_frames",
            },
            "field_type": np.ndarray,
        },
    )
    aperture: Optional[DetectorAperture] = field(
        default=None,
        metadata={
            "imas_type": "detector_aperture",
            "field_type": DetectorAperture,
        },
    )
    reflector: Optional[CurvedObject] = field(
        default_factory=lambda: StructArray(type_input=CurvedObject),
        metadata={
            "imas_type": "curved_object",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": CurvedObject,
        },
    )
    crystal: Optional[SpectrometerXRayCrystalCrystal] = field(
        default=None,
        metadata={
            "imas_type": "spectrometer_x_ray_crystal_crystal",
            "field_type": SpectrometerXRayCrystalCrystal,
        },
    )
    filter_window: Optional[FilterWindow] = field(
        default_factory=lambda: StructArray(type_input=FilterWindow),
        metadata={
            "imas_type": "filter_window",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": FilterWindow,
        },
    )
    camera: Optional[CameraGeometry] = field(
        default=None,
        metadata={"imas_type": "camera_geometry", "field_type": CameraGeometry},
    )
    z_frames: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    wavelength_frames: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "1...N",
                "coordinate2": "../z_frames",
            },
            "field_type": np.ndarray,
        },
    )
    bin: Optional[SpectrometerXRayCrystalBin] = field(
        default_factory=lambda: StructArray(
            type_input=SpectrometerXRayCrystalBin
        ),
        metadata={
            "imas_type": "spectrometer_x_ray_crystal_bin",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": SpectrometerXRayCrystalBin,
        },
    )
    frame: Optional[SpectrometerXRayCrystalFrame] = field(
        default_factory=lambda: StructArray(
            type_input=SpectrometerXRayCrystalFrame
        ),
        metadata={
            "imas_type": "spectrometer_x_ray_crystal_frame",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": SpectrometerXRayCrystalFrame,
        },
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
    profiles_line_integrated: Optional[SpectrometerXRayCrystalProxy] = field(
        default=None,
        metadata={
            "imas_type": "spectrometer_x_ray_crystal_proxy",
            "field_type": SpectrometerXRayCrystalProxy,
        },
    )
    instrument_function: Optional[SpectrometerXRayCrystalInstrumentFunction] = (
        field(
            default=None,
            metadata={
                "imas_type": "spectrometer_x_ray_crystal_instrument_function",
                "field_type": SpectrometerXRayCrystalInstrumentFunction,
            },
        )
    )


@idspy_dataclass(repr=False, slots=True)
class SpectrometerXRayCrystal(IdsBaseClass):
    """

    :ivar ids_properties :
    :ivar channel : Measurement channel, composed of a camera, a crystal, and (optional) a set of reflectors. The light coming from the plasma passes through the (optional) set of reflectors, then the crystal and arrives at the camera
    :ivar latency : Upper bound of the delay between physical information received by the detector and data available on the real-time (RT) network.
    :ivar code :
    :ivar time : Generic time
    """

    class Meta:
        name = "spectrometer_x_ray_crystal"
        is_root_ids = True

    ids_properties: Optional[IdsProperties] = field(
        default=None,
        metadata={"imas_type": "ids_properties", "field_type": IdsProperties},
    )
    channel: Optional[SpectrometerXRayCrystalChannel] = field(
        default_factory=lambda: StructArray(
            type_input=SpectrometerXRayCrystalChannel
        ),
        metadata={
            "imas_type": "spectrometer_x_ray_crystal_channel",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": SpectrometerXRayCrystalChannel,
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
