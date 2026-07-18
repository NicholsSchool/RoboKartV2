<template>
    
    <div ref="joystick-container" class="relative bg-secondary ring-2 ring-primary overflow-hidden">
        <div v-if="mousePressed" class="touchDownPos bg-white/50 rounded-full pointer-events-none"></div>
        <div v-if="mousePressed" class="touchPos bg-white/20 rounded-full pointer-events-none"></div>
        <div v-if="mousePressed" class="stickArea bg-white/10 rounded-sm pointer-events-none"></div>
    </div>
    
</template>

<script setup>
import { useResizeObserver, useMouse, useMousePressed } from '@vueuse/core'

const model = defineModel({ default: {
    "x": 0.0,
    "y": 0.0
}})

const container = useTemplateRef("joystick-container")

const extractor = (event) => {
    if (!(event instanceof MouseEvent)) return null
    return [event.offsetX, event.offsetY]
}

const { x: mouseX, y: mouseY} = useMouse({ target: container, type: extractor})
const { pressed: mousePressed } = useMousePressed({target: container})

const width = ref(0)
const height = ref(0)
const sideLen = computed(() => Math.min(width.value, height.value))

useResizeObserver(container, (entries) => {
    
    width.value = entries[0].contentRect.width
    height.value = entries[0].contentRect.height
    
})

const mouseDownX = ref(0)
const mouseDownY = ref(0)

watch(mousePressed, (p) => {
    if (p) {
        mouseDownX.value = mouseX.value
        mouseDownY.value = mouseY.value
    }
})

const allData = reactive({
    "mouseX": mouseX,
    "mouseY": mouseY,
    "mousePressed": mousePressed,
    "sideLen": sideLen,
    "mouseDownX": mouseDownX,
    "mouseDownY": mouseDownY
})

watch(allData, (d) => {
    if (d.mousePressed) {
        model.value = {
            "x": Math.max(Math.min((d.mouseX - d.mouseDownX) / (0.25 * d.sideLen), 1), -1),
            "y": -Math.max(Math.min((d.mouseY - d.mouseDownY) / (0.25 * d.sideLen), 1), -1)
        }
    } else {
        model.value = {
            "x": 0,
            "y": 0
        }
    }
})


</script>

<style scoped>

.touchDownPos {
    position: absolute;
    width: 40px;
    height: 40px;
    top: calc(v-bind(mouseDownY) * 1px - 20px);
    left: calc(v-bind(mouseDownX) * 1px - 20px);
}

.stickArea {
    position: absolute;
    width: calc(v-bind(sideLen) * 0.5px);
    height: calc(v-bind(sideLen) * 0.5px);;
    top: calc(v-bind(mouseDownY) * 1px - calc(v-bind(sideLen) * 0.25px));
    left: calc(v-bind(mouseDownX) * 1px - calc(v-bind(sideLen) * 0.25px));
}

.touchPos {
    position: absolute;
    width: 20px;
    height: 20px;
    top: calc(v-bind(mouseY) * 1px - 10px);
    left: calc(v-bind(mouseX) * 1px - 10px);
}

</style>