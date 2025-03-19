use std::sync::Once;

#[allow(unused_imports)]
use super::logging::LogLevel;
use tracing_subscriber::{filter::LevelFilter, layer::SubscriberExt, *};

crate::cfg_import_logging!();

pub fn initialize_logging(level: LogLevel) {
  let level: log::Level = level.into();
  init_logging(level);
  info!(
    "{} version: {}",
    env!("CARGO_PKG_NAME"),
    env!("CARGO_PKG_VERSION")
  );
}

pub fn init_logging(level: log::Level) {
  static INIT: Once = Once::new();
  INIT.call_once(|| {
    let console_layer = fmt::Layer::new()
      .with_file(true)
      .with_line_number(true)
      .with_filter(to_log_level_filter(level));

    let subscriber: layer::Layered<
      filter::Filtered<fmt::Layer<Registry>, LevelFilter, Registry>,
      Registry,
    > = Registry::default().with(console_layer);

    tracing::subscriber::set_global_default(subscriber).expect("Failed to set subscriber");
  });
}

fn to_log_level_filter(level: log::Level) -> LevelFilter {
  match level {
    log::Level::Error => LevelFilter::ERROR,
    log::Level::Warn => LevelFilter::WARN,
    log::Level::Info => LevelFilter::INFO,
    log::Level::Debug => LevelFilter::DEBUG,
    log::Level::Trace => LevelFilter::TRACE,
  }
}
