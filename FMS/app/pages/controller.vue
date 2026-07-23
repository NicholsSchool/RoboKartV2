<template>
    <div ref="controller" class="absolute inset-0">
        <div class="flex w-full h-full items-center justify-center">
            <div class="flex p-8 bg-elevated gap-4">
                <ControllerJoystick class="w-80 h-80" v-model="joystickInput" />
                <div class="flex flex-col gap-2 w-72">
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

const joystickInput = ref({"x": 0.0, "y": 0.0})

const name = generateControllerName()

/** 
 * TODO:
 * - Connect to MQTT Broker
 * - Display connection status
 * - Send joystick data to broker using name
 * - Send heartbeat to broker every 500ms
 * - Add gas/brake/steering mode instead of joystick (allow swap between them)
 * - Recieve some data from the broker (potentially color sensor)
*/

</script>