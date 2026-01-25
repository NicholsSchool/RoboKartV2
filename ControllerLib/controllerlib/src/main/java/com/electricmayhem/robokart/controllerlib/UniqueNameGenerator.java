package com.electricmayhem.robokart.controllerlib;

import java.util.Random;

public class UniqueNameGenerator {

    private static final String[] adjectives = new String[] {"Digital", "Virtual", "Binary", "Atomic", "Cyber", "Logic", "Neural", "Turbo", "Static", "Active", "Mobile", "Remote", "Linked", "Stored", "Mapped", "Linear", "Metric", "Global", "Serial", "Damped", "Stable", "Optic", "Signal", "Vector", "Quartz", "Robust", "Direct", "Synced", "Manual", "Kinetic", "Hybrid", "System"};
    private static final String[] nouns = new String[]{"Apex", "Circuit", "Piston", "Driver", "Camber", "Torque", "Slick", "Chassis", "Clutch", "Gearbox", "Draft", "Spoiler", "Turbo", "Lap", "Sprint", "Pole", "Podium", "Grid", "Finish", "Sector", "Tire", "Brake", "Motor", "Valve", "Racer", "Drift", "Shift", "Crank", "Damper", "Stroke", "Flap", "Intake"};

    public static String generate() {
        Random rand = new Random();

        String adjective = adjectives[rand.nextInt(adjectives.length)];
        String noun = nouns[rand.nextInt(nouns.length)];
        int number = rand.nextInt(9000) + 1000;

        return adjective + "-" + noun + "-" + number;
    }

}
