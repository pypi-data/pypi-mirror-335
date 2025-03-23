# cython: language_level=3
# distutils: language=c++
#
# JSBSim python interface using cython.
#
# Copyright (c) 2013 James Goppert
# Copyright (c) 2014-2025 Bertrand Coconnier
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option) any
# later version.

# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.

# You should have received a copy of the GNU Lesser General Public License along
# with this program; if not, write to the Free Software Foundation, Inc., 59
# Temple Place - Suite 330, Boston, MA 02111-1307, USA.

# Further information about the GNU Lesser General Public License can also be
# found on the world wide web at http://www.gnu.org.

"""An Open source flight dynamics & control software library

   Introduction
   ============

   JSBSim is an open source, multi-platform, object-oriented flight dynamics
   model (FDM) framework written in the C++ programming language. It is
   designed to support simulation modeling of any aerospace craft without the
   need for specific compiled and linked program code, instead relying on a
   versatile and powerful specification written in an XML format. The format is
   formally known as JSBSim-ML (JSBSim Markup Language).

   JSBSim (`www.jsbsim.org <https://www.jsbsim.org>`_) was created initially for
   the open source FlightGear flight simulator (`www.flightgear.org
   <https://www.flightgear.org>`_). JSBSim maintains the ability to run as a
   standalone executable in soft real-time, or batch mode. This is useful for
   running tests or sets of tests automatically using the internal scripting
   capability.

   JSBSim does not model specific aircraft in program code. The aircraft itself
   is defined in a file written in an XML-based format where the aircraft mass
   and geometric properties are specified. Additional statements define such
   characteristics as:

   * Landing gear location and properties.
   * Pilot eyepoint
   * Additional point masses (passengers, cargo, etc.)
   * Propulsion system (engines, fuel tanks, and "thrusters")
   * Flight control system
   * Autopilot
   * Aerodynamic stability derivatives and coefficients

   The configuration file format is set up to be easily comprehensible, for
   instance featuring textbook-like coefficients, which enables newcomers to
   become immediately fluent in describing vehicles, and requiring only prior
   basic theoretical aero knowledge.

   One of the more unique features of JSBSim is its method of modeling aircraft
   systems such as a flight control system, autopilot, electrical, etc. These
   are modeled by assembling strings of components that represent filters,
   switches, summers, gains, sensors, and so on.

   Another unique feature is displayed in the use of "properties". Properties
   essentially expose chosen variables as nodes in a tree, in a directory-like
   hierarchy. This approach facilitates plugging in different FDMs (Flight
   Dynamics Model) into FlightGear, but it also is a fundamental tool in
   allowing a wide range of aircraft to be modeled, each having its own unique
   control system, aerosurfaces, and flight deck instrument panel. The use of
   properties allows all these items for a craft to be modeled and integrated
   without the need for specific and unique program source code.

   The equations of motion are modeled essentially as they are presented in
   aerospace textbooks for the benefit of student users, but quaternions are
   used to track orientation, avoiding "gimbal lock". JSBSim can model the
   atmospheric flight of an aircraft, or the motion of a spacecraft in orbit.
   Coriolis and centripetal accelerations are incorporated into the EOM.

   JSBSim can output (log) data in a configurable way. Sets of data that are
   logically related can be selected to be output at a chosen rate, and
   individual properties can be selected for output. The output can be streamed
   to the console, and/or to a file (or files), and/or can be transmitted
   through a socket or sockets, or any combination of the aforementioned
   methods.

   JSBSim has been used in a variety of ways:

   * For developing control laws for a sounding rocket
   * For crafting an aircraft autopilot as part of a thesis project
   * As a flight model for FlightGear
   * As an FDM that drives motion base simulators for some
     commercial/entertainment simulators

   Supported Platforms
   ===================

   JSBSim has been built on the following platforms:

   * Linux (x86)
   * Windows (MSVC, Cygwin, Mingwin)
   * Mac OS X
   * FreeBSD

   Dependencies
   ============

   JSBSim has no external dependencies at present. No code is autogenerated.

   Licensing
   =========

   JSBSim is licensed under the terms of the Lesser GPL (LGPL)

   Website
   =======

   For more information, see the JSBSim web site:
   href="https://www.jsbsim.org">www.jsbsim.org."""

from cython.operator cimport dereference as deref
from typing import Optional

import enum
import errno
import os
import site
import sys

import numpy



__version__='1.2.2'


class BaseError(RuntimeError):
    """JSBSim base exception class."""
    pass


class TrimFailureError(BaseError):
    """Exception class for trim failures."""
    pass


class GeographicError(BaseError):
    """Exception class for geographic computation errors."""
    pass


base_error = <PyObject*>BaseError
trimfailure_error = <PyObject*>TrimFailureError
geographic_error = <PyObject*>GeographicError


def get_default_root_dir() -> str:
    """Return the root dir to default aircraft data."""
    for path in site.getsitepackages() + [site.USER_SITE]:
        root_dir = os.path.join(path, 'jsbsim')
        aircraft_dir = os.path.join(root_dir, 'aircraft')
        if os.path.isdir(aircraft_dir):
            return root_dir
    raise IOError("Can't find the default root directory")


def _append_xml(name: str) -> str:
    if len(name) < 4 or name[-4:] != '.xml':
        return name+'.xml'
    return name


cdef _convertToNumpyMat(const c_FGMatrix33& m):
    return numpy.matrix([[m.Entry(1, 1), m.Entry(1, 2), m.Entry(1, 3)],
                         [m.Entry(2, 1), m.Entry(2, 2), m.Entry(2, 3)],
                         [m.Entry(3, 1), m.Entry(3, 2), m.Entry(3, 3)]])


cdef _convertToNumpyVec(const c_FGColumnVector3& v):
    return numpy.matrix([v.Entry(1), v.Entry(2), v.Entry(3)]).T


cdef class FGPropagate:
    """Models the EOM and integration/propagation of state.

       The Equations of Motion (EOM) for JSBSim are integrated to propagate the
       state of the vehicle given the forces and moments that act on it. The
       integration accounts for a rotating Earth.

       Integration of rotational and translation position and rate can be
       customized as needed or frozen by the selection of no integrator. The
       selection of which integrator to use is done through the setting of the
       associated property. There are four properties which can be set:

       .. code-block:: xml

          simulation/integrator/rate/rotational
          simulation/integrator/rate/translational
          simulation/integrator/position/rotational
          simulation/integrator/position/translational

       Each of the integrators listed above can be set to one of the following
       values:

       .. code-block:: xml

          0: No integrator (Freeze)
          1: Rectangular Euler
          2: Trapezoidal
          3: Adams Bashforth 2
          4: Adams Bashforth 3
          5: Adams Bashforth 4"""

    cdef shared_ptr[c_FGPropagate] thisptr

    def __cinit__(self, FGFDMExec fdmex, *args, **kwargs):
        if fdmex is not None:
            self.thisptr.reset(new c_FGPropagate(fdmex.thisptr))
            if not self.thisptr:
                raise MemoryError()

    def __bool__(self) -> bool:
        """Check if the object is initialized."""
        if self.thisptr:
            return True
        return False

    cdef __intercept_invalid_pointer(self):
        if not self.thisptr:
            raise BaseError("Object is not initialized")

    def get_Tl2b(self) -> numpy.ndarray:
        """Retrieves the local-to-body transformation matrix.

           The quaternion class, being the means by which the orientation of
           the vehicle is stored, manages the local-to-body transformation
           matrix.

           :return: a reference to the local-to-body transformation matrix."""
        self.__intercept_invalid_pointer()
        return _convertToNumpyMat(deref(self.thisptr).GetTl2b())

    def get_Tec2b(self) -> numpy.ndarray:
        """Retrieves the ECEF-to-body transformation matrix.

           :return: a reference to the ECEF-to-body transformation matrix."""
        self.__intercept_invalid_pointer()
        return _convertToNumpyMat(deref(self.thisptr).GetTec2b())

    def get_uvw(self) -> numpy.ndarray:
        """Retrieves a body frame velocity component.

           Retrieves a body frame velocity component. The velocity returned is
           extracted from the vUVW vector (an FGColumnVector). The vector for
           the velocity in Body frame is organized (Vx, Vy, Vz). The vector is
           1-based. In other words, GetUVW(1) returns Vx. Various convenience
           enumerators are defined in :ref:`FGJSBBase`. The relevant
           enumerators for the velocity returned by this call are, eX=1, eY=2,
           eZ=3. units ft/sec

           :param idx: the index of the velocity component desired (1-based).
           

           :return: The body frame velocity component."""
        self.__intercept_invalid_pointer()
        return _convertToNumpyVec(deref(self.thisptr).GetUVW())


