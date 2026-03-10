import os
import xacro
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription, TimerAction
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PythonExpression,TextSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory
from launch.actions import SetEnvironmentVariable


def generate_launch_description():
    
    #configuration arguments: position where the robot must be spawned
    x_position_robot_spawn_arg = DeclareLaunchArgument(
        'x_spawn',
        default_value='0.5',
    )
    x_position_robot_spawn = LaunchConfiguration('x_spawn')

    y_position_robot_spawn_arg = DeclareLaunchArgument(
        'y_spawn',
        default_value='0.5',
    )
    y_position_robot_spawn = LaunchConfiguration('y_spawn')

    #configuration arguments: world name
    world_name_arg = DeclareLaunchArgument(
        'world_name',
        default_value='empty.sdf',
        description='possible values: empty.sdf'
    )
    world_name = LaunchConfiguration('world_name')

    control_type_arg = DeclareLaunchArgument(
        'controller_type',
        default_value='position_control',
        description='possible values: position_control, velocity_control'
    )
    control_type = LaunchConfiguration('controller_type')


    # ============ Include the launch file for the robot description =======
    include_description = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare("ur5_description"),
                "launch",
                "ur5_description.launch.py"
            ])
        ),
        launch_arguments={"use_joint_state_gui": "false","controller": control_type}.items()
    )

    gazebo_launch = PathJoinSubstitution([
        FindPackageShare('ros_gz_sim'),
        'launch',
        'gz_sim.launch.py'
    ])

    pkg_gazebo      = FindPackageShare('ur5_gazebo')   
    world_sdf = PathJoinSubstitution([pkg_gazebo, 'worlds', world_name])


    gazebo_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gazebo_launch),
        launch_arguments={'gz_args': ['-r ', world_sdf] }.items()
        
    )

    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'ur5',
            '-topic', 'robot_description',
            '-x', x_position_robot_spawn,
            '-y', y_position_robot_spawn,
            '-z', '0.01'
        ],
        output='screen'
    )


    
    gz_bridge_params_path = os.path.join(
        get_package_share_directory('ur5_gazebo'),
        'config',
        'arm_bridge.yaml'
    )

    gz_bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '--ros-args', '-p',
            f'config_file:={gz_bridge_params_path}'
        ],    
        output='screen',
     
    )

    joint_state_broadcaster_spawner = Node(
    package='controller_manager',
    executable='spawner',
    arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
    parameters=[{'use_sim_time': True}],
    output='screen',
)

    arm_position_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[control_type, '--controller-manager', '/controller_manager'],
        parameters=[{'use_sim_time': True}],
        output='screen',
    )

    spawn_controllers = TimerAction(
        period=3.0,
        actions=[
            joint_state_broadcaster_spawner,
            arm_position_controller_spawner,
        ]
    )


    ld = LaunchDescription()
    ld.add_action(control_type_arg)
    ld.add_action(x_position_robot_spawn_arg)
    ld.add_action(y_position_robot_spawn_arg)
    ld.add_action(world_name_arg)
    ld.add_action(gazebo_node)
    ld.add_action(include_description)
    ld.add_action(spawn_robot)
    ld.add_action(gz_bridge_node)
    ld.add_action(spawn_controllers)
    return ld