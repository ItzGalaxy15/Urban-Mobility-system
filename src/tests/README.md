# Urban Mobility System - Test Suite

## Overzicht
Deze test suite valideert de beveiligings- en integriteitsprincipes van het Urban Mobility System.

## Test Categorieën

### 1. SQL Injection Tests (`test_sql_injection.py`)
**Doel:** Valideren dat alle database queries prepared statements gebruiken en geen SQL injection mogelijk is.

**Geteste functionaliteiten:**
- ✓ User CRUD operaties (add, update, delete, search)
- ✓ Traveller CRUD operaties
- ✓ Scooter CRUD operaties
- ✓ Backup/Restore operaties
- ✓ Dynamic field updates (userservice, travellerservice)
- ✓ Search queries met user input

**Test Cases:**
- `test_user_add_with_sql_injection` - Probeert SQL injection via username
- `test_user_update_with_malicious_input` - Test dynamic UPDATE queries
- `test_traveller_search_sql_injection` - Test search functionaliteit
- `test_scooter_search_field_injection` - Test field parameter in search
- `test_backup_restore_path_traversal` - Test file path manipulation

**Verwachte Resultaat:** Alle malicious input wordt veilig behandeld via prepared statements.

---

### 2. Input Validatie Tests (`test_input_validation.py`)
**Doel:** Controleren dat alle user input streng gevalideerd wordt volgens de spec.

**Geteste functionaliteiten:**
- ✓ Username validatie (8-10 chars, start met letter/_)
- ✓ Password complexiteit (12-30 chars, mixed case, digit, special char)
- ✓ Email validatie via `validate_email()` uit `utils.validation`
- ✓ Date validatie + 18+ age check via `validate_birthday()`
- ✓ Numeric range validatie (Scooter model: top_speed, battery_capacity)
- ✓ Whitelist validatie (city, gender) via `validate_city()`, `validate_gender()`
- ✓ NULL byte rejection (username regex)
- ✓ Leading/trailing spaces rejection (names, street, brand, model)

**Test Cases:**
- `test_username_format_validation` - Test UserService.validate_username()
- `test_password_complexity_requirements` - Test UserService.validate_password()
- `test_email_format_validation` - Test `validate_email()` direct
- `test_date_validation_and_age_check` - Test `validate_birthday()` met 18+ check
- `test_numeric_range_validation` - Test Scooter model constraints
- `test_whitelist_validation` - Test `validate_city()` en `validate_gender()`
- `test_null_byte_rejection` - Test NULL byte in username
- `test_leading_trailing_spaces_rejection` - Test `validate_first_name()` trimming

**Implementatie Details:**
- Tests gebruiken **directe imports** van `utils.validation` functies
- Geen wrapper methodes in services nodig
- Validatie functies zijn herbruikbaar en testbaar
- Leading/trailing spaces check toegevoegd aan: names, street_name, brand, model

**Verwachte Resultaat:** Ongeldige input wordt afgewezen met duidelijke foutmeldingen.

---

### 3. Encryptie Tests (`test_encryption.py`)
**Doel:** Valideren dat gevoelige data correct encrypted/decrypted wordt.

**Geteste functionaliteiten:**
- ✓ Field-level encryption (user, traveller, scooter)
- ✓ Password hashing (bcrypt)
- ✓ Encryption consistency (encrypt → decrypt = original)
- ✓ NULL handling in encryption
- ✓ Log entry encryption

**Test Cases:**
- `test_user_field_encryption` - Validate username/role/name encryption
- `test_traveller_field_encryption` - Validate all traveller fields
- `test_scooter_field_encryption` - Validate brand/model/serial encryption
- `test_password_hashing_and_verification` - Test bcrypt hash/check
- `test_encryption_roundtrip` - Test encrypt → store → retrieve → decrypt
- `test_null_value_encryption` - Test NULL handling
- `test_log_entry_encryption` - Test activity log encryption

**Verwachte Resultaat:** Alle encrypted data is onleesbaar in DB, correct decryptable.

---

### 4. Authentication Tests (`test_authentication.py`)
**Doel:** Controleren dat authenticatie correct en veilig werkt.

**Geteste functionaliteiten:**
- ✓ Login met juiste credentials
- ✓ Login met foute credentials
- ✓ Super admin hardcoded login
- ✓ Password reset flow (temp codes)
- ✓ Failed login attempt logging
- ✓ Session management

**Test Cases:**
- `test_successful_login` - Test valid credentials
- `test_failed_login` - Test invalid credentials
- `test_super_admin_login` - Test hardcoded super admin
- `test_password_reset_code_generation` - Test temp code creation
- `test_password_reset_with_code` - Test reset flow
- `test_failed_login_logging` - Test suspicious activity logging
- `test_session_persistence` - Test UserSession state

