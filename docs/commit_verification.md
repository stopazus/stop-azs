# Commit Verification and Vigilant Mode

## Default Verification Behavior

By default, commits and tags are marked "Verified" if they are signed with a GPG, SSH, or S/MIME key that was successfully verified. If a commit or tag has a signature that can't be verified by GitHub, we mark the commit or tag "Unverified." In all other cases no verification status is displayed.

## Vigilant Mode

However, you can give other users increased confidence in the identity attributed to your commits and tags by enabling vigilant mode in your GitHub settings. With vigilant mode enabled, all of your commits and tags are marked with one of three verification statuses:

### 1. Verified
- The commit or tag is signed and the signature is successfully verified using your GPG, SSH, or S/MIME key
- The committer is the only author with vigilant mode enabled
- Visually indicated with a green "Verified" badge on GitHub
- This status assures others that the commit definitely comes from you as a trusted source

### 2. Partially Verified
- The commit or tag is signed and the signature is successfully verified, but:
  - The commit has at least one author who is not the committer and who has enabled vigilant mode
- In other words, the commit was co-authored, or the author and committer are different—and at least one has vigilant mode on
- The commit signature doesn't guarantee the consent of all authors, so it's only "Partially Verified"

### 3. Unverified
- Any of the following conditions:
  - The commit or tag is signed, but the signature cannot be verified by GitHub
  - The commit or tag is not signed, and at least the committer or one author has vigilant mode enabled
- All unsigned commits pushed to GitHub after enabling vigilant mode will be marked "Unverified," including previous ones

## Supported Signature Methods

GitHub supports three methods for signing commits and tags:

- **GPG**: The classic method using OpenPGP cryptography. Supports features like key expiration and revocation.
- **SSH**: Newer and easier method that uses your SSH key (which you may already use for repository access).
- **S/MIME**: Generally used within organizations with enterprise security workflows.

## Best Practices

- Enable vigilant mode only if you always sign your commits and tags
- Ensure your commit email matches your verified GitHub email
- Vigilant mode helps surface commit authenticity concerns by turning ambiguous cases into explicit warnings
- This status system works consistently across GPG, SSH, and S/MIME signatures

## References

- [GitHub Docs: About commit signature verification](https://docs.github.com/en/authentication/managing-commit-signature-verification/about-commit-signature-verification)
- [GitHub Docs: Displaying verification statuses for all of your commits](https://docs.github.com/en/authentication/managing-commit-signature-verification/displaying-verification-statuses-for-all-of-your-commits)
