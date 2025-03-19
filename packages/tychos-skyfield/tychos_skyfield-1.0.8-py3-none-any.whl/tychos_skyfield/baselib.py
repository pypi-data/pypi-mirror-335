"""
Tychosium model implementation in Python.
Uses updated Tychosium code as reference.
"""
from scipy.spatial.transform import Rotation as R
import numpy as np


class OrbitCenter:
    """
    Data class to keep orbit center coordinates
    """

    def __init__(self, orbit_center_a=0.0, orbit_center_b=0.0, orbit_center_c=0.0):
        self.x = orbit_center_a
        self.y = orbit_center_c
        self.z = orbit_center_b


class OrbitTilt:
    """
    Data class to keep orbit tilt values
    """

    def __init__(self, orbit_tilt_a=0.0, orbit_tilt_b=0.0):
        self.x = orbit_tilt_a
        self.z = orbit_tilt_b


class PlanetObj:
    """
    Class for planet object definition. It initializes the starting objects parameters
    and allows to calculate rotations, locations and RA/DEC

    Attributes
    ----------
        orbit_radius
        orbit_center
        orbit_tilt
        start_pos
        speed
        children
        rotation
        location
        center
        radius_vec

    Methods
    -------
        move_planet_tt
        move_planet
        move_planet_basic
        add_child
        radec_direct
        location_transformed

    Notes
    -----
    move_planet() method needs to be called for parent first and only then for child.
    speed = 1/period(years) * 2pi, represents rotation of radians per year
    """

    def __init__(self, orbit_radius=100.0, orbit_center=OrbitCenter(),
                 orbit_tilt=OrbitTilt(), start_pos=20.0, speed=0.0):

        self.orbit_radius = orbit_radius
        self.orbit_center = orbit_center
        self.orbit_tilt = orbit_tilt
        self.start_pos = start_pos
        self.speed = speed / (2 * np.pi)
        self.children = []

        self.rotation = None
        self.location = None
        self.center = None
        self.radius_vec = None
        self.initialize_orbit_parameters()

    def initialize_orbit_parameters(self):
        """
        It initializes the object rotation, location, center position, and radius vector
        :return: none
        """

        self.rotation = (R.from_euler('x', self.orbit_tilt.x, degrees=True) *
                         R.from_euler('z', self.orbit_tilt.z, degrees=True))
        self.location = np.array([0.0, 0.0, 0.0])
        self.center = (np.array([self.orbit_center.x, self.orbit_center.y, self.orbit_center.z]).
                       astype(np.float64))
        self.radius_vec = np.array([self.orbit_radius, 0.0, 0.0])

    def move_planet_tt(self, time_julian):
        """
        Moves planet to specified Julian time.
        NOTE: only can use function once, as every usage modifies children values.
        :param time_julian: float
            Julian time to which to move the planet
        :return: none
        """

        pos = (time_julian - 2451717.0) / 365.2425 * 360
        # 2451717 is reference Julian Date tt for date 2000-6-21 12:00:00
        self.move_planet(pos)

    def move_planet(self, pos):
        """
        Moves planet by specified degrees around y-axis.
        NOTE: only can use function once, as everytime it modifies children values.
        :param pos: float
            Position in degrees to rotate around y-axis
        :return: none
        """

        self.move_planet_basic(self.speed * pos - self.start_pos)
        for child in self.children:
            child.rotation = self.rotation * child.rotation
            child.center = self.center + self.rotation.apply(self.radius_vec + child.center)

    def move_planet_basic(self, pos, directions='y'):
        """
        Moves planet by specified pos, assuming self.speed = 0 and self.start_pos = 0.
        Can call this function multiple times - it does not modify children.
        :param pos: float or List[float]
            Position(s) in degrees to rotate around 'directions'
        :param directions: [optional] string
            The direction or multiple directions with respect which to move
        :return: none
        """

        self.rotation = self.rotation * R.from_euler(directions, pos, degrees=True)
        radius_rotated = self.rotation.apply(self.radius_vec)
        self.location = self.center + radius_rotated

    def add_child(self, child_obj):
        """
        Add child to the planet.
        NOTE: Order of move_planet() matters for the children, need to move parent first.
        :param child_obj: PlanetObj
            Child object to be added.
        :return: none
        """

        self.children += [child_obj]

    def radec_direct(self, ref_obj, polar_obj=None, epoch='j2000', formatted=True):
        """
        Calculate RA and DEC for the current location of the planet. It uses projects planet
        location to the appropriate ref frame for the epoch
        :param ref_obj: PlanetObj
            reference object with respect to which calculate RA and DEC, typically earth
        :param polar_obj: Optional[PlanetObj] = None
            reference object that contains transformation for polar axis frame which
            is used to calculate RA, DEC.
            Only required for the epoch = 'date'
        :param epoch: Optional[String]: 'j2000'(default), 'j2000June' or 'date'
            epoch specifies which 'time' is used for ra/dec calculation. 'j2000' corresponds
            to J2000 (and roughly to ICRF), 'j2000June' corresponds to the 2000/06/21 12:00:00 date
             and 'date' is frame associated with current time
        :param formatted: Optional[Boolean] = True
            If True, return formatted ra/dec using hours and degrees.
            If False, return ra/dec in radians.
        :return: tuple[String, String, Float] - (ra, dec, dist)
            ra is calculated in hours
            dec is calculated in degrees
            dist is the distance to the planet from the ref_obj in AU
        NOTE: 'j2000' epoch rotation is obtained by manually getting rotation quaternion of
        polar axis for the date 2000/01/01 12:00
        """

        if epoch == 'j2000':
            rot = R.from_quat([-0.1420654722633656, 0.6927306657799285, -0.14519055921306223,
                               0.6919980692126839])
        elif epoch == 'j2000June':
            rot = R.from_euler('zxy', [-23.439062, 0.26, 90], degrees=True)
        elif epoch == 'date':
            rot = polar_obj.rotation
        else:
            raise AttributeError("Unknown epoch provided: " + epoch +
                            ". Only epochs 'j2000', 'j2000June' and 'date' are supported." )

        unit_prime = rot.apply(np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]))
        loc_prime = np.dot(unit_prime, self.location - ref_obj.location)
        dist = np.linalg.norm(loc_prime) / 100
        dec = np.pi / 2 - np.arccos(loc_prime[1] / np.sqrt(np.dot(loc_prime, loc_prime)))
        ra = (np.sign(loc_prime[0]) *
              np.arccos(loc_prime[2] / np.sqrt(loc_prime[0] ** 2 + loc_prime[2] ** 2)))
        if ra < 0:
            ra += 2 * np.pi
        if not formatted:
            return ra, dec, dist

        dec_sgn = np.sign(dec)
        dec *= dec_sgn * 180 / np.pi
        dec_str = ("{:+.0f}deg {:02.0f}\' {:02.1f}\""
                   .format(dec_sgn * np.floor(dec), np.floor(dec % np.floor(dec) * 60),
                           np.remainder(dec % np.floor(dec) * 60, 1) * 60))
        ra *= 12 / np.pi
        ra_str = "{:.0f}h {:02.0f}m {:02.2f}s".format(
            np.floor(ra), np.floor(np.remainder(ra, 1) * 60),
            np.remainder(np.remainder(ra, 1) * 60, 1) * 60)
        return ra_str, dec_str, dist

    def location_transformed(self, ref_obj, polar_obj, epoch='j2000'):
        """
        Transform object location to be w.r.t. the ref_obj location and rotate coordinate axis
        to align with either (mostly) with ICRF frame or the frame as defined by polar_obj rotation
        corresponding to the epoch of current time
        :param ref_obj: PlanetObj
            reference object with respect to which calculate new location vector, typically earth
        :param polar_obj: PlanetObj
            reference object that contains transformation for polar axis frame that is used in
            Tychos for the RA/DEC calculation.
            Only required for the epoch = 'date'
        :param epoch: Optional[String]: 'j2000'(default), 'j2000June' or 'date'
            epoch specifies which 'time' is used for reference frame rotation. 'j2000' corresponds
            to J2000 (and roughly to the ICRF frame), while 'date' is frame associated with
            current time polar axis direction
        :return: ndarry[float, float, float]
            Location vector in the new rotated reference frame
        NOTE: 'j2000' epoch rotation is obtained by manually getting rotation quaternion of
        polar axis for the date 2000/01/01 12:00
        """

        if epoch == 'j2000':
            r1 = R.from_quat([-0.1420654722633656, 0.6927306657799285, -0.14519055921306223,
                              0.6919980692126839]).inv()
            r2 = R.from_euler('zy', [90, 90], degrees=True)
        elif epoch == 'j2000June':
            r1 = R.from_euler('ZXY', [-23.439062, 0.26, 90], degrees=True)
            r2 = R.from_euler('yx', [-90, 90], degrees=True)
        elif epoch == 'date':
            r1 = polar_obj.rotation.inv()
            r2 = R.from_euler('zy', [90, 90], degrees=True)
        else:
            raise AttributeError("Unknown epoch provided: " + epoch +
                            ". Only epochs 'j2000', 'j2000June' and 'date' are supported." )

        loc = np.transpose((r2 * r1).apply(self.location - ref_obj.location)) / 100
        return loc


