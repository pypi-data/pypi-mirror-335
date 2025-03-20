"""
Trossen Arm Python Bindings
"""
from __future__ import annotations
import pybind11_stubgen.typing_ext
import typing
import typing_extensions
__all__ = ['EndEffectorProperties', 'IPMethod', 'JointCharacteristic', 'LinkProperties', 'Mode', 'Model', 'StandardEndEffector', 'TrossenArmDriver']
class EndEffectorProperties:
    """
    End effector properties
    """
    def __init__(self) -> None:
        ...
    @property
    def finger_left(self) -> LinkProperties:
        """
                Properties of the left finger link
        """
    @finger_left.setter
    def finger_left(self, arg0: LinkProperties) -> None:
        ...
    @property
    def finger_right(self) -> LinkProperties:
        """
                Properties of the right finger link
        """
    @finger_right.setter
    def finger_right(self, arg0: LinkProperties) -> None:
        ...
    @property
    def offset_finger_left(self) -> float:
        """
                Offset from the palm center to the left carriage center in m in home configuration
        """
    @offset_finger_left.setter
    def offset_finger_left(self, arg0: float) -> None:
        ...
    @property
    def offset_finger_right(self) -> float:
        """
                Offset from the palm center to the right carriage center in m in home configuration
        """
    @offset_finger_right.setter
    def offset_finger_right(self, arg0: float) -> None:
        ...
    @property
    def palm(self) -> LinkProperties:
        """
                Properties of the palm link
        """
    @palm.setter
    def palm(self, arg0: LinkProperties) -> None:
        ...
    @property
    def t_max_factor(self) -> float:
        """
                Scaling factor for the max gripper force
        
                Notes
                -----
                It must be within [0.0, 1.0], 0.0 for no force, 1.0 for max force in the specifications
        """
    @t_max_factor.setter
    def t_max_factor(self, arg0: float) -> None:
        ...
class IPMethod:
    """
    @brief IP methods
    
    Members:
    
      manual : Use the manual IP address specified in the configuration
    
      dhcp : Use the DHCP to obtain the IP address, if failed, use the default IP address
    """
    __members__: typing.ClassVar[dict[str, IPMethod]]  # value = {'manual': <IPMethod.manual: 0>, 'dhcp': <IPMethod.dhcp: 1>}
    dhcp: typing.ClassVar[IPMethod]  # value = <IPMethod.dhcp: 1>
    manual: typing.ClassVar[IPMethod]  # value = <IPMethod.manual: 0>
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class JointCharacteristic:
    """
    Joint characteristic
    """
    def __init__(self) -> None:
        ...
    @property
    def continuity_factor(self) -> float:
        """
                Scaling factor in 1 that scales the base continuity constraint
        
                Notes
                -----
                It must be within [1.0, 10.0]
        """
    @continuity_factor.setter
    def continuity_factor(self, arg0: float) -> None:
        ...
    @property
    def effort_correction(self) -> float:
        """
                Effort correction in motor effort unit / Nm or N
        
                Notes
                -----
                It must be within [0.5, 2.0]
        """
    @effort_correction.setter
    def effort_correction(self, arg0: float) -> None:
        ...
    @property
    def friction_constant_term(self) -> float:
        """
                Friction constant term in Nm for arm joints or N for the gripper joint
        """
    @friction_constant_term.setter
    def friction_constant_term(self, arg0: float) -> None:
        ...
    @property
    def friction_coulomb_coef(self) -> float:
        """
                Friction coulomb coef in Nm/Nm for arm joints or N/N for the gripper joint
        """
    @friction_coulomb_coef.setter
    def friction_coulomb_coef(self, arg0: float) -> None:
        ...
    @property
    def friction_transition_velocity(self) -> float:
        """
                Friction transition velocity in rad/s for arm joints or m/s for the gripper joint
        
                Notes
                -----
                It must be positive
        """
    @friction_transition_velocity.setter
    def friction_transition_velocity(self, arg0: float) -> None:
        ...
    @property
    def friction_viscous_coef(self) -> float:
        """
                Friction viscous coef in Nm/(rad/s) for arm joints or N/(m/s) for the gripper joint
        """
    @friction_viscous_coef.setter
    def friction_viscous_coef(self, arg0: float) -> None:
        ...
