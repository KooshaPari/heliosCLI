//! Key event routing and dispatch abstraction for chat composer.
//!
//! This module provides the [`KeyEventRouter`] trait, which abstracts mode-based key event routing
//! patterns found throughout `ChatComposer`. It enables clean separation of:
//!
//! - **Mode-based dispatch**: Route key events to different handlers based on compositor state
//!   (popup active, voice recording, image selection, etc.).
//! - **Modifier key handling**: Simplify matching on Ctrl, Alt, Shift modifiers.
//! - **Event kind filtering**: Handle press/repeat/release events selectively.
//! - **Shortcut interception**: Check for global shortcuts (e.g., overlay keys) before
//!   mode-specific handling.
//!
//! # Examples
//!
//! ```ignore
//! impl KeyEventRouter for ChatComposer {
//!     fn dispatch_key_event(&mut self, key_event: KeyEvent) -> (InputResult, bool) {
//!         if self.handle_voice_space_key_event(&key_event).is_some() {
//!             // Voice transcription has priority
//!             return self.handle_voice_space_key_event(&key_event).unwrap();
//!         }
//!
//!         match &mut self.active_popup {
//!             ActivePopup::Command(_) => self.handle_key_event_with_slash_popup(key_event),
//!             ActivePopup::File(_) => self.handle_key_event_with_file_popup(key_event),
//!             ActivePopup::Skill(_) => self.handle_key_event_with_skill_popup(key_event),
//!             ActivePopup::None => self.handle_key_event_without_popup(key_event),
//!         }
//!     }
//! }
//! ```

use crossterm::event::{KeyCode, KeyEvent, KeyEventKind, KeyModifiers};

/// Key event routing abstraction for mode-based event dispatch.
///
/// Implementers define how to route key events based on the current mode (e.g., active popup,
/// recording state, selection mode). This trait separates the dispatch logic from individual
/// key handlers and provides utilities for modifier-key matching.
pub trait KeyEventRouter {
    /// Dispatch a key event to the appropriate handler based on current mode.
    ///
    /// Returns a tuple `(InputResult, needs_redraw)` indicating:
    /// - The semantic result of key handling (text input, command submission, etc.)
    /// - Whether the UI should be redrawn
    fn dispatch_key_event(&mut self, key_event: KeyEvent) -> (crate::bottom_pane::InputResult, bool);

    /// Check if a key event matches a given code and modifier combination.
    ///
    /// Ignores state, kind, and flags fields; only matches on code and modifiers.
    fn matches_key(key_event: &KeyEvent, code: KeyCode, modifiers: KeyModifiers) -> bool {
        key_event.code == code && key_event.modifiers == modifiers
    }

    /// Check if a key has a control modifier (Ctrl on Unix, Cmd on macOS, Ctrl on Windows).
    fn has_ctrl(key_event: &KeyEvent) -> bool {
        key_event.modifiers.contains(KeyModifiers::CONTROL)
    }

    /// Check if a key has an alt modifier.
    fn has_alt(key_event: &KeyEvent) -> bool {
        key_event.modifiers.contains(KeyModifiers::ALT)
    }

    /// Check if a key has a shift modifier.
    fn has_shift(key_event: &KeyEvent) -> bool {
        key_event.modifiers.contains(KeyModifiers::SHIFT)
    }

    /// Check if a key has either Ctrl or Alt modifier.
    fn has_ctrl_or_alt(key_event: &KeyEvent) -> bool {
        Self::has_ctrl(key_event) || Self::has_alt(key_event)
    }

    /// Check if a key event is a press (not repeat or release).
    fn is_press(key_event: &KeyEvent) -> bool {
        matches!(key_event.kind, KeyEventKind::Press)
    }

    /// Check if a key event is press or repeat.
    fn is_press_or_repeat(key_event: &KeyEvent) -> bool {
        matches!(key_event.kind, KeyEventKind::Press | KeyEventKind::Repeat)
    }

    /// Check if a key event is a release.
    fn is_release(key_event: &KeyEvent) -> bool {
        matches!(key_event.kind, KeyEventKind::Release)
    }

    /// Check if a char key code equals the given character.
    fn char_matches(key_event: &KeyEvent, c: char) -> bool {
        matches!(key_event.code, KeyCode::Char(ch) if ch == c)
    }

    /// Check if a key is alphanumeric (a-z, A-Z, 0-9).
    fn is_alphanumeric(key_event: &KeyEvent) -> bool {
        matches!(key_event.code, KeyCode::Char(c) if c.is_alphanumeric())
    }

    /// Check if a key is a navigation key (Up, Down, Left, Right, Home, End, etc.).
    fn is_navigation_key(key_event: &KeyEvent) -> bool {
        matches!(
            key_event.code,
            KeyCode::Up
                | KeyCode::Down
                | KeyCode::Left
                | KeyCode::Right
                | KeyCode::Home
                | KeyCode::End
                | KeyCode::PageUp
                | KeyCode::PageDown
        )
    }

