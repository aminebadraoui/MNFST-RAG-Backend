"""
Test script to verify database connection pool configuration
"""
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_single_connection():
    """Test a single database connection"""
    from app.database import get_session, get_pool_status
    
    print("Testing single connection...")
    try:
        with next(get_session()) as session:
            result = session.exec("SELECT 1").first()
            print(f"Query result: {result}")
            
        pool_status = get_pool_status()
        print(f"Pool status after single connection: {pool_status}")
        return True
    except Exception as e:
        print(f"Single connection test failed: {e}")
        return False

def test_concurrent_connections(num_connections=10):
    """Test multiple concurrent connections"""
    from app.database import get_session, get_pool_status
    
    print(f"\nTesting {num_connections} concurrent connections...")
    
    def make_connection():
        try:
            with next(get_session()) as session:
                result = session.exec("SELECT 1, pg_sleep(0.1)").first()
                return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    # Run connections concurrently
    with ThreadPoolExecutor(max_workers=num_connections) as executor:
        futures = [executor.submit(make_connection) for _ in range(num_connections)]
        results = [f.result() for f in futures]
    
    success_count = sum(results)
    print(f"Successful connections: {success_count}/{num_connections}")
    
    pool_status = get_pool_status()
    print(f"Pool status after concurrent test: {pool_status}")
    
    return success_count == num_connections

def test_pool_exhaustion():
    """Test behavior when pool is exhausted"""
    from app.database import get_session, get_pool_status
    import time
    
    print("\nTesting pool exhaustion behavior...")
    
    # Get current pool settings
    pool_status = get_pool_status()
    print(f"Initial pool status: {pool_status}")
    
    # Try to get more connections than pool allows
    connections = []
    try:
        for i in range(20):  # Try to get 20 connections
            try:
                session = next(get_session())
                connections.append(session)
                print(f"Got connection {i+1}")
            except Exception as e:
                print(f"Failed to get connection {i+1}: {e}")
                break
        
        pool_status = get_pool_status()
        print(f"Pool status with max connections: {pool_status}")
        
    finally:
        # Close all connections
        for session in connections:
            session.close()
        
        time.sleep(1)  # Give pool time to recover
        pool_status = get_pool_status()
        print(f"Pool status after cleanup: {pool_status}")

def main():
    """Run all connection pool tests"""
    print("=" * 60)
    print("DATABASE CONNECTION POOL TESTS")
    print("=" * 60)
    
    # Check environment
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("ERROR: DATABASE_URL not set in environment")
        return
    
    print(f"Database URL: {db_url.split('@')[0] if '@' in db_url else 'URL not set'}...")
    
    # Run tests
    test1 = test_single_connection()
    test2 = test_concurrent_connections(10)
    test_pool_exhaustion()
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Single connection test: {'PASSED' if test1 else 'FAILED'}")
    print(f"Concurrent connections test: {'PASSED' if test2 else 'FAILED'}")
    
    if test1 and test2:
        print("\nAll tests PASSED! Connection pool is working correctly.")
    else:
        print("\nSome tests FAILED. Check your pool configuration.")

if __name__ == "__main__":
    main()