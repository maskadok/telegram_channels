FROM node:22-alpine

ARG NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_BASE_URL=${NEXT_PUBLIC_API_BASE_URL}

WORKDIR /app

COPY package.json package.json
COPY tsconfig.json tsconfig.json
COPY next.config.js next.config.js
COPY next-env.d.ts next-env.d.ts

RUN npm install

COPY app ./app
COPY components ./components
COPY lib ./lib
COPY public ./public

RUN npm run build

ENV NODE_ENV=production

EXPOSE 3000

CMD ["npm", "run", "start", "--", "--hostname", "0.0.0.0", "--port", "3000"]
