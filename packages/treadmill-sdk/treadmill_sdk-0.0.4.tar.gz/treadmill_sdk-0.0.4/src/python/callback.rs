use crate::generated::treadmill_proto::*;
// use crate::proto::enums::*;
use crate::python::callback::gait_analysis_result::FootStrike;
use pyo3::prelude::*;
use pyo3::types::PyTuple;
use std::sync::Mutex;

crate::cfg_import_logging!();

lazy_static::lazy_static! {
  static ref ON_MSG_RESP: Mutex<Option<PyObject>> = Mutex::new(None);
  static ref ON_EEG_DATA: Mutex<Option<PyObject>> = Mutex::new(None);
  static ref ON_IMU_DATA: Mutex<Option<PyObject>> = Mutex::new(None);
  pub static ref ON_IMP_DATA: Mutex<Option<PyObject>> = Mutex::new(None);

  static ref ON_GAIT_DATA: Mutex<Option<PyObject>> = Mutex::new(None);
  static ref ON_ABNORMAL_EVENT: Mutex<Option<PyObject>> = Mutex::new(None);
}

#[pyfunction]
pub fn set_msg_resp_callback(_py: Python, func: Py<PyAny>) -> PyResult<()> {
  let mut cb = ON_MSG_RESP.lock().unwrap();
  *cb = Some(func.into());
  Ok(())
}

#[pyfunction]
pub fn unresister_msg_resp_callback() {
  let mut cb = ON_MSG_RESP.lock().unwrap();
  *cb = None;
}

#[pyfunction]
pub fn set_gait_data_callback(_py: Python, func: Py<PyAny>) -> PyResult<()> {
  let mut cb = ON_GAIT_DATA.lock().unwrap();
  *cb = Some(func.into());
  Ok(())
}

#[pyfunction]
pub fn unresister_gait_data_callback() {
  let mut cb = ON_GAIT_DATA.lock().unwrap();
  *cb = None;
}

#[pyfunction]
pub fn set_abnormal_event_callback(_py: Python, func: Py<PyAny>) -> PyResult<()> {
  let mut cb = ON_ABNORMAL_EVENT.lock().unwrap();
  *cb = Some(func.into());
  Ok(())
}

#[pyfunction]
pub fn set_imp_data_callback(_py: Python, func: Py<PyAny>) -> PyResult<()> {
  let mut cb = ON_IMP_DATA.lock().unwrap();
  *cb = Some(func.into());
  Ok(())
}

pub fn unresister_imp_data_callback() {
  let mut cb = ON_IMP_DATA.lock().unwrap();
  *cb = None;
}

#[pyfunction]
pub fn set_eeg_data_callback(_py: Python, func: Py<PyAny>) -> PyResult<()> {
  let mut cb = ON_EEG_DATA.lock().unwrap();
  *cb = Some(func.into());
  Ok(())
}

#[pyfunction]
pub fn set_imu_data_callback(_py: Python, func: Py<PyAny>) -> PyResult<()> {
  let mut cb = ON_IMU_DATA.lock().unwrap();
  *cb = Some(func.into());
  Ok(())
}

pub fn is_registered_imp_data() -> bool {
  ON_IMP_DATA.lock().unwrap().is_some()
}

pub fn is_registered_eeg_data() -> bool {
  ON_EEG_DATA.lock().unwrap().is_some()
}

pub fn is_registered_imu_data() -> bool {
  ON_IMU_DATA.lock().unwrap().is_some()
}

pub fn is_registered_msg_resp() -> bool {
  ON_MSG_RESP.lock().unwrap().is_some()
}

pub fn run_msg_resp_callback(device_id: String, resp: String) {
  let cb = ON_MSG_RESP.lock().unwrap();
  if let Some(ref cb) = *cb {
    Python::with_gil(|py| {
      let _ = cb.call1(py, (device_id, resp));
    });
  }
}

pub fn run_eeg_data_callback(data: Vec<u8>) {
  Python::with_gil(|py| {
    let cb = ON_EEG_DATA.lock().unwrap();
    if let Some(ref cb) = *cb {
      let args = PyTuple::new(py, &[data]).unwrap();
      match cb.call1(py, args) {
        Ok(_) => {}
        Err(e) => {
          error!("Error calling callback: {:?}", e);
        }
      }
    }
  });
}

pub fn run_gait_data_callback(timestamp: u32, left_foot: bool, pattern: u8, gait_duration: u32) {
  Python::with_gil(|py| {
    let cb = ON_GAIT_DATA.lock().unwrap();
    if let Some(ref cb) = *cb {
      let args = PyTuple::new(
        py,
        &[
          timestamp,
          if left_foot { 1 } else { 0 },
          pattern as u32,
          gait_duration,
        ],
      )
      .unwrap();
      match cb.call1(py, args) {
        Ok(_) => {}
        Err(e) => {
          error!("Error calling callback: {:?}", e);
        }
      }
    }
  });
}

pub fn run_abnormal_event_callback(timestamp: u32, event_type: u32) {
  Python::with_gil(|py| {
    let cb = ON_ABNORMAL_EVENT.lock().unwrap();
    if let Some(ref cb) = *cb {
      let args = PyTuple::new(py, &[timestamp, event_type]).unwrap();
      match cb.call1(py, args) {
        Ok(_) => {}
        Err(e) => {
          error!("Error calling callback: {:?}", e);
        }
      }
    }
  });
}

pub fn on_recv_gait_result(result: GaitAnalysisResult) {
  if result.abnormal_gait > 0 {
    run_abnormal_event_callback(result.timestamp, result.abnormal_gait as u32);
  }
  if result.foot > 0 && result.gait_duration > 0 {
    run_gait_data_callback(
      result.timestamp,
      result.foot == FootStrike::LeftFoot as i32,
      result.pattern as u8,
      result.gait_duration as u32,
    );
  }
}
