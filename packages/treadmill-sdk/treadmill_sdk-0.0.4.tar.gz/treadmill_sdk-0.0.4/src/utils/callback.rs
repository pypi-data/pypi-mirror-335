// use cfg_if::cfg_if;
use std::sync::Arc;
use tokio::sync::Mutex;

// crate::cfg_import_logging!();

pub fn set_desktop_callback(cb: Arc<Mutex<Box<dyn Fn() + Send + Sync>>>) {
  // Example of how to invoke the callback in a desktop environment
  tokio::spawn(async move {
    let cb = cb.lock().await;
    cb();
  });
}

pub fn set_callback<F>(cb: F)
where
  F: Fn() + 'static + Send + Sync,
{
  use std::sync::Arc;
  use tokio::sync::Mutex;
  let arc_cb = Arc::new(Mutex::new(Box::new(cb) as Box<dyn Fn() + Send + Sync>));
  set_desktop_callback(arc_cb);
}
