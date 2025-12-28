"""
Setup verification script
Checks if all prerequisites are met before starting data collection
"""

import os
import sys
import subprocess
from pathlib import Path

def check_docker():
    """Check if Docker is installed and running"""
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✓ Docker installed: {result.stdout.strip()}")
            return True
        else:
            print("✗ Docker not found")
            return False
    except FileNotFoundError:
        print("✗ Docker not installed")
        print("  Download from: https://www.docker.com/products/docker-desktop")
        return False
    except Exception as e:
        print(f"✗ Error checking Docker: {e}")
        return False

def check_docker_container():
    """Check if PostgreSQL container is running"""
    try:
        result = subprocess.run(['docker', 'ps', '--filter', 'name=ce49x_postgres', '--format', '{{.Names}}'],
                              capture_output=True, text=True, timeout=5)
        if 'ce49x_postgres' in result.stdout:
            print("✓ PostgreSQL container is running")
            return True
        else:
            print("✗ PostgreSQL container is not running")
            print("  Start it with: docker-compose up -d")
            return False
    except Exception as e:
        print(f"✗ Error checking container: {e}")
        return False

def check_env_file():
    """Check if .env file exists and has required variables"""
    env_path = Path(__file__).parent.parent / '.env'
    
    if not env_path.exists():
        print("✗ .env file not found")
        print(f"  Create it at: {env_path}")
        print("  Copy from .env.example and fill in your values")
        return False
    
    print("✓ .env file exists")
    
    # Check for required variables
    from dotenv import load_dotenv
    load_dotenv(env_path)
    
    required_vars = ['NEWSAPI_KEY', 'DB_HOST', 'DB_USER', 'DB_PASSWORD']
    missing = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value or value == 'your_newsapi_key_here':
            missing.append(var)
    
    if missing:
        print(f"✗ Missing or incomplete variables: {', '.join(missing)}")
        return False
    
    print("✓ All required environment variables are set")
    return True

def check_database_connection():
    """Check if we can connect to the database"""
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from database import DatabaseManager
        
        db = DatabaseManager()
        if db.connect():
            count = db.get_article_count()
            print(f"✓ Database connection successful")
            print(f"  Current articles in database: {count}")
            db.disconnect()
            return True
        else:
            print("✗ Cannot connect to database")
            return False
    except ImportError as e:
        print(f"✗ Cannot import database module: {e}")
        print("  Make sure psycopg2 is installed: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"✗ Database connection error: {e}")
        return False

def check_python_packages():
    """Check if required Python packages are installed"""
    required_packages = {
        'psycopg2': 'psycopg2-binary',
        'newsapi': 'newsapi-python',
        'dotenv': 'python-dotenv',
        'pandas': 'pandas'
    }
    
    missing = []
    for module, package in required_packages.items():
        try:
            __import__(module)
            print(f"✓ {package} installed")
        except ImportError:
            print(f"✗ {package} not installed")
            missing.append(package)
    
    if missing:
        print(f"\n  Install missing packages: pip install {' '.join(missing)}")
        return False
    
    return True

def main():
    """Run all checks"""
    print("=" * 60)
    print("CE49X Final Project - Setup Verification")
    print("=" * 60)
    print()
    
    checks = [
        ("Docker Installation", check_docker),
        ("Docker Container", check_docker_container),
        ("Python Packages", check_python_packages),
        ("Environment File", check_env_file),
        ("Database Connection", check_database_connection),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n[{name}]")
        result = check_func()
        results.append(result)
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    if all(results):
        print("\n✓ All checks passed! You're ready to start data collection.")
        print("\nNext step: python scripts/newsapi_collector.py")
    else:
        print("\n✗ Some checks failed. Please fix the issues above.")
        print("\nFor help, see:")
        print("  - START_HERE.md")
        print("  - DOCKER_SETUP.md")

if __name__ == "__main__":
    main()


