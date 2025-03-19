use tracing_subscriber::filter::LevelFilter;

#[allow(dead_code)]
#[repr(u8)]
#[derive(Debug, Clone, Copy, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
pub enum LogLevel {
  Error = 0,
  Warn = 1,
  Info = 2,
  Debug = 3,
  Trace = 4,
}

impl Into<LogLevel> for u8 {
  fn into(self) -> LogLevel {
    match self {
      0 => LogLevel::Error,
      1 => LogLevel::Warn,
      2 => LogLevel::Info,
      3 => LogLevel::Debug,
      4 => LogLevel::Trace,
      _ => LogLevel::Info,
    }
  }
}

impl Into<log::Level> for LogLevel {
  fn into(self) -> log::Level {
    match self {
      LogLevel::Error => log::Level::Error,
      LogLevel::Warn => log::Level::Warn,
      LogLevel::Info => log::Level::Info,
      LogLevel::Debug => log::Level::Debug,
      LogLevel::Trace => log::Level::Trace,
    }
  }
}

impl Into<tracing::Level> for LogLevel {
  fn into(self) -> tracing::Level {
    match self {
      LogLevel::Error => tracing::Level::ERROR,
      LogLevel::Warn => tracing::Level::WARN,
      LogLevel::Info => tracing::Level::INFO,
      LogLevel::Debug => tracing::Level::DEBUG,
      LogLevel::Trace => tracing::Level::TRACE,
    }
  }
}

impl Into<LevelFilter> for LogLevel {
  fn into(self) -> LevelFilter {
    match self {
      LogLevel::Error => LevelFilter::ERROR,
      LogLevel::Warn => LevelFilter::WARN,
      LogLevel::Info => LevelFilter::INFO,
      LogLevel::Debug => LevelFilter::DEBUG,
      LogLevel::Trace => LevelFilter::TRACE,
    }
  }
}
