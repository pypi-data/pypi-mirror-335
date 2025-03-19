use super::filter_bc::*;
use core::iter::Sum;
use lazy_static::lazy_static;
use nalgebra::RealField;
use num_traits::Float;
#[allow(unused_imports)]
use sci_rs::signal::filter::{design::*, sosfiltfilt_dyn};
use sci_rs::stats::*;
use std::sync::Mutex;

use super::enums::{AggOperations, DownsamplingOperations, NoiseTypes};

const BAND_PASS_LOWER_CUTOFF: f64 = 2.0;
const BAND_PASS_HIGHER_CUTOFF: f64 = 45.0;

crate::cfg_import_logging!();

lazy_static! {
  static ref ENV_NOISE_TYPE: Mutex<NoiseTypes> = Mutex::new(NoiseTypes::FIFTY_AND_SIXTY); // Default noise type is 50Hz and 60Hz
  // static ref ENV_NOISE_FILTER_50: Mutex<[Vec<Sos<f64>>; 32]> = Mutex::new(core::array::from_fn(|_| sos_butter_bandstop(4, 49.0, 51.0, 250.0))); // Default FS is 250Hz
  // static ref ENV_NOISE_FILTER_60: Mutex<[Vec<Sos<f64>>; 32]> = Mutex::new(core::array::from_fn(|_| sos_butter_bandstop(4, 59.0, 61.0, 250.0))); // Default FS is 250Hz
  // static ref IMPEDANCE_FILTER_31_2: Mutex<[Vec<Sos<f64>>; 32]> = Mutex::new(core::array::from_fn(|_| sos_butter_bandpass(4, 30.0, 32.0, 250.0))); // Default FS is AC 31.2 Hz
  // static ref EEG_FILTER_2_45: Mutex<[Vec<Sos<f64>>; 32]> = Mutex::new(core::array::from_fn(|_| sos_butter_bandpass(4, BAND_PASS_LOWER_CUTOFF, BAND_PASS_HIGHER_CUTOFF, 250.0))); // Default FS is 250Hz

  static ref ENV_NOISE_FILTER_50: Mutex<[BandStopFilter; 32]> = Mutex::new(core::array::from_fn(|_| BandStopFilter::new(4, 250.0, 49.0, 51.0))); // Default FS is 250Hz
  static ref ENV_NOISE_FILTER_60: Mutex<[BandStopFilter; 32]> = Mutex::new(core::array::from_fn(|_| BandStopFilter::new(4, 250.0, 59.0, 61.0))); // Default FS is 250Hz
  static ref IMPEDANCE_FILTER_31_2: Mutex<[BandPassFilter; 32]> = Mutex::new(core::array::from_fn(|_| BandPassFilter::new(4, 250.0, 30.0, 32.0))); // Default FS is AC 31.2 Hz
  static ref EEG_FILTER_2_45: Mutex<[BandPassFilter; 32]> = Mutex::new(core::array::from_fn(|_| BandPassFilter::new(4, 250.0, BAND_PASS_LOWER_CUTOFF, BAND_PASS_HIGHER_CUTOFF))); // Default FS is 250Hz

  // easy mode filters
  static ref EEG_FILTER_HIGH_PASS_ENABLED: Mutex<bool> = Mutex::new(false);
  static ref EEG_FILTER_LOW_PASS_ENABLED: Mutex<bool> = Mutex::new(false);
  static ref EEG_FILTER_BAND_PASS_ENABLED: Mutex<bool> = Mutex::new(false);
  static ref EEG_FILTER_BAND_STOP_ENABLED: Mutex<bool> = Mutex::new(false);

  static ref EEG_FILTER_HIGH_PASS: Mutex<[HighPassFilter; 32]> = Mutex::new(core::array::from_fn(|_| HighPassFilter::new(4, 250.0, 1.0))); // Default FS is 250Hz
  static ref EEG_FILTER_LOW_PASS: Mutex<[LowPassFilter; 32]> = Mutex::new(core::array::from_fn(|_| LowPassFilter::new(4, 250.0, 30.0))); // Default FS is 250Hz
  static ref EEG_FILTER_BAND_PASS: Mutex<[BandPassFilter; 32]> = Mutex::new(core::array::from_fn(|_| BandPassFilter::new(4, 250.0, 8.0, 13.0))); // Default FS is 250Hz
  static ref EEG_FILTER_BAND_STOP: Mutex<[BandStopFilter; 32]> = Mutex::new(core::array::from_fn(|_| BandStopFilter::new(4, 250.0, 49.0, 51.0))); // Default FS is 250Hz

//   static ref EEG_FILTER_HIGH_PASS: Mutex<[Vec<Sos<f64>>; 32]> = Mutex::new(core::array::from_fn(|_| sos_butter_highpass(4, 1.0, 250.0))); // Default FS is 250Hz
//   static ref EEG_FILTER_LOW_PASS: Mutex<[Vec<Sos<f64>>; 32]> = Mutex::new(core::array::from_fn(|_| sos_butter_lowpass(4, 30.0, 250.0))); // Default FS is 250Hz
//   static ref EEG_FILTER_BAND_PASS: Mutex<[Vec<Sos<f64>>; 32]> = Mutex::new(core::array::from_fn(|_| sos_butter_bandpass(4, 8.0, 13.0, 250.0))); // Default FS is 250Hz
//   static ref EEG_FILTER_BAND_STOP: Mutex<[Vec<Sos<f64>>; 32]> = Mutex::new(core::array::from_fn(|_| sos_butter_bandstop(4, 49.0, 51.0, 250.0))); // Default FS is 250Hz
}

