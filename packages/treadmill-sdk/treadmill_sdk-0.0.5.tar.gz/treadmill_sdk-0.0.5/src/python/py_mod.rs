use super::callback::*;
// use crate::data_handler::enums::*;
// use crate::data_handler::filter_bc::*;
use crate::proto::enums::MsgType;
use crate::python::py_msg_parser::*;
// use crate::python::py_serial::*;
// use crate::python::py_tcp_client::*;
// use cfg_if::cfg_if;
use pyo3::prelude::*;
use pyo3::types::*;

crate::cfg_import_logging!();

cfg_if::cfg_if! {
  if #[cfg(feature = "edu")] {
    use super::edu::py_mod_edu::*;
    use super::edu::py_mod_armband::*;
  }
}

// cfg_if! {
//   if #[cfg(feature = "ble")] {
//     use super::ble::py_mod_ble::*;
//   }
// }

#[pymodule]
fn treadmill_sdk(m: &Bound<'_, PyModule>) -> PyResult<()> {
  pyo3_log::init();
  info!(
    "{} version: {}",
    env!("CARGO_PKG_NAME"),
    env!("CARGO_PKG_VERSION")
  );

  // enums
  m.add_class::<MsgType>()?;
  // m.add_class::<NoiseTypes>()?;
  // m.add_class::<DownsamplingOperations>()?;

  // structs
  m.add_class::<MessageParser>()?;
  m.add_class::<MessageStream>()?;
  // m.add_class::<PyTcpClient>()?;
  // m.add_class::<PyTcpStream>()?;
  // m.add_class::<PySerialStream>()?;

  // filters
  // m.add_class::<LowPassFilter>()?;
  // m.add_class::<HighPassFilter>()?;
  // m.add_class::<BandPassFilter>()?;
  // m.add_class::<BandStopFilter>()?;

  // functions
  // m.add_function(wrap_pyfunction!(get_bytes, m)?)?;
  m.add_function(wrap_pyfunction!(get_sdk_version, m)?)?;
  m.add_function(wrap_pyfunction!(did_receive_data, m)?)?;
  m.add_function(wrap_pyfunction!(encrypt, m)?)?;
  m.add_function(wrap_pyfunction!(decrypt, m)?)?;
  m.add_function(wrap_pyfunction!(wrap_message, m)?)?;

  // m.add_function(wrap_pyfunction!(apply_highpass_filter, m)?)?;
  // m.add_function(wrap_pyfunction!(apply_lowpass_filter, m)?)?;
  // m.add_function(wrap_pyfunction!(apply_bandpass_filter, m)?)?;
  // m.add_function(wrap_pyfunction!(apply_bandstop_filter, m)?)?;
  // m.add_function(wrap_pyfunction!(apply_downsampling, m)?)?;
  // m.add_function(wrap_pyfunction!(set_env_noise_filter_cfg, m)?)?;
  // m.add_function(wrap_pyfunction!(remove_env_noise, m)?)?;

  // m.add_function(wrap_pyfunction!(available_usb_ports, m)?)?;

  // m.add_function(wrap_pyfunction!(set_msg_resp_callback, m)?)?;
  m.add_function(wrap_pyfunction!(set_gait_data_callback, m)?)?;
  m.add_function(wrap_pyfunction!(set_abnormal_event_callback, m)?)?;

  // m.add_function(wrap_pyfunction!(set_eeg_data_callback, m)?)?;
  // m.add_function(wrap_pyfunction!(set_imu_data_callback, m)?)?;
  // m.add_function(wrap_pyfunction!(set_imp_data_callback, m)?)?;

  // Register child module

  // cfg_if::cfg_if! {
  //   if #[cfg(feature = "ble")] {
  //     trace!("Registering child module BLE");
  //     let ble = PyModule::new(m.py(), "ble")?;
  //     register_child_module_ble(&ble)?;
  //     m.add_submodule(&ble)?;
  //   }
  // }

  cfg_if::cfg_if! {
    if #[cfg(feature = "edu")] {
      trace!("Registering child module edu");
      let edu = PyModule::new(m.py(), "edu")?;
      register_child_module_edu(&edu)?;
      m.add_submodule(&edu)?;

      trace!("Registering child module armband");
      let armband = PyModule::new(m.py(), "armband")?;
      register_child_module_armband(&armband)?;
      m.add_submodule(&armband)?;
    }
  }

  Ok(())
}

#[pyfunction]
// #[text_signature = "()"]
pub fn get_sdk_version() -> PyResult<String> {
  Ok(env!("CARGO_PKG_VERSION").to_string())
}

use crate::encrypt::aes_gcm;
use crate::proto::treadmill::msg_builder::tml_msg_builder;
// use crate::generated::treadmill_proto::GaitAnalysisResult;
// use prost::bytes::Bytes;
// use prost::Message;
// use pyo3::exceptions::PyValueError;
use crate::encrypt::callback_c::handle_receive_data;
#[pyfunction]
pub fn did_receive_data(data: &[u8]) {
  handle_receive_data(data);
}

#[pyfunction]
pub fn wrap_message(py: Python, payload: &[u8]) -> PyResult<PyObject> {
  // match GaitAnalysisResult::decode(Bytes::from(payload.to_vec())) {
  //   Ok(msg) => {
  //   }
  //   Err(e) => Err(PyValueError::new_err(e.to_string())),
  // }
  let data = tml_msg_builder::build_to_app(payload);
  let py_bytes = PyBytes::new(py, &data);
  Ok(py_bytes.into())
}

// #[pyfunction]
// pub fn encrypt(
//   py: Python,
//   key: &str,
//   plaintext: &[u8],
//   user_id: &str,
//   sn_code: &str,
// ) -> PyResult<PyObject> {
//   let encrypted = aes_gcm::encrypt(key, plaintext, user_id, sn_code);
//   match encrypted {
//     Ok(encrypted) => {
//       let py_bytes = PyBytes::new(py, &encrypted);
//       Ok(py_bytes.into())
//     }
//     Err(e) => Err(e.into()),
//   }
// }

// #[pyfunction]
// pub fn decrypt(
//   py: Python,
//   key: &str,
//   ciphertext: &[u8],
//   user_id: &str,
//   sn_code: &str,
// ) -> PyResult<PyObject> {
//   let decrypted = aes_gcm::decrypt(key, ciphertext, user_id, sn_code);
//   match decrypted {
//     Ok(decrypted) => {
//       let py_bytes = PyBytes::new(py, &decrypted);
//       Ok(py_bytes.into())
//     }
//     Err(e) => Err(e.into()),
//   }
// }

#[pyfunction]
pub fn encrypt(py: Python, plaintext: &[u8]) -> PyResult<PyObject> {
  let encrypted = aes_gcm::default_encrypt(plaintext);
  match encrypted {
    Ok(encrypted) => {
      let py_bytes = PyBytes::new(py, &encrypted);
      Ok(py_bytes.into())
    }
    Err(e) => Err(e.into()),
  }
}

#[pyfunction]
pub fn decrypt(py: Python, ciphertext: &[u8]) -> PyResult<PyObject> {
  let decrypted = aes_gcm::default_decrypt(ciphertext);
  match decrypted {
    Ok(decrypted) => {
      let py_bytes = PyBytes::new(py, &decrypted);
      Ok(py_bytes.into())
    }
    Err(e) => Err(e.into()),
  }
}
