DS ?= all

.PHONY: build dev debug course course-push add-worktree test-benchmark

build:
	uv run langgraph build -t langgraph-python-agent:$(TAG)

dev:
	uv run langgraph dev --host 0.0.0.0 --port 80

debug:
	uv run langgraph dev --host 0.0.0.0 --port 80 --debug-port 5678

course:
	uv run python scripts/course.py

test-benchmark:
	BENCHMARK_DATASET="$(DS)" uv run pytest -q -s --tb=no tests/benchmarks/test_benchmark.py

course-push:
	@[ -n "$(SHA)" ] || (echo "请提供提交 hash: make course-push SHA=<hash>" && exit 1)
	uv run python scripts/course-push.py $(SHA)

add-worktree:
	git worktree add -b ai-eval/$(branch) /Volumes/数据盘/AppData/worktrees/ai-eval/$(branch)
	rsync -a --exclude='.git' --exclude='.venv' --exclude='__pycache__' --exclude='.DS_Store' ./ /Volumes/数据盘/AppData/worktrees/ai-eval/$(branch)/

remove-worktree:
	git worktree remove --force /Volumes/数据盘/AppData/worktrees/ai-eval/$(branch)
	git branch -D ai-eval/$(branch)
