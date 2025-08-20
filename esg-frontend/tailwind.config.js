/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      colors: {
        // Sophisticated Primary Colors (Muted Green)
        primary: {
          50: '#f4f7f5',
          100: '#e6ede8',
          200: '#d0ddd3',
          300: '#adc4b4',
          400: '#7fa18a',
          500: '#56ab91', // Main sophisticated green
          600: '#4a9b8a',
          700: '#3e8b7a',
          800: '#347869',
          900: '#2d6659',
          950: '#1a3e37',
        },
        // Dark Theme Colors (GitHub Dark inspired)
        dark: {
          50: '#f6f8fa',
          100: '#e6edf3',
          200: '#d0d7de',
          300: '#8b949e',
          400: '#656d76',
          500: '#484f58',
          600: '#32383f',
          700: '#24292f',
          800: '#1c2128',
          900: '#161b22',
          950: '#0d1117',
        },
        // ESG Category Colors
        environmental: {
          50: '#f4f7f5',
          100: '#e6ede8',
          500: '#56ab91',
          600: '#4a9b8a',
          700: '#3e8b7a',
        },
        social: {
          50: '#eff8ff',
          100: '#dbeafe',
          500: '#58a6ff',
          600: '#4493f8',
          700: '#2f81f7',
        },
        governance: {
          50: '#f8f7ff',
          100: '#f0edff',
          500: '#a5a6ff',
          600: '#8b92ff',
          700: '#7c7fff',
        },
        // Status Colors
        success: {
          50: '#f4f7f5',
          100: '#e6ede8',
          400: '#7fa18a',
          500: '#56ab91',
          600: '#4a9b8a',
          700: '#3e8b7a',
        },
        warning: {
          50: '#fffcf5',
          400: '#fb8500',
          500: '#f79009',
          600: '#dc6803',
        },
        danger: {
          50: '#fff5f5',
          400: '#ff6b6b',
          500: '#f85149',
          600: '#da3633',
        },
        // Text Colors
        text: {
          primary: '#e6edf3',
          secondary: '#8b949e',
          muted: '#656d76',
        }
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui'],
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'sophisticated-gradient': 'linear-gradient(135deg, #0f1419 0%, #1a252f 30%, #0d1117 70%, #161b22 100%)',
        'card-gradient': 'linear-gradient(135deg, rgba(22, 27, 34, 0.95) 0%, rgba(33, 38, 45, 0.9) 100%)',
        'green-gradient': 'linear-gradient(135deg, #56ab91 0%, #4a9b8a 100%)',
        'blue-gradient': 'linear-gradient(135deg, #58a6ff 0%, #4493f8 100%)',
        'purple-gradient': 'linear-gradient(135deg, #a5a6ff 0%, #8b92ff 100%)',
      },
      backdropBlur: {
        xs: '2px',
      },
      animation: {
        'fade-in': 'fadeIn 0.6s ease-out',
        'slide-up': 'slideUp 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
        'scale-in': 'scaleIn 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        'pulse-green': 'pulseGreen 2s infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideUp: {
          '0%': { transform: 'translateY(30px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        pulseGreen: {
          '0%, 100%': { boxShadow: '0 0 0 0 rgba(86, 171, 145, 0.4)' },
          '50%': { boxShadow: '0 0 0 6px rgba(86, 171, 145, 0)' },
        },
        glow: {
          '0%': { textShadow: '0 0 5px rgba(86, 171, 145, 0.5)' },
          '100%': { textShadow: '0 0 15px rgba(86, 171, 145, 0.8)' },
        },
      },
      boxShadow: {
        'glow': '0 0 15px rgba(86, 171, 145, 0.2)',
        'glow-lg': '0 0 30px rgba(86, 171, 145, 0.3)',
        'inner-glow': 'inset 0 0 15px rgba(86, 171, 145, 0.1)',
      }
    },
  },
  plugins: [],
  darkMode: 'class',
}