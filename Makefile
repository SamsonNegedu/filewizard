.PHONY: help build build-small build-cuda push pull up down restart rebuild

# Default target
help:
	@echo "FileWizard - Makefile Commands"
	@echo "================================"
	@echo ""
	@echo "Build Commands:"
	@echo "  make build       - Build ARM64 image (full version)"
	@echo "  make build-small - Build ARM64 image (small version)"
	@echo "  make build-cuda  - Build ARM64 image (CUDA version)"
	@echo "  make push        - Push ARM64 image to Docker Hub"
	@echo "  make pull        - Pull ARM64 image from Docker Hub"
	@echo ""
	@echo "Docker Compose Commands:"
	@echo "  make up          - Start containers in detached mode"
	@echo "  make down        - Stop and remove containers"
	@echo "  make restart     - Restart containers"
	@echo "  make rebuild     - Rebuild and restart containers"
	@echo ""

# Build commands
build:
	docker build --platform=linux/arm64 --build-arg BUILD_TYPE=full -t loredcast/filewizard:arm64 .

build-small:
	docker build --platform=linux/arm64 --build-arg BUILD_TYPE=small -t loredcast/filewizard:arm64-small .

build-cuda:
	docker build --platform=linux/arm64 --build-arg BUILD_TYPE=cuda -t loredcast/filewizard:arm64-cuda .

build-no-cache:
	docker build --platform=linux/arm64 --build-arg BUILD_TYPE=full --no-cache -t loredcast/filewizard:arm64 .


# Docker Compose commands
up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose restart

stop:
	docker compose stop

start:
	docker compose start

rebuild:
	docker compose down
	docker compose build --no-cache
	docker compose up -d
