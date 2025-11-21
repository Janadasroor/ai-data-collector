# Contributing to AI Data Collector

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/JanadaSroor/ai-data-collector.git
   cd ai-data-collector
   ```
3. **Create a virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🌿 Branching Strategy

- `main` - Stable, production-ready code
- `develop` - Integration branch for features
- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `docs/*` - Documentation updates

Create your branch from `develop`:
```bash
git checkout develop
git checkout -b feature/your-feature-name
```

## 💻 Development Guidelines

### Code Style

- Follow [PEP 8](https://pep8.org/) style guide
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and small

### Testing

Before submitting a PR:
```bash
# Run a short test
python app.py --duration 0.05

# Check for errors in logs
tail -n 50 crawler.log
```


## 🐛 Reporting Bugs

When reporting bugs, please include:
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Relevant log excerpts
- Configuration used

## 💡 Suggesting Features

Feature requests are welcome! Please:
- Check existing issues first
- Describe the use case
- Explain the expected behavior
- Consider implementation complexity

## 📝 Pull Request Process

1. **Update documentation** if needed
2. **Test your changes** thoroughly
3. **Update CHANGELOG.md** with your changes
4. **Submit PR** with clear description
5. **Respond to feedback** from reviewers

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] Changes have been tested
- [ ] Documentation updated
- [ ] No new warnings or errors
- [ ] Commit messages are clear

## 🎯 Areas for Contribution

### High Priority
- Robots.txt support
- Proxy rotation
- Better duplicate detection
- Database storage option
- Unit tests

### Medium Priority
- Web UI for monitoring
- Docker support
- Cloud deployment guides
- More data source templates

### Documentation
- Video tutorials
- Use case examples
- Performance optimization guide
- Troubleshooting guide

## 📧 Questions?

Feel free to open an issue for questions or discussions!

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.
