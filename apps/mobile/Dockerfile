FROM node:22-alpine
WORKDIR /app
RUN corepack enable
COPY package.json pnpm-workspace.yaml turbo.json tsconfig.base.json .npmrc ./
COPY packages ./packages
COPY apps/mobile ./apps/mobile
RUN pnpm install --frozen-lockfile=false
EXPOSE 19006
CMD ["pnpm", "--filter", "@fo-scanner/mobile", "web"]
