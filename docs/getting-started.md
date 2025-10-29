# Getting Started with DocsFlow

This guide will walk you through setting up and using the DocsFlow automated documentation pipeline.

## Prerequisites

Before you begin, ensure you have:

- **Git** installed and configured
- **Docker** Desktop running
- **Jenkins** access (or CI/CD tool of choice)
- **Python 3.8+** for local development
- **Fluid Topics** credentials for deployment

## Step 1: Clone the Repository

```bash
git clone https://github.com/Tharun135/DocsFlow.git
cd DocsFlow
```

## Step 2: Local Development Setup

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Build and Preview Locally

```bash
# Build the documentation
mkdocs build

# Serve locally for preview
mkdocs serve
```

Your documentation will be available at `http://localhost:8000`

## Step 3: Docker Setup

### Build the Docker Image

```bash
docker build -t docsflow .
```

### Test the Container

```bash
docker run --rm -v ${PWD}:/app docsflow mkdocs build
```

## Step 4: Configure CI/CD Pipeline

### Jenkins Setup

1. Create a new Jenkins pipeline job
2. Point to your repository
3. Use the provided `Jenkinsfile`
4. Configure these environment variables:
   - `FLUID_USER`: Your Fluid Topics username
   - `FLUID_PASS`: Your Fluid Topics password
   - `FLUID_URL`: Your Fluid Topics portal URL

### Environment Variables

```bash
export FLUID_USER=your_username
export FLUID_PASS=your_password
export FLUID_URL=https://your-portal.fluidtopics.com/api/upload
```

## Step 5: Writing Documentation

### File Structure

Place your Markdown files in the `docs/` directory:

```
docs/
├── index.md          # Homepage
├── getting-started.md # This file
├── style-guide.md     # Writing standards
└── api/              # API documentation
    └── endpoints.md
```

### Best Practices

- Use descriptive filenames
- Include a table of contents for long documents
- Add metadata headers where appropriate
- Follow the [style guide](style-guide.md) for consistency

## Step 6: Deployment Workflow

### Automatic Deployment

1. **Commit** your changes to the `main` branch
2. **Jenkins** automatically triggers the pipeline
3. **Validation** runs linting and quality checks
4. **Build** creates the documentation package
5. **Deploy** uploads to Fluid Topics
6. **Notify** sends status updates to the team

### Manual Deployment

If you need to deploy manually:

```bash
# Run all validation scripts
python scripts/lint_docs.py
python scripts/validate_yaml.py

# Build and upload
python scripts/upload_to_fluidtopics.py
```

## Troubleshooting

### Common Issues

**Pipeline Fails at Lint Stage**
- Check markdown syntax in your files
- Ensure YAML frontmatter is valid
- Review the linting output for specific errors

**Docker Build Errors**
- Verify Docker is running
- Check that all dependencies are in `requirements.txt`
- Ensure file paths are correct in the Dockerfile

**Upload Failures**
- Verify Fluid Topics credentials
- Check network connectivity
- Ensure the API endpoint is accessible

### Getting Help

- Check Jenkins console output for detailed error messages
- Review the documentation in this repository
- Contact the DevOps team for infrastructure issues

### Logs and Monitoring

- **Jenkins Logs**: `http://your-jenkins-url/job/docsflow-pipeline/`
- **Docker Logs**: `docker logs <container-id>`
- **Local Logs**: Check `mkdocs.log` in your project directory

## Next Steps

- Review the [Style Guide](style-guide.md) for writing standards
- Explore advanced MkDocs features and plugins
- Set up monitoring and alerting for your pipeline
- Consider implementing branch-based previews for pull requests