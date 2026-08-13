/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./src/**/*.{html,js}",
        "./templates/**/*.html",
    ],
    theme: {
        extend: {
            colors: {
                primary: '#C8102E',
                primaryHover: '#E63946',
                secondary: '#1A1A1A',
                accent: '#F5F5F5',
            },
            fontFamily: {
                heading: ['Playfair Display', 'serif'],
                body: ['Inter', 'sans-serif'],
            },
        },
    },
    plugins: [],
}
