# TODO - Test Coverage Improvements

This document tracks test coverage gaps and recommendations for the gazpar2haws project.

## Summary

Current test coverage analysis reveals critical gaps in configuration loading, model validation, and error handling. While core functionality (pricer, haws, date_array) has good coverage, the foundation layers need significant improvement.

---

## 🔴 CRITICAL Priority

### 1. config_utils.py - NO TEST COVERAGE (0%)

**File:** `tests/test_config_utils.py` (NEW FILE NEEDED)

The configuration loading system has zero dedicated tests, making it the highest risk area.

**Tests to add:**

```python
# Basic functionality
- [ ] test_load_secrets_success
- [ ] test_load_config_success
- [ ] test_resolve_secrets_basic
- [ ] test_resolve_secrets_nested_dict
- [ ] test_resolve_secrets_nested_list
- [ ] test_get_nested_key_success
- [ ] test_get_nested_key_with_default
- [ ] test_dict_returns_config
- [ ] test_dumps_returns_yaml

# Error handling
- [ ] test_load_secrets_file_not_found
- [ ] test_load_config_file_not_found
- [ ] test_resolve_secrets_missing_key_raises
- [ ] test_get_missing_key_returns_default
- [ ] test_invalid_yaml_syntax

# Environment variable substitution
- [ ] test_environment_variable_substitution_in_secrets
- [ ] test_environment_variable_missing_raises
```

**Impact:** Configuration bugs affect the entire application startup and runtime.

---

## 🟠 HIGH Priority

### 2. model.py - Minimal Validation Testing (~10%)

**File:** `tests/test_model.py` (NEW FILE NEEDED)

Model validation logic is only tested indirectly through integration tests.

**Tests to add:**

```python
# Device validation
- [ ] test_device_valid_configuration
- [ ] test_device_invalid_data_source_raises
- [ ] test_device_missing_username_raises
- [ ] test_device_missing_password_raises
- [ ] test_device_missing_pce_identifier_raises
- [ ] test_device_tmp_dir_defaults_to_system_temp
- [ ] test_device_tmp_dir_custom_path
- [ ] test_device_excel_invalid_tmp_dir_raises
- [ ] test_device_test_source_skips_validation

# CompositePriceValue propagation
- [ ] test_composite_price_property_propagation
- [ ] test_composite_price_default_units
- [ ] test_composite_price_vat_id_propagation
- [ ] test_composite_price_price_unit_propagation
- [ ] test_composite_price_quantity_unit_propagation
- [ ] test_composite_price_time_unit_propagation

# ValueArray initialization
- [ ] test_value_array_auto_initialization
- [ ] test_composite_price_array_auto_initialization

# Edge cases
- [ ] test_device_all_fields_optional_for_test_source
- [ ] test_timezone_default_value
- [ ] test_last_days_default_value
- [ ] test_reset_default_value
```

**Impact:** Validation bugs can cause runtime errors or incorrect data processing.

---

### 3. bridge.py - Minimal Testing (~20%)

**File:** `tests/test_bridge.py` (EXPAND EXISTING)

Bridge orchestration has only 1 integration test.

**Tests to add:**

```python
# Signal handling
- [ ] test_handle_signal_sigint_sets_interrupted
- [ ] test_handle_signal_sigterm_sets_interrupted
- [ ] test_await_with_interrupt_respects_interrupt
- [ ] test_await_with_interrupt_completes_if_not_interrupted

# Device handling
- [ ] test_single_device_success
- [ ] test_multiple_devices_all_succeed
- [ ] test_multiple_devices_one_fails_continues_with_others
- [ ] test_device_failure_logs_error

# Scan interval behavior
- [ ] test_scan_interval_zero_runs_once_and_exits
- [ ] test_scan_interval_positive_loops_continuously
- [ ] test_scan_interval_interrupted_exits_loop

# Error scenarios
- [ ] test_all_devices_fail_continues_to_next_scan
- [ ] test_homeassistant_connection_failure_handled
- [ ] test_grdf_connection_failure_handled
```

**Impact:** Bridge is the main orchestrator; bugs affect reliability and error recovery.

---

## 🟡 MEDIUM Priority

### 4. gazpar.py - Partial Coverage (~60%)

**File:** `tests/test_gazpar.py` (EXPAND EXISTING)

Main business logic has gaps in error handling and edge cases.

**Tests to add:**