class LinkProperties:
    """
    Link properties
    """
    def __init__(self) -> None:
        ...
    @property
    def inertia(self) -> typing_extensions.Annotated[list[float], pybind11_stubgen.typing_ext.FixedSize(9)]:
        """
                Inertia in kg m^2
        """
    @inertia.setter
    def inertia(self, arg0: typing_extensions.Annotated[list[float], pybind11_stubgen.typing_ext.FixedSize(9)]) -> None:
        ...
    @property
    def mass(self) -> float:
        """
                Mass in kg
        """
    @mass.setter
    def mass(self, arg0: float) -> None:
        ...
    @property
    def origin_rpy(self) -> typing_extensions.Annotated[list[float], pybind11_stubgen.typing_ext.FixedSize(3)]:
        """
                Inertia frame RPY angles measured in link frame in rad
        """
    @origin_rpy.setter
    def origin_rpy(self, arg0: typing_extensions.Annotated[list[float], pybind11_stubgen.typing_ext.FixedSize(3)]) -> None:
        ...
    @property
    def origin_xyz(self) -> typing_extensions.Annotated[list[float], pybind11_stubgen.typing_ext.FixedSize(3)]:
        """
                Inertia frame translation measured in link frame in m
        """
    @origin_xyz.setter
    def origin_xyz(self, arg0: typing_extensions.Annotated[list[float], pybind11_stubgen.typing_ext.FixedSize(3)]) -> None:
        ...
class Mode:
    """
    Operation modes of a joint
    
    Members:
    
      idle : All joints are braked
    
      position : Control the joint to a desired position
    
      velocity : Control the joint to a desired velocity
    
      external_effort : Control the joint to a desired external effort
    """
    __members__: typing.ClassVar[dict[str, Mode]]  # value = {'idle': <Mode.idle: 0>, 'position': <Mode.position: 1>, 'velocity': <Mode.velocity: 2>, 'external_effort': <Mode.external_effort: 3>}
    external_effort: typing.ClassVar[Mode]  # value = <Mode.external_effort: 3>
    idle: typing.ClassVar[Mode]  # value = <Mode.idle: 0>
    position: typing.ClassVar[Mode]  # value = <Mode.position: 1>
    velocity: typing.ClassVar[Mode]  # value = <Mode.velocity: 2>
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class Model:
    """
    @brief Robot models
    
    Members:
    
      wxai_v0 : WXAI V0
    """
    __members__: typing.ClassVar[dict[str, Model]]  # value = {'wxai_v0': <Model.wxai_v0: 0>}
    wxai_v0: typing.ClassVar[Model]  # value = <Model.wxai_v0: 0>
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class StandardEndEffector:
    """
    End effector properties for the standard variants
    """
    wxai_v0_base: typing.ClassVar[EndEffectorProperties]  # value = <trossen_arm.trossen_arm.EndEffectorProperties object>
    wxai_v0_follower: typing.ClassVar[EndEffectorProperties]  # value = <trossen_arm.trossen_arm.EndEffectorProperties object>
    wxai_v0_leader: typing.ClassVar[EndEffectorProperties]  # value = <trossen_arm.trossen_arm.EndEffectorProperties object>
    def __init__(self) -> None:
        ...