// easy mode filters
pub fn set_easy_eeg_filter(
  high_pass_enabled: bool,
  high_cut: f64,
  low_pass_enabled: bool,
  low_cut: f64,
  band_pass_enabled: bool,
  band_pass_low: f64,
  band_pass_high: f64,
  band_stop_enabled: bool,
  band_stop_low: f64,
  band_stop_high: f64,
  fs: f64,
) {
  let mut eeg_filter_high_pass_enabled = EEG_FILTER_HIGH_PASS_ENABLED.lock().unwrap();
  let mut eeg_filter_low_pass_enabled = EEG_FILTER_LOW_PASS_ENABLED.lock().unwrap();
  let mut eeg_filter_band_pass_enabled = EEG_FILTER_BAND_PASS_ENABLED.lock().unwrap();
  let mut eeg_filter_band_stop_enabled = EEG_FILTER_BAND_STOP_ENABLED.lock().unwrap();
  let mut eeg_filter_high_pass = EEG_FILTER_HIGH_PASS.lock().unwrap();
  let mut eeg_filter_low_pass = EEG_FILTER_LOW_PASS.lock().unwrap();
  let mut eeg_filter_band_pass = EEG_FILTER_BAND_PASS.lock().unwrap();
  let mut eeg_filter_band_stop = EEG_FILTER_BAND_STOP.lock().unwrap();
  *eeg_filter_high_pass_enabled = high_pass_enabled;
  *eeg_filter_low_pass_enabled = low_pass_enabled;
  *eeg_filter_band_pass_enabled = band_pass_enabled;
  *eeg_filter_band_stop_enabled = band_stop_enabled;
  for i in 0..32 {
    eeg_filter_high_pass[i] = HighPassFilter::new(4, fs, high_cut);
    eeg_filter_low_pass[i] = LowPassFilter::new(4, fs, low_cut);
    eeg_filter_band_pass[i] = BandPassFilter::new(4, fs, band_pass_low, band_pass_high);
    eeg_filter_band_stop[i] = BandStopFilter::new(4, fs, band_stop_low, band_stop_high);

    // eeg_filter_high_pass[i] = sos_butter_highpass(4, high_cut.into(), fs);
    // eeg_filter_low_pass[i] = sos_butter_lowpass(4, low_cut.into(), fs);
    // eeg_filter_band_pass[i] =
    //   sos_butter_bandpass(4, band_pass_low.into(), band_pass_high.into(), fs);
    // eeg_filter_band_stop[i] =
    //   sos_butter_bandstop(4, band_stop_low.into(), band_stop_high.into(), fs);
  }
}

