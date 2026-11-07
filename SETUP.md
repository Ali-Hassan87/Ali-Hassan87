# Ali Hassan GitHub Profile — Setup

1. Open the repository named exactly `Ali-Hassan87` (the profile README repository).
2. Replace its `README.md` with this package's `README.md`.
3. Upload the `assets/` folder and `scripts/` folder to the repository root.
4. Upload `.github/workflows/profile-assets.yml` to the same path.
5. In Settings → Actions → General, allow GitHub Actions to have read and write permissions.
6. Open Actions → Refresh profile visuals → Run workflow.
7. Wait for the workflow to finish. It will create `assets/stats.svg`, `assets/languages.svg`, and `assets/contributions.svg`.

The custom stats cards use GitHub's API and are stored in your own repository. This avoids the broken third-party stats-card URLs shown in your screenshot.

GitHub README files cannot run arbitrary JavaScript, custom CSS, or website-style hover transitions. The custom SVG artwork includes supported SVG animation, but the README itself remains subject to GitHub's Markdown and HTML restrictions.

Project links included are the known live URLs. Add repository links or further project destinations once you confirm their exact URLs.
