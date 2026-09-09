<template>
    <div class="flex flex-col w-full h-full gap-4 touch-none select-none">
        <UButton 
            icon="i-ix-chevron-up" 
            class="w-full grow touch-none select-none transition-all"
            :class="isForwardPressed ? 'scale-[0.95] ring-4' : ''"
            :variant="isForwardPressed ? 'outline' : 'subtle'"
            :ui="{ leadingIcon: 'size-16 pointer-events-none' }"
            @pointerdown="forwardPressed"
            @pointerup="forwardReleased"
            @pointercancel="forwardReleased"
            @lostpointercapture="forwardReleased"
        />
        <UButton 
            icon="i-ix-chevron-down" 
            class="w-full grow touch-none select-none transition-all"
            :class="isReversePressed ? 'scale-[0.95] ring-4' : ''"
            :variant="isReversePressed ? 'outline' : 'subtle'"
            :ui="{ leadingIcon: 'size-16 pointer-events-none' }"
            @pointerdown="backwardsPressed"
            @pointerup="backwardsReleased"
            @pointercancel="backwardsReleased"
            @lostpointercapture="backwardsReleased"
        />
    </div>
</template>

<script setup>
const model = defineModel({ default: 0.0 })

const isForwardPressed = ref(false)
const isReversePressed = ref(false)

function updateModel() {
    if (isForwardPressed.value && !isReversePressed.value) {
        model.value = 1.0
    } else if (isReversePressed.value && !isForwardPressed.value) {
        model.value = -1.0
    } else {
        model.value = 0.0
    }
}

function forwardPressed(event) {
    event.preventDefault()
    try {
        event.currentTarget?.setPointerCapture?.(event.pointerId)
    } catch (e) {}
    isForwardPressed.value = true
    updateModel()
}

function forwardReleased(event) {
    event.preventDefault()
    try {
        if (event.currentTarget?.hasPointerCapture?.(event.pointerId)) {
            event.currentTarget?.releasePointerCapture?.(event.pointerId)
        }
    } catch (e) {}
    isForwardPressed.value = false
    updateModel()
}

function backwardsPressed(event) {
    event.preventDefault()
    try {
        event.currentTarget?.setPointerCapture?.(event.pointerId)
    } catch (e) {}
    isReversePressed.value = true
    updateModel()
}

function backwardsReleased(event) {
    event.preventDefault()
    try {
        if (event.currentTarget?.hasPointerCapture?.(event.pointerId)) {
            event.currentTarget?.releasePointerCapture?.(event.pointerId)
        }
    } catch (e) {}
    isReversePressed.value = false
    updateModel()
}

onUnmounted(() => {
    isForwardPressed.value = false
    isReversePressed.value = false
    model.value = 0.0
})
</script>