pub fn apply_easy_eeg_filters(data: Vec<f64>, channel: usize) -> Vec<f64> {
  let eeg_filter_high_pass_enabled = EEG_FILTER_HIGH_PASS_ENABLED.lock().unwrap();
  let eeg_filter_low_pass_enabled = EEG_FILTER_LOW_PASS_ENABLED.lock().unwrap();
  let eeg_filter_band_pass_enabled = EEG_FILTER_BAND_PASS_ENABLED.lock().unwrap();
  let eeg_filter_band_stop_enabled = EEG_FILTER_BAND_STOP_ENABLED.lock().unwrap();

  let mut filter_data = data;
  if *eeg_filter_high_pass_enabled {
    let mut high_pass = EEG_FILTER_HIGH_PASS.lock().unwrap();
    filter_data = high_pass[channel].process_iter(filter_data);
    // filter_data = sosfiltfilt_dyn(filter_data.into_iter(), &high_pass[channel]);
  }
  if *eeg_filter_low_pass_enabled {
    let mut low_pass = EEG_FILTER_LOW_PASS.lock().unwrap();
    filter_data = low_pass[channel].process_iter(filter_data);
    // filter_data = sosfiltfilt_dyn(filter_data.into_iter(), &low_pass[channel]);
  }
  if *eeg_filter_band_pass_enabled {
    let mut band_pass = EEG_FILTER_BAND_PASS.lock().unwrap();
    filter_data = band_pass[channel].process_iter(filter_data);
    // filter_data = sosfiltfilt_dyn(filter_data.into_iter(), &band_pass[channel]);
  }
  if *eeg_filter_band_stop_enabled {
    let mut band_stop = EEG_FILTER_BAND_STOP.lock().unwrap();
    filter_data = band_stop[channel].process_iter(filter_data);
    // filter_data = sosfiltfilt_dyn(filter_data.into_iter(), &band_stop[channel]);
  }
  filter_data
}

// Set the noise type & FS for the environment
pub fn set_env_noise_type(noise_type: NoiseTypes, fs: f64) {
  let mut env_noise_type = ENV_NOISE_TYPE.lock().unwrap();
  *env_noise_type = noise_type;

  let mut env_noise_filter_50 = ENV_NOISE_FILTER_50.lock().unwrap();
  let mut env_noise_filter_60 = ENV_NOISE_FILTER_60.lock().unwrap();
  let mut impedance_filter = IMPEDANCE_FILTER_31_2.lock().unwrap();
  let mut eeg_filter = EEG_FILTER_2_45.lock().unwrap();

  let sample_rate = fs;
  for i in 0..32 {
    env_noise_filter_50[i] = BandStopFilter::new(4, sample_rate, 49.0, 51.0);
    env_noise_filter_60[i] = BandStopFilter::new(4, sample_rate, 59.0, 61.0);
    impedance_filter[i] = BandPassFilter::new(4, sample_rate, 30.0, 32.0);
    eeg_filter[i] = BandPassFilter::new(
      4,
      sample_rate,
      BAND_PASS_LOWER_CUTOFF,
      BAND_PASS_HIGHER_CUTOFF,
    );
    // env_noise_filter_50[i] = sos_butter_bandstop(4, 49.0, 51.0, fs);
    // env_noise_filter_60[i] = sos_butter_bandstop(4, 59.0, 61.0, fs);
    // impedance_filter[i] = sos_butter_bandpass(4, 30.0, 32.0, fs);
    // eeg_filter[i] = sos_butter_bandpass(4, BAND_PASS_LOWER_CUTOFF, BAND_PASS_HIGHER_CUTOFF, fs);
  }
}

// Remove environmental noise from input data
pub fn remove_environmental_noise<I>(input: I, channel: usize) -> Vec<f64>
where
  I: IntoIterator<Item = f64>,
{
  let env_noise_type = ENV_NOISE_TYPE.lock().unwrap();
  match *env_noise_type {
    NoiseTypes::FIFTY => {
      // info!("Removing 50Hz noise");
      let mut env_noise_filter_50 = ENV_NOISE_FILTER_50.lock().unwrap();
      env_noise_filter_50[channel].process_iter(input)
      // sosfiltfilt_dyn(input.into_iter(), &env_noise_filter_50[channel])
    }
    NoiseTypes::SIXTY => {
      // info!("Removing 60Hz noise");
      let mut env_noise_filter_60 = ENV_NOISE_FILTER_60.lock().unwrap();
      env_noise_filter_60[channel].process_iter(input)
      // sosfiltfilt_dyn(input.into_iter(), &env_noise_filter_60[channel])
    }
    NoiseTypes::FIFTY_AND_SIXTY => {
      // info!("Removing 50Hz and 60Hz noise");
      let mut env_noise_filter_50 = ENV_NOISE_FILTER_50.lock().unwrap();
      let mut env_noise_filter_60 = ENV_NOISE_FILTER_60.lock().unwrap();
      let data = env_noise_filter_50[channel].process_iter(input);
      env_noise_filter_60[channel].process_iter(data)
      // let data = sosfiltfilt_dyn(input.into_iter(), &env_noise_filter_50[channel]);
      // sosfiltfilt_dyn(data.into_iter(), &env_noise_filter_60[channel])
    }
  }
}

