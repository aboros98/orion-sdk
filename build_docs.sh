#!/bin/bash

# Build Orion documentation
echo "Building Orion documentation..."

# Change to docs directory and build
cd docs
make html

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "✅ Documentation built successfully!"
    echo "📖 Open docs/_build/html/index.html in your browser to view the documentation"
    
    # Try to open the documentation in the default browser
    if command -v open >/dev/null 2>&1; then
        echo "🌐 Opening documentation in browser..."
        open _build/html/index.html
    elif command -v xdg-open >/dev/null 2>&1; then
        echo "🌐 Opening documentation in browser..."
        xdg-open _build/html/index.html
    else
        echo "Please manually open docs/_build/html/index.html in your browser"
    fi
else
    echo "❌ Documentation build failed!"
    exit 1
fi 