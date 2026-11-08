#!/bin/bash
# macOS settings, applied by `./install.sh macos`. These are personal choices:
# edit or delete lines before running this on your own Mac.
#
# Each line is a `defaults write`. If Apple renames a setting in a new macOS
# version, the line still runs but has no effect, so check the result in
# System Settings after logging out and in again. Some of these only take
# effect after a logout.
#
# Find the name of a setting yourself: `defaults read > before.txt`, change
# it in System Settings, `defaults read > after.txt`, `diff before.txt after.txt`.

# Every line runs even if one fails; the script then exits with an error.
failed=0
trap 'failed=1' ERR

# ===== Appearance =====
defaults write -g AppleInterfaceStyle -string Dark
defaults write -g AppleAccentColor -int 1                                   # orange
defaults write -g AppleHighlightColor -string "1.000000 0.874510 0.701961 Orange"
defaults write -g AppleIconAppearanceTintColor -string Orange
defaults write -g UIPreferredContentSizeCategoryName -string UICTContentSizeCategoryL   # text size L

# Norwegian quotation marks when smart quotes are on
defaults write -g KB_DoubleQuoteOption -string "«abc»"
defaults write -g KB_SingleQuoteOption -string "‘abc’"
defaults write -g NSUserQuotesArray -array "«" "»" "‘" "’"

# ===== Trackpad and scrolling =====
defaults write -g com.apple.swipescrolldirection -bool false                # "natural" scrolling off
defaults write -g com.apple.trackpad.scaling -float 1.5                     # pointer speed
defaults write -g AppleEnableSwipeNavigateWithScrolls -bool false           # no swipe between pages
# Tap to click (built-in and Magic Trackpad, and for the login screen)
defaults write com.apple.AppleMultitouchTrackpad Clicking -bool true
defaults write com.apple.driver.AppleBluetoothMultitouch.trackpad Clicking -bool true
defaults -currentHost write -g com.apple.mouse.tapBehavior -int 1

# ===== Dock =====
defaults write com.apple.dock tilesize -float 53
defaults write com.apple.dock show-recents -bool false
defaults write com.apple.dock minimize-to-application -bool true
defaults write com.apple.dock wvous-br-corner -int 1                        # bottom-right hot corner: nothing
defaults write com.apple.dock wvous-br-modifier -int 0

# ===== Finder =====
defaults write com.apple.finder FXPreferredViewStyle -string clmv           # column view
defaults write com.apple.finder ShowPathbar -bool true
defaults write com.apple.finder FXDefaultSearchScope -string SCcf           # search the current folder
defaults write com.apple.finder ShowRecentTags -bool false
defaults write com.apple.finder NewWindowTarget -string PfID                # new windows open iCloud Drive
defaults write com.apple.finder NewWindowTargetPath -string "file://$HOME/Library/Mobile%20Documents/com~apple~CloudDocs/"

# ===== Windows =====
defaults write com.apple.WindowManager EnableStandardClickToShowDesktop -bool false   # clicking the wallpaper does not reveal the desktop
defaults write com.apple.WindowManager EnableTiledWindowMargins -bool false          # no gaps between tiled windows

# ===== Menu bar =====
defaults write com.apple.menuextra.clock ShowDayOfWeek -bool true

exit "$failed"