cdef class FGPropertyNode:
    """Class wrapper for property handling."""

    cdef SGSharedPtr[c_FGPropertyNode] thisptr

    def __bool__(self) -> bool:
        """Check if the object is initialized."""
        return self.thisptr.ptr() is not NULL

    def __str__(self) -> str:
        if self.thisptr.ptr() is not NULL:
            return f"Property '{self.get_fully_qualified_name()}' (value: {self.get_double_value()})"
        return "Uninitialized property"

    cdef __intercept_invalid_pointer(self):
        if self.thisptr.ptr() is NULL:
            raise BaseError("Object is not initialized")

    cdef __validate_node_pointer(self, create: bool):
        if self.thisptr.ptr() is not NULL:
            return self
        else:
            if create:
                raise MemoryError()
            return None

    def get_name(self) -> str:
        """Get the name of a node."""
        self.__intercept_invalid_pointer()
        return self.thisptr.ptr().GetName().decode()

    def get_fully_qualified_name(self) -> str:
        """Get the fully qualified name of a node This function is very slow, so is probably useful for debugging only."""
        self.__intercept_invalid_pointer()
        return self.thisptr.ptr().GetFullyQualifiedName().decode()

    def get_node(self, path: str, create: bool = False) -> Optional[FGPropertyNode]:
        """Get a property node.

           :param path: The path of the node, relative to root.
           :param create: true to create the node if it doesn't exist.
           

           :return: The node, or 0 if none exists and none was created."""
        self.__intercept_invalid_pointer()
        node = FGPropertyNode()
        node.thisptr = self.thisptr.ptr().GetNode(path.encode(), create)
        return node.__validate_node_pointer(create)

    def get_double_value(self) -> float:
        """Get the property value.

           :return: The property value as a double."""
        self.__intercept_invalid_pointer()
        return self.thisptr.ptr().getDoubleValue()

    def set_double_value(self, value: float) -> bool:
        """Set the property value.

           :param value: The new value.
           :return: True if the assignment succeeded, False otherwise."""
        self.__intercept_invalid_pointer()
        return self.thisptr.ptr().setDoubleValue(value)

cdef class FGPropertyManager:
    """
       .. note::

          This feature is not yet documented."""

    cdef shared_ptr[c_FGPropertyManager] thisptr

    def __cinit__(self, FGPropertyNode node = None, *args, **kwargs):
        if node is None:
            self.thisptr.reset(new c_FGPropertyManager())
        else:
            try:
                node.__intercept_invalid_pointer()
            except BaseError:
                raise BaseError("Cannot instantiate FGPropertyManager with an uninitialized property node.")
            self.thisptr.reset(new c_FGPropertyManager(node.thisptr.ptr()))

        if not self.thisptr:
            raise MemoryError()

    def get_node(self, path: Optional[str] = None, create: bool = False) -> Optional[FGPropertyNode]:
        """
           .. note::

              This feature is not yet documented."""
        node = FGPropertyNode()
        if path is None:
            node.thisptr = deref(self.thisptr).GetNode()
        else:
            node.thisptr = deref(self.thisptr).GetNode(path.encode(), create)
        return node.__validate_node_pointer(create)

    def hasNode(self, path: str) -> bool:
        """
           .. note::

              This feature is not yet documented."""
        return deref(self.thisptr).HasNode(path.encode())

cdef class FGGroundReactions:
    """Manages ground reactions modeling.

       Maintains a list of landing gear and ground contact points, all
       instances of :ref:`FGLGear`. Sums their forces and moments so that these
       may be provided to :ref:`FGPropagate`. Parses the <ground_reactions>
       section of the aircraft configuration file.

       .. rubric:: Configuration File Format of <ground_reactions> Section:

       .. code-block:: xml

          <ground_reactions>
              <contact>
                 ... {see FGLGear for specifics of this format}
              </contact>
              ... {more contacts}
          </ground_reactions>"""

    cdef shared_ptr[c_FGGroundReactions] thisptr

    def __cinit__(self, FGFDMExec fdmex, *args, **kwargs):
        if fdmex is not None:
            self.thisptr.reset(new c_FGGroundReactions(fdmex.thisptr))
            if not self.thisptr:
                raise MemoryError()

    def __bool__(self) -> bool:
        """Check if the object is initialized."""
        if self.thisptr:
            return True
        return False

    cdef __intercept_invalid_pointer(self):
        if not self.thisptr:
            raise BaseError("Object is not initialized")

    def get_gear_unit(self, gear: int) -> FGLGear:
        """Gets a gear instance.

           :param gear: index of gear instance
           

           :return: a pointer to the :ref:`FGLGear` instance of the gear unit
                    requested"""
        self.__intercept_invalid_pointer()
        lgear = FGLGear()
        lgear.thisptr = deref(self.thisptr).GetGearUnit(gear)
        return lgear

    def get_num_gear_units(self) -> int:
        """Gets the number of gears.

           :return: the number of gears of the aircraft."""
        self.__intercept_invalid_pointer()
        return deref(self.thisptr).GetNumGearUnits()

