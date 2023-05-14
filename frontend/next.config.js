require('dotenv').config();

module.exports = {
  output: 'standalone',
  publicRuntimeConfig: {
    websocketUrl: 'ws://192.168.0.153:5090/ws',
    //redirectUri: "https://discord.com/api/oauth2/authorize?client_id=1077474383779606600&redirect_uri=http%3A%2F%2F149.28.167.4%3A5090%2Fauth%2Fredirect&response_type=code&scope=identify%20guilds"
    redirectUri: "https://discord.com/api/oauth2/authorize?client_id=1077474383779606600&redirect_uri=http%3A%2F%2F192.168.0.153%3A5090%2Fauth%2Fredirect&response_type=code&scope=guilds%20identify"
  },
  images: {
    domains: ['img.youtube.com'],
  },
  async rewrites() {
    return Promise.resolve([
      {
        source: '/:path*',
        destination: `http://192.168.0.153:5090/:path*`,
      },
    ]);
  },
};