from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.conditions import IfCondition


def generate_launch_description():

     # Arguments: this is for ROS2 to use Gazebo time, important in simulation
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
    )
    use_sim_time = LaunchConfiguration('use_sim_time')

    use_joint_state_gui_arg = DeclareLaunchArgument(
    'use_joint_state_gui',
    default_value='true'
    )
    use_joint_state_gui = LaunchConfiguration('use_joint_state_gui')

    turtlebot_config_arg = DeclareLaunchArgument(
        'robot_file',
        default_value='turtlebot3_waffle.urdf',
        description='se puede seleccionar turtlebot3_burger, turtlebot3_waffle'
    )
    turtlebot_config  = LaunchConfiguration('robot_file')


    robot_description_pkg = FindPackageShare('turtlebot_description')

    rviz_config_path = PathJoinSubstitution([
        robot_description_pkg,
        'rviz',
        'model.rviz'   
    ])

    # This is the path of our xacro file
    robot_model_path = PathJoinSubstitution([
        robot_description_pkg,
        'urdf',
        turtlebot_config   # <-- this is my xacro file
    ])

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'robot_description': Command(['xacro ', robot_model_path])
        }]
    )

 

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_path]
    )

    joint_state_gui = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
        output="screen",
        condition=IfCondition(use_joint_state_gui)
    )

    ld = LaunchDescription()
    ld.add_action(use_sim_time_arg)
    ld.add_action(turtlebot_config_arg)
    ld.add_action(robot_state_publisher_node)
    ld.add_action(use_joint_state_gui_arg)
    ld.add_action(joint_state_gui)
    ld.add_action(rviz_node)

    return ld
    