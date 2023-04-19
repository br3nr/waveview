require('dotenv').config();

module.exports = {
  publicRuntimeConfig: {
    websocketUrl: 'ws://localhost:5090/ws',
    redirectUri: "https://discord.com/api/oauth2/authorize?client_id=1077474383779606600&redirect_uri=http%3A%2F%2Flocalhost%3A5090%2Fauth%2Fredirect&response_type=code&scope=identify%20guilds"
  },
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