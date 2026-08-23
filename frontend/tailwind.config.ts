import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: '#080c14',
        foreground: '#f1f5f9',
        card: {
          DEFAULT: 'rgba(13, 20, 36, 0.7)',
          border: 'rgba(56, 189, 248, 0.15)',
        },
        brand: {
          cyan: '#00f2fe',
          blue: '#4facfe',
          purple: '#8b5cf6',
          emerald: '#10b981',
          dark: '#0a0f1d'
        }
      },
      animation: {
        'pulse-glow': 'pulseGlow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 0.3s ease-in-out forwards',
        'slide-up': 'slideUp 0.4s ease-out forwards',
      },
      keyframes: {
        pulseGlow: {
          '0%, 100%': { opacity: '0.4', filter: 'drop-shadow(0 0 15px rgba(0, 242, 254, 0.6))' },
          '50%': { opacity: '0.8', filter: 'drop-shadow(0 0 25px rgba(79, 172, 254, 0.9))' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(12px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        }
      }
    },
  },
  plugins: [],
};

export default config;
