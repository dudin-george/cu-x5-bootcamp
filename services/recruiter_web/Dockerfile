# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Build arguments for environment variables
ARG VITE_ENVIRONMENT=dev
ARG VITE_ORY_SDK_URL=
ARG VITE_API_URL=/api

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci || npm install

# Copy source code
COPY . .

# Build application with environment variables
RUN VITE_ENVIRONMENT=$VITE_ENVIRONMENT \
    VITE_ORY_SDK_URL=$VITE_ORY_SDK_URL \
    VITE_API_URL=$VITE_API_URL \
    npm run build

# Production stage
FROM nginx:alpine

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget -q --spider http://localhost/nginx-health || exit 1

# Run nginx
CMD ["nginx", "-g", "daemon off;"]
