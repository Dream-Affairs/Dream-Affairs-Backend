# Contributing Guidelines

Thank you for considering contributing to this project! We appreciate your interest and welcome contributions from the community. Whether you're reporting a bug, proposing a new feature, or improving our documentation, your input is valuable.

Here's how you can get involved and contribute to the project:

## Contribution Workflow
### Prerequisite
Before considering contributing to the project, ensure you have the following installed on your system:

- Python (recommended version 3.6 or higher)
- pip (Python package manager)
- make (To run Makefile)
- nodejs (Recommended version 16 or higher)
- npm (Required to run commitlint)

 1. **Clone your repository to your local machine**
    ```
    git clone https://github.com/Dream-Affairs/Dream-Affairs-Backend
    ```

 2. **Change to the repository directory on your computer**
    ```
    cd Dream-Affairs-Backend
    ```

 3. **Install Pre commit hook**
    To avoid failed CI checks on Pull requests, use the makefile to install the pre commit hooks.
    This may take some mins.
    ```bash
    make pre-commit
    ```

 4. **Create a branch using the `git checkout` command**
    ```bash
    git checkout -B category/description
    ```
    **Refer to the [Branch Naming Convention](###branch-naming) for appropriate branch naming.**

 5. **Make all necessary changes, following our coding style and guidelines [[Pep 8]](https://peps.python.org/pep-0008/).**

 6. **If changes were made to any table, use the makefile to upgrade the database. It's alembic under the hood**
    ```
    make upgrade
    ```
    **To go back to a previous version the database, run:**
    ```
    make downgrade
    ```

    **Always sync your branch with the dev branch**

 7. **Commit your changes and push them to the remote repository**
    ```bash
    git add .
    git commit -m "category(scope): message"
    git push origin category/description
    ```
    **Refer to the [Commit Message Convention](#commmit-message) for guidance on commit message format.**

 8. **Create a Pull Request**
    Go to the Pull Requests section of our repository.
    Click on the "New Pull Request" button.
    Select the branch containing your changes from your forked repository.
    Provide a clear and concise description of your changes in the PR description.
    Submit the pull request, and we'll review your changes as soon as possible.

## Opening an Issue
Before creating issues, search through existing [issues](https://github.com/Dream-Affairs/Dream-Affairs-Backend/issues) to see if your issue has previously been reported. If your issue exists, comment with any additional information you have. You may simply note "I have this problem too", which helps prioritize the most common problems and requests.

### Bug Reports
A great way to contribute to the project is to send a detailed issue when you encounter a problem. We always appreciate a well-written, thorough bug report.

Since we are developers, we should write bug reports as a ticket that you would like to receive.

**Fully complete the provided [issue template](https://github.com/Dream-Affairs/Dream-Affairs-Backend/issues/new?assignees=&labels=&projects=&template=bug_report.yaml&title=%5BBug%5D+).** The bug report template requests all the information we need to quickly and efficiently address your issue. Be clear, concise, and descriptive. Provide as much information as you can, including steps to reproduce, stack traces, compiler errors, library versions, OS versions, and screenshots (if applicable).

### Feature Requests
If you have an idea for a new feature or improvement that you'd like to see in this project, please let us know.

**Fully complete the provided [issue template](https://github.com/Dream-Affairs/Dream-Affairs-Backend/issues/new?assignees=&labels=&projects=&template=feature_functionality_request.yaml&title=%5BFeature+Request%5D+)**. The feature request template asks for all necessary information for us to begin a productive conversation. Be precise about the proposed outcome of the feature and how it relates to existing features. Include implementation details if possible.

## Pull Requests

We appreciate your contributions through pull requests! Here's how to create and submit a pull request effectively:

### Creating a Pull Request

1. **Open an Issue**: Before forking the repository and creating a pull request, consider opening an issue to discuss the proposed changes. If no issue exists for your changes, initiate a new discussion to ensure alignment with the project's goals.

2. **PR Template**: When creating your pull request, please use the provided Pull Request template. This template ensures that essential information is included in your request.

3. **Naming Convention**: Name your pull request using the format `category: Description`. This naming convention helps us quickly identify the purpose of the pull request.

### Code Quality and Clarity

1. **Prioritize Clarity**: When writing code, prioritize clarity over cleverness. Code should be clear and concise. Remember that code is often read more than it's written. Make sure your code is understandable to a reasonably skilled developer. If necessary, include comments to explain complex logic.

2. **Coding Style**: Follow the existing coding style and conventions of the project. We adhere to the [Pep 8](https://peps.python.org/pep-0008/) style, formatting, and coding conventions. When possible, these will be enforced by a linter. Consistency makes it easier for the team to review and maintain the code in the future.

3. **Test Coverage**: Add tests whenever possible. Follow existing patterns for implementing tests. This ensures the reliability and stability of your changes.

4. **Documentation**: Document your changes using code doc comments or update existing documentation like README.md or DOCUMENTATION.md if your changes affect these resources.

### Housekeeping

1. **Resolve Conflicts**: If any merge conflicts occur during the review process, promptly resolve them.

2. **Address CI Failures**: If your pull request fails to build or pass tests, take immediate action by pushing another commit to fix it.

3. **Communication**: When making comments during the review, please use properly constructed sentences with appropriate punctuation. Clear and concise communication helps streamline the review process.


## Branch Naming and Commit Convention
When you create a branch or make a commit, please follow this convention:

### Branch Naming
Use the format `category/description` for branch names. Choose one of the following categories:

- `feat`: For changes that introduce completely new code or new features.
- `fix`: For changes that fix a bug. Ideally, reference an issue if it exists.
- `refactor`: For any code-related changes that are neither fixes nor features.
- `docs`: For changes to existing documentation or the creation of new documentation (e.g., README or usage guides).
- `build`: Use this category for changes related to the software build, such as modifications to dependencies or the addition of new dependencies.
- `test`: For changes related to testing, including adding new tests or modifying existing ones.
- `ci`: Use this category for changes related to the configuration of continuous integration systems (e.g., GitHub Actions or CI setups).
- `chore`: For all other changes to the repository that don't fit into the above categories.

Here are some examples:

- `feat/user-authentication`: This branch is for adding a new user authentication feature.
- `fix/bug-fix-123`: Use this branch to fix a specific bug, referenced by issue number 123.
- `refactor/api-improvements`: When making code-related changes that aren't fixes or features, this branch is appropriate.

### Commit Message
In your commit message, follow the format `category(scope): message`. Here's a breakdown:

- `category`: The category from the list above.
- `scope` (optional): This is where you can specify the area or component of your code that the commit affects. Use it when relevant.
- `message`: A brief, descriptive message about the commit.

Here are some examples:

- `feat(user-auth): Implement user authentication feature.`
- `fix(bug-123): Resolve issue with data not saving properly.`
- `refactor(api): Improve API response handling.`
- `docs(readme): Update installation instructions.`
- `build(deps): Add new library as a dependency.`
- `test(unit): Add unit tests for the user service.`
- `ci(github-actions): Configure automated testing workflows.`
- `chore(clean-up): Remove unused code and files.`

## License Information
Any contributions you make will be under the MIT Software License. In short, when you submit code changes, your submissions are understood to be under the same [MIT License](#LICENSE) that covers the project.

## Feedback and Discussions
If you have general questions, suggestions, or want to discuss ideas with the community, you can also participate in discussions in the Discussions section.

Your contributions help make our project better, and we're grateful for your support! If you have any questions or need further assistance, feel free to reach out to us via the project's communication channels.