```python
# extract_property_from_daily_gazpar_history
- [ ] test_extract_property_success
- [ ] test_extract_property_missing_time_period
- [ ] test_extract_property_missing_property_name
- [ ] test_extract_property_invalid_date_format
- [ ] test_extract_property_empty_history
- [ ] test_extract_property_type_absence_de_donnees

# as_of_date
- [ ] test_as_of_date_returns_today_if_none
- [ ] test_as_of_date_returns_configured_date
- [ ] test_as_of_date_in_past
- [ ] test_as_of_date_in_future

# Error handling
- [ ] test_publish_grdf_api_failure
- [ ] test_publish_homeassistant_unreachable
- [ ] test_publish_incomplete_grdf_data
- [ ] test_publish_pricing_computation_error

# Cost breakdown (unit tests)
- [ ] test_publish_cost_breakdown_all_five_entities
- [ ] test_publish_cost_breakdown_correct_values
- [ ] test_publish_no_cost_when_pricing_not_configured
- [ ] test_publish_cost_queries_all_five_sensors

# Edge cases
- [ ] test_publish_no_new_data_since_last_scan
- [ ] test_publish_reset_true_clears_all_entities
- [ ] test_publish_handles_timezone_correctly
```

**Impact:** Gazpar is the core data processor; error handling gaps can cause data loss.

---

### 5. pricer.py - Good but Missing Edge Cases (~75%)

**File:** `tests/test_pricer.py` (EXPAND EXISTING)

Pricer has good coverage but lacks error handling and edge case tests.

**Tests to add:**

```python
# Helper methods
- [ ] test_fill_composite_component_array_quantity
- [ ] test_fill_composite_component_array_time
- [ ] test_fill_composite_component_array_empty_list
- [ ] test_fill_composite_quantity_array_wrapper
- [ ] test_fill_composite_time_array_wrapper

# Error handling
- [ ] test_get_composite_price_array_invalid_vat_id
- [ ] test_compute_invalid_price_unit
- [ ] test_compute_negative_quantities_raises
- [ ] test_get_vat_rate_array_missing_vat_id

# Edge cases
- [ ] test_compute_all_prices_zero
- [ ] test_compute_zero_quantities
- [ ] test_compute_empty_price_arrays
- [ ] test_get_composite_price_array_future_dates
- [ ] test_get_composite_price_array_past_dates_only
- [ ] test_convert_with_same_units_returns_unchanged

# VAT edge cases
- [ ] test_vat_rate_interpolation_across_periods
- [ ] test_vat_rate_missing_for_date_uses_nearest
```

**Impact:** Pricer bugs affect billing accuracy; edge cases can cause incorrect costs.

---

### 6. configuration.py - Partial Testing (~50%)

**File:** `tests/test_configuration.py` (EXPAND EXISTING)

Configuration class has minimal testing (only 1 assertion).

**Tests to add:**

```python
# Configuration loading
- [ ] test_configuration_load_success
- [ ] test_configuration_all_fields_populated
- [ ] test_configuration_grdf_devices_loaded
- [ ] test_configuration_pricing_loaded
- [ ] test_configuration_homeassistant_loaded
- [ ] test_configuration_logging_loaded

# Validation through pydantic
- [ ] test_configuration_invalid_structure_raises
- [ ] test_configuration_missing_required_fields_raises
- [ ] test_configuration_invalid_device_raises

# Multiple devices
- [ ] test_configuration_multiple_devices
- [ ] test_configuration_device_with_pricing
- [ ] test_configuration_device_without_pricing
```

**Impact:** Configuration parsing errors affect application startup.

---

## 🟢 LOW Priority

### 7. haws.py - Well Tested (~85%)

**File:** `tests/test_haws.py` (MINOR ADDITIONS)

Good coverage, only minor gaps.

**Tests to add:**

```python
# Error handling
- [ ] test_connect_authentication_failure
- [ ] test_connect_websocket_connection_refused
- [ ] test_connect_timeout

# Edge cases
- [ ] test_import_statistics_empty_list
- [ ] test_clear_statistics_empty_list
- [ ] test_get_last_statistic_no_statistics_available
```

**Impact:** Low; already well-tested.

---

### 8. date_array.py - Well Tested (~80%)

**File:** `tests/test_date_array.py` (MINOR ADDITIONS)

Good coverage, only edge cases missing.

**Tests to add:**

```python
# Edge cases
- [ ] test_date_array_empty
- [ ] test_date_array_single_element
- [ ] test_slice_empty_range
- [ ] test_slice_inverted_range
- [ ] test_cumsum_empty_array
```

**Impact:** Low; already well-tested.

---

## 📊 Test Coverage Goals

| Module | Current | Target | Priority |
|--------|---------|--------|----------|
| config_utils.py | 0% | 90%+ | 🔴 CRITICAL |
| model.py | 10% | 80%+ | 🟠 HIGH |
| bridge.py | 20% | 80%+ | 🟠 HIGH |
| gazpar.py | 60% | 85%+ | 🟡 MEDIUM |
| pricer.py | 75% | 90%+ | 🟡 MEDIUM |
| configuration.py | 50% | 80%+ | 🟡 MEDIUM |
| haws.py | 85% | 90%+ | 🟢 LOW |
| date_array.py | 80% | 90%+ | 🟢 LOW |