    /// Check if a key is a cursor movement key (Up, Down, Left, Right).
    fn is_cursor_movement(key_event: &KeyEvent) -> bool {
        matches!(
            key_event.code,
            KeyCode::Up | KeyCode::Down | KeyCode::Left | KeyCode::Right
        )
    }

    /// Clear modifier state for a key event, returning only code and kind.
    ///
    /// Useful for checking unmodified key codes in fallback patterns.
    fn strip_modifiers(key_event: &KeyEvent) -> (KeyCode, KeyEventKind) {
        (key_event.code, key_event.kind)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crossterm::event::KeyEvent;

    #[test]
    fn matches_key_exact_match() {
        let event = KeyEvent::new(KeyCode::Char('a'), KeyModifiers::CONTROL);
        assert!(KeyEventRouter::matches_key(
            &event,
            KeyCode::Char('a'),
            KeyModifiers::CONTROL
        ));
    }

    #[test]
    fn matches_key_ignores_kind() {
        let event = KeyEvent::new_with_kind(
            KeyCode::Up,
            KeyModifiers::NONE,
            KeyEventKind::Press,
        );
        assert!(KeyEventRouter::matches_key(
            &event,
            KeyCode::Up,
            KeyModifiers::NONE
        ));

        let release = KeyEvent::new_with_kind(
            KeyCode::Up,
            KeyModifiers::NONE,
            KeyEventKind::Release,
        );
        assert!(KeyEventRouter::matches_key(
            &release,
            KeyCode::Up,
            KeyModifiers::NONE
        ));
    }

    #[test]
    fn has_ctrl_detects_control_modifier() {
        let with_ctrl = KeyEvent::new(KeyCode::Char('a'), KeyModifiers::CONTROL);
        assert!(KeyEventRouter::has_ctrl(&with_ctrl));

        let without_ctrl = KeyEvent::new(KeyCode::Char('a'), KeyModifiers::NONE);
        assert!(!KeyEventRouter::has_ctrl(&without_ctrl));
    }

    #[test]
    fn is_press_or_repeat_matches_both() {
        let press = KeyEvent::new_with_kind(
            KeyCode::Char('a'),
            KeyModifiers::NONE,
            KeyEventKind::Press,
        );
        assert!(KeyEventRouter::is_press_or_repeat(&press));

        let repeat = KeyEvent::new_with_kind(
            KeyCode::Char('a'),
            KeyModifiers::NONE,
            KeyEventKind::Repeat,
        );
        assert!(KeyEventRouter::is_press_or_repeat(&repeat));

        let release = KeyEvent::new_with_kind(
            KeyCode::Char('a'),
            KeyModifiers::NONE,
            KeyEventKind::Release,
        );
        assert!(!KeyEventRouter::is_press_or_repeat(&release));
    }

    #[test]
    fn char_matches_compares_character() {
        let event = KeyEvent::new(KeyCode::Char('a'), KeyModifiers::NONE);
        assert!(KeyEventRouter::char_matches(&event, 'a'));
        assert!(!KeyEventRouter::char_matches(&event, 'b'));
    }

    #[test]
    fn is_navigation_key_identifies_arrows() {
        let up = KeyEvent::new(KeyCode::Up, KeyModifiers::NONE);
        assert!(KeyEventRouter::is_navigation_key(&up));

        let down = KeyEvent::new(KeyCode::Down, KeyModifiers::NONE);
        assert!(KeyEventRouter::is_navigation_key(&down));

        let a = KeyEvent::new(KeyCode::Char('a'), KeyModifiers::NONE);
        assert!(!KeyEventRouter::is_navigation_key(&a));
    }

    #[test]
    fn is_cursor_movement_identifies_directions() {
        let up = KeyEvent::new(KeyCode::Up, KeyModifiers::NONE);
        assert!(KeyEventRouter::is_cursor_movement(&up));

        let home = KeyEvent::new(KeyCode::Home, KeyModifiers::NONE);
        assert!(!KeyEventRouter::is_cursor_movement(&home));
    }

    #[test]
    fn is_alphanumeric_matches_letters_and_digits() {
        let letter = KeyEvent::new(KeyCode::Char('a'), KeyModifiers::NONE);
        assert!(KeyEventRouter::is_alphanumeric(&letter));

        let digit = KeyEvent::new(KeyCode::Char('5'), KeyModifiers::NONE);
        assert!(KeyEventRouter::is_alphanumeric(&digit));

        let space = KeyEvent::new(KeyCode::Char(' '), KeyModifiers::NONE);
        assert!(!KeyEventRouter::is_alphanumeric(&space));
    }
}