class TrossenArmDriver:
    """
    Trossen Arm Driver
    """
    def __init__(self) -> None:
        ...
    def cleanup(self) -> None:
        """
                Cleanup the driver.
        """
    def configure(self, model: Model, end_effector: EndEffectorProperties, serv_ip: str, clear_error: bool) -> None:
        """
                Configure the driver.
        
                Parameters
                ----------
                model : Model
                    Model of the robot.
                end_effector : EndEffectorProperties
                    End effector properties.
                serv_ip : str
                    IP address of the robot.
                clear_error : bool
                    Whether to clear the error state of the robot.
        """
    def get_compensation_efforts(self) -> list[float]:
        """
                Get the compensation efforts.
        
                Returns
                -------
                list of float
                    Compensation efforts in Nm for arm joints and N for the gripper joint.
        """
    def get_continuity_factors(self) -> list[float]:
        """
                Get the continuity factors.
        
                Returns
                -------
                list of float
                    Continuity factors in 1 that scales the base continuity constraint.
        """
    def get_controller_version(self) -> str:
        """
                Get the controller firmware version.
        
                Returns
                -------
                str
                    Controller firmware version.
        """
    def get_dns(self) -> str:
        """
                Get the DNS.
        
                Returns
                -------
                str
                    DNS address.
        """
    def get_driver_version(self) -> str:
        """
                Get the driver version.
        
                Returns
                -------
                str
                    Driver version.
        """
    def get_effort_corrections(self) -> list[float]:
        """
                Get the effort corrections.
        
                Returns
                -------
                list of float
                    Effort corrections in motor effort unit / Nm or N.
        """
    def get_efforts(self) -> list[float]:
        """
                Get the efforts.
        
                Returns
                -------
                list of float
                    Efforts in Nm for arm joints and N for the gripper joint.
        """
    def get_end_effector(self) -> EndEffectorProperties:
        """
                Get the end effector mass properties.
        
                Returns
                -------
                EndEffectorProperties
                    The end effector mass property structure.
        """
    def get_error_information(self) -> str:
        """
                Get the error information of the robot.
        
                Returns
                -------
                str
                    Error information.
        """
    def get_external_efforts(self) -> list[float]:
        """
                Get the external efforts.
        
                Returns
                -------
                list of float
                    External efforts in Nm for arm joints and N for the gripper joint.
        """
    def get_factory_reset_flag(self) -> bool:
        """
                Get the factory reset flag.
        
                Returns
                -------
                bool
                    True if the configurations will be reset to factory defaults at the next startup, False otherwise.
        """
    def get_friction_constant_terms(self) -> list[float]:
        """
                Get the friction constant terms.
        
                Returns
                -------
                list of float
                    Friction constant terms in Nm for arm joints and N for the gripper joint.
        """
    def get_friction_coulomb_coefs(self) -> list[float]:
        """
                Get the friction coulomb coefs.
        
                Returns
                -------
                list of float
                    Friction coulomb coefs in Nm/Nm for arm joints and N/N for the gripper joint.
        """
    def get_friction_transition_velocities(self) -> list[float]:
        """
                Get the friction transition velocities.
        
                Returns
                -------
                list of float
                    Friction transition velocities in rad/s for arm joints and m/s for the gripper joint.
        """
    def get_friction_viscous_coefs(self) -> list[float]:
        """
                Get the friction viscous coefs.
        
                Returns
                -------
                list of float
                    Friction viscous coefs in Nm/(rad/s) for arm joints and N/(m/s) for the gripper joint.
        """
    def get_gateway(self) -> str:
        """
                Get the gateway.
        
                Returns
                -------
                str
                    Gateway address.
        """
    def get_gripper_force_limit_scaling_factor(self) -> float:
        """
                Get the gripper force limit scaling factor.
        
                Returns
                -------
                float
                    Scaling factor for the max gripper force, 0.0 for no force, 1.0 for max force in the specifications.
        """
    def get_ip_method(self) -> IPMethod:
        """
                Get the IP method.
        
                Returns
                -------
                IPMethod
                    IP method.
        """
    def get_joint_characteristics(self) -> list[JointCharacteristic]:
        """
                Get the joint characteristics.
        
                Returns
                -------
                list of JointCharacteristic
                    Joint characteristics.
        """
    def get_manual_ip(self) -> str:
        """
                Get the manual IP.
        
                Returns
                -------
                str
                    Manual IP address.
        """
    def get_modes(self) -> list[Mode]:
        """
                Get the modes.
        
                Returns
                -------
                list of Mode
                    Modes of all joints.
        """
    def get_num_joints(self) -> int:
        """
                Get the number of joints.
        
                Returns
                -------
                int
                    Number of joints.
        """
    def get_positions(self) -> list[float]:
        """
                Get the positions.
        
                Returns
                -------
                list of float
                    Positions in rad for arm joints and m for the gripper joint.
        """
    def get_subnet(self) -> str:
        """
                Get the subnet.
        
                Returns
                -------
                str
                    Subnet address.
        """
    def get_velocities(self) -> list[float]:
        """
                Get the velocities.
        
                Returns
                -------
                list of float
                    Velocities in rad/s for arm joints and m/s for the gripper joint.
        """
    def load_configs_from_file(self, file_path: str) -> None:
        """
                Load configurations from a YAML file and set them.
        
                Parameters
                ----------
                file_path : str
                    The file path to load the configurations.
        """
    def save_configs_to_file(self, file_path: str) -> None:
        """
                Save configurations to a YAML file.
        
                Parameters
                ----------
                file_path : str
                    The file path to store the configurations.
        """
    def set_all_external_efforts(self, goal_external_efforts: list[float], goal_time: float = 2.0, blocking: bool = True) -> None:
        """
                Set the external efforts of all joints.
        
                Parameters
                ----------
                goal_external_efforts : list of float
                    External efforts in Nm for arm joints and N for the gripper joint.
                goal_time : float, optional
                    Goal time in seconds when the goal external efforts should be reached, default is 2.0s.
                blocking : bool, optional
                    Whether to block until the goal external efforts are reached, default is true.
        
                Notes
                -----
                The size of the vectors should be equal to the number of joints.
        """
    def set_all_modes(self, mode: Mode = ...) -> None:
        """
                Set all joints to the same mode.
        
                Parameters
                ----------
                mode : Mode
                    Mode for all joints, one of
                    - Mode.idle
                    - Mode.position
                    - Mode.velocity
                    - Mode.external_effort
        """
    def set_all_positions(self, goal_positions: list[float], goal_time: float = 2.0, blocking: bool = True, goal_feedforward_velocities: list[float] | None = None, goal_feedforward_accelerations: list[float] | None = None) -> None:
        """
                Set the positions of all joints.
        
                Parameters
                ----------
                goal_positions : list of float
                    Positions in rad for arm joints and m for the gripper joint.
                goal_time : float, optional
                    Goal time in seconds when the goal positions should be reached, default is 2.0s.
                blocking : bool, optional
                    Whether to block until the goal positions are reached, default is true.
                goal_feedforward_velocities : list of float, optional
                    Feedforward velocities in rad/s for arm joints and m/s for the gripper joint, default is zeros.
                goal_feedforward_accelerations : list of float, optional
                    Feedforward accelerations in rad/s^2 for arm joints and m/s^2 for the gripper joint, default is zeros.
        
                Notes
                -----
                The size of the vectors should be equal to the number of joints.
        """
    def set_all_velocities(self, goal_velocities: list[float], goal_time: float = 2.0, blocking: bool = True, goal_feedforward_accelerations: list[float] | None = None) -> None:
        """
                Set the velocities of all joints.
        
                Parameters
                ----------
                goal_velocities : list of float
                    Velocities in rad/s for arm joints and m/s for the gripper joint.
                goal_time : float, optional
                    Goal time in seconds when the goal velocities should be reached, default is 2.0s.
                blocking : bool, optional
                    Whether to block until the goal velocities are reached, default is true.
                goal_feedforward_accelerations : list of float, optional
                    Feedforward accelerations in rad/s^2 for arm joints and m/s^2 for the gripper joint, default is zeros.
        
                Notes
                -----
                The size of the vectors should be equal to the number of joints.
        """
    def set_arm_external_efforts(self, goal_external_efforts: list[float], goal_time: float = 2.0, blocking: bool = True) -> None:
        """
                Set the external efforts of the arm joints.
        
                Parameters
                ----------
                goal_external_efforts : list of float
                    External efforts in Nm.
                goal_time : float, optional
                    Goal time in seconds when the goal external efforts should be reached, default is 2.0s.
                blocking : bool, optional
                    Whether to block until the goal external efforts are reached, default is true.
        
                Notes
                -----
                The size of the vectors should be equal to the number of arm joints.
        """
    def set_arm_modes(self, mode: Mode = ...) -> None:
        """
                Set the mode of the arm joints.
        
                Parameters
                ----------
                mode : Mode
                    Mode for the arm joints, one of
                    - Mode.idle
                    - Mode.position
                    - Mode.velocity
                    - Mode.external_effort
        
                Notes
                -----
                This method does not change the gripper joint's mode.
        """
    def set_arm_positions(self, goal_positions: list[float], goal_time: float = 2.0, blocking: bool = True, goal_feedforward_velocities: list[float] | None = None, goal_feedforward_accelerations: list[float] | None = None) -> None:
        """
                Set the positions of the arm joints.
        
                Parameters
                ----------
                goal_positions : list of float
                    Positions in rad.
                goal_time : float, optional
                    Goal time in seconds when the goal positions should be reached, default is 2.0s.
                blocking : bool, optional
                    Whether to block until the goal positions are reached, default is true.
                goal_feedforward_velocities : list of float, optional
                    Feedforward velocities in rad/s, default is zeros.
                goal_feedforward_accelerations : list of float, optional
                    Feedforward accelerations in rad/s^2, default is zeros.
        
                Notes
                -----
                The size of the vectors should be equal to the number of arm joints.
        """
    def set_arm_velocities(self, goal_velocities: list[float], goal_time: float = 2.0, blocking: bool = True, goal_feedforward_accelerations: list[float] | None = None) -> None:
        """
                Set the velocities of the arm joints.
        
                Parameters
                ----------
                goal_velocities : list of float
                    Velocities in rad.
                goal_time : float, optional
                    Goal time in seconds when the goal velocities should be reached, default is 2.0s.
                blocking : bool, optional
                    Whether to block until the goal velocities are reached, default is true.
                goal_feedforward_accelerations : list of float, optional
                    Feedforward accelerations in rad/s^2, default is zeros.
        
                Notes
                -----
                The size of the vectors should be equal to the number of arm joints.
        """
    def set_continuity_factors(self, continuity_factors: list[float]) -> None:
        """
                Set the continuity factors.
        
                Parameters
                ----------
                continuity_factors : list of float
                    Continuity factors in 1 that scales the base continuity constraint.
        
                Notes
                -----
                The size of the vector should be equal to the number of joints.
        
                Each element in the vector should be within the range [1.0, 10.0].
        """
    def set_dns(self, dns: str = '8.8.8.8') -> None:
        """
                Set the DNS.
        
                Parameters
                ----------
                dns : str
                    DNS address.
        """
    def set_effort_corrections(self, effort_corrections: list[float]) -> None:
        """
                Set the effort corrections.
        
                Parameters
                ----------
                effort_corrections : list of float
                    Effort corrections in motor effort unit / Nm or N.
        
                Notes
                -----
                This configuration is used to map the efforts in Nm or N to the motor effort unit, i.e., effort_correction = motor effort unit / Nm or N.
        
                The size of the vector should be equal to the number of joints.
        
                Each element in the vector should be within the range [0.5, 2.0].
        """
    def set_end_effector(self, end_effector: EndEffectorProperties) -> None:
        """
                Set the end effector properties.
        
                Parameters
                ----------
                end_effector : EndEffectorProperties
                    The end effector properties.
        """
    def set_factory_reset_flag(self, flag: bool = True) -> None:
        """
                Set the factory reset flag.
        
                Parameters
                ----------
                flag : bool
                    Whether to reset the configurations to factory defaults at the next startup.
        """
    def set_friction_constant_terms(self, friction_constant_terms: list[float]) -> None:
        """
                Set the friction constant terms.
        
                Parameters
                ----------
                friction_constant_terms : list of float
                    Friction constant terms in Nm for arm joints and N for the gripper joint.
        
                Notes
                -----
                The size of the vector should be equal to the number of joints.
        """
    def set_friction_coulomb_coefs(self, friction_coulomb_coefs: list[float]) -> None:
        """
                Set the friction coulomb coefs.
        
                Parameters
                ----------
                friction_coulomb_coefs : list of float
                    Friction coulomb coefs in Nm/Nm for arm joints and N/N for the gripper joint.
        
                Notes
                -----
                The size of the vector should be equal to the number of joints.
        """
    def set_friction_transition_velocities(self, friction_transition_velocities: list[float]) -> None:
        """
                Set the friction transition velocities.
        
                Parameters
                ----------
                friction_transition_velocities : list of float
                    Friction transition velocities in rad/s for arm joints and m/s for the gripper joint.
        
                Notes
                -----
                The size of the vector should be equal to the number of joints.
        
                Each element in the vector should be positive.
        """
    def set_friction_viscous_coefs(self, friction_viscous_coefs: list[float]) -> None:
        """
                Set the friction viscous coefs.
        
                Parameters
                ----------
                friction_viscous_coefs : list of float
                    Friction viscous coefs in Nm/(rad/s) for arm joints and N/(m/s) for the gripper joint.
        
                Notes
                -----
                The size of the vector should be equal to the number of joints.
        """
    def set_gateway(self, gateway: str = '192.168.1.1') -> None:
        """
                Set the gateway.
        
                Parameters
                ----------
                gateway : str
                    Gateway address.
        """
    def set_gripper_external_effort(self, goal_external_effort: float, goal_time: float = 2.0, blocking: bool = True) -> None:
        """
                Set the external effort of the gripper.
        
                Parameters
                ----------
                goal_external_effort : float
                    External effort in N.
                goal_time : float, optional
                    Goal time in seconds when the goal external effort should be reached, default is 2.0s.
                blocking : bool, optional
                    Whether to block until the goal external effort is reached, default is true.
        """
    def set_gripper_force_limit_scaling_factor(self, scaling_factor: float = 0.5) -> None:
        """
                Set the gripper force limit scaling factor.
        
                Parameters
                ----------
                scaling_factor : float
                    Scaling factor for the max gripper force.
        
                Notes
                -----
                It must be within [0.0, 1.0], 0.0 for no force, 1.0 for max force in the specifications.
        """
    def set_gripper_mode(self, mode: Mode = ...) -> None:
        """
                Set the mode of the gripper joint.
        
                Parameters
                ----------
                mode : Mode
                    Mode for the gripper joint, one of
                    - Mode.idle
                    - Mode.position
                    - Mode.velocity
                    - Mode.external_effort
        
                Notes
                -----
                This method does not change the arm joints' mode.
        """
    def set_gripper_position(self, goal_position: float, goal_time: float = 2.0, blocking: bool = True, goal_feedforward_velocity: float = 0.0, goal_feedforward_acceleration: float = 0.0) -> None:
        """
                Set the position of the gripper.
        
                Parameters
                ----------
                goal_position : float
                    Position in meters.
                goal_time : float, optional
                    Goal time in seconds when the goal position should be reached, default is 2.0s.
                blocking : bool, optional
                    Whether to block until the goal position is reached, default is true.
                goal_feedforward_velocity : float, optional
                    Feedforward velocity in m/s, default is zero.
                goal_feedforward_acceleration : float, optional
                    Feedforward acceleration in m/s^2, default is zero.
        """
    def set_gripper_velocity(self, goal_velocity: float, goal_time: float = 2.0, blocking: bool = True, goal_feedforward_acceleration: float = 0.0) -> None:
        """
                Set the velocity of the gripper.
        
                Parameters
                ----------
                goal_velocity : float
                    Velocity in m/s.
                goal_time : float, optional
                    Goal time in seconds when the goal velocity should be reached, default is 2.0s.
                blocking : bool, optional
                    Whether to block until the goal velocity is reached, default is true.
                goal_feedforward_acceleration : float, optional
                    Feedforward acceleration in m/s^2, default is zero.
        """
    def set_ip_method(self, method: IPMethod = ...) -> None:
        """
                Set the IP method.
        
                Parameters
                ----------
                method : IPMethod
                    The IP method to set, one of IPMethod.manual or IPMethod.dhcp.
        """
    def set_joint_characteristics(self, joint_characteristics: list[JointCharacteristic]) -> None:
        """
                Set the joint characteristics.
        
                Parameters
                ----------
                joint_characteristics : list of JointCharacteristic
                    Joint characteristics.
        
                Notes
                -----
                The size of the vector should be equal to the number of joints.
        
                Some joint characteristics are required to be within the following ranges:
                - effort_correction: [0.5, 2.0]
                - friction_transition_velocity: positive
                - continuity_factor: [1.0, 10.0]
        """
    def set_joint_external_effort(self, joint_index: int, goal_external_effort: float, goal_time: float = 2.0, blocking: bool = True) -> None:
        """
                Set the external effort of a joint.
        
                Parameters
                ----------
                joint_index : int
                    The index of the joint in [0, num_joints - 1].
                goal_external_effort : float
                    External effort in Nm for arm joints and N for the gripper joint.
                goal_time : float, optional
                    Goal time in seconds when the goal external effort should be reached, default is 2.0s.
                blocking : bool, optional
                    Whether to block until the goal external effort is reached, default is true.
        """
    def set_joint_modes(self, modes: list[Mode]) -> None:
        """
                Set the modes of each joint.
        
                Parameters
                ----------
                modes : list of Mode
                    Desired modes for each joint, one of
                    - Mode.idle
                    - Mode.position
                    - Mode.velocity
                    - Mode.external_effort
        
                Notes
                -----
                The size of the vector should be equal to the number of joints.
        """
    def set_joint_position(self, joint_index: int, goal_position: float, goal_time: float = 2.0, blocking: bool = True, goal_feedforward_velocity: float = 0.0, goal_feedforward_acceleration: float = 0.0) -> None:
        """
                Set the position of a joint.
        
                Parameters
                ----------
                joint_index : int
                    The index of the joint in [0, num_joints - 1].
                goal_position : float
                    Position in rad for arm joints and m for the gripper joint.
                goal_time : float, optional
                    Goal time in seconds when the goal position should be reached, default is 2.0s.
                blocking : bool, optional
                    Whether to block until the goal position is reached, default is true.
                goal_feedforward_velocity : float, optional
                    Feedforward velocity in rad/s for arm joints and m/s for the gripper joint, default is zero.
                goal_feedforward_acceleration : float, optional
                    Feedforward acceleration in rad/s^2 for arm joints and m/s^2 for the gripper joint, default is zero.
        """
    def set_joint_velocity(self, joint_index: int, goal_velocity: float, goal_time: float = 2.0, blocking: bool = True, goal_feedforward_acceleration: float = 0.0) -> None:
        """
                Set the velocity of a joint.
        
                Parameters
                ----------
                joint_index : int
                    The index of the joint in [0, num_joints - 1].
                goal_velocity : float
                    Velocity in rad/s for arm joints and m/s for the gripper joint.
                goal_time : float, optional
                    Goal time in seconds when the goal velocity should be reached, default is 2.0s.
                blocking : bool, optional
                    Whether to block until the goal velocity is reached, default is true.
                goal_feedforward_acceleration : float, optional
                    Feedforward acceleration in rad/s^2 for arm joints and m/s^2 for the gripper joint, default is zero.
        """
    def set_manual_ip(self, manual_ip: str = '192.168.1.2') -> None:
        """
                Set the manual IP.
        
                Parameters
                ----------
                manual_ip : str
                    Manual IP address.
        """
    def set_subnet(self, subnet: str = '255.255.255.0') -> None:
        """
                Set the subnet.
        
                Parameters
                ----------
                subnet : str
                    Subnet address.
        """
