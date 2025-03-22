#[derive(thiserror::Error, Debug)]
pub enum WarningKind {
    #[error("An empty quoted key is allowed, but it is not recommended")]
    KeyEmpty,
}

#[derive(Debug)]
pub struct Warning {
    pub kind: WarningKind,
    pub range: text::Range,
}

impl diagnostic::SetDiagnostics for Warning {
    fn set_diagnostics(&self, diagnostics: &mut Vec<diagnostic::Diagnostic>) {
        diagnostics.push(diagnostic::Diagnostic::new_warning(
            self.kind.to_string(),
            self.range,
        ))
    }
}
