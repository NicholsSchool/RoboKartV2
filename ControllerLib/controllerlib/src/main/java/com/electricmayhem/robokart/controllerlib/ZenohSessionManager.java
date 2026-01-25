package com.electricmayhem.robokart.controllerlib;

import android.content.Context;
import android.os.BatteryManager;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.net.DatagramPacket;
import java.net.InetAddress;
import java.net.MulticastSocket;
import java.net.NetworkInterface;
import java.net.SocketException;
import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Enumeration;
import java.util.Optional;
import java.util.logging.Logger;

import io.zenoh.Config;
import io.zenoh.Session;
import io.zenoh.Zenoh;
import io.zenoh.exceptions.ZError;
import io.zenoh.keyexpr.KeyExpr;
import io.zenoh.pubsub.Publisher;

public class ZenohSessionManager {

    static Logger LOGGER = Logger.getLogger("ZenohSessionManager");

    private static NetworkInterface netInterface;

    private static String connectionInfo = "";
    private static String controllerName = "";

    private static Session session;
    private static final JSONObject heartbeatData = new JSONObject();
    private static Publisher inputPublisher;
    private static Publisher heartbeatPublisher;

    private static boolean initSuccess = false;
    private static String initFailReason = "Unknown Error.";

    public static void initializeSession(Context context, String controllerName) {

        //Check if Session already exists
        if (initSuccess) {
            LOGGER.warning("Call to initializeSession after Session already initialized.");
            return;
        }

        ZenohSessionManager.controllerName = controllerName;

        //Find WLAN interface (for Config and UDP test)
        try {
            ArrayList<NetworkInterface> interfaces = Collections.list(NetworkInterface.getNetworkInterfaces());

            LOGGER.info("Found interfaces: " + interfaces);
            for (NetworkInterface iface : interfaces) {
                LOGGER.info("Testing interface: " + iface);
                if (iface.isUp() && !iface.isLoopback() && iface.getName().startsWith("wlan")) {
                    netInterface = iface;
                    LOGGER.info("Using interface: " + netInterface.getName());
                    break;
                }
            }

            if (netInterface == null) {
                LOGGER.severe("No WLAN interface found. Using fallback wlan0 in Zenoh config.");
                initFailReason = "No WLAN interface found.";
                return;
            }

        } catch (SocketException e) {
            LOGGER.severe("SocketException occured while finding WLAN interface: \n" + e.getMessage());
            initFailReason = "Could not find WLAN interface.";
            return;
        } catch (Exception e) {
            LOGGER.severe("Unknown exception occured while finding WLAN interface: \n" + e.getMessage());
            initFailReason = "Could not find WLAN interface.";
            return;
        }

        //Define Config for scouting and receive, adding interface name.
        Config config;
        try {
            config = Config.fromJson("""
            {
                "mode": "peer",
                "listen": {
                    "endpoints": {
                        "peer": ["udp/0.0.0.0:7447"]
                    }
                },
                "scouting": {
                    "multicast": {
                        "enabled": true,
                        "address": "224.0.0.225:7446",
                    },
                    "gossip": {
                        "enabled": true,
                        "multihop": true
                    }
                }
            }
        """);
            config.insertJson5("scouting/multicast/interface", "\"" + netInterface.getName() + "\"");
        } catch (ZError e) {
            LOGGER.severe("Failed to configure Zenoh session: \n" + e.getMessage());
            initFailReason = "Zenoh config failed.";
            return;
        }

        try {
            heartbeatData.put("battery", 0);
        } catch (JSONException e) {
            LOGGER.warning("JSONException while populating heartbeatData.");
        }

        //Actually opening the session :P
        try {
            session = Zenoh.open(config);
        } catch (ZError e) {
            LOGGER.severe("Failed to open Zenoh session with error: " + e.getMessage());
            initFailReason = "Failed to open session - check logs.";
            return;
        }

        //Publishers
        try {
            inputPublisher = session.declarePublisher(KeyExpr.tryFrom("Controller/" + controllerName + "/Input"));
            heartbeatPublisher = session.declarePublisher(KeyExpr.tryFrom("Controller/" + controllerName + "/Heartbeat"));
        } catch (ZError e) {
            LOGGER.severe("Failed to register Zenoh publishers.");
            initFailReason = "Failed to register publishers.";
            session.close();
            return;
        }

        //Run these outside of thread once, to make sure we have data on init.
        heartbeatActions(context);

        initSuccess = true;

        //Publish new heartbeat data every half-second, and update connection info.
        Thread heartbeatThread = new Thread(() -> {
        while (true) {

            heartbeatActions(context);

            try { Thread.sleep(500); } catch (InterruptedException e) { LOGGER.warning("Heartbeat Thread Interrupted."); }
        }
    });

        heartbeatThread.setDaemon(true);
        heartbeatThread.start();

    }

    private static void heartbeatActions(Context context) {
        BatteryManager bm = (BatteryManager) context.getSystemService(Context.BATTERY_SERVICE);
        try {
            heartbeatData.put("battery", bm.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY));
            heartbeatPublisher.put(heartbeatData.toString());
        } catch (ZError e) {
            LOGGER.warning("Failed to publish Heartbeat.");
        } catch (JSONException e) {
            LOGGER.warning("JSONException while updating battery info.");
        }
        connectionInfo = new StringBuilder()
                .append(controllerName)
                .append(" IP: ")
                .append(netInterface.getName())
                .append(netInterface.getInterfaceAddresses().get(netInterface.getInterfaceAddresses().size() - 1).toString())
                .append(" PEERS: ").append(Optional.<String>empty().orElseGet(() -> {try {return Integer.toString(session.info().peersZid().size());} catch (ZError e) {return "NULL";}}))
                .toString();
    }

    public static boolean initSuccessful() { return initSuccess; }

    public static String getConnInfoOrFailReason() { return initSuccess ? connectionInfo : initFailReason; }

    public static void stopSession() {
        session.close();
    }

    public static void sendInput(double turn, double strafe, boolean forward, boolean backward) {

        if (!initSuccess) {
            return;
        }

        try {
            JSONObject inputData = new JSONObject()
                    .put("turn", turn)
                    .put("strafe", strafe)
                    .put("forward", forward)
                    .put("backward", backward);
            inputPublisher.put(inputData.toString());
        } catch (JSONException e) {
            LOGGER.severe("Failed to create input JSONObject.");
        } catch (ZError e) {
            LOGGER.severe("Failed to publish input on Zenoh.");
        }
    }

    public static void testUDP() {
        Thread networkThread = new Thread(() -> {
            if (!initSuccess) {
                LOGGER.info("UDP test failed: Session not initialized.");
                return;
            }
            try {
                var socket = new MulticastSocket();
                socket.setNetworkInterface(netInterface);

                InetAddress group = InetAddress.getByName("224.0.0.224");
                byte[] msg = "ZENOH UDP TEST".getBytes();
                DatagramPacket packet = new DatagramPacket(msg, msg.length, group, 7446);

                socket.send(packet);
                LOGGER.info("UDP Packet Test Passed.");

                socket.close();
            } catch (NullPointerException e) {
                LOGGER.info( "UDP test failed: Network interface was not found, or session was not initialized.");
            } catch (UnknownHostException ignored) {
            } catch (SocketException e) {
                LOGGER.info("UDP test failed: Could not set interface for MulticastSocket.");
            } catch (IOException e) {
                LOGGER.info("UDP test failed: IOException\n" + e.getMessage());
            }
        });

        networkThread.start();
    }

}