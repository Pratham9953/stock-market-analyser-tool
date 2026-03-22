.PHONY: install dev build lint typecheck test docker-up docker-down

install:
	pnpm install

dev:
	pnpm dev

build:
	pnpm build

lint:
	pnpm lint

typecheck:
	pnpm typecheck

test:
	pnpm test

docker-up:
	pnpm docker:up

docker-down:
	pnpm docker:down
