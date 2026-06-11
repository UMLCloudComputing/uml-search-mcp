#!/bin/zsh

# Build
docker build -t uml-search-mcp-server .

# Run
docker run -p 8000:8000 uml-search-mcp-server:latest
