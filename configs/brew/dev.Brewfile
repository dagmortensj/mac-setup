# dev.Brewfile: development tools. Installed by `./install.sh dev`.
#
# There is deliberately no `brew "python"` here. uv installs and manages
# Python (see configs/python/), and a Homebrew Python next to it is how
# Python setups on macOS get messy.

brew "gh"                  # GitHub CLI, also used by git to sign in to GitHub over HTTPS
brew "gcc"                 # C/C++ compiler
brew "progress"            # shows progress for cp, mv, dd and similar
brew "uv"                  # Python versions, environments and packages

cask "visual-studio-code"  # also puts the `code` command on PATH

# Full TeX Live without TeXShop, BibDesk and LaTeXiT, since editing happens
# in VS Code. About 6 GB. Its installer needs the admin password, and
# Homebrew asks for it when the download is done. Packages are updated with
# tlmgr; see the LaTeX section of the README before upgrading it with Homebrew.
cask "mactex-no-gui"
