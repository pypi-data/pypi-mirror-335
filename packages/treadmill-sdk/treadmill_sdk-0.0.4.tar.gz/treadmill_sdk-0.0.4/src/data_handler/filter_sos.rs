use sci_rs::signal::filter::{design::*, sosfiltfilt_dyn};

use crate::data_handler::filter::*;

crate::cfg_import_logging!();

#[cfg_attr(target_family = "wasm", wasm_bindgen::prelude::wasm_bindgen)]
pub struct SosFilter {
  sos_filter: Vec<Sos<f64>>,
}

impl SosFilter {
  // pub fn new(sos: Vec<Sos<f64>>) -> Self {
  //   SosFilter { sos }
  // }

  pub fn create_lowpass(order: usize, lowcut: f64, fs: f64) -> Self {
    let sos_filter = sos_butter_lowpass(order, lowcut, fs);
    SosFilter { sos_filter }
  }

  pub fn create_highpass(order: usize, highcut: f64, fs: f64) -> Self {
    let sos_filter = sos_butter_highpass(order, highcut, fs);
    SosFilter { sos_filter }
  }

  pub fn create_bandpass(order: usize, lowcut: f64, highcut: f64, fs: f64) -> Self {
    let sos_filter = sos_butter_bandpass(order, lowcut, highcut, fs);
    SosFilter { sos_filter }
  }

  pub fn create_bandstop(order: usize, lowcut: f64, highcut: f64, fs: f64) -> Self {
    let sos_filter = sos_butter_bandstop(order, lowcut, highcut, fs);
    SosFilter { sos_filter }
  }

  pub fn perform<I>(self, input: I) -> Vec<f64>
  where
    I: IntoIterator<Item = f64>,
  {
    sosfiltfilt_dyn(input.into_iter(), &self.sos_filter)
  }

  // pub fn perform_lowpass<I>(self, input: I) -> Vec<f64>
  // where
  //   I: IntoIterator<Item = f64>,
  // {
  //   sosfiltfilt_dyn(input.into_iter(), &self.sos_filter)
  // }

  // pub fn perform_highpass<I>(self, input: I) -> Vec<f64>
  // where
  //   I: IntoIterator<Item = f64>,
  // {
  //   sosfiltfilt_dyn(input.into_iter(), &self.sos_filter)
  // }

  // pub fn perform_bandpass<I>(self, input: I) -> Vec<f64>
  // where
  //   I: IntoIterator<Item = f64>,
  // {
  //   sosfiltfilt_dyn(input.into_iter(), &self.sos_filter)
  // }

  // pub fn perform_bandstop<I>(self, input: I) -> Vec<f64>
  // where
  //   I: IntoIterator<Item = f64>,
  // {
  //   sosfiltfilt_dyn(input.into_iter(), &self.sos_filter)
  // }
}
