# Session-Based Job Scoping

Session-based job scoping provides anonymous, browser-session-based job isolation. This feature is **only available in LOCAL_ONLY mode** (anonymous access).

## Configuration

```bash
# Enable session-based scoping (requires LOCAL_ONLY=True)
export SESSION_BASED_SCOPING=True
export LOCAL_ONLY=True
```

**Important**: `SESSION_BASED_SCOPING=True` is only allowed when `LOCAL_ONLY=True`. The application will refuse to start if you try to enable session-based scoping with authentication enabled.

## Behavior

### When SESSION_BASED_SCOPING=True (with LOCAL_ONLY=True):
- Each browser session gets a unique session ID stored in localStorage
- Jobs are scoped to the session ID instead of user authentication
- Multiple browser windows/tabs will have different session IDs
- Jobs from one session are not visible in another session

### When SESSION_BASED_SCOPING=False:

#### With LOCAL_ONLY=True (default):
- All users see all jobs (original behavior)
- No job isolation between sessions

#### With LOCAL_ONLY=False:
- Uses real user authentication (OIDC)
- Jobs are scoped by authenticated user identity
- Requires OIDC configuration

## Three Modes of Operation

1. **Anonymous Sessions** (`SESSION_BASED_SCOPING=True`, `LOCAL_ONLY=True`):
   - Browser sessions get unique IDs
   - Jobs isolated per session
   - No user authentication required

2. **Shared Anonymous** (`SESSION_BASED_SCOPING=False`, `LOCAL_ONLY=True`):
   - Original behavior
   - All users share job history
   - No authentication

3. **Authenticated Users** (`SESSION_BASED_SCOPING=False`, `LOCAL_ONLY=False`):
   - Real user authentication via OIDC
   - Jobs scoped by user identity
   - Requires OIDC configuration

## Database Migration

### Automatic Migration (Recommended)

When you enable `SESSION_BASED_SCOPING=True`, the application will **automatically migrate** your database on startup:

```bash
export SESSION_BASED_SCOPING=True
python main.py
# App will automatically add session_id column if missing
```

**Benefits:**
- ✅ Zero-downtime migration
- ✅ Works in Docker/Kubernetes
- ✅ No manual intervention needed
- ✅ Safe rollback (just disable SESSION_BASED_SCOPING)

### Manual Migration (Alternative)

If you prefer to migrate manually:

```bash
# Backup first (recommended)
cp jobs.db jobs.db.backup

# Run migration
python migrate_session_scoping.py
```

### Docker Compose

The migration happens automatically when the container starts:

```yaml
services:
  filewizard:
    image: filewizard:latest  # Use local image name
    build:
      context: .
      target: full-final
    environment:
      # Enable session scoping (triggers auto-migration)
      - SESSION_BASED_SCOPING=True
      - LOCAL_ONLY=True

      # Configure automatic file cleanup
      - FILE_CLEANUP_ENABLED=true
      - UPLOAD_FILE_RETENTION=86400     # 24 hours
      - PROCESSED_FILE_RETENTION=604800 # 7 days

    volumes:
      - ./data/jobs.db:/app/jobs.db          # Persistent DB with auto-migration
      - ./data/uploads:/app/uploads          # File storage
      - ./data/processed:/app/processed

    ports:
      - "8000:8000"
```

### First-Time Setup Process

**Build the image:**
```bash
docker-compose build
```

**Start the container:**
```bash
docker-compose up
```

**What happens automatically:**
1. **Database Creation**: SQLite database is created if it doesn't exist
2. **Auto-Migration**: App detects `SESSION_BASED_SCOPING=True` and missing `session_id` column
3. **Schema Update**: Adds `session_id` column and index automatically
4. **Service Startup**: App starts with session-based job scoping enabled

**Expected logs:**
```
✓ Auto-migration completed: added session_id column and index
✓ Session-based scoping database schema verified.
INFO: File cleanup thread started.
```

**Zero manual intervention required!** 🚀

## Cloudflare/CDN Compatibility

Session scoping works seamlessly through Cloudflare and other CDNs:

### **Automatic Fallback Storage**
- **Primary**: localStorage (fastest, most reliable)
- **Fallback 1**: sessionStorage (per-tab isolation)
- **Fallback 2**: HTTP Cookies (works through all proxies/CDNs)

### **Why Multiple Storage Methods?**
Some production environments restrict localStorage access:
- **HTTPS requirements**: localStorage behaves differently over HTTPS
- **Browser security policies**: Some contexts disable localStorage
- **Incognito/Private browsing**: localStorage is limited or disabled
- **CDN caching**: May interfere with dynamic content

### **How It Works**
1. **Tries localStorage first** (fastest, most reliable)
2. **Falls back to sessionStorage** (if localStorage unavailable)
3. **Uses cookies as last resort** (always works through CDNs)
4. **Syncs session ID** across all available storage methods

