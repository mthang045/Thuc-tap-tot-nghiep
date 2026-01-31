# Development - Note: Base image vulnerability is from Node.js upstream, will be fixed in next release
FROM node:22-bookworm-slim

WORKDIR /app

# Install security updates
RUN apt-get update && apt-get upgrade -y && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--host"]
