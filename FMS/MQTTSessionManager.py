import json, threading, time, logging
import paho.mqtt.client as mqtt
import UIUtil

LOG_TAG = "MQTTSessionManager"

client: mqtt.Client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
heartbeatThread: threading.Thread = None
acceptedTypes = ["Controller", "Robot"]
sessionPeers = []

class Subscription:
    
    def __init__(self, name: str, subKey: str):
        self.subKey = subKey
        self.name = name
        self.callbacks = []
        
    def addCallback(self, desc: str, callback):
        self.callbacks.append(callback)
        UIUtil.log(logging.INFO, LOG_TAG, f"Registering callback {self.name} for subscriber {desc}")
        
    def handleMessage(self, client, userdata, msg: mqtt.MQTTMessage):
        
        if not mqtt.topic_matches_sub(self.subKey, msg.topic):
            return
        
        UIUtil.log(logging.DEBUG, LOG_TAG, f"Message Matched ({self.name}): {str(msg.payload)}")
        for callback in self.callbacks:
            callback(client, userdata, msg)

subscriptions: dict = {
    "HEARTBEAT": Subscription("Peer Heartbeats", "+/+/Heartbeat"),
    "CONTROLLER_INPUT": Subscription("Controller Inputs", "Controller/+/Input")
}

def updatePeerList(client, userdata, msg):
    global sessionPeers
    if (acceptedTypes.count(str(msg.topic).split("/")[0]) < 1):
        return
    peer = {
        "type": str(msg.topic).split("/")[0],
        "id": str(msg.topic).split("/")[1],
        "timestamp": time.time(),
        "heartbeatInfo": json.loads(msg.payload) or {}
    }

    for i in range(len(sessionPeers)):
        if sessionPeers[i]["id"] == peer["id"]:
            sessionPeers[i] = peer
            break
    else:
        sessionPeers.append(peer)
        UIUtil.log(logging.INFO, LOG_TAG, f"Peer Connected: {peer['id']}")

subscriptions["HEARTBEAT"].addCallback("Peer List", updatePeerList)

def stalePeerCheck():
    while True:
        global sessionPeers
        currentTime = time.time()
        alivePeers = [peer for peer in sessionPeers if currentTime - peer["timestamp"] < 1] # All peers that have sent heartbeats in the last second
        if (len(alivePeers) != len(sessionPeers)):
            UIUtil.log(logging.INFO, LOG_TAG, f"Devices went stale: {[peer['id'] for peer in sessionPeers if peer not in alivePeers]}")
            sessionPeers = alivePeers
            for callback in subscriptions["HEARTBEAT"].callbacks: # Manually trigger HEARTBEAT callbacks after loss of peer
                callback(client, None, mqtt.MQTTMessage())
            
        time.sleep(0.5)
        
def onConnect(client: mqtt.Client, userdata, flags: mqtt.ConnectFlags, reasonCode, properties):
    UIUtil.log(logging.INFO, LOG_TAG, f"FMS Connected to MQTT Broker with RC: {reasonCode}")
    UIUtil.log(logging.INFO, LOG_TAG, f"Host: {client.host} | Port: {client.port} | Protocol: {client.protocol}")
    
    for sub in subscriptions.values():
        client.subscribe(sub.subKey)
        UIUtil.log(logging.INFO, LOG_TAG, f"Registered subscriber {sub.name}")
    
    heartbeatThread = threading.Thread(target=stalePeerCheck, daemon=True)
    heartbeatThread.start()
    
def onMessage(client, userdata, msg):

    for sub in subscriptions.values():
        sub.handleMessage(client, userdata, msg)
    

def init():
    global client

    if client.is_connected():
        UIUtil.log(logging.WARNING, LOG_TAG, "Attempted to initialize more than once.")
        return
    
    client.on_connect = onConnect
    client.on_message = onMessage

    client.connect_async("localhost", 1883, 60)
    
    client.loop_start()
    
    UIUtil.log(logging.INFO, LOG_TAG, "MQTT Client Initialized, waiting for connection.")
    
def close():
    global heartbeatThread
    if heartbeatThread and heartbeatThread.is_alive():
        heartbeatThread.join()
    client.disconnect()