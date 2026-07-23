export default defineAppConfig({
    ui: {
        colors: {
            primary: 'teal',
            secondary: 'pink',
            neutral: 'taupe'
        },
        button: {
            defaultVariants: {
                variant: "outline"
            },
            slots: {
                base: "justify-center"
            }
        }
    }
})