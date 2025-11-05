# Hybrid LLM Feedback Loop - Research Website

An interactive static website showcasing the research results for the Hybrid LLM Feedback Loop project.

## 📁 Files

- `index.html` - Main HTML structure
- `styles.css` - Complete styling (responsive, modern design)
- `script.js` - Interactive charts and animations using Chart.js
- `README.md` - This file
- `DEPLOYMENT.md` - Detailed deployment instructions

## 🚀 Quick Start

### Local Testing

1. Open `index.html` in your browser:
```bash
cd website
open index.html  # macOS
# or double-click the file in File Explorer (Windows)
# or xdg-open index.html (Linux)
```

### Live Server (Recommended for Development)

If you have VS Code:
1. Install the "Live Server" extension
2. Right-click on `index.html` → "Open with Live Server"
3. The site will open at `http://localhost:5500`

Or using Python:
```bash
cd website
python3 -m http.server 8000
# Visit http://localhost:8000
```

## 🌐 Free Deployment Options

### Option 1: GitHub Pages (Recommended - Easiest)
✅ Free, fast, HTTPS included, custom domain support

See `DEPLOYMENT.md` for step-by-step instructions.

### Option 2: Netlify
✅ Drag-and-drop deployment, automatic HTTPS, continuous deployment

### Option 3: Vercel
✅ Fast global CDN, automatic HTTPS, excellent performance

## 📊 Features

- **Interactive Charts**: Pass@k metrics, SOTA comparisons, critic performance
- **Responsive Design**: Works on mobile, tablet, and desktop
- **Smooth Animations**: Scroll-triggered animations for engaging UX
- **Modern UI**: Clean, professional design with gradient accents
- **Fast Loading**: Pure HTML/CSS/JS, no build process required
- **SEO Ready**: Semantic HTML, meta tags included

## 🎨 Customization

### Update Content

Edit `index.html` to change:
- Text content
- Stats and numbers
- Links to GitHub/arXiv

### Change Colors

Edit `styles.css` → `:root` variables:
```css
:root {
    --primary: #6366f1;      /* Main blue */
    --secondary: #8b5cf6;    /* Purple accent */
    --success: #10b981;      /* Green for metrics */
    /* ... */
}
```

### Modify Charts

Edit `script.js` to update chart data:
- ICPC results: `icpcCtx` section
- Codeforces results: `cfCtx` section
- Comparisons: `sotaCtx` section

## 📱 Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 📄 License

Same as the parent project.

## 🔗 Links

- **GitHub Repo**: [Update with your repo URL]
- **Paper**: [Update with arXiv link]
- **Dataset**: [Update with dataset link]

## 🤝 Contributing

To improve the website:
1. Make your changes to HTML/CSS/JS
2. Test locally
3. Submit a PR to the main repo

## 📧 Contact

For questions about the website, contact: [your.email@example.com]

---

**Note**: This is a static website (no backend required). All data is embedded in the HTML/JS files. Update the data directly in `script.js` when you have new results.