cdef class FGLGear:
    """Landing gear model.

       Calculates forces and moments due to landing gear reactions. This is
       done in several steps, and is dependent on what kind of gear is being
       modeled. Here are the parameters that can be specified in the config
       file for modeling landing gear:

       .. rubric:: Physical Characteristics

       1. X, Y, Z location, in inches in structural coordinate frame
       2. Spring constant, in lbs/ft
       3. Damping coefficient, in lbs/ft/sec
       4. Dynamic Friction Coefficient
       5. Static Friction Coefficient

       .. rubric:: Operational Properties

       1. Name
       2. Brake Group Membership {one of LEFT | CENTER | RIGHT | NOSE | TAIL |
          NONE}
       3. Max Steer Angle, in degrees

       .. rubric:: Algorithm and Approach to Modeling

       1. Find the location of the uncompressed landing gear relative to the CG
          of the aircraft. Remember, the structural coordinate frame that the
          aircraft is defined in is: X positive towards the tail, Y positive
          out the right side, Z positive upwards. The locations of the various
          parts are given in inches in the config file.
       2. The vector giving the location of the gear (relative to the cg) is
          rotated 180 degrees about the Y axis to put the coordinates in body
          frame (X positive forwards, Y positive out the right side, Z positive
          downwards, with the origin at the cg). The lengths are also now given
          in feet.
       3. The new gear location is now transformed to the local coordinate
          frame using the body-to-local matrix. (Mb2l).
       4. Knowing the location of the center of gravity relative to the ground
          (height above ground level or AGL) now enables gear deflection to be
          calculated. The gear compression value is the local frame gear Z
          location value minus the height AGL. [Currently, we make the
          assumption that the gear is oriented - and the deflection occurs in -
          the Z axis only. Additionally, the vector to the landing gear is
          currently not modified - which would (correctly) move the point of
          contact to the actual compressed-gear point of contact. Eventually,
          articulated gear may be modeled, but initially an effort must be made
          to model a generic system.] As an example, say the aircraft left main
          gear location (in local coordinates) is Z = 3 feet (positive) and the
          height AGL is 2 feet. This tells us that the gear is compressed 1
          foot.
       5. If the gear is compressed, a Weight-On-Wheels (WOW) flag is set.
       6. With the compression length calculated, the compression velocity may
          now be calculated. This will be used to determine the damping force
          in the strut. The aircraft rotational rate is multiplied by the
          vector to the wheel to get a wheel velocity in body frame. That
          velocity vector is then transformed into the local coordinate frame.
       7. The aircraft cg velocity in the local frame is added to the just-
          calculated wheel velocity (due to rotation) to get a total wheel
          velocity in the local frame.
       8. The compression speed is the Z-component of the vector.
       9. With the wheel velocity vector no longer needed, it is normalized and
          multiplied by a -1 to reverse it. This will be used in the friction
          force calculation.
       10. Since the friction force takes place solely in the runway plane, the
           Z coordinate of the normalized wheel velocity vector is set to zero.
       11. The gear deflection force (the force on the aircraft acting along
           the local frame Z axis) is now calculated given the spring and
           damper coefficients, and the gear deflection speed and stroke
           length. Keep in mind that gear forces always act in the negative
           direction (in both local and body frames), and are not capable of
           generating a force in the positive sense (one that would attract the
           aircraft to the ground). So, the gear forces are always negative -
           they are limited to values of zero or less. The gear force is simply
           the negative of the sum of the spring compression length times the
           spring coefficient and the gear velocity times the damping
           coefficient.
       12. The lateral/directional force acting on the aircraft through the
           landing
       13. gear (along the local frame X and Y axes) is calculated next. First,
           the friction coefficient is multiplied by the recently calculated
           Z-force. This is the friction force. It must be given direction in
           addition to magnitude. We want the components in the local frame X
           and Y axes. From step 9, above, the conditioned wheel velocity
           vector is taken and the X and Y parts are multiplied by the friction
           force to get the X and Y components of friction.
       14. The wheel force in local frame is next converted to body frame.
       15. The moment due to the gear force is calculated by multiplying r x F
           (radius to wheel crossed into the wheel force). Both of these
           operands are in body frame.

       .. rubric:: Configuration File Format for <contact> Section:

       .. code-block:: xml

          <contact type="{BOGEY | STRUCTURE}" name="{string}">
              <location unit="{IN | M}">
                  <x> {number} </x>
                  <y> {number} </y>
                  <z> {number} </z>
              </location>
              <orientation unit="{RAD | DEG}">
                  <pitch> {number} </pitch>
                  <roll> {number} </roll>
                  <yaw> {number} </yaw>
              </orientation>
              <static_friction> {number} </static_friction>
              <dynamic_friction> {number} </dynamic_friction>
              <rolling_friction> {number} </rolling_friction>
              <spring_coeff unit="{LBS/FT | N/M}"> {number} </spring_coeff>
              <damping_coeff type="{ | SQUARE}" unit="{LBS/FT/SEC | N/M/SEC}"> {number} </damping_coeff>
              <damping_coeff_rebound type="{ | SQUARE}" unit="{LBS/FT/SEC | N/M/SEC}"> {number} </damping_coeff_rebound>
              <max_steer unit="DEG"> {number | 0 | 360} </max_steer>
              <brake_group> {NONE | LEFT | RIGHT | CENTER | NOSE | TAIL} </brake_group>
              <retractable>{0 | 1}</retractable>
              <table name="{CORNERING_COEFF}" type="internal">
                  <tableData>
                      {cornering parameters}
                  </tableData>
              </table>
          </contact>"""

    cdef shared_ptr[c_FGLGear] thisptr

    def __bool__(self) -> bool:
        """Check if the object is initialized."""
        if self.thisptr:
            return True
        return False

    cdef __intercept_invalid_pointer(self):
        if not self.thisptr:
            raise BaseError("Object is not initialized")

    def get_steer_norm(self) -> float:
        """
           .. note::

              This feature is not yet documented."""
        self.__intercept_invalid_pointer()
        return deref(self.thisptr).GetSteerNorm()

    def get_body_x_force(self) -> float:
        """
           .. note::

              This feature is not yet documented."""
        self.__intercept_invalid_pointer()
        return deref(self.thisptr).GetBodyXForce()

    def get_body_y_force(self) -> float:
        """
           .. note::

              This feature is not yet documented."""
        self.__intercept_invalid_pointer()
        return deref(self.thisptr).GetBodyYForce()

    def get_body_z_force(self) -> float:
        """
           .. note::

              This feature is not yet documented."""
        self.__intercept_invalid_pointer()
        return deref(self.thisptr).GetBodyZForce()

    def get_location(self) -> numpy.ndarray:
        self.__intercept_invalid_pointer()
        return _convertToNumpyVec(deref(self.thisptr).GetLocation())

    def get_acting_location(self) -> numpy.ndarray:
        self.__intercept_invalid_pointer()
        return _convertToNumpyVec(deref(self.thisptr).GetActingLocation())

cdef class FGAuxiliary:
    """Encapsulates various uncategorized scheduled functions.

       Pilot sensed accelerations are calculated here. This is used for the
       coordinated turn ball instrument. Motion base platforms sometimes use
       the derivative of pilot sensed accelerations as the driving parameter,
       rather than straight accelerations.

       The theory behind pilot-sensed calculations is presented:

       For purposes of discussion and calculation, assume for a minute that the
       pilot is in space and motionless in inertial space. She will feel no
       accelerations. If the aircraft begins to accelerate along any axis or
       axes (without rotating), the pilot will sense those accelerations. If
       any rotational moment is applied, the pilot will sense an acceleration
       due to that motion in the amount:

       [wdot X R] + [w X (w X R)] Term I Term II

       where:

       wdot = omegadot, the rotational acceleration rate vector w = omega, the
       rotational rate vector R = the vector from the aircraft CG to the pilot
       eyepoint

       The sum total of these two terms plus the acceleration of the aircraft
       body axis gives the acceleration the pilot senses in inertial space. In
       the presence of a large body such as a planet, a gravity field also
       provides an accelerating attraction. This acceleration can be
       transformed from the reference frame of the planet so as to be expressed
       in the frame of reference of the aircraft. This gravity field
       accelerating attraction is felt by the pilot as a force on her tushie as
       she sits in her aircraft on the runway awaiting takeoff clearance.

       In JSBSim the acceleration of the body frame in inertial space is given
       by the F = ma relation. If the vForces vector is divided by the aircraft
       mass, the acceleration vector is calculated. The term wdot is equivalent
       to the JSBSim vPQRdot vector, and the w parameter is equivalent to vPQR."""

    cdef shared_ptr[c_FGAuxiliary] thisptr

    def __cinit__(self, FGFDMExec fdmex, *args, **kwargs):
        if fdmex is not None:
            self.thisptr.reset(new c_FGAuxiliary(fdmex.thisptr))
            if not self.thisptr:
                raise MemoryError()

    def __bool__(self) -> bool:
        """Check if the object is initialized."""
        if self.thisptr:
            return True
        return False

    cdef __intercept_invalid_pointer(self):
        if not self.thisptr:
            raise BaseError("Object is not initialized")

    def get_Tw2b(self) -> numpy.ndarray:
        """Calculates and returns the wind-to-body axis transformation matrix.

           :return: a reference to the wind-to-body transformation matrix."""
        self.__intercept_invalid_pointer()
        return _convertToNumpyMat(deref(self.thisptr).GetTw2b())

    def get_Tb2w(self) -> numpy.ndarray:
        """Calculates and returns the body-to-wind axis transformation matrix.

           :return: a reference to the wind-to-body transformation matrix."""
        self.__intercept_invalid_pointer()
        return _convertToNumpyMat(deref(self.thisptr).GetTb2w())