class TychosSystem:
    """
    Class specifying dynamic Tychos planet system

    Attributes
    ----------
    julian_day

    Methods
    -------
    move_system
    get_all_objects
    get_observable_objects

    """

    _all_objects = ['earth', 'polar_axis', 'sun_def', 'sun',
            'mercury_def_a', 'mercury_def_b', 'mercury',
            'moon_def_a', 'moon_def_b', 'moon', 'venus_def_a', 'venus_def_b', 'venus',
            'mars_def_e', 'mars_def_s', 'mars', 'phobos', 'deimos', 'jupiter_def', 'jupiter',
            'saturn_def', 'saturn', 'uranus_def', 'uranus', 'neptune_def', 'neptune',
            'halleys_def', 'halleys', 'eros_def_a', 'eros_def_b', 'eros']
    _observable_objects = ['sun', 'mercury', 'moon', 'venus', 'mars', 'phobos', 'deimos',
            'jupiter', 'saturn', 'uranus', 'neptune', 'halleys', 'eros']

    def __init__(self, julian_day = 2451717.0):
        self.julian_day = julian_day
        self._objs = {}
        self._initialize_objects()
        self._set_dependencies()
        self.move_system(julian_day)

    def __getitem__(self, item):
        item = item.lower()
        try:
            obj = self._objs[item]
            return obj
        except Exception as e:
            raise AttributeError(
                "Unknown object {0}, possible objects: {1}"
                .format(item, self.get_all_objects())) from e

    def _initialize_objects(self):
        """
        Defines initial parameters for each planet
        :return: none
        """

        self._objs["earth"] = PlanetObj(37.8453, OrbitCenter(0, 0, 0),
                                        OrbitTilt(0, 0), 0, -0.0002479160869310127)
        self._objs["polar_axis"] = PlanetObj(0, OrbitCenter(0, 0, 0),
                                             OrbitTilt(0, 0), 0, 0.0)

        self._objs["sun_def"] = PlanetObj(0.0, OrbitCenter(1.4, -0.6, 0.0),
                                          OrbitTilt(0.1, 0.0), 0.0, 0.0)
        self._objs["sun"] = PlanetObj(100.0, OrbitCenter(1.2, -0.1, 0.0),
                                      OrbitTilt(0.1, 0.0), 0.0, 2 * np.pi)

        self._objs["mercury_def_a"] = PlanetObj(100, OrbitCenter(-6.9, -3.2, 0),
                                                OrbitTilt(0, 0), 0, 2 * np.pi)
        self._objs["mercury_def_b"] = PlanetObj(0, OrbitCenter(0, 0, 0),
                                                OrbitTilt(-1.3, 0.5), 33, -2 * np.pi)
        self._objs["mercury"] = PlanetObj(38.710225, OrbitCenter(0.6, 3, -0.1),
                                          OrbitTilt(3, 0.5), -180.8, 26.08763045)

        m_factor = 39.2078
        self._objs["moon_def_a"] = PlanetObj(0.0279352315075 / m_factor,
                                             OrbitCenter(0 / m_factor, 0 / m_factor, 0 / m_factor),
                                             OrbitTilt(-0.2, 0.5), 226.4, 0.71015440177343)
        self._objs["moon_def_b"] = (
            PlanetObj(0 / m_factor,
                      OrbitCenter(-0.38 / m_factor, 0.22 / m_factor, 0 / m_factor),
                      OrbitTilt(2.3, 2.6), -1.8, 0.0))
        self._objs["moon"] = (
            PlanetObj(10 / m_factor,
                      OrbitCenter(0.8 / m_factor, -0.81 / m_factor, -0.07 / m_factor),
                      OrbitTilt(-1.8, -2.6), 261.2, 83.28521))

        self._objs["venus_def_a"] = PlanetObj(100, OrbitCenter(0.5, 0.5, 0),
                                              OrbitTilt(0, 0), 0, 2 * np.pi)
        self._objs["venus_def_b"] = PlanetObj(0, OrbitCenter(0, 0.65, 0),
                                              OrbitTilt(0, 0), 16.6, -2 * np.pi)
        self._objs["venus"] = PlanetObj(72.327789, OrbitCenter(0.6, -0.9, 0),
                                        OrbitTilt(3.2, -0.05), -23.6, 10.21331385)

        self._objs["mars_def_e"] = PlanetObj(100, OrbitCenter(10.1, -20.7, 0),
                                             OrbitTilt(0, 0), 0, 2 * np.pi)
        self._objs["mars_def_s"] = PlanetObj(7.44385, OrbitCenter(0, 0, 0),
                                             OrbitTilt(0, 0), -115, 0.3974599)
        self._objs["mars"] = PlanetObj(152.677, OrbitCenter(0, 0, 0),
                                       OrbitTilt(-0.2, -1.7), 119.3, -3.33985)

        self._objs["phobos"] = PlanetObj(5, OrbitCenter(0, 0, 0),
                                         OrbitTilt(0, 0), 122, 6986.5)
        self._objs["deimos"] = PlanetObj(10, OrbitCenter(0, 0, 0),
                                         OrbitTilt(0, 0), 0, 1802.0)

        self._objs["jupiter_def"] = PlanetObj(0.0, OrbitCenter(0.0, 0.0, 0.0),
                                              OrbitTilt(0.0, 0.0), 75.4, -2 * np.pi)
        self._objs["jupiter"] = PlanetObj(520.4, OrbitCenter(-49.0, 3.0, -1.0),
                                          OrbitTilt(0.0, -1.2), -34.0, 0.52994136)

        self._objs["saturn_def"] = PlanetObj(20, OrbitCenter(11, 0, 0),
                                             OrbitTilt(0, 0), 518, -2 * np.pi)
        self._objs["saturn"] = PlanetObj(958.2, OrbitCenter(69, 40, 0),
                                         OrbitTilt(-2.5, 0), -123.8, 0.21351984)

        self._objs["uranus_def"] = PlanetObj(20, OrbitCenter(0, 0, 0),
                                             OrbitTilt(0, 0), 123, -2 * np.pi)
        self._objs["uranus"] = PlanetObj(1920.13568, OrbitCenter(150, -65, 0),
                                         OrbitTilt(-0.2, -0.7), 371.8, 0.07500314)

        self._objs["neptune_def"] = PlanetObj(20, OrbitCenter(0, 0, 0),
                                              OrbitTilt(0, 0), 175.2, -2 * np.pi)
        self._objs["neptune"] = PlanetObj(3004.72, OrbitCenter(0, 20, 0),
                                          OrbitTilt(-1.6, 1.15), 329.3, 0.03837314)

        self._objs["halleys_def"] = PlanetObj(20, OrbitCenter(-5, 10, 11),
                                              OrbitTilt(0, 0), 179, -2 * np.pi)
        self._objs["halleys"] = PlanetObj(1674.5, OrbitCenter(-1540, -233.5, -507),
                                          OrbitTilt(6.4, 18.55), 76.33, -0.0830100973)

        self._objs["eros_def_a"] = PlanetObj(100, OrbitCenter(-40, 31.5, -0.5),
                                             OrbitTilt(-7.3, 3.6), 0, 2 * np.pi)
        self._objs["eros_def_b"] = PlanetObj(0, OrbitCenter(-16, -4.5, 0),
                                             OrbitTilt(0, 0), 0, -7.291563307179587)
        self._objs["eros"] = PlanetObj(145.79, OrbitCenter(5.2, -6, 0),
                                       OrbitTilt(0, 0), 171.8, 4.57668492)

    def _add_child(self, parent, child):
        """
        A wrapper around parent object add_child() to specify parent and child objects as strings
        :param parent: string
        :param child: string
        :return: none
        """

        self._objs[parent].add_child(self._objs[child])

    def _set_dependencies(self):
        """
        Sets the dependencies between the system objects
        :return: none
        """

        self._add_child("earth", "polar_axis")

        self._add_child("earth", "sun_def")
        self._add_child("sun_def", "sun")

        self._add_child("earth", "moon_def_a")

        self._add_child("moon_def_a", "moon_def_b")
        self._add_child("moon_def_b", "moon")

        self._add_child("earth", "mercury_def_a")
        self._add_child("mercury_def_a", "mercury_def_b")
        self._add_child("mercury_def_b", "mercury")

        self._add_child("earth", "venus_def_a")
        self._add_child("venus_def_a", "venus_def_b")
        self._add_child("venus_def_b", "venus")

        self._add_child("earth", "mars_def_e")
        self._add_child("mars_def_e", "mars_def_s")
        self._add_child("mars_def_s", "mars")

        self._add_child("mars", "phobos")
        self._add_child("mars", "deimos")

        self._add_child("sun", "jupiter_def")
        self._add_child("jupiter_def", "jupiter")

        self._add_child("sun", "saturn_def")
        self._add_child("saturn_def", "saturn")

        self._add_child("sun", "uranus_def")
        self._add_child("uranus_def", "uranus")

        self._add_child("sun", "neptune_def")
        self._add_child("neptune_def", "neptune")

        self._add_child("sun", "halleys_def")
        self._add_child("halleys_def", "halleys")

        self._add_child("earth", "eros_def_a")
        self._add_child("eros_def_a", "eros_def_b")
        self._add_child("eros_def_b", "eros")

    def move_system(self, julian_day):
        """
        Moves the system to the specified julian time.
        It re-initializes each object parameters before executing the move
        :param julian_day: float
            Julian Day to which move the Tychos object system
        :return: none
        """

        self.julian_day = julian_day
        for p in self._all_objects:
            self._objs[p].initialize_orbit_parameters()

        self._objs["polar_axis"].move_planet_basic([-23.439062, 0.26], 'zx')
        self._objs["earth"].move_planet_basic(90)
        for p in self._all_objects:
            self._objs[p].move_planet_tt(julian_day)

    @classmethod
    def get_all_objects(cls):
        """
        Returns all possible objects
        :return: list[string]
        """

        return cls._all_objects

    @classmethod
    def get_observable_objects(cls):
        """
        Returns observable objects
        :return: list[string]
        """

        return cls._observable_objects
