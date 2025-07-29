# GitHub Actions Workflows

This directory contains automated workflows for building and releasing WordCloud Magic.

## Workflows

### 1. Build Release (`build-release.yml`)

**Trigger**: 
- Push of version tags (e.g., `v1.0.0`, `v2.1.3`)
- Manual dispatch with version input

**Purpose**: Creates official release builds with:
- Windows 64-bit executable
- Portable ZIP archive
- SHA256 checksums
- Automated GitHub Release draft

**Usage**:
```bash
# Create and push a version tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# Or trigger manually from GitHub Actions tab
```

### 2. Test Build (`test-build.yml`)

**Trigger**:
- Push to main, develop, or ui-ux-improvements branches
- Pull requests to main
- Manual dispatch

**Purpose**: Validates that the code can be built successfully without creating releases.

## How to Trigger a Release

1. **Update version information**:
   - Update version in `CHANGELOG.md`
   - Commit changes

2. **Create a version tag**:
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

3. **Monitor the build**:
   - Go to Actions tab on GitHub
   - Watch the "Build Release" workflow
   - Once complete, a draft release will be created

4. **Publish the release**:
   - Go to Releases page
   - Edit the draft release
   - Add release notes
   - Publish

## Build Configuration

The workflows use:
- **Python**: 3.11
- **PyInstaller**: Latest version
- **Icon**: `icons/icon_256.ico`
- **Output**: Single executable file

## Artifacts

Each release includes:
- `WordCloudMagic-{version}-win64.zip` - Portable archive
- `WordCloudMagic-{version}-win64.zip.sha256` - Checksum file

## Security

- Builds run in isolated GitHub-hosted runners
- Dependencies are cached for faster builds
- SHA256 checksums provided for verification
- Consider code signing for production releases

## Troubleshooting

If builds fail:
1. Check the Actions log for errors
2. Ensure all dependencies are in `requirements.txt`
3. Verify icon files exist in `icons/` directory
4. Test locally with `python build_exe.py`