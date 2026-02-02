# 🔧 Fix: Render Not Showing GitHub Repos

## Problem
You connected GitHub to Render but can't see your `ai-research-assistant` repository.

## Solutions (Try in order)

### Solution 1: Grant Repository Access (Most Common)

When you connected GitHub to Render, you might have selected "Only select repositories" instead of "All repositories".

**Fix it:**

1. **Go to GitHub Settings:**
   - Open new tab: https://github.com/settings/installations
   - OR: GitHub → Your Profile (top right) → Settings → Applications → Installed GitHub Apps

2. **Find Render:**
   - Look for "Render" in the list
   - Click **"Configure"** next to Render

3. **Grant Access:**
   - Under "Repository access", you'll see either:
     - **"Only select repositories"** ← This is your problem!
     - **"All repositories"**
   
4. **Select Your Repo:**
   - If it says "Only select repositories":
     - Click the **"Select repositories"** dropdown
     - Find and check **"ai-research-assistant"**
     - Click **"Save"**
   
   OR
   
   - Change to **"All repositories"** (easier)
   - Click **"Save"**

5. **Go Back to Render:**
   - Refresh the Render page
   - Your repo should now appear!

---

### Solution 2: Reconnect GitHub

If Solution 1 doesn't work:

1. **In Render Dashboard:**
   - Click your profile icon (top right)
   - Go to **"Account Settings"**

2. **Disconnect GitHub:**
   - Find "Connected Accounts" section
   - Click **"Disconnect"** next to GitHub

3. **Reconnect:**
   - Click **"Connect GitHub"**
   - When prompted, select **"All repositories"**
   - Click **"Authorize Render"**

4. **Try Creating Web Service Again:**
   - New + → Web Service
   - Your repo should show up now!

---

### Solution 3: Make Sure Repo is Public

Render free tier only works with **public** repositories.

1. **Check if your repo is public:**
   - Go to: https://github.com/abhishiktha-15/ai-research-assistant
   - Look for a **"Public"** or **"Private"** badge

2. **If it says "Private":**
   - Click **"Settings"** (in your repo)
   - Scroll to bottom → **"Danger Zone"**
   - Click **"Change visibility"**
   - Select **"Make public"**
   - Confirm

3. **Go back to Render** and refresh

---

### Solution 4: Check Repository Name

1. Make sure you're looking for the right name
2. Your repo is: **`ai-research-assistant`**
3. In Render, search for it in the search box

---

## Quick Test

After trying solutions above:

1. Go to Render
2. Click **"New +"** → **"Web Service"**
3. You should see **"ai-research-assistant"** in the list
4. Click **"Connect"**

---

## Still Not Working?

### Alternative: Use Manual Git Deploy

1. In Render, create **"Web Service"**
2. Instead of selecting a repo, choose **"Public Git repository"**
3. Enter: `https://github.com/abhishiktha-15/ai-research-assistant`
4. Continue with normal configuration

---

## Which Solution Fixed It?

Let me know which one worked so I can update the main guide!

**Most likely cause:** Solution 1 (repository access permissions)
