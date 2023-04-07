require('dotenv').config();

module.exports = {
  images: {
    domains: ['img.youtube.com'],
  },
  async rewrites() {
    return Promise.resolve([
      {
        source: '/:path*',
        destination: `http://45.32.191.6:5090/:path*`,
      },
    ]);
  },
};
