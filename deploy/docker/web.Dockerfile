# FR-PLAT-004 / COV-027: Next.js web app
FROM node:24-bookworm-slim AS build
WORKDIR /src
RUN corepack enable
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY apps/web ./apps/web
# Browser-facing origin (host). Server-side/in-compose origin for rewrites.
ARG NEXT_PUBLIC_API_BASE=http://127.0.0.1:8000
ARG API_URL=http://api:8000
ENV NEXT_PUBLIC_API_BASE=$NEXT_PUBLIC_API_BASE
ENV API_URL=$API_URL
RUN pnpm --filter web install --ignore-scripts \
  && pnpm --filter web build

FROM node:24-bookworm-slim AS runtime
# Security patches + remove unused package managers that ship vulnerable
# transitive deps (npm's undici, yarn) not needed for Next standalone.
RUN apt-get update \
  && apt-get upgrade -y --no-install-recommends \
  && rm -rf /var/lib/apt/lists/* \
  && rm -rf /usr/local/lib/node_modules/npm \
            /usr/local/lib/node_modules/corepack \
            /opt/yarn-v* \
  && rm -f /usr/local/bin/npm \
           /usr/local/bin/npx \
           /usr/local/bin/corepack \
           /usr/local/bin/yarn \
           /usr/local/bin/yarnpkg
WORKDIR /app
ENV NODE_ENV=production
# Default for local compose network; override via compose environment.
ENV API_URL=http://api:8000
COPY --from=build /src/apps/web/.next/standalone ./
COPY --from=build /src/apps/web/.next/static ./apps/web/.next/static
COPY --from=build /src/apps/web/public ./apps/web/public
USER node
EXPOSE 3000
CMD ["node", "apps/web/server.js"]
