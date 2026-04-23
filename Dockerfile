FROM python:3.12-alpine

LABEL maintainer="webkubor"
LABEL description="cicd-init - Auto-detect frontend project and generate CI/CD config"

WORKDIR /app

# Install git (needed for remote detection)
RUN apk add --no-cache git

# Copy source and install
COPY . .
RUN pip install --no-cache-dir .

# Default: show help
ENTRYPOINT ["cicd-init"]
CMD ["--help"]
