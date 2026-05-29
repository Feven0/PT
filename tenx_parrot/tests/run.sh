

# Show which tests would be run
make test-app-health PYTEST_ARGS="--collect-only -v"

# Show extra test info
make test-app-health PYTEST_ARGS="-vv"

## ---------------------------
# Run all health tests:
## ---------------------------
make test-app-health

# Run only the basic health check test
make test-app-health PYTEST_ARGS="-k test_app_health"

# Run only the configuration test
make test-app-health PYTEST_ARGS="-k test_app_configuration"

# Run only the core services test
make test-app-health PYTEST_ARGS="-k test_core_services"

## ---------------------------
# Run all component tests:
## ---------------------------
make test-app-components

# Test only user repository
make test-app-components PYTEST_ARGS="-k test_user_repository"

# Test only cache system
make test-app-components PYTEST_ARGS="-k test_cache_system"

# Test only external services
make test-app-components PYTEST_ARGS="-k test_external_services"



# Run with detailed output
make test-app-health PYTEST_ARGS="-vv"

# Run with print statements
make test-app-components PYTEST_ARGS="-s"

# Run with both
make test-app-health PYTEST_ARGS="-vv -s"

# Run both user repository and service tests
make test-app-components PYTEST_ARGS="-k 'test_user_repository or test_user_service'"