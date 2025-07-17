# Repository Access in DocGen

DocGen supports accessing and analyzing code from external repositories to generate context-aware documentation. This feature allows you to reference code hosted on GitHub and other platforms (coming soon) when documenting your own projects.

## Supported Repository Providers

- GitHub
- GitLab (coming soon)
- Bitbucket (coming soon)

## Getting Started

### Adding a Repository

You can add a repository using the `repo add` command:

```bash
# Add a GitHub repository
docgen repo add --repo-url https://github.com/username/repo --repo-name my-repo

# Add with a specific local cache path
docgen repo add --repo-url https://github.com/username/repo --local-path ./cache/my-repo

# Add with interactive authentication
docgen repo add --provider github --interactive

# Add a repository with a specific branch
docgen repo add --repo-url https://github.com/username/repo --branch develop
```

When you add a repository, DocGen automatically prepares it based on your selected caching strategy.

### Listing Repositories

To see all configured repositories:

```bash
docgen repo list
```

### Removing a Repository

To remove a repository:

```bash
docgen repo remove --repo-name my-repo
```

### Updating a Repository

To update repository settings:

```bash
docgen repo update --repo-name my-repo --local-path ./new-path
```

### Logging Out

To log out and remove stored authentication tokens:

```bash
docgen repo logout --provider github
```

## Authentication

### GitHub Authentication

For GitHub repositories, you can authenticate in two ways:

1. **Personal Access Token**:
   ```bash
   docgen repo add --provider github --token YOUR_TOKEN
   ```

2. **Interactive Authentication**:
   ```bash
   docgen repo add --provider github --interactive
   ```

## Caching Strategies

DocGen supports different caching strategies for repositories:

- **API** (default): Uses the provider's API to access files as needed
- **Sparse**: Creates a sparse checkout of the repository
- **Full**: Creates a full clone of the repository

Example:
```bash
docgen repo add --repo-url https://github.com/username/repo --cache-strategy sparse
```

## Using External Repositories in Documentation

When generating documentation, DocGen will automatically use the external repositories you've added to provide context and references. This helps create more comprehensive documentation that understands the relationships between your code and external dependencies.

## Security Considerations

- Authentication tokens are stored securely using the system's keychain when available
- No sensitive information is stored in plain text
- You can remove stored tokens at any time using the `repo logout` command 