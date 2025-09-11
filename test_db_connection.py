#!/usr/bin/env python3
"""
Script to test MySQL database connection for SaaS project
"""
import sys
import os

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_mysql_connection():
    """Test MySQL connection using different available libraries"""
    
    # Database configuration from settings.py
    db_config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': 'marshmellox300',  # Empty password as configured
        'database': 'saas'
    }
    
    print("Testing MySQL database connection...")
    print(f"Host: {db_config['host']}")
    print(f"Port: {db_config['port']}")
    print(f"User: {db_config['user']}")
    print(f"Database: {db_config['database']}")
    print("-" * 50)
    
    # Try different MySQL libraries
    connection_successful = False
    
    # Try mysqlclient (recommended for Django)
    try:
        import MySQLdb
        print("✓ Found MySQLdb (mysqlclient)")
        
        conn = MySQLdb.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            passwd=db_config['password'],
            db=db_config['database']
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"✓ Connection successful! MySQL version: {version[0]}")
        
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"✓ Database 'SaaS' exists with {len(tables)} tables")
        
        if tables:
            print("Tables found:")
            for table in tables:
                print(f"  - {table[0]}")
        else:
            print("  No tables found (this is normal for a new database)")
        
        cursor.close()
        conn.close()
        connection_successful = True
        
    except ImportError:
        print("✗ MySQLdb (mysqlclient) not installed")
    except Exception as e:
        print(f"✗ MySQLdb connection failed: {e}")
    
    # Try PyMySQL as alternative
    if not connection_successful:
        try:
            import pymysql
            print("✓ Found PyMySQL")
            
            conn = pymysql.connect(
                host=db_config['host'],
                port=db_config['port'],
                user=db_config['user'],
                password=db_config['password'],
                database=db_config['database']
            )
            
            cursor = conn.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"✓ Connection successful! MySQL version: {version[0]}")
            
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"✓ Database 'SaaS' exists with {len(tables)} tables")
            
            if tables:
                print("Tables found:")
                for table in tables:
                    print(f"  - {table[0]}")
            else:
                print("  No tables found (this is normal for a new database)")
            
            cursor.close()
            conn.close()
            connection_successful = True
            
        except ImportError:
            print("✗ PyMySQL not installed")
        except Exception as e:
            print(f"✗ PyMySQL connection failed: {e}")
    
    # Try mysql-connector-python
    if not connection_successful:
        try:
            import mysql.connector
            print("✓ Found mysql-connector-python")
            
            conn = mysql.connector.connect(
                host=db_config['host'],
                port=db_config['port'],
                user=db_config['user'],
                password=db_config['password'],
                database=db_config['database']
            )
            
            cursor = conn.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"✓ Connection successful! MySQL version: {version[0]}")
            
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"✓ Database 'SaaS' exists with {len(tables)} tables")
            
            if tables:
                print("Tables found:")
                for table in tables:
                    print(f"  - {table[0]}")
            else:
                print("  No tables found (this is normal for a new database)")
            
            cursor.close()
            conn.close()
            connection_successful = True
            
        except ImportError:
            print("✗ mysql-connector-python not installed")
        except Exception as e:
            print(f"✗ mysql-connector-python connection failed: {e}")
    
    print("-" * 50)
    
    if connection_successful:
        print("🎉 DATABASE CONNECTION SUCCESSFUL!")
        print("\nNext steps:")
        print("1. Run: python manage.py makemigrations")
        print("2. Run: python manage.py migrate")
        return True
    else:
        print("❌ DATABASE CONNECTION FAILED!")
        print("\nTroubleshooting steps:")
        print("1. Install MySQL client library:")
        print("   pip install mysqlclient")
        print("   (or pip install PyMySQL)")
        print("2. Make sure MySQL server is running")
        print("3. Verify database 'SaaS' exists in MySQL")
        print("4. Check username/password in settings.py")
        return False

def test_django_connection():
    """Test Django's database connection"""
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        
        import django
        django.setup()
        
        from django.db import connection
        from django.core.management.color import no_style
        
        print("\nTesting Django database connection...")
        
        # Test the connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        if result and result[0] == 1:
            print("✓ Django database connection successful!")
            
            # Get database info
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"✓ MySQL version: {version[0]}")
            
            return True
        else:
            print("✗ Django database connection failed")
            return False
            
    except Exception as e:
        print(f"✗ Django connection test failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("         MYSQL DATABASE CONNECTION TEST")
    print("=" * 60)
    
    # Test direct MySQL connection
    mysql_success = test_mysql_connection()
    
    # Test Django connection if MySQL works
    if mysql_success:
        django_success = test_django_connection()
    
    print("\n" + "=" * 60)