pub fn perform_impendance_filter<I>(input: I, channel: usize) -> Vec<f64>
where
  I: IntoIterator<Item = f64>,
{
  // info!("Performing impedance filter");
  // let mut filter = IMPEDANCE_FILTER_31_2_0.lock().unwrap();
  // filter.process_iter(input)

  let mut filter = IMPEDANCE_FILTER_31_2.lock().unwrap();
  filter[channel].process_iter(input)
  // sosfiltfilt_dyn(input.into_iter(), &filter[channel])
}

pub fn perform_default_filter<I>(input: I, channel: usize) -> Vec<f64>
where
  I: IntoIterator<Item = f64>,
{
  let mut eeg_filter = EEG_FILTER_2_45.lock().unwrap();
  eeg_filter[channel].process_iter(input)
  // sosfiltfilt_dyn(input.into_iter(), &eeg_filter[channel])
}

// pub fn perform_lowpass<I>(input: I, order: usize, lowcut: f64, fs: f64) -> Vec<f64>
// where
//   I: IntoIterator<Item = f64>,
// {
//   let sos_filter = sos_butter_lowpass(order, lowcut, fs);
//   sosfiltfilt_dyn(input.into_iter(), &sos_filter)
// }

// pub fn perform_highpass<I>(input: I, order: usize, highcut: f64, fs: f64) -> Vec<f64>
// where
//   I: IntoIterator<Item = f64>,
// {
//   let sos_filter = sos_butter_highpass(order, highcut, fs);
//   sosfiltfilt_dyn(input.into_iter(), &sos_filter)
// }

// pub fn perform_bandpass<I>(input: I, order: usize, lowcut: f64, highcut: f64, fs: f64) -> Vec<f64>
// where
//   I: IntoIterator<Item = f64>,
// {
//   let sos_filter = sos_butter_bandpass(order, lowcut, highcut, fs);
//   sosfiltfilt_dyn(input.into_iter(), &sos_filter)
// }

// pub fn perform_bandstop<I>(input: I, order: usize, lowcut: f64, highcut: f64, fs: f64) -> Vec<f64>
// where
//   I: IntoIterator<Item = f64>,
// {
//   let sos_filter = sos_butter_bandstop(order, lowcut, highcut, fs);
//   sosfiltfilt_dyn(input.into_iter(), &sos_filter)
// }

// MATLAB style function to generate Second Order Section (SOS) lowpass filter
pub fn sos_butter_lowpass<F>(order: usize, lowcut: F, fs: F) -> Vec<Sos<F>>
where
  F: Float + RealField + Sum,
{
  // Design Second Order Section (SOS) filter
  let filter = butter_dyn(
    order,
    [lowcut].to_vec(),
    Some(FilterBandType::Lowpass),
    Some(false),
    Some(FilterOutputType::Sos),
    Some(fs),
  );
  let DigitalFilter::Sos(SosFormatFilter { sos }) = filter else {
    panic!("Failed to design filter");
  };
  sos
}

// MATLAB style function to generate Second Order Section (SOS) highpass filter
pub fn sos_butter_highpass<F>(order: usize, highcut: F, fs: F) -> Vec<Sos<F>>
where
  F: Float + RealField + Sum,
{
  // Design Second Order Section (SOS) filter
  let filter = butter_dyn(
    order,
    [highcut].to_vec(),
    Some(FilterBandType::Highpass),
    Some(false),
    Some(FilterOutputType::Sos),
    Some(fs),
  );
  let DigitalFilter::Sos(SosFormatFilter { sos }) = filter else {
    panic!("Failed to design filter");
  };
  sos
}