cdef class FGAerodynamics:
    """Encapsulates the aerodynamic calculations.

       This class owns and contains the list of force/coefficients that define
       the aerodynamic properties of an aircraft. Here also, such unique
       phenomena as ground effect, aerodynamic reference point shift, and
       maximum lift curve tailoff are handled.

       .. rubric:: Configuration File Format for <aerodynamics> Section:

       .. code-block:: xml

          <aerodynamics>
             <alphalimits unit="{RAD | DEG}">
               <min> {number} </min>
               <max> {number} </max>
             </alphalimits>
             <hysteresis_limits unit="{RAD | DEG}">
               <min> {number} </min>
               <max> {number} </max>
             </hysteresis_limits>
             <aero_ref_pt_shift_x>  
               <function>
                 {function contents}
               </function> 
             </aero_ref_pt_shift_x>  
             <function>
               {function contents}
             </function>
             <axis name="{LIFT | DRAG | SIDE | ROLL | PITCH | YAW}">
               {force or moment definitions}
             </axis>
             {additional axis definitions}
          </aerodynamics>

       Optionally two other coordinate systems may be used.
       
       1) Body coordinate system:

       .. code-block:: xml

          <axis name="{X | Y | Z}">
 
       2) Axial-Normal coordinate system:

       .. code-block:: xml

          <axis name="{AXIAL | NORMAL | SIDE}">
 
       Systems may NOT be combined, or a load error will occur."""

    cdef shared_ptr[c_FGAerodynamics] thisptr

    def __cinit__(self, FGFDMExec fdmex, *args, **kwargs):
        if fdmex is not None:
            self.thisptr.reset(new c_FGAerodynamics(fdmex.thisptr))
            if not self.thisptr:
                raise MemoryError()

    def __bool__(self) -> bool:
        """Check if the object is initialized."""
        if self.thisptr:
            return True
        return False

    cdef __intercept_invalid_pointer(self):
        if not self.thisptr:
            raise BaseError("Object is not initialized")

    def get_moments_MRC(self) -> numpy.ndarray:
        """Gets the aerodynamic moment about the Moment Reference Center for an axis.

           :return: the moment about a single axis (as described also in the
                    similar call to GetForces(int n)."""
        self.__intercept_invalid_pointer()
        return _convertToNumpyVec(deref(self.thisptr).GetMomentsMRC())

    def get_forces(self) -> numpy.ndarray:
        """Gets the aerodynamic force for an axis.

           :param n: Axis index. This could be 0, 1, or 2, or one of the axis
                     enums: eX, eY, eZ.
           

           :return: the force acting on an axis"""
        self.__intercept_invalid_pointer()
        return _convertToNumpyVec(deref(self.thisptr).GetForces())

cdef class FGAircraft:
    """Encapsulates an Aircraft and its systems.

       Owns all the parts (other classes) which make up this aircraft. This
       includes the Engines, Tanks, Propellers, Nozzles, Aerodynamic and Mass
       properties, landing gear, etc. These constituent parts may actually run
       as separate JSBSim models themselves, but the responsibility for
       initializing them and for retrieving their force and moment
       contributions falls to :ref:`FGAircraft`.

       The <metrics> section of the aircraft configuration file is read here,
       and the metrical information is held by this class.

       .. rubric:: Configuration File Format for <metrics> Section:

       .. code-block:: xml

          <metrics>
              <wingarea unit="{FT2 | M2}"> {number} </wingarea>
              <wingspan unit="{FT | M}"> {number} </wingspan>
              <chord unit="{FT | M}"> {number} </chord>
              <htailarea unit="{FT2 | M2}"> {number} </htailarea>
              <htailarm unit="{FT | M}"> {number} </htailarm>
              <vtailarea unit="{FT2 | M}"> {number} </vtailarea>
              <vtailarm unit="{FT | M}"> {number} </vtailarm>
              <wing_incidence unit="{RAD | DEG}"> {number} </wing_incidence>
              <location name="{AERORP | EYEPOINT | VRP}" unit="{IN | M}">
                  <x> {number} </x>
                  <y> {number} </y>
                  <z> {number} </z>
              </location>
              {other location blocks}
          </metrics>"""

    cdef shared_ptr[c_FGAircraft] thisptr

    def __cinit__(self, FGFDMExec fdmex, *args, **kwargs):
        if fdmex is not None:
            self.thisptr.reset(new c_FGAircraft(fdmex.thisptr))
            if not self.thisptr:
                raise MemoryError()

    def __bool__(self) -> bool:
        """Check if the object is initialized."""
        if self.thisptr:
            return True
        return False

    cdef __intercept_invalid_pointer(self):
        if not self.thisptr:
            raise BaseError("Object is not initialized")

    def get_xyz_rp(self) -> numpy.ndarray:
        """
           .. note::

              This feature is not yet documented."""
        self.__intercept_invalid_pointer()
        return _convertToNumpyVec(deref(self.thisptr).GetXYZrp())


class eTemperature(enum.Enum):
    eNoTempUnit = 0
    eFahrenheit = 1
    eCelsius    = 2
    eRankine    = 3
    eKelvin     = 4


class ePressure(enum.Enum):
    eNoPressUnit= 0
    ePSF        = 1
    eMillibars  = 2
    ePascals    = 3
    eInchesHg   = 4


cdef class FGAtmosphere:
    """Models an empty, abstract base atmosphere class.

       .. rubric:: Properties

       * **atmosphere/T-R** The current modeled temperature in degrees Rankine.
       * **atmosphere/rho-slugs_ft3**
       * **atmosphere/P-psf**
       * **atmosphere/a-fps**
       * **atmosphere/T-sl-R**
       * **atmosphere/rho-sl-slugs_ft3**
       * **atmosphere/P-sl-psf**
       * **atmosphere/a-sl-fps**
       * **atmosphere/theta**
       * **atmosphere/sigma**
       * **atmosphere/delta**
       * **atmosphere/a-ratio**"""

    cdef shared_ptr[c_FGAtmosphere] thisptr

    def __bool__(self) -> bool:
        """Check if the object is initialized."""
        if self.thisptr:
            return True
        return False

    cdef __intercept_invalid_pointer(self):
        if not self.thisptr:
            raise BaseError("Object is not initialized")

    def set_temperature(self, t: float, h: float, unit: eTemperature) -> None:
        """Sets the temperature at the supplied altitude.

           :param t: The temperature value in the unit provided.
           :param h: The altitude in feet above sea level.
           :param unit: The unit of the temperature."""
        self.__intercept_invalid_pointer()
        deref(self.thisptr).SetTemperature(t, h, unit.value)

    def get_temperature(self, h: float) -> float:
        """Returns the actual modeled temperature in degrees Rankine at a specified altitude.

           :param altitude: The altitude above sea level (ASL) in feet.
           

           :return: Modeled temperature in degrees Rankine at the specified
                    altitude."""
        self.__intercept_invalid_pointer()
        return deref(self.thisptr).GetTemperature(h)

    def set_pressure_SL(self, unit: ePressure, p: float) -> None:
        """Sets the sea level pressure for modeling.

           :param pressure: The pressure in the units specified.
           :param unit: the unit of measure that the specified pressure is
                        supplied in."""
        self.__intercept_invalid_pointer()
        deref(self.thisptr).SetPressureSL(unit.value, p)

