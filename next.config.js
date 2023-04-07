require('dotenv').config();

module.exports = {
  images: {
    domains: ['img.youtube.com'],
  },
  async rewrites() {
    return Promise.resolve([
      {
        source: '/:path*',
        destination: `http://localhost:5090/:path*`,
      },
    ]);
  },
};
