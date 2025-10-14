/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'attention-green': '#10b981',
        'attention-yellow': '#f59e0b', 
        'attention-red': '#ef4444',
      }
    },
  },
  plugins: [],
}

