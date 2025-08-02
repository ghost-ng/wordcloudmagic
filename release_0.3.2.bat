@echo off
echo Creating Release v0.3.2
echo ======================

echo.
echo Staging changes...
git add __version__.py CHANGELOG.md .github/workflows/build-release.yml

echo.
echo Committing changes...
git commit -m "Release version 0.3.2" -m "" -m "- Fix GitHub Actions to use bundled UPX instead of downloading" -m "- Clean up source releases to exclude build artifacts" -m "- Optimize CI/CD pipeline"

echo.
echo Creating tag v0.3.2...
git tag -a v0.3.2 -m "Release version 0.3.2 - Fixed build workflow"

echo.
echo Pushing to origin...
git push origin main --tags

echo.
echo Release v0.3.2 has been pushed!
echo GitHub Actions will now build the release.
echo.
pause