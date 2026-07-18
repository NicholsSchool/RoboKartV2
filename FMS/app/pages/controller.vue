<template>
    <div ref="controller" class="absolute inset-0">
        <div class="flex flex-col w-full h-full items-center justify-center">
            <ControllerJoystick class="w-96 h-96" v-model="joystickInput" />
            <div>
                <p class="font-bold">Joystick Values</p>
                <p> X: {{ joystickInput.x }} </p>
                <p> Y: {{ joystickInput.y }} </p>
                <button @click="toggle">Fullscreen</button>
            </div>
        </div>
    </div>
</template>

<script setup>

const joystickInput = ref({"x": 0.0, "y": 0.0})

</script>