**Verwachte Resultaat:** Alleen geldige credentials geven toegang, failed attempts worden gelogd.

---

### 5. Authorization Tests (`test_authorization.py`)
**Doel:** Valideren dat role-based access control (RBAC) correct werkt met strikte role hierarchy enforcement.

**Geteste functionaliteiten:**
- ✓ Role hierarchy (super > system_admin > service_engineer)
- ✓ `@require_role` decorator enforcement
- ✓ UserController permission checks voor CRUD operaties
- ✓ Privilege escalation prevention
- ✓ Self-modification restrictions
- ✓ Cross-role boundary enforcement

**Test Cases:**
- `test_role_hierarchy_levels` - Validate ROLE_HIERARCHY definitions
- `test_service_engineer_cannot_add_user` - Service engineers hebben geen user management
- `test_system_admin_can_add_service_engineer` - System admin kan engineers toevoegen
- `test_system_admin_cannot_add_system_admin` - **System admin kan GEEN andere admins maken**
- `test_system_admin_cannot_add_super_admin` - System admin kan geen super admin maken
- `test_super_admin_can_add_any_role` - Super admin heeft alle rechten
- `test_system_admin_cannot_delete_system_admin` - **System admin kan geen andere admins verwijderen**
- `test_users_cannot_modify_higher_roles` - **System admin kan geen super admin wijzigen**
- `test_role_cannot_escalate_own_privileges` - **Users kunnen eigen rol niet verhogen**
- `test_unauthorized_access_returns_error` - Permission denied met duidelijke error
- `test_cross_user_data_access_prevention` - Users kunnen anderen niet wijzigen
- `test_password_reset_permissions` - Validate password reset role checks
- `test_backup_restore_permissions` - Test backup role via has_permission()

**Belangrijke Security Enhancements:**
1. **UserController.add_user()**: System admin kan alleen service_engineers toevoegen
2. **UserController.update_user()**: 
   - System admin kan alleen service_engineers wijzigen
   - Users kunnen eigen rol niet wijzigen (zelfs super admin niet)
   - Dual parameter: `user_id` (actor) en `target_user_id` (target)
3. **UserController.delete_user()**: 
   - System admin kan alleen service_engineers verwijderen
   - System admin kan zichzelf NIET verwijderen
   - Dual parameter voor actor/target onderscheid

**Tests gebruiken UserController:**
- Alle authorization tests roepen **UserController** methodes aan (niet direct service layer)
- Dit test de daadwerkelijke authorization logic zoals gebruikt in productie
- Parameter signature: `user_id` (actor), `target_user_id` (target voor update/delete)

**Verwachte Resultaat:** 
- Strikte role hierarchy enforcement
- Privilege escalation niet mogelijk
- Self-modification geblokkeerd
- Clear separation tussen role levels

---

## Test Uitvoeren

### Alle tests uitvoeren:
```bash
cd src
python -m pytest tests/ -v
```

### Specifieke test file uitvoeren:
```bash
python -m pytest tests/test_sql_injection.py -v
```

### Specifieke test case uitvoeren:
```bash
python -m pytest tests/test_sql_injection.py::test_user_add_with_sql_injection -v
```

### Coverage report genereren:
```bash
python -m pytest tests/ --cov=. --cov-report=html
```

---

## Test Database

Tests gebruiken een aparte test database (`test_urban_mobility.db`) die wordt:
- Aangemaakt vóór elke test run
- Gereset na elke test
- Verwijderd na de test suite

**Let op:** De test database is volledig geïsoleerd van de productie database.

---

## Test Dependencies

Installeer test dependencies:
```bash
pip install pytest pytest-cov
```

---

## Test Resultaten Interpreteren

### ✅ PASSED
- Test is geslaagd
- Functionaliteit werkt zoals verwacht
- Beveiliging is correct geïmplementeerd

### ❌ FAILED
- Test is mislukt
- Er is een beveiligingsprobleem of bug gevonden
- Bekijk de error message voor details

### ⚠ SKIPPED
- Test is overgeslagen (meestal door ontbrekende dependencies)

---

## Nieuwe Tests Toevoegen

1. Maak een nieuw test bestand aan in `tests/`
2. Gebruik `conftest.py` fixtures voor setup/teardown
3. Volg naming convention: `test_*.py` en `test_*()` functions
4. Update deze README met de nieuwe test categorie

---

## Contact

Voor vragen over de tests:
- Chris van der Elst - 1029000
- Aymane Aazouz - 1073235
- Amer Alhasoun - 0992644
