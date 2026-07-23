const adjectives = [
  "Active", "Atomic", "Auto", "Binary", "Bionic", "Bound", "Chrome", 
  "Cyber", "Damped", "Data", "Digital", "Direct", "Dual", "Dynamic", 
  "Electric", "Fast", "Fused", "Giga", "Global", "Heavy", "Holo", 
  "Hybrid", "Hyper", "Ion", "Kinetic", "Laminar", "Linear", "Linked", 
  "Logic", "Manual", "Mapped", "Matrix", "Meg", "Metric", "Mobile", 
  "Nano", "Neural", "Neon", "Optic", "Phasic", "Power", "Pulse", 
  "Quantum", "Quartz", "Remote", "Robust", "Serial", "Signal", "Solid", 
  "Stable", "Static", "Stored", "Synced", "System", "Thermal", "Torque", 
  "Torsional", "Twin", "Vector", "Virtual", "Warp", "Zero"]

const nouns = [
  "Apex", "Array", "Axle", "Beacon", "Bearing", "Block", "Brake", 
  "Buffer", "Bypass", "Camber", "Camshaft", "Chassis", "Circuit", "Clutch", 
  "Conduit", "Core", "Crank", "Cyber", "Damper", "Draft", "Drift", 
  "Driver", "Engine", "Exhaust", "Finish", "Flap", "Flywheel", "Frame", 
  "Gasket", "Gearbox", "Grid", "Impeller", "Injector", "Intake", "Lap", 
  "Linkage", "Manifold", "Matrix", "Module", "Motor", "Node", "Piston", 
  "Podium", "Pole", "Plexus", "Probe", "Racer", "Radiator", "Rotor", 
  "Sector", "Sensor", "Servo", "Shift", "Slick", "Spoiler", "Sprint", 
  "Sprocket", "Stator", "Stroke", "Strut", "Subframe", "Throttle", "Tire", 
  "Torque", "Turbine", "Turbo", "Valve", "Vortex"
]
export default function () {

    const noun = nouns[Math.floor(Math.random() * nouns.length)]
    const adjective = adjectives[Math.floor(Math.random() * adjectives.length)]

    return `${adjective}${noun}${1000 + Math.floor(Math.random() * 8999)}`

}