**Overall Goal:** 85%+ test coverage across all modules

---

## 🎯 Quick Wins (High Value, Low Effort)

These tests provide maximum value with minimal implementation effort:

```python
# tests/test_config_utils.py
1. test_resolve_secrets_basic
2. test_resolve_secrets_missing_key_raises
3. test_get_nested_key

# tests/test_model.py
4. test_device_invalid_data_source
5. test_device_tmp_dir_defaults_to_system_temp
6. test_composite_price_property_propagation

# tests/test_gazpar.py
7. test_extract_property_from_daily_gazpar_history
8. test_as_of_date

# tests/test_bridge.py
9. test_handle_signal
10. test_multiple_devices
```

**Estimated effort:** 2-3 hours for all 10 tests
**Impact:** Covers the most critical untested code paths

---

## 🔧 Implementation Guidelines

### Test Structure
- Use pytest fixtures for common setup
- Mock external dependencies (GrDF API, Home Assistant)
- Use `pytest.raises` for exception testing
- Use `pytest.mark.asyncio` for async tests
- Use `@pytest.mark.parametrize` for multiple test cases

### Test Naming Convention
- `test_<function>_<scenario>_<expected_result>`
- Example: `test_load_secrets_file_not_found_raises`

### Mock Strategy
- Mock PyGazpar for GrDF data
- Mock WebSocket for Home Assistant
- Use `unittest.mock.patch` or `pytest-mock`
- Prefer dependency injection where possible

### Coverage Measurement
```bash
# Run with coverage
poetry run pytest --cov=gazpar2haws --cov-report=html

# View report
open htmlcov/index.html
```

---

## 📅 Suggested Implementation Schedule

### Phase 1 - Critical (Week 1)
- [ ] Create `tests/test_config_utils.py` with all tests
- [ ] Create `tests/test_model.py` with Device validation tests
- [ ] Add signal handling tests to `tests/test_bridge.py`

### Phase 2 - High Priority (Week 2)
- [ ] Add CompositePriceValue propagation tests to `tests/test_model.py`
- [ ] Add multi-device tests to `tests/test_bridge.py`
- [ ] Add error handling tests to `tests/test_gazpar.py`

### Phase 3 - Medium Priority (Week 3)
- [ ] Add edge case tests to `tests/test_pricer.py`
- [ ] Add property extraction tests to `tests/test_gazpar.py`
- [ ] Expand `tests/test_configuration.py`

### Phase 4 - Polish (Week 4)
- [ ] Add remaining edge cases to `tests/test_haws.py`
- [ ] Add remaining edge cases to `tests/test_date_array.py`
- [ ] Run full coverage report and address remaining gaps

---

## 📚 Additional Test Documentation Needs

### Integration Tests
- [ ] Document which tests require Home Assistant container
- [ ] Create docker-compose for test environment
- [ ] Add integration test documentation to README

### Test Data
- [ ] Document test configuration files in `tests/config/`
- [ ] Add more example configurations for edge cases
- [ ] Create test data generator for GrDF responses

### CI/CD
- [ ] Add coverage reporting to GitHub Actions
- [ ] Add coverage badge to README
- [ ] Set minimum coverage threshold (e.g., 80%)
- [ ] Fail CI if coverage drops below threshold

---

## 🐛 Known Issues to Test

Based on code review, these specific scenarios should have tests:

1. **config_utils.py line 44**: Secret key not found - needs explicit test
2. **model.py line 69**: Invalid data_source - needs test with actual invalid value
3. **model.py line 76**: Invalid tmp_dir for excel - needs test
4. **gazpar.py line 101**: HA clear_statistics exception - needs test
5. **gazpar.py line 305**: HA import_statistics exception - needs test
6. **pricer.py**: VAT ID not found in dictionary - needs test
7. **bridge.py line 51**: Signal handler - needs test for both SIGINT and SIGTERM

---

## ✅ Recently Completed (v0.4.0)

- [x] Cost breakdown functionality tested through integration tests
- [x] All 5 cost entities verified in test_publish
- [x] CompositePriceArray tested with quantity/time scenarios
- [x] CostBreakdown structure verified
- [x] Cross-platform tmp_dir fix tested

---

## 📝 Notes

- Tests should be added incrementally to avoid blocking development
- Each PR should maintain or improve test coverage
- Critical bugs should trigger new test cases
- Regular coverage reviews (monthly) recommended

---

**Last Updated:** 2025-10-30
**Version:** 0.4.0
**Next Review:** When starting v0.5.0 development
