<template>
    <div class="flex h-20 min-w-40">
    <div 
        class="flex h-20 min-w-40 touch-none select-none"
        @pointercancel="resetModel"
        @lostpointercapture="resetModel"
    >
        <USlider :min="-1" :max="1" :step="0.01" v-model="model" @change="model = 0" :ui="{
            thumb: 'rounded-none size-16 shadow-[0_0_32px] shadow-primary/50',
            track: 'h-12 bg-chevron-right',
            range: 'bg-chevron-left'
        }" />
    </div>
</template>

<script setup>
import { onUnmounted } from 'vue'

const model = defineModel({ default: 0.0 })

function resetModel() {
    model.value = 0.0
}

onUnmounted(() => {
    model.value = 0.0
})
</script>