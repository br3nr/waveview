FROM node:18-alpine

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .

ENV NEXT_WEBSOCKET_URL=ws://localhost:5090/ws
ENV NEXT_REDIRECT_URI=https://discord.com/api/oauth2/authorize?client_id=1077474383779606600&redirect_uri=http%3A%2F%2Flocalhost%3A5090%2Fauth%2Fredirect&response_type=code&scope=identify%20guilds
ENV NEXT_API_URL=http://botapi:5090/:path*

RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
