FROM mcr.microsoft.com/playwright:v1.42.1-jammy

# Install n8n
RUN npm install -g n8n

# Create n8n folder (no chown needed)
RUN mkdir -p /home/node/.n8n

USER node

EXPOSE 5678

CMD ["n8n"]