// MATLAB style function to generate Second Order Section (SOS) bandpass filter
pub fn sos_butter_bandpass<F>(order: usize, lowcut: F, highcut: F, fs: F) -> Vec<Sos<F>>
where
  F: Float + RealField + Sum,
{
  // Design Second Order Section (SOS) filter
  let filter = butter_dyn(
    order,
    vec![lowcut, highcut],
    Some(FilterBandType::Bandpass),
    Some(false),
    Some(FilterOutputType::Sos),
    Some(fs),
  );
  let DigitalFilter::Sos(SosFormatFilter { sos }) = filter else {
    panic!("Failed to design filter");
  };
  sos
}

// MATLAB style function to generate Second Order Section (SOS) bandstop filter
pub fn sos_butter_bandstop<F>(order: usize, lowcut: F, highcut: F, fs: F) -> Vec<Sos<F>>
where
  F: Float + RealField + Sum,
{
  // Design Second Order Section (SOS) filter
  let filter = butter_dyn(
    order,
    vec![lowcut, highcut],
    Some(FilterBandType::Bandstop),
    Some(false),
    Some(FilterOutputType::Sos),
    Some(fs),
  );
  let DigitalFilter::Sos(SosFormatFilter { sos }) = filter else {
    panic!("Failed to design filter");
  };
  sos
}

// Perform rolling filter operation
pub fn perform_rolling_filter<I>(
  input: I,
  window_size: usize,
  agg_operation: AggOperations,
) -> Vec<f64>
where
  I: IntoIterator<Item = f64>,
{
  let input: Vec<f64> = input.into_iter().collect();
  let input_len = input.len();
  let mut output = Vec::with_capacity(input_len);

  for i in 0..input_len {
    let start = if i >= window_size / 2 {
      i - window_size / 2
    } else {
      0
    };
    let end = if i + window_size / 2 < input_len {
      i + window_size / 2
    } else {
      input_len - 1
    };
    let window_slice = (&input[start..=end]).iter();

    let value = match agg_operation {
      AggOperations::Mean => {
        let (mean_value, _) = mean(window_slice);
        mean_value
      }
      AggOperations::Median => {
        let (median_value, _) = median(window_slice);
        median_value
      }
    };

    output.push(value);
  }

  output
}

// perform_downsampling
pub fn perform_downsampling<I>(
  input: I,
  window_size: usize,
  operation: DownsamplingOperations,
) -> Vec<f64>
where
  I: IntoIterator<Item = f64>,
{
  let input: Vec<f64> = input.into_iter().collect();
  let num_values = input.len() / window_size;
  let mut output = Vec::with_capacity(match operation {
    DownsamplingOperations::Extremes => num_values * 2,
    _ => num_values,
  });

  for i in 0..num_values {
    let segment = &input[i * window_size..(i + 1) * window_size];
    match operation {
      DownsamplingOperations::Mean => {
        let (mean_value, _) = mean(segment.iter());
        output.push(mean_value);
      }
      DownsamplingOperations::Median => {
        let (media_value, _) = median(segment.iter());
        output.push(media_value);
      }
      DownsamplingOperations::Max => {
        if let Some(max) = segment
          .iter()
          .cloned()
          .max_by(|a, b| a.partial_cmp(b).unwrap())
        {
          output.push(max);
        }
      }
      DownsamplingOperations::Min => {
        if let Some(min) = segment
          .iter()
          .cloned()
          .min_by(|a, b| a.partial_cmp(b).unwrap())
        {
          output.push(min);
        }
      }
      DownsamplingOperations::Sum => {
        let sum: f64 = segment.iter().sum();
        output.push(sum);
      }
      DownsamplingOperations::First => {
        output.push(segment[0]);
      }
      DownsamplingOperations::Last => {
        output.push(segment[window_size - 1]);
      }
      DownsamplingOperations::Extremes => {
        if let Some(min) = segment
          .iter()
          .cloned()
          .min_by(|a, b| a.partial_cmp(b).unwrap())
        {
          output.push(min);
        }
        if let Some(max) = segment
          .iter()
          .cloned()
          .max_by(|a, b| a.partial_cmp(b).unwrap())
        {
          output.push(max);
        }
      }
    }
  }

  output
}
