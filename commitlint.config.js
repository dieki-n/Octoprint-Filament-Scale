const Configuration = {
    extends: ['@commitlint/config-conventional'],
    rules: {
        'subject-case': [1, 'never'],
    },
}

module.exports = Configuration
