# Branching Strategy

## Overview
Our branching system is designed to maintain code stability and enable continuous development through a clear, structured workflow. This document outlines our branch hierarchy and processes.

## Branch Structure

### 🎯 `main` (Production)
- Contains stable, production-ready code
- No direct development occurs here
- Only accepts merges from `release` branch
- Protected branch requiring review

### 🚀 `release`
- Final testing ground before production
- Merges from `working-code-branch`
- Undergoes thorough testing and validation
- Direct push to `main` after validation

### 🔨 `working-code-branch`
- Staging area for pre-release testing
- Collects verified changes from `dev`
- Integration testing happens here
- Promotes to `release` after testing

### 💻 `dev`
- Active development branch
- All new features and fixes start here
- Local testing required before promotion
- Merges into `working-code-branch`

## Workflow Steps

1. **Development Phase**
   ```bash
   git checkout dev
   # Make changes
   git add .
   git commit -m "feat: implement new feature"
   git push origin dev
   ```

2. **Staging Phase**
   ```bash
   git checkout working-code-branch
   git merge dev
   git push origin working-code-branch
   ```

3. **Release Phase**
   ```bash
   git checkout release
   git merge working-code-branch
   git push origin release
   ```

4. **Production Deployment**
   ```bash
   git checkout main
   git merge release
   git push origin main
   ```

## Best Practices

- Always create feature branches from `dev`
- Use conventional commits with descriptive messages
- Require code reviews before merging
- Run tests before promoting between branches
- Keep branches synchronized regularly

## Branch Protection Rules

- `main`: Requires PR approval and passing tests
- `release`: Requires testing validation
- `working-code-branch`: Requires basic tests
- `dev`: Open for development team

## Hotfix Process

For urgent fixes:
1. Branch from `main`
2. Fix the issue
3. Merge to both `main` and `dev`
4. Tag the hotfix version

## Version Control

- Use semantic versioning (MAJOR.MINOR.PATCH)
- Tag all releases in `main`
- Document changes in CHANGELOG.md 