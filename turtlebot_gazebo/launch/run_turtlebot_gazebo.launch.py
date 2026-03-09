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
    pkg_gazebo = get_package_share_directory('turtlebot_gazebo')
    worlds_path = os.path.join(pkg_gazebo, 'worlds')
    set_gz_resource_path = SetEnvironmentVariable(name='GZ_SIM_RESOURCE_PATH',value=worlds_path)

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
        default_value='hause.sdf',
        description='possible values: empty.sdf, hause.sdf, obstacles,sdf'
    )
    world_name = LaunchConfiguration('world_name')

    robot_type_arg = DeclareLaunchArgument(
        'robot_type',
        default_value='turtlebot3_burger',
        description='se puede seleccionar turtlebot3_burger, turtlebot3_waffle'
    )
    robot_type = LaunchConfiguration('robot_type')
    
    robot_type_name = PythonExpression(["'",robot_type,"' + '.urdf'"])


    # ============ Include the launch file for the robot description =======
    include_description = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare("turtlebot_description"),
                "launch",
                "turtlebot_description.launch.py"
            ])
        ),
        launch_arguments={"use_joint_state_gui": "false", "robot_file": robot_type_name}.items()
    )

    gazebo_launch = PathJoinSubstitution([
        FindPackageShare('ros_gz_sim'),
        'launch',
        'gz_sim.launch.py'
    ])

    pkg_gazebo      = FindPackageShare('turtlebot_gazebo')   
    world_sdf = PathJoinSubstitution([pkg_gazebo, 'worlds', world_name])


    gazebo_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gazebo_launch),
        launch_arguments={'gz_args': ['-r ', world_sdf] }.items()
        
    )

    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', robot_type,
            '-topic', 'robot_description',
            '-x', x_position_robot_spawn,
            '-y', y_position_robot_spawn,
            '-z', '0.01'
        ],
        output='screen'
    )

    bridge_file = PythonExpression([
    "'",
    robot_type,
    "'",
    " + '_bridge.yaml'"
])
    
    gz_bridge_params_path = PathJoinSubstitution([
    FindPackageShare('turtlebot_gazebo'),
    'config',
    bridge_file
])

    gz_bridge_node = Node(
    package='ros_gz_bridge',
    executable='parameter_bridge',
    arguments=[
        '--ros-args',
        '-p',
        ['config_file:=', gz_bridge_params_path]
    ],
    output='screen',
)


    ld = LaunchDescription()
    ld.add_action(set_gz_resource_path)
    ld.add_action(x_position_robot_spawn_arg)
    ld.add_action(y_position_robot_spawn_arg)
    ld.add_action(world_name_arg)
    ld.add_action(robot_type_arg)
    ld.add_action(gazebo_node)
    ld.add_action(include_description)
    ld.add_action(spawn_robot)
    ld.add_action(gz_bridge_node)
    return ld