cdef class FGMassBalance:
    """Models weight, balance and moment of inertia information.

       Maintains a vector of point masses. Sums the contribution of all, and
       provides this to :ref:`FGPropagate`. Loads the <mass_balance> section of
       the aircraft configuration file. There can be any number of
       <pointmasses>. Each can also have a shape which - if present - causes an
       associated moment of inertia to be calculated based on the shape. Note
       that a cylinder is solid, a tube is hollow, a ball is solid and a sphere
       is hollow.

       The inertia tensor must be specified in the structural frame (x axis
       positive aft, y axis positive out of the right wing and z axis upward).
       The sign of the inertia cross products are optional by JSBSim. if
       negated_crossproduct_inertia == "true", then define: ixy = -integral( x
       * y * dm ), ixz = -integral( x * z * dm ), iyz = -integral( y * z * dm
       ). else if negated_crossproduct_inertia == "false", then define: ixy =
       integral( x * y * dm ), ixz = integral( x * z * dm ), iyz = integral( y
       * z * dm ). default is negated_crossproduct_inertia = "true". We
       strongly recommend defining negated_crossproduct_inertia = "false",
       which is consistent with the specifications in the field of flight
       dynamics.

       .. rubric:: Configuration File Format for <mass_balance> Section:

       .. code-block:: xml

          <mass_balance negated_crossproduct_inertia="true|false">
              <ixx unit="{SLUG*FT2 | KG*M2}"> {number} </ixx>
              <iyy unit="{SLUG*FT2 | KG*M2}"> {number} </iyy>
              <izz unit="{SLUG*FT2 | KG*M2}"> {number} </izz>
              <ixy unit="{SLUG*FT2 | KG*M2}"> {number} </ixy>
              <ixz unit="{SLUG*FT2 | KG*M2}"> {number} </ixz>
              <iyz unit="{SLUG*FT2 | KG*M2}"> {number} </iyz>
              <emptywt unit="{LBS | KG"> {number} </emptywt>
              <location name="CG" unit="{IN | FT | M}">
                  <x> {number} </x>
                  <y> {number} </y>
                  <z> {number} </z>
              </location>
              [<pointmass name="{string}">
                  <form shape="{tube | cylinder | sphere | ball}">
                     <radius unit="{IN | FT | M}"> {number} </radius>
                     <length unit="{IN | FT | M}"> {number} </length>
                  </form> 
                  <weight unit="{LBS | KG}"> {number} </weight>
                  <location name="{string}" unit="{IN | FT | M}">
                      <x> {number} </x>
                      <y> {number} </y>
                      <z> {number} </z>
                  </location>
              </pointmass>
              ... other point masses ...]
          </mass_balance>"""

    cdef shared_ptr[c_FGMassBalance] thisptr

    def __cinit__(self, FGFDMExec fdmex, *args, **kwargs):
        if fdmex is not None:
            self.thisptr.reset(new c_FGMassBalance(fdmex.thisptr))
            if not self.thisptr:
                raise MemoryError()

    def __bool__(self) -> bool:
        """Check if the object is initialized."""
        if self.thisptr:
            return True
        return False

    cdef __intercept_invalid_pointer(self):
        if not self.thisptr:
            raise BaseError("Object is not initialized")

    def get_xyz_cg(self) -> numpy.ndarray:
        """
           .. note::

              This feature is not yet documented."""
        self.__intercept_invalid_pointer()
        return _convertToNumpyVec(deref(self.thisptr).GetXYZcg())

    def get_J(self) -> numpy.ndarray:
        """Returns the inertia matrix expressed in the body frame."""
        self.__intercept_invalid_pointer()
        return _convertToNumpyMat(deref(self.thisptr).GetJ())

    def get_Jinv(self) -> numpy.ndarray:
        """Returns the inverse of the inertia matrix expressed in the body frame."""
        self.__intercept_invalid_pointer()
        return _convertToNumpyMat(deref(self.thisptr).GetJinv())

cdef class FGJSBBase:
    """JSBSim Base class.

       This class provides universal constants, utility functions, messaging
       functions, and enumerated constants to JSBSim."""

    cdef c_FGJSBBase *baseptr

    def __cinit__(self, *args, **kwargs):
        if type(self) is FGJSBBase: # Check if it is called from a derived class
            self.baseptr = new c_FGJSBBase()
            if not self.baseptr:
                raise MemoryError()

    def __dealloc__(self) -> None:
        if type(self) is FGJSBBase:
            del self.baseptr

    @property
    def debug_lvl(self) -> None:
        return self.baseptr.debug_lvl

    @debug_lvl.setter
    def debug_lvl(self, dbglvl: int) -> None:
        self.baseptr.debug_lvl = dbglvl

    def get_version(self) -> str:
        """Returns the version number of JSBSim.

           :return: The version number of JSBSim."""
        return self.baseptr.GetVersion().decode('utf-8')

    def disable_highlighting(self) -> None:
        """Disables highlighting in the console output."""
        self.baseptr.disableHighLighting()

cdef class FGPropulsion:
    """Propulsion management class.

       The Propulsion class is the container for the entire propulsion system,
       which is comprised of engines, and tanks. Once the Propulsion class gets
       the config file, it reads in the <propulsion> section. Then:

       1. The appropriate engine type instance is created
       2. At least one tank object is created, and is linked to an engine.

       At Run time each engine's Calculate() method is called.

       .. rubric:: Configuration File Format:

       .. code-block:: xml

          <propulsion>
              <engine file="{string}">
                ... see FGEngine, FGThruster, and class for engine type ...
              </engine>
              ... more engines ...
              <tank type="{FUEL | OXIDIZER}"> 
                ... see FGTank ...
              </tank>
              ... more tanks ...
              <dump-rate unit="{LBS/MIN | KG/MIN}"> {number} </dump-rate>
              <refuel-rate unit="{LBS/MIN | KG/MIN}"> {number} </refuel-rate>
          </propulsion>"""

    cdef shared_ptr[c_FGPropulsion] thisptr

    def __cinit__(self, FGFDMExec fdmex, *args, **kwargs):
        if fdmex is not None:
            self.thisptr.reset(new c_FGPropulsion(fdmex.thisptr))
            if not self.thisptr:
                raise MemoryError()

    def __bool__(self) -> bool:
        """Check if the object is initialized."""
        if self.thisptr:
            return True
        return False

    cdef __intercept_invalid_pointer(self):
        if not self.thisptr:
            raise BaseError("Object is not initialized")

    def init_running(self, n: int) -> None:
        """Sets up the engines as running."""
        self.__intercept_invalid_pointer()
        deref(self.thisptr).InitRunning(n)

    def get_num_engines(self) -> int:
        """Retrieves the number of engines defined for the aircraft."""
        self.__intercept_invalid_pointer()
        return deref(self.thisptr).GetNumEngines()

    def get_engine(self, idx: int) -> FGEngine:
        """Retrieves an engine object pointer from the list of engines.

           :param index: the engine index within the vector container
           

           :return: the address of the specific engine, or zero if no such
                    engine is available"""
        self.__intercept_invalid_pointer()
        engine = FGEngine()
        engine.thisptr = deref(self.thisptr).GetEngine(idx)
        return engine

    def get_steady_state(self) -> bool:
        """Loops the engines until thrust output steady (used for trimming)"""
        self.__intercept_invalid_pointer()
        return deref(self.thisptr).GetSteadyState()

cdef class FGEngine:
    """Base class for all engines.

       This base class contains methods and members common to all engines, such
       as logic to drain fuel from the appropriate tank, etc.

       .. rubric:: Configuration File Format:

       .. code-block:: xml

          <engine file="{string}">
              <feed> {integer} </feed>
              ... optional more feed tank index numbers ... 
              <thruster file="{string}">
                  <location unit="{IN | M}">
                      <x> {number} </x>
                      <y> {number} </y>
                      <z> {number} </z>
                  </location>
                  <orient unit="{RAD | DEG}">
                      <roll> {number} </roll>
                      <pitch> {number} </pitch>
                      <yaw> {number} </yaw>
                  </orient>
              </thruster>
          </engine>"""

    cdef shared_ptr[c_FGEngine] thisptr

    def __bool__(self) -> bool:
        """Check if the object is initialized."""
        if self.thisptr:
            return True
        return False

    cdef __intercept_invalid_pointer(self):
        if not self.thisptr:
            raise BaseError("Object is not initialized")

    def init_running(self) -> int:
        """
           .. note::

              This feature is not yet documented."""
        self.__intercept_invalid_pointer()
        return deref(self.thisptr).InitRunning()

