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
class WavesCpx1D(IdsBaseClass):
    """

    :ivar real : Real part
    :ivar imaginary : Imaginary part
    """

    class Meta:
        name = "waves_CPX_1D"
        is_root_ids = False

    real: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../length"},
            "field_type": np.ndarray,
        },
    )
    imaginary: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../../length"},
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
class SignalFlt1DValidityPosition(IdsBaseClass):
    """

    :ivar data : Data
    :ivar rho_tor_norm : Normalized toroidal flux coordinate of the measurement
    :ivar validity_timed : Indicator of the validity of the data for each time slice. 0: valid from automated processing, 1: valid and certified by the diagnostic RO; - 1 means problem identified in the data processing (request verification by the diagnostic RO), -2: invalid data, should not be used (values lower than -2 have a code-specific meaning detailing the origin of their invalidity)
    :ivar validity : Indicator of the validity of the data for the whole acquisition period. 0: valid from automated processing, 1: valid and certified by the diagnostic RO; - 1 means problem identified in the data processing (request verification by the diagnostic RO), -2: invalid data, should not be used (values lower than -2 have a code-specific meaning detailing the origin of their invalidity)
    :ivar time : Time
    """

    class Meta:
        name = "signal_flt_1d_validity_position"
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
    rho_tor_norm: Optional[np.ndarray] = field(
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
class PhysicalQuantityFlt1DTime1(IdsBaseClass):
    """

    :ivar data : Data
    :ivar validity_timed : Indicator of the validity of the data for each time slice. 0: valid from automated processing, 1: valid and certified by the diagnostic RO; - 1 means problem identified in the data processing (request verification by the diagnostic RO), -2: invalid data, should not be used (values lower than -2 have a code-specific meaning detailing the origin of their invalidity)
    :ivar validity : Indicator of the validity of the data for the whole acquisition period. 0: valid from automated processing, 1: valid and certified by the diagnostic RO; - 1 means problem identified in the data processing (request verification by the diagnostic RO), -2: invalid data, should not be used (values lower than -2 have a code-specific meaning detailing the origin of their invalidity)
    """

    class Meta:
        name = "physical_quantity_flt_1d_time_1"
        is_root_ids = False

    data: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time"},
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
class WavesBeamTracingBeamK(IdsBaseClass):
    """

    :ivar k_r : Wave vector component in the major radius direction
    :ivar k_z : Wave vector component in the vertical direction
    :ivar k_phi : Wave vector component in the toroidal direction
    :ivar k_r_norm : Normalized wave vector component in the major radius direction = k_r / norm(k)
    :ivar k_z_norm : Normalized wave vector component in the vertical direction = k_z / norm(k)
    :ivar k_phi_norm : Normalized wave vector component in the toroidal direction = k_phi / norm(k)
    :ivar n_parallel : Parallel refractive index
    :ivar n_perpendicular : Perpendicular refractive index
    :ivar n_phi : Toroidal wave number, contains a single value if varying_n_phi = 0 to avoid useless repetition of constant values. The wave vector toroidal component is defined as k_phi = n_phi grad phi where phi is the toroidal angle so that a positive n_phi means a wave propagating in the positive phi direction
    :ivar varying_n_phi : Flag telling whether n_phi is constant along the ray path (0) or varying (1)
    """

    class Meta:
        name = "waves_beam_tracing_beam_k"
        is_root_ids = False

    k_r: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../length"},
            "field_type": np.ndarray,
        },
    )
    k_z: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../length"},
            "field_type": np.ndarray,
        },
    )
    k_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../length"},
            "field_type": np.ndarray,
        },
    )
    k_r_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../length"},
            "field_type": np.ndarray,
        },
    )
    k_z_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../length"},
            "field_type": np.ndarray,
        },
    )
    k_phi_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../length"},
            "field_type": np.ndarray,
        },
    )
    n_parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../length"},
            "field_type": np.ndarray,
        },
    )
    n_perpendicular: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../length"},
            "field_type": np.ndarray,
        },
    )
    n_phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=int),
        metadata={
            "imas_type": "INT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../length OR 1...1"},
            "field_type": np.ndarray,
        },
    )
    varying_n_phi: Optional[int] = field(
        default=999999999, metadata={"imas_type": "INT_0D", "field_type": int}
    )


