# WordPress REST API Setup Guide

## 🌐 Overview

Nexuzy Publisher Desk integrates with WordPress using the **WordPress REST API** to publish articles directly from the application. This guide will walk you through setting up WordPress for seamless integration.

---

## 📝 Prerequisites

- WordPress **5.6+** (for Application Passwords feature)
- WordPress site with **HTTPS** enabled (required for REST API)
- Admin or Editor access to WordPress
- Plugin permissions (if REST API is disabled)

---

## ⚙️ Step-by-Step Setup

### Step 1: Verify REST API is Enabled

WordPress REST API is enabled by default. To verify:

**Test REST API Endpoint:**
```bash
curl https://yoursite.com/wp-json/wp/v2/posts
```

**Expected Response:** JSON array of posts (or error if authentication required)

If you get a **404 error**, the REST API might be disabled by a plugin. Check:

1. **Disable REST API** plugins - Temporarily disable any security plugins
2. **Permalink Settings** - Go to Settings → Permalinks and click "Save Changes"
3. **.htaccess** - Ensure WordPress can write to `.htaccess`

---

### Step 2: Generate Application Password

Application Passwords provide secure authentication without using your main WordPress password.

**2.1 Navigate to User Profile**
```
WordPress Admin Dashboard
└─ Users
   └─ Profile (or Your Profile)
```

**2.2 Scroll to "Application Passwords" Section**

