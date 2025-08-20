module.exports = {
    plugins: {
      tailwindcss: {},
      autoprefixer: {},
      ...(process.env.NODE_ENV === 'production' ? {
        '@fullhuman/postcss-purgecss': {
          content: [
            './src/**/*.{js,jsx,ts,tsx}',
            './public/index.html',
          ],
          defaultExtractor: content => content.match(/[\w-/:]+(?<!:)/g) || [],
          safelist: [
            'html', 'body',
            /^fade-/,
            /^slide-/,
            /^scale-/,
            /^animate-/,
            /^hover:/,
            /^focus:/,
            /^active:/,
            /^group-hover:/,
            /^transition-/,
            /^duration-/,
            /^ease-/,
            /^delay-/
          ]
        },
        'cssnano': {
          preset: 'default',
        }
      } : {})
    },
  }