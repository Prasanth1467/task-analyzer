#!/bin/bash

# Deployment Setup Helper Script
# This script helps you prepare for deployment

echo "🚀 Smart Task Analyzer - Deployment Setup"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

echo "📋 This script will help you:"
echo "   1. Generate a Django SECRET_KEY"
echo "   2. Show you what environment variables you need"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "🔑 Generating Django SECRET_KEY..."
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2>/dev/null)

if [ -z "$SECRET_KEY" ]; then
    echo "⚠️  Could not generate SECRET_KEY automatically."
    echo "   Please run: python -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\""
else
    echo "✅ Your SECRET_KEY:"
    echo "   $SECRET_KEY"
    echo ""
    echo "📝 Copy this for your Render environment variables!"
fi

echo ""
echo "📝 Environment Variables Checklist:"
echo ""
echo "=== RENDER (Backend) ==="
echo "SECRET_KEY = <generated-above>"
echo "DEBUG = False"
echo "ALLOWED_HOSTS = your-app-name.onrender.com"
echo "CORS_ALLOWED_ORIGINS = https://your-vercel-app.vercel.app"
echo "DATABASE_URL = <auto-set-if-using-postgres>"
echo ""
echo "=== VERCEL (Frontend) ==="
echo "No environment variables needed (update index.html instead)"
echo ""
echo "📖 For detailed instructions, see DEPLOYMENT.md"
echo ""
echo "✅ Setup complete! Good luck with deployment! 🎉"


