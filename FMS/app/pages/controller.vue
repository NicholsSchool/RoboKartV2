<template>
    <div ref="controller" class="absolute inset-0 flex flex-col controller-touch-surface select-none touch-none overflow-hidden">
        <div class="flex flex-col gap-4 h-full w-full">
            <div class="flex items-center bg-elevated h-12 w-full border-t-4" :class="mqttStatus == mqttStates.CONN ? 'border-success-500' : 'border-error-500'">
                <HeaderTitle title="Controller" class="text-xl" />
                <div class="flex items-center gap-2">
                    <p class="text-xl">{{ name }}</p>
                    <UIcon :name="batteryIcon" class="size-6"/>
                </div>
                <div class="w-full h-0.5 mx-4" :class="mqttStatus == mqttStates.CONN ? 'bg-success-500' : 'bg-error-500'" />
                <div class="flex h-full w-50 items-center justify-center text-xl px-8 cut-corners" :class="mqttStatus == mqttStates.CONN ? 'bg-success-800/25' : 'bg-error-800/25'">
                    <p class="font-extrabold">{{ mqttStatus }}</p>
                </div>
                <UButton size="xl" variant="soft" class="pl-8 cut-left-corner" :icon="isFullscreen ? 'i-ix-full-screen-exit' : 'i-ix-full-screen'" v-on:click="toggle"/>
            </div>
            <div v-if="isFullscreen" class="flex *:p-6 items-center justify-between h-full touch-none select-none">
                <div class="flex flex-col justify-center w-1/2 h-full gap-4">
                    <div class="w-full h-1/2 bg-elevated border-2 border-neutral-100/25" />
                    <ControllerSlider v-model="sliderInput" />
                </div>
                <div class="flex w-1/2 h-full">
                    <ControllerThrottle v-model="throttleInput" />
                </div>
            </div>
            <div v-if="!isFullscreen" class="flex items-center justify-center h-full">
                <div class="flex-col p-2 border-t-4 shadow-lg border-error-500 bg-error-800/25 shadow-error-600/35"> 
                    <p class="font-extrabold">CONTROLS DISABLED</p>
                    <p class="font-light"> Please press the fullscreen button to enable the controls. </p>
                </div>
            </div>
        </div>
        <div class="absolute bottom-0 left-0 bg-accented/50 px-4">
            <p> X: {{ sliderInput }} | Y: {{ throttleInput }} | {{ mqttStatus }} </p>
        </div>
    </div>
</template>

<script setup>
import { generateControllerName } from '#imports';
import { useBattery, watchDebounced, useScreenOrientation, useFullscreen, useWakeLock } from '@vueuse/core'
import mqtt from 'mqtt'

const mqttStates = Object.freeze({
    CONN: "CONNECTED",
    DCONN: "DISCONNECTED",
    ERR: "ERROR",
    IDLE: "IDLE"
})

const client = mqtt.connect("mqtt://localhost:8080/");

const sliderInput = ref(0.0)
const throttleInput = ref(0.0)

const { lockOrientation } = useScreenOrientation()
lockOrientation('landscape')

const { isFullscreen, toggle } = useFullscreen()

const { request: lockScreen } = useWakeLock()
lockScreen()

const name = generateControllerName()

const mqttStatus = ref(mqttStates.IDLE)

const batteryState = useBattery()

const batteryIcon = computed(() => {

    if (!batteryState.isSupported.value) return 'i-ix-battery-empty-question'
    if (batteryState.charging.value) return 'i-ix-battery-charge'

    let level = batteryState.level.value

    if (level <= 1/20) return 'i-ix-battery-exclamation'
    if (level <= 1/10) return 'i-ix-battery-low'
    if (level <= 1/4) return 'i-ix-battery-quarter'
    if (level <= 1/2) return 'i-ix-battery-half'
    if (level <= 3/4) return 'i-ix-battery-three-quarter'
    return 'i-ix-battery-full'
})

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


watchDebounced(sliderInput, (newValue) => {
    if (mqttStatus.value != mqttStates.CONN) return
    client.publish(`controller/${name}/x`, floatToBuffer(newValue), {qos: Math.abs(newValue) < 0.1 ? 1 : 0})
}, { debounce: 20, maxWait: 50 })

watch(throttleInput, (newValue) => {
    if (mqttStatus.value != mqttStates.CONN) return
    client.publish(`controller/${name}/y`, floatToBuffer(newValue), {qos: Math.abs(newValue) < 0.1 ? 1 : 0})
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

function floatToBuffer(val) {
    const buf = new Int8Array(1)
    buf[0] = Math.round(127 * Math.max(-1, Math.min(1, val)));
    return new Uint8Array(buf.buffer);
}

/** 
 * TODO:
 * - Connect to MQTT Broker ✅
 * - Display connection status ✅
 * - Send joystick data to broker using name ✅
 * - Send heartbeat to broker every 500ms ✅
 * - Add gas/brake/steering mode instead of joystick (allow swap between them) ✅
 * - Recieve some data from the broker (potentially color sensor)
 * - Get app to work with HTTPS on FMS Server (unlocks battery, screen lock, screen orientation APIs)
*/

</script>

<style>

.cut-corners {
    clip-path: polygon(0% 0%, 16px 100%, 100% 100%, calc(100% - 16px) 0%);
}

.cut-left-corner {
    clip-path: polygon(0% 0%, 16px 100%, 100% 100%, 100% 0%);
}

.controller-touch-surface {
    touch-action: none !important;
    -webkit-touch-callout: none !important;
    -webkit-user-select: none !important;
    user-select: none !important;
    overscroll-behavior: none !important;
}

.controller-touch-surface * {
    -webkit-touch-callout: none !important;
}

</style>