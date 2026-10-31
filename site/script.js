// Turns the download buttons into direct links to the latest installer and shows
// its version. Without JavaScript, or if the GitHub API can't be reached, the
// buttons keep pointing to the latest release page.
(async () => {
  try {
    const response = await fetch("https://api.github.com/repos/ruester/eye-care-reminder/releases/latest");
    if (!response.ok) {
      return;
    }
    const release = await response.json();
    const msi = release.assets.find((asset) => asset.name.endsWith("-windows-x64.msi"));
    if (msi) {
      for (const link of document.querySelectorAll('[data-download="windows"]')) {
        link.href = msi.browser_download_url;
      }
    }
    const version = release.tag_name.replace(/^v/, "");
    for (const element of document.querySelectorAll("[data-version]")) {
      element.textContent = ` · version ${version}`;
    }
  } catch {
    // Keep the fallback links.
  }
})();
