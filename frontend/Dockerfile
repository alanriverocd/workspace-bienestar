FROM node:20.19.0-slim
ENV CI=true DEBIAN_FRONTEND=noninteractive
WORKDIR /app
COPY package.json package-lock.json* ./
# Provide a small set of tools and CA certs, then install JS deps
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
		ca-certificates \
		curl \
		wget \
	&& rm -rf /var/lib/apt/lists/*
# Use legacy-peer-deps to avoid peer dependency resolution failures inside container
RUN npm install --legacy-peer-deps --silent
COPY . .
# Pre-install Playwright browsers (with system deps) so tests run reliably in CI
RUN npx playwright install --with-deps
RUN npm run build
EXPOSE 5173
CMD ["npm","run","preview","--","--port", "5173", "--host"]
