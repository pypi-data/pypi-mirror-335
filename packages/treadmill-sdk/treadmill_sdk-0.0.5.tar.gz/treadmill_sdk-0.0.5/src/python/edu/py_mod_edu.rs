use crate::edu::data::*;
use crate::proto::edu::enums::*;
use crate::proto::edu::msg_builder::edu_msg_builder;
use crate::python::py_msg_parser::MessageParser;
use crate::python::py_serial::PySerialStream;
use pyo3::prelude::*;

crate::cfg_import_logging!();

pub fn register_child_module_edu(m: &Bound<'_, PyModule>) -> PyResult<()> {
  // enums
  m.add_class::<SamplingRate>()?;
  m.add_class::<AfeSampleRate>()?;
  m.add_class::<EduImuSampleRate>()?;
  m.add_class::<MagSampleRate>()?;
  m.add_class::<CtrlBoxPort>()?;

  // structs
  m.add_class::<PyEduDevice>()?;

  // functions
  // m.add_function(wrap_pyfunction!(set_adc_cfg, m)?)?;
  m.add_function(wrap_pyfunction!(edu_set_afe_buffer_cfg, m)?)?;
  m.add_function(wrap_pyfunction!(edu_set_imu_buffer_cfg, m)?)?;
  m.add_function(wrap_pyfunction!(edu_set_mag_buffer_cfg, m)?)?;
  m.add_function(wrap_pyfunction!(edu_clear_afe_buffer, m)?)?;
  m.add_function(wrap_pyfunction!(edu_clear_imu_buffer, m)?)?;
  m.add_function(wrap_pyfunction!(edu_clear_mag_buffer, m)?)?;
  m.add_function(wrap_pyfunction!(get_afe_buffer, m)?)?;
  m.add_function(wrap_pyfunction!(get_imu_buffer, m)?)?;
  m.add_function(wrap_pyfunction!(get_mag_buffer, m)?)?;

  // BLE commands

  Ok(())
}

#[pyclass]
pub struct PyEduDevice {
  serial: PySerialStream,
}

#[pymethods]
impl PyEduDevice {
  #[new]
  pub fn new(port_name: String, baudrate: u32) -> PyResult<Self> {
    let stream = PySerialStream::new(port_name, baudrate)?;
    Ok(PyEduDevice { serial: stream })
  }

  pub fn start_data_stream<'a>(
    &self,
    py: Python<'a>,
    py_parser: PyRefMut<MessageParser>,
  ) -> PyResult<Bound<'a, PyAny>> {
    self.serial.start_data_stream(py, py_parser)
  }

  pub fn get_dongle_info<'a>(&self, py: Python<'a>) -> PyResult<Bound<'a, PyAny>> {
    let (_msg_id, cmd) = edu_msg_builder::get_dongle_info();
    self.serial.write_data(py, cmd)
  }

  pub fn get_dongle_pair_stat<'a>(&self, py: Python<'a>) -> PyResult<Bound<'a, PyAny>> {
    let (_msg_id, cmd) = edu_msg_builder::get_dongle_pair_stat();
    self.serial.write_data(py, cmd)
  }

  pub fn get_dongle_pair_cfg<'a>(&self, py: Python<'a>) -> PyResult<Bound<'a, PyAny>> {
    let (_msg_id, cmd) = edu_msg_builder::get_dongle_pair_cfg();
    self.serial.write_data(py, cmd)
  }

  pub fn get_device_info<'a>(&self, py: Python<'a>) -> PyResult<Bound<'a, PyAny>> {
    let (_msg_id, cmd) = edu_msg_builder::get_device_info();
    self.serial.write_data(py, cmd)
  }

  pub fn get_port_stat<'a>(&self, py: Python<'a>) -> PyResult<Bound<'a, PyAny>> {
    info!("get_port_stat");
    let (_msg_id, cmd) = edu_msg_builder::get_port_stat();
    info!("get_port_stat: {:?}", cmd);
    self.serial.write_data(py, cmd)
  }

  pub fn get_sensor_cfg<'a>(&self, py: Python<'a>) -> PyResult<Bound<'a, PyAny>> {
    let (_msg_id, cmd) = edu_msg_builder::get_sensor_cfg();
    self.serial.write_data(py, cmd)
  }

  pub fn start_sensor_data_stream<'a>(&self, py: Python<'a>) -> PyResult<Bound<'a, PyAny>> {
    let (_msg_id, cmd) = edu_msg_builder::start_data_stream();
    self.serial.write_data(py, cmd)
  }

  pub fn stop_sensor_data_stream<'a>(&self, py: Python<'a>) -> PyResult<Bound<'a, PyAny>> {
    let (_msg_id, cmd) = edu_msg_builder::stop_data_stream();
    self.serial.write_data(py, cmd)
  }

  pub fn set_afe_config<'a>(
    &self,
    py: Python<'a>,
    fs: AfeSampleRate,
    channel_bits: u32,
  ) -> PyResult<Bound<'a, PyAny>> {
    let (_msg_id, cmd) = edu_msg_builder::set_afe_config(fs as i32, channel_bits);
    self.serial.write_data(py, cmd)
  }

  pub fn set_imu_config<'a>(
    &self,
    py: Python<'a>,
    fs: EduImuSampleRate,
  ) -> PyResult<Bound<'a, PyAny>> {
    let (_msg_id, cmd) = edu_msg_builder::set_imu_config(ImuMode::ACC_GYRO as i32, fs as i32, 0, 0);
    self.serial.write_data(py, cmd)
  }
}
