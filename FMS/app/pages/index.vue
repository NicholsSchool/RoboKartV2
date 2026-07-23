<template>
    <div class="absolute flex inset-0 items-center justify-center">   
        <div class="flex flex-col gap-8 bg-elevated p-4 w-120 border-2 border-secondary">
            <img src="/logos/LogoChroma.svg">
            <div class="flex flex-col items-center w-full gap-4 px-4">
                <p class="text-lg text-center">
                    Welcome to the RoboKart FMS. <br> Choose an option below to continue.
                </p>
                <UButton size="lg" to="/FMS" icon="i-ix-screen-pc-tower" class="w-full"> Access FMS Control Panel </UButton>
                <UButton size="lg" to="/controller" icon="i-ix-car-filled" class="w-full"> Access Kart Controller </UButton>
            </div>
            <div class="flex w-full text-xs text-neutral-400 justify-between mt-10">
                <p> RoboKart FMS Client App</p>
                <p> Powered by <span class="text-rainbow font-bold">Electric Mayhem</span></p>
            </div>
        </div>
    </div>
</template>