cdef class FGLinearization:
    """Class used to create linear models from"""

    cdef shared_ptr[c_FGLinearization] thisptr

    def __cinit__(self, FGFDMExec fdmex, *args, **kwargs):
        if fdmex is not None:
            self.thisptr.reset(new c_FGLinearization(fdmex.thisptr))
            if not self.thisptr:
                raise MemoryError()

    def __bool__(self) -> bool:
        """Check if the object is initialized."""
        if self.thisptr:
            return True
        return False

    cdef __intercept_invalid_pointer(self):
        if not self.thisptr:
            raise BaseError("Object is not initialized")

    def write_scicoslab(self, path: str) -> None:
        """Write Scicoslab source file with the state space model to a file in the current working directory."""
        self.__intercept_invalid_pointer()
        if path is None:
            deref(self.thisptr).WriteScicoslab()
        else:
            deref(self.thisptr).WriteScicoslab(path.encode("utf-8"))

    @property
    def x0(self) -> numpy.ndarray:
        """Initial state"""
        self.__intercept_invalid_pointer()
        return numpy.array(deref(self.thisptr).GetInitialState())

    @property
    def u0(self) -> numpy.ndarray:
        """Initial input"""
        self.__intercept_invalid_pointer()
        return numpy.array(deref(self.thisptr).GetInitialInput())

    @property
    def y0(self) -> numpy.ndarray:
        """Initial output"""
        self.__intercept_invalid_pointer()
        return numpy.array(deref(self.thisptr).GetInitialOutput())

    @property
    def system_matrix(self) -> numpy.ndarray:
        self.__intercept_invalid_pointer()
        cdef const vector[vector[double]]* cdef_A = &deref(self.thisptr).GetSystemMatrix()
        return numpy.array(deref(cdef_A))

    @property
    def input_matrix(self) -> numpy.ndarray:
        self.__intercept_invalid_pointer()
        cdef const vector[vector[double]]* cdef_B = &deref(self.thisptr).GetInputMatrix()
        return numpy.array(deref(cdef_B))

    @property
    def output_matrix(self) -> numpy.ndarray:
        self.__intercept_invalid_pointer()
        cdef const vector[vector[double]]* cdef_C = &deref(self.thisptr).GetOutputMatrix()
        return numpy.array(deref(cdef_C))

    @property
    def feedforward_matrix(self) -> numpy.ndarray:
        self.__intercept_invalid_pointer()
        cdef const vector[vector[double]]* cdef_D = &deref(self.thisptr).GetFeedforwardMatrix()
        return numpy.array(deref(cdef_D))

    @property
    def state_space(self) -> tuple[numpy.ndarray]:
        return (self.system_matrix, self.input_matrix, self.output_matrix, self.feedforward_matrix)

    @property
    def x_names(self) -> tuple[str]:
        """State names"""
        self.__intercept_invalid_pointer()
        cdef vector[string] names = deref(self.thisptr).GetStateNames()
        return tuple(name.decode("utf-8") for name in names)

    @property
    def u_names(self) -> tuple[str]:
        "Input names"
        self.__intercept_invalid_pointer()
        cdef vector[string] names = deref(self.thisptr).GetInputNames()
        return tuple(name.decode("utf-8") for name in names)

    @property
    def y_names(self) -> tuple[str]:
        """Output names"""
        self.__intercept_invalid_pointer()
        cdef vector[string] names = deref(self.thisptr).GetOutputNames()
        return tuple(name.decode("utf-8") for name in names)

    @property
    def x_units(self) -> tuple[str]:
        """State units"""
        self.__intercept_invalid_pointer()
        cdef vector[string] units = deref(self.thisptr).GetStateUnits()
        return tuple(unit.decode("utf-8") for unit in units)

    @property
    def u_units(self) -> tuple[str]:
        """Input unit"""
        self.__intercept_invalid_pointer()
        cdef vector[string] units = deref(self.thisptr).GetInputUnits()
        return tuple(unit.decode("utf-8") for unit in units)

    @property
    def y_units(self) -> tuple[str]:
        """Output units"""
        self.__intercept_invalid_pointer()
        cdef vector[string] units = deref(self.thisptr).GetOutputUnits()
        return tuple(unit.decode("utf-8") for unit in units)