@idspy_dataclass(repr=False, slots=True)
class Rphizrhopsitheta1DDynamicAos1CommonTime1(IdsBaseClass):
    """

    :ivar r : Major radius
    :ivar phi : Toroidal angle  (oriented counter-clockwise when viewing from above)
    :ivar z : Height
    :ivar psi : Poloidal flux
    :ivar rho_tor_norm : Normalized toroidal flux coordinate
    :ivar theta : Poloidal angle (oriented clockwise when viewing the poloidal cross section on the right hand side of the tokamak axis of symmetry, with the origin placed on the plasma magnetic axis)
    """

    class Meta:
        name = "rphizrhopsitheta1d_dynamic_aos1_common_time_1"
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
    phi: Optional[np.ndarray] = field(
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
class Polarizer(IdsBaseClass):
    """

    :ivar centre : If geometry_type=2, coordinates of the centre of the circle. If geometry_type=1 or 3, coordinates of the origin of the local coordinate system (X1,X2,X3) describing the plane polarizer. This origin is located within the polarizer area. Note that there is some flexibility here and the data provider should choose the most convenient coordinate system for the object, respecting the definitions of (X1,X2,X3) indicated below.
    :ivar radius : Radius of the circle, used only if geometry_type = 2
    :ivar x1_unit_vector : Components of the X1 direction unit vector in the (X,Y,Z) coordinate system, where X is the major radius axis for phi = 0, Y is the major radius axis for phi = pi/2, and Z is the height axis. The X1 vector is more horizontal than X2 (has a smaller abs(Z) component) and oriented in the positive phi direction (counter-clockwise when viewing from above).
    :ivar x2_unit_vector : Components of the X2 direction unit vector in the (X,Y,Z) coordinate system, where X is the major radius axis for phi = 0, Y is the major radius axis for phi = pi/2, and Z is the height axis. The X2 axis is orthonormal so that uX2 = uX3 x uX1.
    :ivar x3_unit_vector : Components of the X3 direction unit vector in the (X,Y,Z) coordinate system, where X is the major radius axis for phi = 0, Y is the major radius axis for phi = pi/2, and Z is the height axis. The X3 axis is normal to the polarizer plane and oriented towards the plasma.
    :ivar polarization_angle : Alignment angle of the polarizer in the (x1,x2) plane. Electric fields parallel to the polarizer angle will be reflected. The angle is defined with respect to the x1 unit vector, positive in the counter-clockwise direction when looking towards the plasma
    """

    class Meta:
        name = "polarizer"
        is_root_ids = False

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
    polarization_angle: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class WavesBeamTracingElectrons(IdsBaseClass):
    """

    :ivar power : Power absorbed along the beam by the species
    """

    class Meta:
        name = "waves_beam_tracing_electrons"
        is_root_ids = False

    power: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../length"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WavesRphizpsitheta1DDynamicAos3(IdsBaseClass):
    """

    :ivar r : Major radius
    :ivar z : Height
    :ivar phi : Toroidal angle
    :ivar psi : Poloidal flux
    :ivar rho_tor_norm : Normalised toroidal flux coordinate
    :ivar theta : Poloidal angle (oriented clockwise when viewing the poloidal cross section on the right hand side of the tokamak axis of symmetry, with the origin placed on the plasma magnetic axis)
    """

    class Meta:
        name = "waves_rphizpsitheta1d_dynamic_aos3"
        is_root_ids = False

    r: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../length"},
            "field_type": np.ndarray,
        },
    )
    z: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../length"},
            "field_type": np.ndarray,
        },
    )
    phi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../length"},
            "field_type": np.ndarray,
        },
    )
    psi: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../length"},
            "field_type": np.ndarray,
        },
    )
    rho_tor_norm: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../length"},
            "field_type": np.ndarray,
        },
    )
    theta: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../length"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WavesBeamPhase(IdsBaseClass):
    """

    :ivar curvature : Inverse curvature radii for the phase ellipse, positive/negative for divergent/convergent beams, in the horizontal direction (first index of the first coordinate) and in the vertical direction (second index of the first coordinate)
    :ivar angle : Rotation angle for the phase ellipse
    """

    class Meta:
        name = "waves_beam_phase"
        is_root_ids = False

    curvature: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "1...2",
                "coordinate2": "../../length",
            },
            "field_type": np.ndarray,
        },
    )
    angle: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../length"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WavesBeamSpot(IdsBaseClass):
    """

    :ivar size : Size of the spot ellipse: distance between the central ray and the peripheral rays in the horizontal (first index of the first coordinate) and vertical direction (second index of the first coordinate)
    :ivar angle : Rotation angle for the spot ellipse
    """

    class Meta:
        name = "waves_beam_spot"
        is_root_ids = False

    size: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 2, dtype=float),
        metadata={
            "imas_type": "FLT_2D",
            "ndims": 2,
            "coordinates": {
                "coordinate1": "1...2",
                "coordinate2": "../../length",
            },
            "field_type": np.ndarray,
        },
    )
    angle: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../length"},
            "field_type": np.ndarray,
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
class WavesBeamTracingPowerFlow(IdsBaseClass):
    """

    :ivar perpendicular : Normalized power flow in the direction perpendicular to the magnetic field
    :ivar parallel : Normalized power flow in the direction parallel to the magnetic field
    """

    class Meta:
        name = "waves_beam_tracing_power_flow"
        is_root_ids = False

    perpendicular: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../length"},
            "field_type": np.ndarray,
        },
    )
    parallel: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../length"},
            "field_type": np.ndarray,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class WavesBeamTracingBeamEField(IdsBaseClass):
    """

    :ivar plus : Left hand polarised electric field component
    :ivar minus : Right hand polarised electric field component
    :ivar parallel : Parallel to magnetic field polarised electric field component
    """

    class Meta:
        name = "waves_beam_tracing_beam_e_field"
        is_root_ids = False

    plus: Optional[WavesCpx1D] = field(
        default=None,
        metadata={"imas_type": "waves_CPX_1D", "field_type": WavesCpx1D},
    )
    minus: Optional[WavesCpx1D] = field(
        default=None,
        metadata={"imas_type": "waves_CPX_1D", "field_type": WavesCpx1D},
    )
    parallel: Optional[WavesCpx1D] = field(
        default=None,
        metadata={"imas_type": "waves_CPX_1D", "field_type": WavesCpx1D},
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
class Int1DTime1AndTypeChange(IdsBaseClass):
    """

    :ivar data : Data
    :ivar validity_timed : Indicator of the validity of the data for each time slice. 0: valid from automated processing, 1: valid and certified by the diagnostic RO; - 1 means problem identified in the data processing (request verification by the diagnostic RO), -2: invalid data, should not be used (values lower than -2 have a code-specific meaning detailing the origin of their invalidity)
    :ivar validity : Indicator of the validity of the data for the whole acquisition period. 0: valid from automated processing, 1: valid and certified by the diagnostic RO; - 1 means problem identified in the data processing (request verification by the diagnostic RO), -2: invalid data, should not be used (values lower than -2 have a code-specific meaning detailing the origin of their invalidity)
    """

    class Meta:
        name = "int_1d_time_1_and_type_change"
        is_root_ids = False

    data: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=int),
        metadata={
            "imas_type": "INT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "../../time"},
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
class EceBeamTracingBeam(IdsBaseClass):
    """

    :ivar power_initial : Initial power in the ray/beam
    :ivar mode : X or O mode for this beam
    :ivar length : Ray/beam curvilinear length
    :ivar position : Position of the ray/beam along its path
    :ivar wave_vector : Wave vector of the ray/beam along its path
    :ivar e_field : Electric field polarization of the ray/beam along its path
    :ivar power_flow_norm : Normalised power flow
    :ivar electrons : Quantities related to the electrons
    :ivar spot : Spot ellipse characteristics
    :ivar phase : Phase ellipse characteristics
    """

    class Meta:
        name = "ece_beam_tracing_beam"
        is_root_ids = False

    power_initial: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    mode: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    length: Optional[np.ndarray] = field(
        default_factory=lambda: np.zeros(shape=(0,) * 1, dtype=float),
        metadata={
            "imas_type": "FLT_1D",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": np.ndarray,
        },
    )
    position: Optional[WavesRphizpsitheta1DDynamicAos3] = field(
        default=None,
        metadata={
            "imas_type": "waves_rphizpsitheta1d_dynamic_aos3",
            "field_type": WavesRphizpsitheta1DDynamicAos3,
        },
    )
    wave_vector: Optional[WavesBeamTracingBeamK] = field(
        default=None,
        metadata={
            "imas_type": "waves_beam_tracing_beam_k",
            "field_type": WavesBeamTracingBeamK,
        },
    )
    e_field: Optional[WavesBeamTracingBeamEField] = field(
        default=None,
        metadata={
            "imas_type": "waves_beam_tracing_beam_e_field",
            "field_type": WavesBeamTracingBeamEField,
        },
    )
    power_flow_norm: Optional[WavesBeamTracingPowerFlow] = field(
        default=None,
        metadata={
            "imas_type": "waves_beam_tracing_power_flow",
            "field_type": WavesBeamTracingPowerFlow,
        },
    )
    electrons: Optional[WavesBeamTracingElectrons] = field(
        default=None,
        metadata={
            "imas_type": "waves_beam_tracing_electrons",
            "field_type": WavesBeamTracingElectrons,
        },
    )
    spot: Optional[WavesBeamSpot] = field(
        default=None,
        metadata={"imas_type": "waves_beam_spot", "field_type": WavesBeamSpot},
    )
    phase: Optional[WavesBeamPhase] = field(
        default=None,
        metadata={
            "imas_type": "waves_beam_phase",
            "field_type": WavesBeamPhase,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class EceBeamTracing(IdsBaseClass):
    """

    :ivar beam : Set of rays/beams describing the wave propagation
    :ivar time : Time
    """

    class Meta:
        name = "ece_beam_tracing"
        is_root_ids = False

    beam: Optional[EceBeamTracingBeam] = field(
        default_factory=lambda: StructArray(type_input=EceBeamTracingBeam),
        metadata={
            "imas_type": "ece_beam_tracing_beam",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": EceBeamTracingBeam,
        },
    )
    time: Optional[float] = field(
        default=9e40, metadata={"imas_type": "flt_type", "field_type": float}
    )


@idspy_dataclass(repr=False, slots=True)
class EceChannelBeamSpot(IdsBaseClass):
    """

    :ivar size : Size of the spot ellipse
    :ivar angle : Rotation angle for the spot ellipse
    """

    class Meta:
        name = "ece_channel_beam_spot"
        is_root_ids = False

    size: Optional[SignalFlt2D] = field(
        default_factory=lambda: StructArray(type_input=SignalFlt2D),
        metadata={
            "imas_type": "signal_flt_2d",
            "ndims": 2,
            "coordinates": {"coordinate1": "1...2", "coordinate2": "time"},
            "field_type": SignalFlt2D,
        },
    )
    angle: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )


@idspy_dataclass(repr=False, slots=True)
class EceChannelBeamPhase(IdsBaseClass):
    """

    :ivar curvature : Inverse curvature radii for the phase ellipse, positive/negative for divergent/convergent beams
    :ivar angle : Rotation angle for the phase ellipse
    """

    class Meta:
        name = "ece_channel_beam_phase"
        is_root_ids = False

    curvature: Optional[SignalFlt2D] = field(
        default_factory=lambda: StructArray(type_input=SignalFlt2D),
        metadata={
            "imas_type": "signal_flt_2d",
            "ndims": 2,
            "coordinates": {"coordinate1": "1...2", "coordinate2": "time"},
            "field_type": SignalFlt2D,
        },
    )
    angle: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )


@idspy_dataclass(repr=False, slots=True)
class EceChannelBeam(IdsBaseClass):
    """

    :ivar spot : Spot ellipse characteristics
    :ivar phase : Phase ellipse characteristics
    """

    class Meta:
        name = "ece_channel_beam"
        is_root_ids = False

    spot: Optional[EceChannelBeamSpot] = field(
        default=None,
        metadata={
            "imas_type": "ece_channel_beam_spot",
            "field_type": EceChannelBeamSpot,
        },
    )
    phase: Optional[EceChannelBeamPhase] = field(
        default=None,
        metadata={
            "imas_type": "ece_channel_beam_phase",
            "field_type": EceChannelBeamPhase,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class EceChannel(IdsBaseClass):
    """

    :ivar name : Short string identifier (unique for a given device)
    :ivar description : Description, e.g. “channel viewing the upper divertor”
    :ivar frequency : Frequency of the channel
    :ivar harmonic : Harmonic detected by the channel. 1 corresponds to the &#34;O1&#34; mode, while 2 corresponds to the &#34;X2&#34; mode.
    :ivar line_of_sight : Line of sight of this channel, defined by two points. By convention, the first point is the closest to the diagnostic. Fill only in case the channels have different lines of sight
    :ivar if_bandwidth : Full-width of the Intermediate Frequency (IF) bandpass filter
    :ivar position : Position of the measurements (taking into account the suprathermal shift)
    :ivar delta_position_suprathermal : Simple estimate of the difference in position induced by the presence of suprathermal electrons. Position without corrections = position - delta_position_suprathermal
    :ivar t_radiation : Radiation temperature
    :ivar t_radiation_x : Predicted radiation temperature of the e(X)traordinary mode
    :ivar t_radiation_o : Predicted radiation temperature of the Ordinary mode
    :ivar voltage_t_radiation : Raw voltage measured on each channel, from which the calibrated temperature data is then derived
    :ivar optical_depth : Optical depth of the plasma at the position of the measurement. This parameter is a proxy for the local / non-local character of the ECE emission. It must be greater than 1 to guarantee that the measurement is dominated by local ECE emission (non-local otherwise)
    :ivar time : Timebase for the processed dynamic data of this channel (outside of the beam and calibration_offset structures)
    :ivar calibration_factor : Calibration factor, used as t_radiation = calibration_factor * (voltage_t_radiation - calibration_offset)
    :ivar calibration_offset : Calibration offset, may be re-evaluated dynamically during long pulses on some experiments
    :ivar beam : ECE Gaussian optics parameters taken at the line_of_sight/first_point position (for synthetic modelling of the ECE emission)
    :ivar beam_tracing : Beam tracing calculations, for various time slices
    """

    class Meta:
        name = "ece_channel"
        is_root_ids = False

    name: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    description: Optional[str] = field(
        default="", metadata={"imas_type": "STR_0D", "field_type": str}
    )
    frequency: Optional[PhysicalQuantityFlt1DTime1] = field(
        default=None,
        metadata={
            "imas_type": "physical_quantity_flt_1d_time_1",
            "field_type": PhysicalQuantityFlt1DTime1,
        },
    )
    harmonic: Optional[Int1DTime1AndTypeChange] = field(
        default=None,
        metadata={
            "imas_type": "int_1d_time_1_and_type_change",
            "field_type": Int1DTime1AndTypeChange,
        },
    )
    line_of_sight: Optional[LineOfSight2Points] = field(
        default=None,
        metadata={
            "imas_type": "line_of_sight_2points",
            "field_type": LineOfSight2Points,
        },
    )
    if_bandwidth: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    position: Optional[Rphizrhopsitheta1DDynamicAos1CommonTime1] = field(
        default=None,
        metadata={
            "imas_type": "rphizrhopsitheta1d_dynamic_aos1_common_time_1",
            "field_type": Rphizrhopsitheta1DDynamicAos1CommonTime1,
        },
    )
    delta_position_suprathermal: Optional[
        Rphizrhopsitheta1DDynamicAos1CommonTime1
    ] = field(
        default=None,
        metadata={
            "imas_type": "rphizrhopsitheta1d_dynamic_aos1_common_time_1",
            "field_type": Rphizrhopsitheta1DDynamicAos1CommonTime1,
        },
    )
    t_radiation: Optional[PhysicalQuantityFlt1DTime1] = field(
        default=None,
        metadata={
            "imas_type": "physical_quantity_flt_1d_time_1",
            "field_type": PhysicalQuantityFlt1DTime1,
        },
    )
    t_radiation_x: Optional[PhysicalQuantityFlt1DTime1] = field(
        default=None,
        metadata={
            "imas_type": "physical_quantity_flt_1d_time_1",
            "field_type": PhysicalQuantityFlt1DTime1,
        },
    )
    t_radiation_o: Optional[PhysicalQuantityFlt1DTime1] = field(
        default=None,
        metadata={
            "imas_type": "physical_quantity_flt_1d_time_1",
            "field_type": PhysicalQuantityFlt1DTime1,
        },
    )
    voltage_t_radiation: Optional[SignalFlt1DValidity] = field(
        default=None,
        metadata={
            "imas_type": "signal_flt_1d_validity",
            "field_type": SignalFlt1DValidity,
        },
    )
    optical_depth: Optional[PhysicalQuantityFlt1DTime1] = field(
        default=None,
        metadata={
            "imas_type": "physical_quantity_flt_1d_time_1",
            "field_type": PhysicalQuantityFlt1DTime1,
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
    calibration_factor: Optional[float] = field(
        default=9e40, metadata={"imas_type": "FLT_0D", "field_type": float}
    )
    calibration_offset: Optional[SignalFlt1D] = field(
        default=None,
        metadata={"imas_type": "signal_flt_1d", "field_type": SignalFlt1D},
    )
    beam: Optional[EceChannelBeam] = field(
        default=None,
        metadata={
            "imas_type": "ece_channel_beam",
            "field_type": EceChannelBeam,
        },
    )
    beam_tracing: Optional[EceBeamTracing] = field(
        default_factory=lambda: StructArray(type_input=EceBeamTracing),
        metadata={
            "imas_type": "ece_beam_tracing",
            "ndims": 1,
            "coordinates": {"coordinate1": "time"},
            "field_type": EceBeamTracing,
        },
    )


@idspy_dataclass(repr=False, slots=True)
class Ece(IdsBaseClass):
    """

    :ivar ids_properties :
    :ivar line_of_sight : Line of sight of the diagnostic (fill when valid for all channels), defined by two points. By convention, the first point is the closest to the diagnostic. In case the channels have different lines of sight, they should be described within the channel array of structures
    :ivar t_radiation_central : Radiation temperature from the closest channel to the magnetic axis, together with its radial location
    :ivar t_radiation_central_x : Predicted radiation temperature of the channel closest to the magnetic axis, together with its radial location (eXtraordinary mode)
    :ivar t_radiation_central_o : Predicted radiation temperature of the channel closest to the magnetic axis, together with its radial location (Ordinary mode)
    :ivar channel : Set of channels (frequency)
    :ivar polarizer : Set of polarizers placed in front of the diagnostic (if any). Polarizers are assumed to be orthogonal to the line of sight, so that the x3 unit vector is aligned with the line of sight
    :ivar psi_normalization : Quantities to use to normalize psi, as a function of time
    :ivar latency : Upper bound of the delay between physical information received by the detector and data available on the real-time (RT) network.
    :ivar code :
    :ivar time : Generic time
    """

    class Meta:
        name = "ece"
        is_root_ids = True

    ids_properties: Optional[IdsProperties] = field(
        default=None,
        metadata={"imas_type": "ids_properties", "field_type": IdsProperties},
    )
    line_of_sight: Optional[LineOfSight2Points] = field(
        default=None,
        metadata={
            "imas_type": "line_of_sight_2points",
            "field_type": LineOfSight2Points,
        },
    )
    t_radiation_central: Optional[SignalFlt1DValidityPosition] = field(
        default=None,
        metadata={
            "imas_type": "signal_flt_1d_validity_position",
            "field_type": SignalFlt1DValidityPosition,
        },
    )
    t_radiation_central_x: Optional[SignalFlt1DValidityPosition] = field(
        default=None,
        metadata={
            "imas_type": "signal_flt_1d_validity_position",
            "field_type": SignalFlt1DValidityPosition,
        },
    )
    t_radiation_central_o: Optional[SignalFlt1DValidityPosition] = field(
        default=None,
        metadata={
            "imas_type": "signal_flt_1d_validity_position",
            "field_type": SignalFlt1DValidityPosition,
        },
    )
    channel: Optional[EceChannel] = field(
        default_factory=lambda: StructArray(type_input=EceChannel),
        metadata={
            "imas_type": "ece_channel",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": EceChannel,
        },
    )
    polarizer: Optional[Polarizer] = field(
        default_factory=lambda: StructArray(type_input=Polarizer),
        metadata={
            "imas_type": "polarizer",
            "ndims": 1,
            "coordinates": {"coordinate1": "1...N"},
            "field_type": Polarizer,
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