### **Debugging Production Issues**
```javascript
// Check current session and storage locations
getFileWizardSessionId()

// Clear all session storage (useful for testing)
clearFileWizardSession()

// Run comprehensive storage diagnostic
// Load session_debug.js in browser console, then:
debugSessionStorage()
```

**Result**: Session scoping works reliably in all deployment environments! 🌐

## Session Isolation Levels

Choose how strictly to isolate sessions:

### Per-Window Isolation (Recommended Default)
```javascript
const USE_SESSION_STORAGE = false; // Uses localStorage
```
- **Same browser, different tabs**: Same session ID ✅
- **Different browser windows**: Different session IDs ✅
- **Different browsers**: Different session IDs ✅
- **Incognito/Private**: Different session IDs ✅

**Why this makes sense:**
- Users often open results/downloads in new tabs
- Natural workflow: "I uploaded a file in one tab, I should see it in another"
- Less confusing for typical usage patterns

### Per-Tab Isolation (Advanced)
```javascript
const USE_SESSION_STORAGE = true; // Uses sessionStorage
```
- **Every tab/window**: Different session ID
- **Same browser, different tabs**: Different session IDs
- **Tab close**: Session lost

**When this might be useful:**
- Classroom demonstrations (each student gets their own tab)
- Testing different conversion scenarios
- Shared browser environments
- Maximum isolation requirements

### Changing Isolation Level

Edit `static/js/script.js`:
```javascript
const USE_SESSION_STORAGE = true; // true = per-tab, false = per-window
```

**Note**: Existing sessions will continue until localStorage/sessionStorage is cleared.

## Debugging Session IDs

If session IDs aren't appearing in API calls:

### 1. Check Browser Console
Open browser developer tools and look for:
```
[Session] Generated new session_id: abc123...
[Session] Adding session_id=abc123... to /jobs
```

### 2. Check Network Tab
- Open Network tab in developer tools
- Make the app load jobs (or trigger any action)
- Look for requests to `/jobs`, `/convert-file`, etc.
- Check the URL/query parameters for `session_id=...`

### 3. Manual Session Check
Run in browser console:
```javascript
getFileWizardSessionId()  // Should return current session ID
```

### 4. Test Page
Open `session_test.html` in your browser to verify session scoping is working.

### 5. Clear Session for Testing
```javascript
localStorage.removeItem('filewizard_session_id')
```
Then refresh the page to generate a new session ID.

## Troubleshooting

**Issue: No session_id in API calls**
- Check browser console for JavaScript errors
- Verify `SESSION_BASED_SCOPING=true` in environment
- Check that requests are going to expected endpoints

**Issue: Same session across browsers**
- Each browser tab/window should have different session IDs
- Clear localStorage if sessions are persisting incorrectly

**Issue: API returns no jobs**
- Check that session_id is being sent with requests
- Verify backend is filtering by session_id when SESSION_BASED_SCOPING=true

**Issue: Session ID not persisting through Cloudflare/CDN**
- localStorage blocked or unavailable in production environment
- Check browser console for `[Session]` messages and errors
- System automatically falls back to cookies if localStorage fails
- Run `getFileWizardSessionId()` in browser console to debug storage
- Run `clearFileWizardSession()` to reset all session storage

## File Cleanup

The system automatically cleans up old files to manage disk space:

### Configuration (Environment Variables)
```bash
# Enable/disable automatic file cleanup
FILE_CLEANUP_ENABLED=true

# How often to check for old files (seconds)
FILE_CLEANUP_INTERVAL=3600

# Retention times (seconds)
UPLOAD_FILE_RETENTION=86400      # Keep uploads for 24 hours
PROCESSED_FILE_RETENTION=604800  # Keep processed files for 7 days
TEMP_FILE_RETENTION=3600         # Clean temp files after 1 hour

# Session isolation level (JavaScript setting)
USE_SESSION_STORAGE=false        # false=per-window (recommended), true=per-tab
```

These settings are configured via environment variables for security - they cannot be viewed or modified by anonymous users through the web interface.

### What Gets Cleaned
- **Upload files**: Original uploaded files after retention period
- **Processed files**: Converted/transcribed files after longer retention
- **Temp files**: Chunked upload fragments after short retention
- **Empty directories**: Automatically removed empty subdirectories

### Session-Aware Cleanup
When session-based scoping is enabled, files are cleaned based on their age regardless of session activity. This ensures disk space is managed efficiently even with many anonymous sessions.

## Testing

1. Open the app in two different browser windows
2. Upload a file in the first window
3. Check that the job only appears in the first window's history
4. Upload a file in the second window  
5. Verify each window only sees its own jobs

