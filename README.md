# Racing Sparrow 750 Robot Model

A robot model based on designer Bryn Heveldt's Racing Sparrow 750 yacht
[http://www.racingsparrow.co.nz/](http://www.racingsparrow.co.nz/).

![rs750_ardupilot_4](https://user-images.githubusercontent.com/24916364/226215397-ec2c1114-83fd-438d-a900-f2bb5d42765a.jpg)

## Overview

These packages contain a robot model based upon the Racing Sparrow 750
model yacht. They include a robot model that may be simulated in Gazebo
using the plugins from the [`asv_sim`](https://github.com/srmainwaring/asv_sim)
and [`asv_wave_sim`](https://github.com/srmainwaring/asv_wave_sim) projects.
The model has been scaled by a factor of 3.2 to have a
simulated LOA of approx. 2.4m.

This repository is a fork of Rhys Mainwaring's original Racing Sparrow 750 simulation, found [here](https://github.com/srmainwaring/rs750).  It is being modified to support the Green Energy Ship project, adding Gazebo plugins to simulate a hydrokinetic turbine and additional control logic to support mission-level simulation.

## Dependencies

You will need a working installation of
[Gazebo Garden](https://gazebosim.org/docs/garden/install) in order to use
this package. There is no dependency on ROS. The original version of this
project archived in the branch
[gazebo11](https://github.com/srmainwaring/rs750/tree/gazebo11) depends on
ROS Melodic. 

The model uses plugins from the marine simulation libraries
[`asv_sim`](https://github.com/srmainwaring/asv_sim) and
[`asv_wave_sim`](https://github.com/srmainwaring/asv_wave_sim),
and is controlled using ArduPilot which requires the
[`ardupilot_gazebo`](https://github.com/ArduPilot/ardupilot_gazebo) plugin.

You will need a working installation of [ArduPilot](https://ardupilot.org/dev/docs/building-setup-linux.html) on your system to control the sailboat.

## Installation

Create and configure a colcon workspace, clone and build the repo:

```bash
mkdir -p ~/gz_ws/src

# Install repo dependencies
sudo apt update
sudo apt install libgz-sim7-dev rapidjson-dev libcgal-dev libfftw3-dev

# Clone dependencies
cd ~/gz_ws/src
git clone https://github.com/srmainwaring/asv_sim.git
git clone https://github.com/srmainwaring/asv_wave_sim.git
git clone https://github.com/ArduPilot/ardupilot_gazebo.git

# Clone this repo
git clone https://github.com/j-herman/rs750.git

# Build
cd ~/gz_ws
colcon build --symlink-install --merge-install --cmake-args \
-DCMAKE_BUILD_TYPE=RelWithDebInfo \
-DBUILD_TESTING=ON \
-DCMAKE_CXX_STANDARD=17

# Build the ArduPilot plugin
cd ~/gz_ws/ardupilot_gazebo
mkdir build && cd build
cmake ..
make

# Source the workspace
cd ~/gz_ws
source install/setup.bash

# From your root workspace directory, add resources to the path
export GZ_SIM_RESOURCE_PATH=$GZ_SIM_RESOURCE_PATH:\
$(pwd)/src/rs750/rs750_gazebo/models:\
$(pwd)/src/rs750/rs750_gazebo/worlds:\
$(pwd)/src/asv_wave_sim/gz-waves-models/models:\
$(pwd)/src/asv_wave_sim/gz-waves-models/world_models:\
$(pwd)/src/asv_wave_sim/gz-waves-models/worlds:\
$(pwd)/src/ardupilot_gazebo/models:\
$(pwd)/src/ardupilot_gazebo/worlds

# Add libraries to the plugin path
export GZ_SIM_SYSTEM_PLUGIN_PATH=$GZ_SIM_SYSTEM_PLUGIN_PATH:\
$(pwd)/install/lib:\
$(pwd)/src/ardupilot_gazebo/build

# Check the Gazebo environment variables
printenv | grep GZ
```

## Usage

### Method 1: Control RS750 with ArduPilot

#### Run Gazebo

```bash
gz sim -v4 -r sailing_course_ges.sdf
```

#### Run ArduPilot SITL

```bash
sim_vehicle.py -D -v Rover -f rover --model JSON --add-param-file=~/gz_ws/src/rs750/rs750_gazebo/config/rs750.param --console
```

### Method 2: Control RS750 with ROS2

```bash
ros2 launch rs750_ros rs750.launch.py
```
Sails will autotrim.  To steer, publish to the /cmd_vel topic.  Only the angular z component will affect the RS750's motion through the rudder joint position controller.
Example:
`ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: -1.0}}"`

### Usage notes
To pause charging from the command line:
```
gz topic -t "/ges_connect_topic" -m gz.msgs.Boolean -p "data: true"
```
To manually adjust the axial induction factor from the command line:
```
gz topic -t "/ges/zeta" -m gz.msgs.Float -p "data: 0.6"
```

## License

This is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This software is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
[GNU General Public License](LICENSE) for more details.

## Acknowledgments

The Racing Sparrow 750 was designed by Bryn Heveldt and is used here with
his kind permission.
The model plans and original 3D CAD files are available at:
[Racing Sparrow Model RC Yachts](http://www.racingsparrow.co.nz/theboat/).

