# RoboKart ControllerLib

This is the Android library for the RoboKart controllers, which interfaces with the network using Zenoh. It is used as a platform library in the DriverStation Unity project, which handles the graphics and UI of the controller.

## Building

- Import the ControllerLib folder with Android Studio, and complete a Gradle sync.
- In the Gradle tab, under "ControllerLib/controllerlib/Tasks/build", run the "build" task.
- The resulting output AAR file will generate under "ControllerLib/controllerlib/build/outputs/aar".
- Copy the "controllerlib-release.aar" file into the Unity project.

## ControllerLib Testing

- To test ControllerLib without importing into Unity, use the "controllerlibtesting" app.
- Build the whole project, then use the "ControllerLib/controllerlibtesting/Tasks/install/installDebug" task to install to a connected device.