# this is the python wrapper class
cdef class FGFDMExec(FGJSBBase):
    """Encapsulates the JSBSim simulation executive.

       This class is the executive class through which all other simulation
       classes are instantiated, initialized, and run. When integrated with
       FlightGear (or other flight simulator) this class is typically
       instantiated by an interface class on the simulator side.

       At the time of simulation initialization, the interface class creates an
       instance of this executive class. The executive is subsequently directed
       to load the chosen aircraft specification file:

       .. code-block:: cpp

          fdmex = new FGFDMExec( ... );
          result = fdmex->LoadModel( ... );

       When an aircraft model is loaded, the config file is parsed and for each
       of the sections of the config file (propulsion, flight control, etc.)
       the corresponding Load() method is called (e.g. FGFCS::Load()).

       Subsequent to the creation of the executive and loading of the model,
       initialization is performed. Initialization involves copying control
       inputs into the appropriate JSBSim data storage locations, configuring
       it for the set of user supplied initial conditions, and then copying
       state variables from JSBSim. The state variables are used to drive the
       instrument displays and to place the vehicle model in world space for
       visual rendering:

       .. code-block:: cpp

          copy_to_JSBsim(); // copy control inputs to JSBSim
          fdmex->RunIC(); // loop JSBSim once w/o integrating
          copy_from_JSBsim(); // update the bus

       Once initialization is complete, cyclic execution proceeds:

       .. code-block:: cpp

          copy_to_JSBsim(); // copy control inputs to JSBSim
          fdmex->Run(); // execute JSBSim
          copy_from_JSBsim(); // update the bus

       JSBSim can be used in a standalone mode by creating a compact stub
       program that effectively performs the same progression of steps as
       outlined above for the integrated version, but with two exceptions.
       First, the copy_to_JSBSim() and copy_from_JSBSim() functions are not
       used because the control inputs are handled directly by the scripting
       facilities and outputs are handled by the output (data logging) class.
       Second, the name of a script file can be supplied to the stub program.
       Scripting (see FGScript) provides a way to supply command inputs to the
       simulation:

       .. code-block:: cpp

          FDMExec = new JSBSim::FGFDMExec();
          FDMExec->LoadScript( ScriptName ); // the script loads the aircraft and ICs
          result = FDMExec->Run();
          while (result) { // cyclic execution
            result = FDMExec->Run(); // execute JSBSim
          }

       The standalone mode has been useful for verifying changes before
       committing updates to the source code repository. It is also useful for
       running sets of tests that reveal some aspects of simulated aircraft
       performance, such as range, time-to-climb, takeoff distance, etc.

       .. rubric:: JSBSim Debugging Directives

       This describes to any interested entity the debug level requested by
       setting the JSBSIM_DEBUG environment variable. The bitmasked value
       choices are as follows:

       * **unset**: In this case (the default) JSBSim would only print out the
         normally expected messages, essentially echoing the config files as
         they are read. If the environment variable is not set, debug_lvl is
         set to 1 internally
       * **0**: This requests JSBSim not to output any messages whatsoever
       * **1**: This value explicity requests the normal JSBSim startup
         messages
       * **2**: This value asks for a message to be printed out when a class is
         instantiated
       * **4**: When this value is set, a message is displayed when a FGModel
         object executes its Run() method
       * **8**: When this value is set, various runtime state variables are
         printed out periodically
       * **16**: When set various parameters are sanity checked and a message
         is printed out when they go out of bounds

       .. rubric:: Properties

       * **simulator/do_trim** (write only) Can be set to the integer
         equivalent to one of tLongitudinal (0), tFull (1), tGround (2),
         tPullup (3), tCustom (4), tTurn (5). Setting this to a legal value
         (such as by a script) causes a trim to be performed. This property
         actually maps toa function call of DoTrim()."""

    cdef c_FGFDMExec *thisptr      # hold a C++ instance which we're wrapping
    cdef dict properties_cache     # Dictionary cache of property nodes

    def __cinit__(self, root_dir, FGPropertyManager pm_root=None, *args,
                  **kwargs):
        cdef c_FGPropertyManager* root

        if pm_root:
            root = pm_root.thisptr.get()
        else:
            root = NULL

        self.thisptr = self.baseptr = new c_FGFDMExec(root, NULL)
        if self.thisptr is NULL:
            raise MemoryError()

        if root_dir:
            if not os.path.isdir(root_dir):
                raise IOError("Can't find root directory: {0}".format(root_dir))
            self.set_root_dir(root_dir)
            self.set_output_path(".")
        else:
            self.set_root_dir(get_default_root_dir())
            self.set_output_path(os.getcwd())

        self.set_engine_path("engine")
        self.set_aircraft_path("aircraft")
        self.set_systems_path("systems")

        self.properties_cache = { }

    def __dealloc__(self) -> None:
        del self.thisptr

    def __repr__(self) -> str:
        return "FGFDMExec \n" \
            "root dir\t:\t{0}\n" \
            "aircraft path\t:\t{1}\n" \
            "engine path\t:\t{2}\n" \
            "systems path\t:\t{3}\n" \
            "output path\t:\t{4}\n" \
                .format(
                self.get_root_dir(),
                self.get_aircraft_path(),
                self.get_engine_path(),
                self.get_systems_path(),
                self.get_output_path())

    def __getitem__(self, key: str) -> float:
        _key = key.strip()
        try:
            property_node = self.properties_cache[_key]
            return property_node.get_double_value()
        except KeyError:
            pm = self.get_property_manager()
            property_node = pm.get_node(_key)
            if property_node is not None:
                self.properties_cache[_key] = property_node
                return property_node.get_double_value()
            else:
                raise KeyError(f'No property named {_key}')

    def __setitem__(self, key: str, value: float) -> None:
        self.set_property_value(key.strip(), value)

    def run(self) -> bool:
        """This function executes each scheduled model in succession.

           :return: true if successful, false if sim should be ended"""
        return self.thisptr.Run()

    def run_ic(self) -> bool:
        """Initializes the sim from the initial condition object and executes each scheduled model without integrating i.e.

           dt=0.

           :return: true if successful"""
        return  self.thisptr.RunIC()

    def load_model(self, model: str, add_model_to_path: bool = True) -> bool:
        """Loads an aircraft model.

           The paths to the aircraft and engine config file directories must be
           set prior to calling this. See below.

           :param model: the name of the aircraft model itself. This file will
                         be looked for in the directory specified in the
                         AircraftPath variable, and in turn under the directory
                         with the same name as the model. For instance:
                         "aircraft/x15/x15.xml"
           :param addModelToPath: set to true to add the model name to the
                                  AircraftPath, defaults to true
           

           :return: true if successful"""
        return self.thisptr.LoadModel(model.encode(), add_model_to_path)

    def load_model_with_paths(self, model: str, aircraft_path: str,
                   engine_path: str, systems_path: str,
                   add_model_to_path: bool = True) -> bool:
        """Loads an aircraft model.

           :param AircraftPath: path to the aircraft/ directory. For instance:
                                "aircraft". Under aircraft, then, would be
                                directories for various modeled aircraft such
                                as C172/, x15/, etc.
           :param EnginePath: path to the directory under which engine config
                              files are kept, for instance "engine"
           :param SystemsPath: path to the directory under which systems config
                               files are kept, for instance "systems"
           :param model: the name of the aircraft model itself. This file will
                         be looked for in the directory specified in the
                         AircraftPath variable, and in turn under the directory
                         with the same name as the model. For instance:
                         "aircraft/x15/x15.xml"
           :param addModelToPath: set to true to add the model name to the
                                  AircraftPath, defaults to true
           

           :return: true if successful"""
        return self.thisptr.LoadModel(c_SGPath(aircraft_path.encode(), NULL),
                                      c_SGPath(engine_path.encode(), NULL),
                                      c_SGPath(systems_path.encode(), NULL),
                                      model.encode(), add_model_to_path)

    def load_script(self, script: str, delta_t: float = 0.0, initfile:str = "") -> bool:
        """Load a script.

           :param Script: The full path name and file name for the script to be
                          loaded.
           :param deltaT: The simulation integration step size, if given. If no
                          value is supplied then 0.0 is used and the value is
                          expected to be supplied in the script file itself.
           :param initfile: The initialization file that will override the
                            initialization file specified in the script file.
                            If no file name is given on the command line, the
                            file specified in the script will be used. If an
                            initialization file is not given in either place,
                            an error will result.
           

           :return: true if successfully loads; false otherwise."""
        scriptfile = os.path.join(self.get_root_dir(), script)
        if not os.path.exists(scriptfile):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT),
                                    scriptfile)
        return self.thisptr.LoadScript(c_SGPath(script.encode(), NULL), delta_t,
                                       c_SGPath(initfile.encode(),NULL))

    def load_planet(self, planet_path: str, useAircraftPath: bool) -> bool:
        """Loads the planet.

           Loads the definition of the planet on which the vehicle will evolve
           such as its radius, gravity or its atmosphere characteristics.

           :param PlanetPath: The name of a planet definition file
           :param useAircraftPath: true if path is given relative to the
                                   aircraft path.
           

           :return: true if successful"""
        planet_file = _append_xml(planet_path)
        if useAircraftPath and not os.path.isabs(planet_file):
            planet_file = os.path.join(self.get_full_aircraft_path(), planet_file)
        if not os.path.exists(planet_file):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT),
                                    planet_file)
        return self.thisptr.LoadPlanet(c_SGPath(planet_file.encode(), NULL),
                                       useAircraftPath)

    def set_engine_path(self, path: str) -> bool:
        """Set the path to the engine config file directories.

           Relative paths are taken from the root directory.

           :param path: path to the directory under which engine config files
                        are kept, for instance "engine". """
        return self.thisptr.SetEnginePath(c_SGPath(path.encode(), NULL))

    def set_aircraft_path(self, path: str) -> bool:
        """Set the path to the aircraft config file directories.

           Under this path, then, would be directories for various modeled
           aircraft such as C172/, x15/, etc. Relative paths are taken from the
           root directory.

           :param path: path to the aircraft directory, for instance
                        "aircraft"."""
        return self.thisptr.SetAircraftPath(c_SGPath(path.encode(), NULL))

    def set_systems_path(self, path: str) -> bool:
        """Set the path to the systems config file directories.

           Relative paths are taken from the root directory.

           :param path: path to the directory under which systems config files
                        are kept, for instance "systems" """
        return self.thisptr.SetSystemsPath(c_SGPath(path.encode(), NULL))

    def set_output_path(self, path: str) -> bool:
        """Set the directory where the output files will be written.

           Relative paths are taken from the root directory.

           :param path: path to the directory under which the output files will
                        be written. """
        return self.thisptr.SetOutputPath(c_SGPath(path.encode(), NULL))

    def set_root_dir(self, path: str) -> None:
        """Set the root directory that is used to obtain absolute paths from relative paths.

           Aircraft, engine, systems and output paths are not updated by this
           method. You must call each methods ( SetAircraftPath(),
           SetEnginePath(), etc.) individually if you need to update these
           paths as well.

           :param rootDir: the path to the root directory."""
        self.thisptr.SetRootDir(c_SGPath(path.encode(), NULL))

    def get_engine_path(self) -> str:
        """Retrieves the engine path."""
        return self.thisptr.GetEnginePath().utf8Str().decode('utf-8')

    def get_aircraft_path(self) -> str:
        """Retrieves the aircraft path."""
        return self.thisptr.GetAircraftPath().utf8Str().decode('utf-8')

    def get_systems_path(self) -> str:
        """Retrieves the systems path."""
        return self.thisptr.GetSystemsPath().utf8Str().decode('utf-8')

    def get_output_path(self) -> str:
        """Retrieves the path to the output files."""
        return self.thisptr.GetOutputPath().utf8Str().decode('utf-8')

    def get_full_aircraft_path(self) -> str:
        """Retrieves the full aircraft path name."""
        return self.thisptr.GetFullAircraftPath().utf8Str().decode('utf-8')

    def get_root_dir(self) -> str:
        """Retrieve the Root Directory.

           :return: the path to the root (base) JSBSim directory."""
        return self.thisptr.GetRootDir().utf8Str().decode('utf-8')

    def get_property_value(self, name: str) -> float:
        """Retrieves the value of a property.

           :param property: the name of the property
           

           :return: the value of the specified property """
        return self.thisptr.GetPropertyValue(name.encode())

    def set_property_value(self, name: str, value: float) -> None:
        """Sets a property value.

           :param property: the property to be set
           :param value: the value to set the property to"""
        self.thisptr.SetPropertyValue(name.encode(), value)

    def get_model_name(self) -> str:
        """Returns the model name."""
        return self.thisptr.GetModelName().decode()

    def set_output_directive(self, fname: str) -> bool:
        """Sets the output (logging) mechanism for this run.

           Calling this function passes the name of an output directives file
           to the FGOutput object associated with this run. The call to this
           function should be made prior to loading an aircraft model. This
           call results in an FGOutput object being built as the first Output
           object in the FDMExec-managed list of Output objects that may be
           created for an aircraft model. If this call is made after an
           aircraft model is loaded, there is no effect. Any Output objects
           added by the aircraft model itself (in an <output> element) will be
           added after this one. Care should be taken not to refer to the same
           file name. An output directives file contains an <output> </output>
           element, within which should be specified the parameters or
           parameter groups that should be logged.

           :param fname: the filename of an output directives file."""
        return self.thisptr.SetOutputDirectives(c_SGPath(fname.encode(), NULL))

    # def force_output(self, index: int) -> None:
    #     """Forces the specified output object to print its items once."""
    #     self.thisptr.ForceOutput(index)

    def set_logging_rate(self, rate: float) -> None:
        """Sets the logging rate in Hz for all output objects (if any)."""
        self.thisptr.SetLoggingRate(rate)

    def set_output_filename(self, n: int, fname: str) -> bool:
        """Sets (or overrides) the output filename.

           :param n: index of file
           :param fname: the name of the file to output data to
           

           :return: true if successful, false if there is no output specified
                    for the flight model"""
        return self.thisptr.SetOutputFileName(n, fname.encode())

    def get_output_filename(self, n: int) -> str:
        """Retrieves the current output filename.

           :param n: index of file
           

           :return: the name of the output file for the output specified by the
                    flight model. If none is specified, the empty string is
                    returned."""
        return self.thisptr.GetOutputFileName(n).decode()

    def do_trim(self, mode: int) -> None:
        """Executes trimming in the selected mode.

           :param mode: Specifies how to trim: * tLongitudinal=0 * tFull *
                        tGround * tPullup * tCustom * tTurn * tNone """
        self.thisptr.DoTrim(mode)

    def disable_output(self) -> None:
        """Disables data logging to all outputs."""
        self.thisptr.DisableOutput()

    def enable_output(self) -> None:
        """Enables data logging to all outputs."""
        self.thisptr.EnableOutput()

    def hold(self) -> None:
        """Pauses execution by preventing time from incrementing."""
        self.thisptr.Hold()

    def enable_increment_then_hold(self, time_steps: int) -> None:
        """Turn on hold after increment."""
        self.thisptr.EnableIncrementThenHold(time_steps)

    def check_incremental_hold(self) -> None:
        """Checks if required to hold afer increment."""
        self.thisptr.CheckIncrementalHold()

    def resume(self) -> None:
        """Resumes execution from a "Hold"."""
        self.thisptr.Resume()

    def holding(self) -> bool:
        """Returns true if the simulation is Holding (i.e. simulation time is not moving)."""
        return self.thisptr.Holding()

    def reset_to_initial_conditions(self, mode: int) -> None:
        """Resets the initial conditions object and prepares the simulation to run again.

           If the mode's first bit is set the output instances will take
           special actions such as closing the current output file and open a
           new one with a different name. If the second bit is set then RunIC()
           won't be executed, leaving it to the caller to call RunIC(), e.g. in
           case the caller wants to set some other state like control surface
           deflections which would've been reset.

           :param mode: Sets the reset mode."""
        self.thisptr.ResetToInitialConditions(mode)

    def set_debug_level(self, level: int) -> None:
        """Sets the debug level."""
        self.thisptr.SetDebugLevel(level)

    def query_property_catalog(self, check: str) -> str:
        """Retrieves property or properties matching the supplied string.

           A string is returned that contains a carriage return delimited list
           of all strings in the property catalog that matches the supplied
           check string.

           :param check: The string to search for in the property catalog.
           :param end_of_line: End of line (CR+LF if needed for Windows).
           

           :return: the carriage-return-delimited string containing all
                    matching strings in the catalog."""
        return (self.thisptr.QueryPropertyCatalog(check.encode())).decode('utf-8')

    def get_property_catalog(self) -> list[str]:
        """Retrieves the property catalog as a list."""
        return self.query_property_catalog('').rstrip().split('\n')

    def print_property_catalog(self) -> None:
        """
           .. note::

              This feature is not yet documented."""
        self.thisptr.PrintPropertyCatalog()

    def print_simulation_configuration(self) -> None:
        """
           .. note::

              This feature is not yet documented."""
        self.thisptr.PrintSimulationConfiguration()

    def set_trim_status(self, status: bool) -> None:
        """
           .. note::

              This feature is not yet documented."""
        self.thisptr.SetTrimStatus(status)

    def get_trim_status(self) -> bool:
        """
           .. note::

              This feature is not yet documented."""
        return self.thisptr.GetTrimStatus()

    def get_propulsion_tank_report(self) -> str:
        """
           .. note::

              This feature is not yet documented."""
        return self.thisptr.GetPropulsionTankReport().decode()

    def get_sim_time(self) -> float:
        """Returns the cumulative simulation time in seconds."""
        return self.thisptr.GetSimTime()

    def get_delta_t(self) -> float:
        """Returns the simulation delta T."""
        return self.thisptr.GetDeltaT()

    def suspend_integration(self) -> None:
        """Suspends the simulation and sets the delta T to zero."""
        self.thisptr.SuspendIntegration()

    def resume_integration(self) -> None:
        """Resumes the simulation by resetting delta T to the correct value."""
        self.thisptr.ResumeIntegration()

    def integration_suspended(self) -> bool:
        """Returns the simulation suspension state.

           :return: true if suspended, false if executing"""
        return self.thisptr.IntegrationSuspended()

    def set_sim_time(self, time: float) -> bool:
        """Sets the current sim time.

           :param cur_time: the current time
           

           :return: the current simulation time."""
        return self.thisptr.Setsim_time(time)

    def set_dt(self, dt: float) -> None:
        """Sets the integration time step for the simulation executive.

           :param delta_t: the time step in seconds."""
        self.thisptr.Setdt(dt)

    def incr_time(self) -> float:
        """Increments the simulation time if not in Holding mode.

           The Frame counter is also incremented.

           :return: the new simulation time."""
        return self.thisptr.IncrTime()

    def get_debug_level(self) -> int:
        """Retrieves the current debug level setting. """
        return self.thisptr.GetDebugLevel()

    def load_ic(self, rstfile: str, useAircraftPath: bool) -> bool:
        reset_file = _append_xml(rstfile)
        if useAircraftPath and not os.path.isabs(reset_file):
            reset_file = os.path.join(self.get_full_aircraft_path(), reset_file)
        if not os.path.exists(reset_file):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT),
                                    reset_file)
        return deref(self.thisptr.GetIC()).Load(c_SGPath(rstfile.encode(), NULL),
                                                useAircraftPath)

    def get_propagate(self) -> FGPropagate:
        """Returns the"""
        propagate = FGPropagate(None)
        propagate.thisptr = self.thisptr.GetPropagate()
        return propagate

    def get_property_manager(self) -> FGPropertyManager:
        """Returns a pointer to the property manager object."""
        pm = FGPropertyManager()
        pm.thisptr = self.thisptr.GetPropertyManager()
        return pm

    def get_ground_reactions(self) -> FGGroundReactions:
        """Returns the"""
        grndreact = FGGroundReactions(None)
        grndreact.thisptr = self.thisptr.GetGroundReactions()
        return grndreact

    def get_auxiliary(self) -> FGAuxiliary:
        """Returns the"""
        auxiliary = FGAuxiliary(None)
        auxiliary.thisptr = self.thisptr.GetAuxiliary()
        return auxiliary

    def get_aerodynamics(self) -> FGAerodynamics:
        """Returns the"""
        aerodynamics = FGAerodynamics(None)
        aerodynamics.thisptr = self.thisptr.GetAerodynamics()
        return aerodynamics

    def get_aircraft(self) -> FGAircraft:
        """Returns the"""
        aircraft = FGAircraft(None)
        aircraft.thisptr = self.thisptr.GetAircraft()
        return aircraft

    def get_mass_balance(self) -> FGMassBalance:
        """Returns the"""
        massbalance = FGMassBalance(None)
        massbalance.thisptr = self.thisptr.GetMassBalance()
        return massbalance

    def get_atmosphere(self) -> FGAtmosphere:
        """Returns the :ref:`FGAtmosphere` pointer."""
        atmosphere = FGAtmosphere()
        atmosphere.thisptr = self.thisptr.GetAtmosphere()
        return atmosphere

    def get_propulsion(self) -> FGPropulsion:
        """Returns the"""
        propulsion = FGPropulsion(None)
        propulsion.thisptr = self.thisptr.GetPropulsion()
        return propulsion
