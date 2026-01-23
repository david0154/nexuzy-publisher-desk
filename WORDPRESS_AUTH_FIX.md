# WordPress 401 Authentication Fix

If you're getting a **401 Unauthorized** error when testing your WordPress connection:

```
WARNING - WordPress connection test failed with status code: 401
Response: {"code":"rest_not_logged_in","message":"You are not currently logged in."...}
```

This means your WordPress credentials are not working. Follow these steps to fix it:

---

## Step 1: Generate a New Application Password

### For WordPress.com Sites:
1. Go to https://wordpress.com/me/security/application-passwords
2. Create a new application password
3. Name it "Nexuzy Publisher Desk"
4. Copy the generated password immediately (you won't see it again)

### For Self-Hosted WordPress:
1. Log in to your WordPress dashboard
2. Go to: **Users → Profile**
3. Scroll down to **Application Passwords** section
4. If you don't see this section, you need WordPress 5.6+ or the "Application Passwords" plugin
5. Enter a name: "Nexuzy Publisher Desk"
6. Click **Add New Application Password**
7. Copy the generated password (format: `xxxx xxxx xxxx xxxx xxxx xxxx`)

---

## Step 2: Update Credentials in Nexuzy Publisher Desk

1. Open Nexuzy Publisher Desk
2. Go to **WordPress API** tab
3. Enter your credentials:
   - **Site URL:** `https://yourdomain.com` (no trailing slash)
   - **Username:** Your WordPress username (NOT email)
   - **Password:** The application password you just generated
     - Remove all spaces: `xxxxxxxxxxxxxxxxxxxxxxxx`
4. Click **Test Connection**
5. You should see: ✅ **Connected successfully**

---

## Step 3: Verify WordPress REST API is Enabled

### Check if REST API is accessible:

Open your browser and visit:
```
https://yourdomain.com/wp-json/wp/v2/posts
```

**Expected responses:**
- ✅ **Working:** You see JSON data or an error about authentication
- ❌ **Not working:** 404 error or "No route was found"

### If REST API is disabled:

**Option A: Enable via plugin**
1. Install "WP REST API Controller" plugin
2. Activate WordPress REST API

**Option B: Enable via code**

Add to your `wp-config.php`:
```php
// Enable REST API
define('REST_API_ENABLED', true);
```

Or add to your theme's `functions.php`:
```php
// Remove REST API disable filter
remove_filter('rest_authentication_errors', '__return_false');
```

---

## Step 4: Check for Security Plugins Blocking REST API

Some security plugins block REST API access. Check these:

### **Wordfence:**
- Go to: Wordfence → Firewall → All Firewall Options
- Find: "Disable REST API"
- Make sure it's **OFF**

### **iThemes Security:**
- Go to: Security → Settings → WordPress Tweaks
- Find: "REST API"
- Make sure "Restrict Access" is **disabled**

### **All In One WP Security:**
- Go to: WP Security → Firewall
- Check if REST API blocking is enabled
- Disable it or whitelist your IP

---

## Step 5: Test with cURL (Advanced)

To verify your credentials work, run this command:

```bash
curl -u "your_username:your_app_password" \
  https://yourdomain.com/wp-json/wp/v2/users/me
```

**Replace:**
- `your_username`: Your WordPress username
- `your_app_password`: Your application password (no spaces)
- `yourdomain.com`: Your actual domain

**Expected response:**
```json
{
  "id": 1,
  "name": "Your Name",
  "url": "...",
  ...
}
```

If this works but Nexuzy doesn't, check for firewall issues.

---

## Common Issues & Solutions

### Issue: "Invalid username or password"

**Solution:**
- Make sure you're using your **username**, not your email
- Remove ALL spaces from the application password
- Regenerate the application password

### Issue: "REST API is disabled"

**Solution:**
- Check your WordPress version (need 5.6+)
- Install "Application Passwords" plugin for older versions
- Check security plugin settings

### Issue: "SSL certificate verify failed"

**Solution:**
- Make sure your site has a valid SSL certificate
- Use `https://` in the site URL
- If using self-signed certificate, contact support

### Issue: Works in browser but not in app

**Solution:**
- Your server might be blocking Python/requests user agent
- Add this to your `.htaccess`:
```apache
<IfModule mod_setenvif.c>
    SetEnvIf User-Agent "python-requests" allowed
</IfModule>
```

---

## Still Not Working?

### Enable Debug Logging:

1. Open Nexuzy Publisher Desk
2. Check `nexuzy_publisher.log` file
3. Look for detailed error messages

### Contact Support:

If none of these solutions work:
1. Check your `nexuzy_publisher.log` file
2. Try the cURL test above
3. Contact your hosting provider
4. Open an issue on GitHub with:
   - WordPress version
   - Hosting provider
   - Error logs
   - cURL test results

---

## Security Notes

⚠️ **Important:**
- Application passwords are **NOT** your regular WordPress password
- Never share your application password publicly
- You can revoke application passwords anytime without changing your main password
- Each application should have its own unique password

---

## Quick Checklist

- [ ] WordPress 5.6+ or Application Passwords plugin installed
- [ ] Generated a new application password
- [ ] Using WordPress **username** (not email)
- [ ] Removed all spaces from application password
- [ ] Site URL has `https://` prefix
- [ ] REST API is accessible at `/wp-json/wp/v2/posts`
- [ ] No security plugins blocking REST API
- [ ] SSL certificate is valid
- [ ] Test connection shows ✅ success

---

Once all steps are complete, you should be able to push articles directly from Nexuzy Publisher Desk to your WordPress site!