![Application Passwords Section](https://i.imgur.com/XXXXXXX.png)

**2.3 Create New Application Password**
```
1. Application Name: Nexuzy Publisher Desk
2. Click "Add New Application Password"
3. COPY the generated password (shown ONLY ONCE)
```

**Example Generated Password:**
```
AbCd EfGh IjKl MnOp QrSt UvWx
```

⚠️ **IMPORTANT:** Remove spaces when entering in Nexuzy:
```
AbCdEfGhIjKlMnOpQrStUvWx
```

**2.4 Save Password Securely**
- Store in password manager
- Never share publicly
- Can be revoked anytime

---

### Step 3: Configure in Nexuzy Publisher Desk

**3.1 Open WordPress Settings**
```
Nexuzy Publisher Desk
└─ 🌐 WordPress (left sidebar)
```

**3.2 Enter Credentials**

| Field | Value | Example |
|-------|-------|----------|
| **Site URL** | Your WordPress site URL | `https://myblog.com` |
| **Username** | Your WordPress username | `admin` or `editor123` |
| **App Password** | Generated password (no spaces) | `AbCdEfGhIjKlMnOpQrStUvWx` |

**3.3 Test Connection**
```
Click "🔗 Test Connection"
```

**Success:** ✓ Green message "WordPress connection successful!"

**Failure:** See [Troubleshooting](#-troubleshooting) below

**3.4 Save Configuration**
```
Click "💾 Save"
```

Credentials are stored locally in `nexuzy.db` (encrypted in future versions)

---

## 🚀 Publishing Workflow

### Publishing a Draft

**Step 1: Edit Draft**
```
1. Go to "✏️ Editor"
2. Review AI-generated draft
3. Edit headline and body
4. Check ✓ "Edited by Human"
5. Click "💾 Save Draft"
```

**Step 2: Publish to WordPress**
```
Click "📤 Send to WordPress"
```

**What Happens:**
1. Nexuzy sends POST request to `/wp-json/wp/v2/posts`
2. WordPress creates draft post
3. Categories and tags auto-assigned
4. Returns WordPress post ID and URL
5. Nexuzy stores WordPress post ID for tracking

**Result:**
```
✓ Published to WordPress!
URL: https://yourblog.com/2026/01/22/your-article-title/
```

---

## 🔑 REST API Authentication

### Authentication Methods

Nexuzy uses **Basic Authentication with Application Password**:

```http
POST /wp-json/wp/v2/posts HTTP/1.1
Host: yourblog.com
Authorization: Basic base64(username:app_password)
Content-Type: application/json

{
  "title": "Article Title",
  "content": "Article body...",
  "status": "draft",
  "categories": [1, 5],
  "tags": [10, 15]
}
```

### Supported Endpoints

Nexuzy uses these WordPress REST API endpoints:

| Endpoint | Method | Purpose |
|----------|--------|----------|
| `/wp-json/wp/v2/posts` | GET | Test connection |
| `/wp-json/wp/v2/posts` | POST | Create new post |
| `/wp-json/wp/v2/posts/{id}` | PUT | Update existing post |
| `/wp-json/wp/v2/categories` | GET | Fetch categories |
| `/wp-json/wp/v2/tags` | GET | Fetch tags |

---

## 🔒 Security Best Practices

### 1. Use HTTPS

⚠️ **NEVER use HTTP** - Application passwords are sent via Basic Auth

```bash
# Good
https://yourblog.com

# Bad (insecure!)
http://yourblog.com
```

### 2. Application Password Permissions

- Application passwords inherit user role permissions
- Use **Editor** or **Author** role (not Administrator)
- Create dedicated user for Nexuzy if needed

### 3. Revoke Unused Passwords

```
WordPress Admin → Users → Profile → Application Passwords
└─ Click "Revoke" on unused passwords
```

### 4. Monitor API Usage

Use plugins to monitor REST API activity:
- **WP Activity Log** - Tracks all API requests
- **Wordfence** - Security monitoring

---

## 🐛 Troubleshooting

### Issue 1: "Connection Failed"

**Symptoms:** Test connection fails with error

**Solutions:**

1. **Check URL Format**
   ```bash
   # Correct
   https://yourblog.com
   
   # Incorrect
   https://yourblog.com/
   https://yourblog.com/wp-admin/
   ```

2. **Verify HTTPS**
   - Site must use HTTPS
   - Check SSL certificate is valid

3. **Test Manually**
   ```bash
   curl -u username:app_password https://yourblog.com/wp-json/wp/v2/posts
   ```

---

### Issue 2: "401 Unauthorized"

**Symptoms:** Authentication fails

**Solutions:**

1. **Remove Spaces from App Password**
   ```
   # WordPress shows
   AbCd EfGh IjKl
   
   # Enter in Nexuzy
   AbCdEfGhIjKl
   ```

2. **Check Username**
   - Use WordPress login username (not display name)
   - Case-sensitive

3. **Regenerate App Password**
   - Revoke old password
   - Generate new one
   - Try again

---

### Issue 3: "403 Forbidden"

**Symptoms:** REST API blocked

**Solutions:**

1. **Check User Permissions**
   - User must be Editor or higher
   - Cannot be Subscriber/Contributor

2. **Disable Security Plugins**
   - Temporarily disable:
     - iThemes Security
     - Wordfence
     - All In One WP Security
   - Test connection
   - Re-enable and whitelist Nexuzy

3. **Check .htaccess Rules**
   ```apache
   # Remove any REST API blocking rules
   # <IfModule mod_rewrite.c>
   #   RewriteRule ^wp-json/ - [F,L]
   # </IfModule>
   ```

---

### Issue 4: "404 Not Found"

**Symptoms:** `/wp-json/` endpoint not found

**Solutions:**

1. **Flush Permalinks**
   ```
   WordPress Admin → Settings → Permalinks
   └─ Click "Save Changes" (don't change anything)
   ```

2. **Check REST API Disabled Plugin**
   ```
   WordPress Admin → Plugins
   └─ Deactivate "Disable REST API" or similar
   ```

3. **Verify .htaccess Writable**
   - Ensure WordPress can write to `.htaccess`
   - File permissions: 644 or 664

---

### Issue 5: "SSL Certificate Error"

**Symptoms:** SSL verification fails

**Solutions:**

1. **Update SSL Certificate**
   - Use Let's Encrypt (free)
   - Check expiration date

2. **Test SSL**
   ```bash
   curl -I https://yourblog.com
   ```

3. **Check Mixed Content**
   - Ensure all resources load via HTTPS
   - Update Site URL in WordPress settings

---

## 🛠️ Advanced Configuration

### Custom Post Status

By default, Nexuzy publishes as **"draft"**. To auto-publish:

**Edit:** `core/wordpress_api.py`

```python
def publish_draft(self, draft_id: int, workspace_id: int):
    # ...
    post_data = {
        "title": title,
        "content": body,
        "status": "publish",  # Changed from "draft"
        # ...
    }
```

**Available Statuses:**
- `draft` - Save as draft (default, recommended)
- `publish` - Publish immediately
- `pending` - Pending review
- `private` - Private post

---

### Custom Categories and Tags

Nexuzy auto-assigns categories based on RSS feed category.

**Manual Assignment:**

```python
# In core/wordpress_api.py
post_data = {
    "categories": [1, 5, 10],  # Category IDs
    "tags": [15, 20, 25],      # Tag IDs
}
```

**Fetch Category IDs:**
```bash
curl https://yourblog.com/wp-json/wp/v2/categories
```

**Fetch Tag IDs:**
```bash
curl https://yourblog.com/wp-json/wp/v2/tags
```

---

### Custom Fields and Metadata

Add custom fields to posts:

```python
post_data = {
    "title": title,
    "content": body,
    "meta": {
        "custom_field_key": "custom_value",
        "seo_description": summary,
    }
}
```

---

## 📚 Additional Resources

### Official Documentation

- [WordPress REST API Handbook](https://developer.wordpress.org/rest-api/)
- [Application Passwords Documentation](https://make.wordpress.org/core/2020/11/05/application-passwords-integration-guide/)
- [Posts Endpoint Reference](https://developer.wordpress.org/rest-api/reference/posts/)

### Testing Tools

- **Postman** - API testing tool
- **Insomnia** - REST API client
- **curl** - Command-line testing

### WordPress Plugins

- **WP REST API Controller** - Fine-grained API permissions
- **JWT Authentication** - Alternative auth method
- **Basic Auth Plugin** - For development only

---

## 👥 Support

If you encounter issues not covered here:

1. 🐛 [Report Bug](https://github.com/david0154/nexuzy-publisher-desk/issues/new?template=bug_report.md)
2. 💬 [Ask in Discussions](https://github.com/david0154/nexuzy-publisher-desk/discussions)
3. 📝 Check [FAQ](FAQ.md)

---

## 📄 Example Request

**Full WordPress REST API Request:**

```bash
curl -X POST https://yourblog.com/wp-json/wp/v2/posts \
  -u "username:AbCdEfGhIjKlMnOpQrStUvWx" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Breaking: AI Transforms News Publishing",
    "content": "<p>Nexuzy Publisher Desk brings AI-powered automation...</p>",
    "status": "draft",
    "categories": [1],
    "tags": [5, 10],
    "excerpt": "AI automates news publishing workflow"
  }'
```

**Response:**
```json
{
  "id": 123,
  "link": "https://yourblog.com/2026/01/22/ai-transforms-news-publishing/",
  "status": "draft",
  "title": {
    "rendered": "Breaking: AI Transforms News Publishing"
  }
}
```

---

**Last Updated:** January 22, 2026

**Author:** David & Nexuzy Tech
