require('dotenv').config();

module.exports = {
  images: {
    domains: ['img.youtube.com'],
  },
  async rewrites() {
    return Promise.resolve([
      {
        source: '/:path*',
        destination: `${process.env.FLASK_APP_URL}/:path*`,
      },
    ]);
  },
};
