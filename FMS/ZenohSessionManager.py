import json, threading, time, logging
import zenoh as zn
import UIUtil

LOG_TAG = "ZenohSessionManager"

session: zn.Session = None
heartbeatThread: threading.Thread = None
acceptedTypes = ["Controller", "Robot"]
sessionPeers = []
sessionPeerUpdateCallbacks = []
controllerUpdateCallbacks = []

def handleControllerInput(sample: zn.Sample):
    UIUtil.log(logging.DEBUG, LOG_TAG, f"Received Controller Input: {str(sample.payload)}")
    for callback in controllerUpdateCallbacks:
        callback(sample)

def handlePeerHeartbeat(sample: zn.Sample):
    global sessionPeers
    if (acceptedTypes.count(str(sample.key_expr).split("/")[0]) < 1):
        return
    UIUtil.log(logging.DEBUG, LOG_TAG, f"Received Peer Heartbeat: {str(sample.payload)}")

    peer = {
        "type": str(sample.key_expr).split("/")[0],
        "id": str(sample.key_expr).split("/")[1],
        "timestamp": time.time(),
        "heartbeatInfo": str(sample.payload)
    }

    for i in range(len(sessionPeers)):
        if sessionPeers[i]["id"] == peer["id"]:
            sessionPeers[i] = peer
            break
    else:
        sessionPeers.append(peer)
        UIUtil.log(logging.INFO, LOG_TAG, f"Peer Connected: {peer['id']}")

    for callback in sessionPeerUpdateCallbacks:
        callback(sessionPeers)

def deleteStaleHeartbeats():
    while True:
        global sessionPeers
        currentTime = time.time()
        sessionPeers_new = [peer for peer in sessionPeers if currentTime - peer["timestamp"] < 1]
        if (len(sessionPeers_new) != len(sessionPeers)):
            UIUtil.log(logging.INFO, LOG_TAG, f"Devices went stale: {[peer['id'] for peer in sessionPeers if peer not in sessionPeers_new]}")
            sessionPeers = sessionPeers_new
            for callback in sessionPeerUpdateCallbacks:
                callback(sessionPeers)
            
        time.sleep(0.5)

def registerControllerUpdateCallback(desc: str, callback: callable):
    global controllerUpdateCallbacks
    UIUtil.log(logging.INFO, LOG_TAG, f"Registering callback \"{desc}\" for Controller Updates.")
    if (controllerUpdateCallbacks.count(callback) == 0):
        controllerUpdateCallbacks.append(callback)

def registerSessionPeerUpdateCallback(desc: str, callback: callable):
    global sessionPeerUpdateCallbacks
    UIUtil.log(logging.INFO, LOG_TAG, f"Registering callback \"{desc}\" for Session Peer Updates.")
    if (sessionPeerUpdateCallbacks.count(callback) == 0):
        sessionPeerUpdateCallbacks.append(callback)

def closeZenohSession():
    global session
    if session and not session.is_closed():
        session.close()
        UIUtil.log(logging.INFO, LOG_TAG, "RoboKart FMS Zenoh Session CLOSED")

def initializeZenohSession():
    global session

    if session:
        UIUtil.log(logging.WARNING, LOG_TAG, "initializeZenohSession called more than once.")
        return

    config = zn.Config.from_file("zenohServerConf.json")
    session = zn.open(config)
    UIUtil.log(logging.INFO, LOG_TAG, "RoboKart FMS Zenoh Session INITIALIZED")
    UIUtil.log(logging.INFO, LOG_TAG, f"Server ZID: {session.info.zid()}")
    UIUtil.log(logging.INFO, LOG_TAG, f"Listening to {json.loads(config.get_json('listen'))['endpoints']['peer'][0]} on interface {json.loads(config.get_json('scouting'))['multicast']['interface']}")
    
    session.declare_subscriber("Controller/*/Input", handleControllerInput)
    session.declare_subscriber("*/*/Heartbeat", handlePeerHeartbeat)

    heartbeatThread = threading.Thread(target=deleteStaleHeartbeats, daemon=True)
    heartbeatThread.start()
    
def close():
    global heartbeatThread
    if heartbeatThread and heartbeatThread.is_alive():
        heartbeatThread.join()
    session.close()