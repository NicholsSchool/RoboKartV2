<template>
    <div class="flex flex-col w-full h-full gap-4">
        <UButton icon="i-ix-chevron-up" class="w-full grow"/>
        <UButton icon="i-ix-chevron-down" class="w-full grow"/>
    <div class="flex flex-col w-full h-full gap-4 touch-none select-none">
        <UButton 
            icon="i-ix-chevron-up" 
            class="w-full grow touch-none select-none transition-all active:scale-[0.98]"
            :color="isForwardPressed ? 'primary' : 'neutral'"
            :variant="isForwardPressed ? 'solid' : 'subtle'"
            :ui="{ leadingIcon: 'size-16 pointer-events-none' }"
            @pointerdown="handleForwardPointerDown"
            @pointerup="handleForwardPointerUp"
            @pointercancel="handleForwardPointerCancel"
            @lostpointercapture="handleForwardPointerCancel"
        />
        <UButton 
            icon="i-ix-chevron-down" 
            class="w-full grow touch-none select-none transition-all active:scale-[0.98]"
            :color="isReversePressed ? 'primary' : 'neutral'"
            :variant="isReversePressed ? 'solid' : 'subtle'"
            :ui="{ leadingIcon: 'size-16 pointer-events-none' }"
            @pointerdown="handleReversePointerDown"
            @pointerup="handleReversePointerUp"
            @pointercancel="handleReversePointerCancel"
            @lostpointercapture="handleReversePointerCancel"
        />
    </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'

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

function handleForwardPointerDown(event) {
    event.preventDefault()
    try {
        event.currentTarget?.setPointerCapture?.(event.pointerId)
    } catch (e) {}
    isForwardPressed.value = true
    updateModel()
}

function handleForwardPointerUp(event) {
    event.preventDefault()
    try {
        if (event.currentTarget?.hasPointerCapture?.(event.pointerId)) {
            event.currentTarget?.releasePointerCapture?.(event.pointerId)
        }
    } catch (e) {}
    isForwardPressed.value = false
    updateModel()
}

function handleForwardPointerCancel(event) {
    try {
        if (event.currentTarget?.hasPointerCapture?.(event.pointerId)) {
            event.currentTarget?.releasePointerCapture?.(event.pointerId)
        }
    } catch (e) {}
    isForwardPressed.value = false
    updateModel()
}

function handleReversePointerDown(event) {
    event.preventDefault()
    try {
        event.currentTarget?.setPointerCapture?.(event.pointerId)
    } catch (e) {}
    isReversePressed.value = true
    updateModel()
}

function handleReversePointerUp(event) {
    event.preventDefault()
    try {
        if (event.currentTarget?.hasPointerCapture?.(event.pointerId)) {
            event.currentTarget?.releasePointerCapture?.(event.pointerId)
        }
    } catch (e) {}
    isReversePressed.value = false
    updateModel()
}

function handleReversePointerCancel(event) {
    try {
        if (event.currentTarget?.hasPointerCapture?.(event.pointerId)) {
            event.currentTarget?.releasePointerCapture?.(event.pointerId)
        }
    } catch (e) {}
    isReversePressed.value = false
    updateModel()
}

onUnmounted(() => {
    model.value = 0.0
})
</script>