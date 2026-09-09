<template>
    <div class="relative h-full">
        <img src="/logos/Flag.svg" class="absolute top-0 left-0 h-full object-cover opacity-50">
        <div class="flex items-center pl-4 pr-8 h-full">
            <h1 class="font-extrabold">{{ props.title }}</h1>
        </div>
    </div>
</template>

<script setup>

const props = defineProps({
    title: String
})

</script>