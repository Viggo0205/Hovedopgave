# Kravopfyldelse: Administrator Fjernelse af Udviklere

## Funktionelle Krav

### 1. ✅ Markere udvikler som slettet
**Krav:** Systemet skal give administratoren mulighed for at markere en udvikler som sletter vedkommende helt fra systemet.

**Implementering:**
- **Soft delete:** `remove_developer()` - [repository.py:491](c:\\Users\\tobia\\OneDrive - Zealand\\datamatiker\\Hovedopgave\\Hovedopgave\\src\\db\\repository.py#L491)
  - Sætter `is_active = FALSE`
  - Bevarer al data for historik
  - Kan genaktiveres
  
- **Hard delete:** `delete_user_permanently()` - [repository.py:662](c:\\Users\\tobia\\OneDrive - Zealand\\datamatiker\\Hovedopgave\\Hovedopgave\\src\\db\\repository.py#L662)
  - Fjerner permanent al brugerdata (GDPR)
  - Cascade delete af relateret data
  - IKKE reversibel

**MCP Tools:**
- `remove_developer(github_username, jira_email, performed_by, reason)`
- `permanently_delete_developer(github_username, jira_email, confirm=True)`

---

### 2. ✅ Undgå i API-svar
**Krav:** Systemet skal sikre, at slettede udviklere ikke optræder i API-svar, rapporter, kompetencelister eller forslag til projekter.

**Implementering:**
- Alle queries har `is_active = TRUE` filter
- `get_user_by_identifier()` - parameter `include_inactive=False` (default)
- `get_users_by_competence()` - parameter `include_inactive=False` (default)
- `get_all_employees()` - filtrerer automatisk inaktive

**Eksempel:**
```sql
WHERE u.is_active = TRUE
```

---

### 3. ✅ Log administrator og tidspunkt
**Krav:** Systemet skal logge, hvilken administrator der har deaktiveret/slettet en udvikler, samt tidspunkt for handlingen.

**Implementering:**

#### Database Schema
- **users.deactivated_by** - Hvem deaktiverede brugeren
- **users.deactivated_at** - Hvornår blev brugeren deaktiveret
- **user_audit_log** tabel - [migration](c:\\Users\\tobia\\OneDrive - Zealand\\datamatiker\\Hovedopgave\\Hovedopgave\\migrations\\add_audit_log_and_admin_tracking.sql)

```sql
CREATE TABLE user_audit_log (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    action VARCHAR(50) NOT NULL,
    performed_by VARCHAR(100),
    performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reason TEXT,
    additional_data JSONB
);
```

#### Audit Log Metoder
- `deactivate_user()` - Logger til audit_log med admin identifier
- `reactivate_user()` - Logger genaktivering
- `get_audit_log()` - Hent audit historik

**MCP Tool:**
- `get_admin_audit_log(user_id, action, limit)` - Vis alle admin handlinger

---

### 4. ✅ GDPR Sletning
**Krav:** Systemet skal slette alt data vedrørende udviklere, udfra GDPR opbevaringstidslov.

**Implementering:**
- `delete_user_permanently()` med CASCADE DELETE
- Fjerner:
  - User profil
  - Alle kompetencer (user_competence)
  - Analyse historik (analysis_archive)
  - Relateret data via CASCADE

**Advarsel:**
```
⚠️ WARNING: This is a hard delete. Data cannot be recovered!
```

---

## Non-Funktionelle Krav

### 1. ⚠️ Administrator Rolle-check
**Krav:** Kun brugere med administratorrollen må kunne deaktivere eller slette udviklere.

**Status:** Delvis implementeret

**Nuværende:**
- `performed_by` parameter er påkrævet
- Validering af parameter eksistens
- TODO kommentar for rolle-check:
```python
# TODO: Add role check here when authentication is implemented
# admin_user = db_repo.get_user_by_identifier(github_username=performed_by)
# if not admin_user or admin_user.get('role_name') != 'Administrator':
#     return {"status": "error", "error": "Unauthorized: Administrator role required"}
```

**Mangler:**
- Fuld autentifikation system
- Rolle verificering mod database
- Session management

**Database struktur klar:**
- `users.role_id` - Foreign key til role tabel
- `role` tabel med rollenavne

---

### 2. ⚠️ Historik bevares anonymiseret
**Krav:** Systemet skal sikre, at data om tidligere projekter og historik fortsat kan bruges i statistiske analyser.

**Nuværende:**
- ✅ **Soft delete:** Bevarer AL data - kan bruges til statistik
- ❌ **Hard delete:** Fjerner ALT - historik går tabt

**Anbefalinger:**
1. Brug soft delete som standard (`is_active = FALSE`)
2. Hard delete kun ved eksplicit GDPR anmodning
3. Implementer anonymisering:
   ```sql
   -- Fremtidig forbedring
   UPDATE analysis_archive 
   SET analysis_data = anonymize_personal_data(analysis_data)
   WHERE user_id = %s;
   ```

---

## Anvendelse

### Fjern udvikler (soft delete)
```python
# Fra Claude Desktop MCP
remove_developer(
    github_username="old_developer",
    performed_by="admin@company.com",
    reason="No longer employed"
)
```

### Se audit log
```python
get_admin_audit_log(
    action="deactivate",
    limit=50
)
```

### Permanent sletning (GDPR)
```python
permanently_delete_developer(
    github_username="user",
    confirm=True
)
```

---

## Kørsel af Migration

For at tilføje audit log og admin tracking:

```bash
psql -U postgres -d developer_skills -f migrations/add_audit_log_and_admin_tracking.sql
```

---

## Opsummering

| Krav | Status | Noter |
|------|--------|-------|
| Markere som slettet | ✅ | Både soft og hard delete |
| Undgå i API-svar | ✅ | `is_active` filter overalt |
| Log admin + tidspunkt | ✅ | Audit log implementeret |
| GDPR sletning | ✅ | CASCADE delete |
| Rolle-check | ⚠️ | TODO - kræver auth system |
| Historik bevares | ⚠️ | Soft delete bevarer, hard delete fjerner |

**Næste skridt:**
1. Implementer fuld autentifikation
2. Tilføj rolle verificering
3. Implementer anonymisering for statistik ved hard delete
