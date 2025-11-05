# Free Deployment Guide

This guide provides step-by-step instructions to deploy your research website for **FREE** using popular hosting services.

## 🏆 Recommended: GitHub Pages

**Best for**: Academic projects, research websites, portfolios
**Cost**: Free forever
**Features**: Custom domain, HTTPS, version control

### Step-by-Step Instructions

#### 1. Create a GitHub Repository

```bash
# Navigate to your project root
cd "/Users/sifathossain/Desktop/Dev/Hybrid LLM Feedback Loop"

# Initialize git (if not already done)
git init

# Create a new branch for GitHub Pages
git checkout -b gh-pages

# Add all files
git add website/

# Commit
git commit -m "Add research website"
```

#### 2. Push to GitHub

```bash
# Create a new repository on GitHub.com (https://github.com/new)
# Name it: hybrid-llm-feedback-loop
# Make it public
# DO NOT initialize with README

# Add remote
git remote add origin https://github.com/YOUR_USERNAME/hybrid-llm-feedback-loop.git

# Push
git push -u origin gh-pages
```

#### 3. Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** → **Pages** (left sidebar)
3. Under "Source":
   - Branch: `gh-pages`
   - Folder: `/root` or `/website` (depending on structure)
4. Click **Save**

#### 4. Wait 1-2 Minutes

Your site will be live at:
```
https://YOUR_USERNAME.github.io/hybrid-llm-feedback-loop/
```

### Using Custom Domain (Optional)

1. Buy a domain (Namecheap, Google Domains, etc.)
2. In your domain DNS settings, add:
   ```
   Type: CNAME
   Name: www
   Value: YOUR_USERNAME.github.io
   ```
3. In GitHub Pages settings, add your custom domain
4. Enable "Enforce HTTPS"

---

## 🎨 Option 2: Netlify

**Best for**: Continuous deployment, drag-and-drop simplicity
**Cost**: Free forever
**Features**: Instant deployment, form handling, serverless functions

### Method A: Drag and Drop (Easiest)

1. Go to https://app.netlify.com/drop
2. Drag your entire `website` folder onto the page
3. Done! Your site is live instantly

You'll get a URL like: `https://random-name-12345.netlify.app`

### Method B: Git Integration (Better for updates)

1. Sign up at https://netlify.com
2. Click "Add new site" → "Import an existing project"
3. Connect your GitHub account
4. Select your repository
5. Build settings:
   - Base directory: `website`
   - Build command: (leave empty)
   - Publish directory: `.` (or leave as default)
6. Click "Deploy site"

### Custom Domain on Netlify

1. Go to Site settings → Domain management
2. Click "Add custom domain"
3. Follow instructions to update DNS
4. HTTPS is automatic!

---

## ⚡ Option 3: Vercel

**Best for**: Fast global CDN, best performance
**Cost**: Free forever
**Features**: Automatic HTTPS, serverless functions, analytics

### Deployment Steps

1. Go to https://vercel.com/signup
2. Sign up with GitHub
3. Click "New Project"
4. Import your repository
5. Configure:
   - Root Directory: `website`
   - Build Command: (leave empty)
   - Output Directory: (leave empty)
6. Click "Deploy"

Your site will be live at: `https://project-name.vercel.app`

### Custom Domain on Vercel

1. Go to Settings → Domains
2. Add your custom domain
3. Update DNS records as instructed
4. Automatic HTTPS included

---

## 🔧 Alternative Option: GitLab Pages

### Steps:

1. Create account at https://gitlab.com
2. Create new project
3. Push your code
4. Create `.gitlab-ci.yml` in root:

```yaml
pages:
  stage: deploy
  script:
    - mkdir .public
    - cp -r website/* .public
    - mv .public public
  artifacts:
    paths:
      - public
  only:
    - main
```

5. Push changes
6. Site will be at: `https://YOUR_USERNAME.gitlab.io/project-name`

---

## 📊 Comparison Table

| Feature | GitHub Pages | Netlify | Vercel |
|---------|-------------|---------|---------|
| **Cost** | Free | Free | Free |
| **Setup Time** | 5 min | 2 min | 3 min |
| **Custom Domain** | ✅ Yes | ✅ Yes | ✅ Yes |
| **HTTPS** | ✅ Auto | ✅ Auto | ✅ Auto |
| **Build Time** | N/A | Instant | Instant |
| **CDN** | ✅ Global | ✅ Global | ✅ Best |
| **Analytics** | ❌ No | ✅ Basic | ✅ Advanced |
| **Forms** | ❌ No | ✅ Yes | ✅ Limited |
| **Best For** | Academic | Simplicity | Performance |

---

## 🎯 Recommended Workflow

### For Academic/Research Projects:
**Use GitHub Pages** - It's associated with your code repository and shows professionalism.

### For Quick Demos:
**Use Netlify** - Drag and drop is unbeatable for speed.

### For Production/Portfolio:
**Use Vercel** - Best performance and features.

---

## 🔄 Updating Your Live Site

### GitHub Pages:
```bash
cd website
# Make your changes
git add .
git commit -m "Update results"
git push origin gh-pages
# Wait 1-2 minutes for changes to appear
```

### Netlify/Vercel:
Just push to your GitHub repo - they auto-deploy! ✨

---

## 🐛 Troubleshooting

### GitHub Pages shows 404
- Ensure branch is `gh-pages`
- Check that `index.html` is in the root of selected folder
- Wait 5 minutes after initial setup

### Netlify deploy failed
- Check that `website` folder contains `index.html`
- Try manual deploy: Drag the folder to app.netlify.com/drop

### Vercel build error
- Set Root Directory to `website` in project settings
- Leave build command empty (it's pure HTML/CSS/JS)

### Charts not showing
- Check browser console for errors
- Ensure Chart.js CDN is loading (check network tab)
- Clear cache and hard reload (Ctrl/Cmd + Shift + R)

---

## 🎁 Bonus: Add Analytics

### Google Analytics (Free)

1. Get tracking ID from https://analytics.google.com
2. Add to `index.html` before `</head>`:

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-YOUR-ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-YOUR-ID');
</script>
```

### Simple Analytics (Privacy-friendly, $9/month)

Add to `index.html`:
```html
<script async defer src="https://scripts.simpleanalyticcdn.com/latest.js"></script>
```

---

## 📧 Need Help?

- **GitHub Pages**: https://docs.github.com/en/pages
- **Netlify**: https://docs.netlify.com
- **Vercel**: https://vercel.com/docs

## ✅ Deployment Checklist

Before deploying, ensure:

- [ ] All links work (test locally)
- [ ] Images load properly
- [ ] Charts display correctly
- [ ] Mobile responsive (test on phone)
- [ ] Update email/GitHub links in footer
- [ ] Add meta tags for SEO (already included)
- [ ] Test on multiple browsers

---

## 🎉 You're Done!

Your research website is now live and accessible worldwide for free! Share the URL on:
- Your paper (footnote with live demo)
- arXiv submission
- Twitter/LinkedIn
- Academic presentations
- Email signature

**Pro Tip**: Add a QR code to your poster/slides pointing to your live website!

Generate QR code at: https://qr-code-generator.com/

