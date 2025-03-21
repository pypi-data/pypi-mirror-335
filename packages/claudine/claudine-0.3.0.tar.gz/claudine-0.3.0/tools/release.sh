#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Check if hatch is installed
if ! command -v hatch &> /dev/null; then
    print_error "hatch is not installed. Please install it first."
fi

# Check if twine is installed
if ! command -v twine &> /dev/null; then
    print_error "twine is not installed. Please install it first."
fi

# Get version from pyproject.toml
if [ ! -f "pyproject.toml" ]; then
    print_error "pyproject.toml not found. Are you running this from the project root?"
fi

PROJECT_VERSION=$(grep -E "^version = \"[0-9]+\.[0-9]+\.[0-9]+\"" pyproject.toml | cut -d'"' -f2)
if [ -z "$PROJECT_VERSION" ]; then
    print_error "Could not find version in pyproject.toml"
fi

print_info "Project version from pyproject.toml: $PROJECT_VERSION"

# Get current git tag
CURRENT_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
if [ -z "$CURRENT_TAG" ]; then
    print_error "No git tags found. Please create a tag before releasing."
else
    # Remove 'v' prefix if present
    CURRENT_TAG_VERSION=${CURRENT_TAG#v}
    print_info "Current git tag: $CURRENT_TAG (version: $CURRENT_TAG_VERSION)"
    
    if [ "$PROJECT_VERSION" != "$CURRENT_TAG_VERSION" ]; then
        print_error "Version mismatch: pyproject.toml ($PROJECT_VERSION) != git tag ($CURRENT_TAG_VERSION)"
    fi
    
    # Check if the tag points to the current commit
    CURRENT_COMMIT=$(git rev-parse HEAD)
    TAG_COMMIT=$(git rev-parse "$CURRENT_TAG")
    if [ "$CURRENT_COMMIT" != "$TAG_COMMIT" ]; then
        print_error "Tag $CURRENT_TAG does not point to the current commit. Please update the tag or create a new one."
    fi
fi

# Check if the working directory is clean
if [ -n "$(git status --porcelain)" ]; then
    print_error "Working directory is not clean. Please commit all changes before releasing."
fi

# Check PyPI for existing version
print_info "Checking if version $PROJECT_VERSION already exists on PyPI..."
if curl -f -s "https://pypi.org/pypi/claudine/$PROJECT_VERSION/json" > /dev/null 2>&1; then
    print_error "Version $PROJECT_VERSION already exists on PyPI. Please update the version in pyproject.toml."
fi

# Confirm with the user
echo ""
echo "Ready to publish version $PROJECT_VERSION to PyPI."
read -p "Do you want to continue? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_info "Release cancelled."
    exit 0
fi

# Build the package
print_info "Building package..."
hatch build

# Publish to PyPI
print_info "Publishing to PyPI..."
twine upload dist/*

# Create a new git tag if one doesn't exist for this version
if [ -z "$CURRENT_TAG" ] || [ "$CURRENT_TAG_VERSION" != "$PROJECT_VERSION" ]; then
    print_info "Creating git tag v$PROJECT_VERSION..."
    git tag -a "v$PROJECT_VERSION" -m "Release version $PROJECT_VERSION"
    git push origin "v$PROJECT_VERSION"
fi

print_info "Release completed successfully!"