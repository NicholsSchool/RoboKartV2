<template>
    <div ref="controller" class="absolute inset-0">
        <div class="flex w-full h-full items-center justify-center">
            <div class="flex p-8 bg-elevated gap-4">
                <ControllerJoystick class="w-80 h-80" v-model="joystickInput" />
                <div class="flex flex-col gap-4 w-72">
                    <div class="flex-col p-2 border-t-4 shadow-lg" :class="mqttStatus == mqttStates.CONN ? 'border-success-500 bg-success-800/25 shadow-success-600/35' : 'border-error-500 bg-error-800/25 shadow-error-600/35'"> 
                        <p class="font-extrabold">Status: {{mqttStatus}}</p>
                        <p class="font-light text-xs" v-if="mqttStatus == mqttStates.CONN"> Your controller is connected to the RoboKart system. </p>
                        <p class="font-light text-xs" v-if="mqttStatus != mqttStates.CONN"> If your controller doesn't connect soon, ask a RoboKart technician for help. </p>
                    </div>
                    <p class="font-bold">Joystick Values</p>
                    <p> X: {{ joystickInput.x }} </p>
                    <p> Y: {{ joystickInput.y }} </p>
                    <UButton>Fullscreen</UButton>
                    <p>{{ name }}</p>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { generateControllerName } from '#imports';
import { useBattery } from '@vueuse/core'
import mqtt from 'mqtt'

const mqttStates = Object.freeze({
    CONN: "CONNECTED",
    DCONN: "DISCONNECTED",
    ERR: "ERROR",
    IDLE: "IDLE"
})

const client = mqtt.connect("mqtt://localhost:8080/");

const joystickInput = ref({"x": 0.0, "y": 0.0})

const name = generateControllerName()

const mqttStatus = ref(mqttStates.IDLE)

const batteryState = useBattery()

client.on("connect", () => { //Successful connection to broker
    mqttStatus.value = mqttStates.CONN
});

client.on("disconnect", (e) => { //Disconnect packet is recieved from broker
    mqttStatus.value = mqttStates.DCONN
    console.log("Disconnected from broker: ", e)
});

client.on("close", (e) => { //Websocket connection is closed
    mqttStatus.value = mqttStates.DCONN
    console.log("Connection closed: ", e)
});

client.on("offline", () => { // Client goes offline
    mqttStatus.value = mqttStates.ERR
});

client.on("error", () => { //Connection error
    mqttStatus.value = mqttStates.ERR
});


watch(joystickInput, (newValue, oldValue) => {
    if (mqttStatus.value != mqttStates.CONN) return
    if (newValue.x != oldValue.x) {
        client.publish(`controller/${name}/x`, newValue.x.toString())
    }
    if (newValue.y != oldValue.y) {
        client.publish(`controller/${name}/y`, newValue.y.toString())
    }
})

setInterval(() => {
    if (mqttStatus.value != mqttStates.CONN) return
    client.publish(`controller/${name}/heartbeat`, JSON.stringify({
        type: "controller",
        id: name,
        battery: batteryState.isSupported ? batteryState.level.value * 100 : "unknown",
        charging: batteryState.isSupported ? batteryState.charging.value : false,
    }))
}, 500)


/** 
 * TODO:
 * - Connect to MQTT Broker ✅
 * - Display connection status ✅
 * - Send joystick data to broker using name ✅
 * - Send heartbeat to broker every 500ms ✅
 * - Add gas/brake/steering mode instead of joystick (allow swap between them)
 * - Recieve some data from the broker (potentially color sensor)
*/

</script>