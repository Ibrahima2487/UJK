/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './**/templates/**/*.html',
    './static/**/*.js',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#2563eb',
          dark: '#1d4ed8',
          light: '#eff6ff',
        },
        success: {
          DEFAULT: '#16a34a',
          dark: '#15803d',
          light: '#f0fdf4',
        },
        warning: {
          DEFAULT: '#d97706',
          dark: '#b45309',
          light: '#fffbeb',
        },
        danger: {
          DEFAULT: '#dc2626',
          dark: '#b91c1c',
          light: '#fef2f2',
        },
        info: {
          DEFAULT: '#0891b2',
          dark: '#0e7490',
          light: '#ecfeff',
        },
        secondary: {
          DEFAULT: '#475569',
          dark: '#334155',
          light: '#f8fafc',
        },
        accent: '#2563eb',
      },
      fontFamily: {
        poppins: ['Poppins', 'sans-serif'],
      },
      animation: {
        'fade-down': 'fadeDown 0.6s ease-out',
        'fade-in': 'fadeIn 0.8s ease-out',
        'fade-in-up': 'fadeInUp 0.5s ease-out forwards',
      },
      keyframes: {
        fadeDown: {
          '0%': { opacity: '0', transform: 'translateY(-12px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(24px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/line-clamp'),
    require('@tailwindcss/forms'),
  ],
}