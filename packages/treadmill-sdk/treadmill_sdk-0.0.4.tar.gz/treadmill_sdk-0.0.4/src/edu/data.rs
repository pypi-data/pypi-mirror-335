use crate::data_handler::data_handler::{parse_afe_data, parse_imu_data};
use crate::generated::edu_proto::*;
use crate::proto::edu::msg_builder::*;
use std::sync::Mutex;

crate::cfg_import_logging!();

lazy_static::lazy_static! {
  // 默认缓冲区长度, 1000个数据点
  static ref AFE_BUFFER_LEN: Mutex<usize> = Mutex::new(1000);
  static ref AFE_DATA_BUFFER: Mutex<Vec<AfeData>> = Mutex::new(Vec::new());
  static ref AFE_CFG: Mutex<AfeConfig> = Mutex::new(AfeConfig::default());

  // 默认缓冲区长度, 1000个数据点
  static ref IMU_BUFFER_LEN: Mutex<usize> = Mutex::new(1000);
  static ref IMU_DATA_BUFFER: Mutex<Vec<ImuData>> = Mutex::new(Vec::new());

  static ref MAG_BUFFER_LEN: Mutex<usize> = Mutex::new(1000);
  static ref MAG_DATA_BUFFER: Mutex<Vec<MagData>> = Mutex::new(Vec::new());
}

#[allow(unused_variables)]
fn notify_edu_message(device_id: String, msg: &EduMessage) {
  // cfg_if::cfg_if! {
  // if #[cfg(feature = "examples")] {
  //   crate::callback::callback::run_msg_resp_callback(device_id, serde_json::to_string(msg).unwrap_or_else(|_| "".to_string()));
  // } else if #[cfg(feature = "python")] {
  //   if !crate::python::callback::is_registered_msg_resp() {
  //     return;
  //   }
  //   crate::python::callback::run_msg_resp_callback(
  //     device_id,
  //     serde_json::to_string(msg).unwrap_or_else(|_| "".to_string()),
  //   );
  // }
  // else if #[cfg(target_family = "wasm")] {
  //   crate::wasm::edu::wasm_edu::run_resp_callback(msg);
  // }
  // }
}

pub fn handle_edu_message(device_id: String, msg: &EduMessage) {
  match msg {
    EduMessage::Sensor2App(ref message) => {
      if let Some(afe_data) = &message.afe_data {
        add_afe_data_to_buffer(afe_data);
        return;
      } else if let Some(imu_data) = &message.imu_data {
        add_imu_data_to_buffer(imu_data);
        return;
      } else if let Some(_mag_data) = &message.mag_data {
        // add_mag_data_to_buffer(mag_data);
        return;
      }
      notify_edu_message(device_id, msg);
    }
    _ => {
      info!("Received message: {:?}", msg);
      notify_edu_message(device_id, msg);
    }
  }
}

#[cfg_attr(feature = "python", pyo3::pyfunction)]
#[cfg_attr(target_family = "wasm", wasm_bindgen::prelude::wasm_bindgen)]
pub fn edu_set_afe_buffer_cfg(buff_len: usize) {
  let mut buff_len_guard = AFE_BUFFER_LEN.lock().unwrap();
  *buff_len_guard = buff_len;
}

#[cfg_attr(feature = "python", pyo3::pyfunction)]
#[cfg_attr(target_family = "wasm", wasm_bindgen::prelude::wasm_bindgen)]
pub fn edu_set_imu_buffer_cfg(imu_buffer_len: usize) {
  let mut imu_buffer_len_guard = IMU_BUFFER_LEN.lock().unwrap();
  *imu_buffer_len_guard = imu_buffer_len;
}

#[cfg_attr(feature = "python", pyo3::pyfunction)]
#[cfg_attr(target_family = "wasm", wasm_bindgen::prelude::wasm_bindgen)]
pub fn edu_set_mag_buffer_cfg(mag_buffer_len: usize) {
  let mut mag_buffer_len_guard = MAG_BUFFER_LEN.lock().unwrap();
  *mag_buffer_len_guard = mag_buffer_len;
}

#[cfg_attr(feature = "python", pyo3::pyfunction)]
#[cfg_attr(target_family = "wasm", wasm_bindgen::prelude::wasm_bindgen)]
pub fn edu_clear_afe_buffer() {
  let mut buff = AFE_DATA_BUFFER.lock().unwrap();
  buff.clear();
}

#[cfg_attr(feature = "python", pyo3::pyfunction)]
#[cfg_attr(target_family = "wasm", wasm_bindgen::prelude::wasm_bindgen)]
pub fn edu_clear_imu_buffer() {
  let mut buff = IMU_DATA_BUFFER.lock().unwrap();
  buff.clear();
}

#[cfg_attr(feature = "python", pyo3::pyfunction)]
#[cfg_attr(target_family = "wasm", wasm_bindgen::prelude::wasm_bindgen)]
pub fn edu_clear_mag_buffer() {
  let mut buff = MAG_DATA_BUFFER.lock().unwrap();
  buff.clear();
}

pub fn get_afe_sample_buffer(take: usize, clean: bool) -> Vec<AfeData> {
  let mut afe_data_buffer = AFE_DATA_BUFFER.lock().unwrap();
  let len = afe_data_buffer.len();

  let take = take.min(len); // 确保 take 不超过缓冲区长度

  // 获取最后 n 个元素
  let data = afe_data_buffer[len - take..].to_vec();

  if clean {
    afe_data_buffer.clear();
  } else {
    afe_data_buffer.drain(len - take..);
  }
  data
}

pub fn get_imu_sample_buffer(take: usize, clean: bool) -> Vec<ImuData> {
  let mut imu_data_buffer = IMU_DATA_BUFFER.lock().unwrap();
  let len = imu_data_buffer.len();
  let take = take.min(len); // 确保 take 不超过缓冲区长度

  // 获取最后 n 个元素
  let imu_data = imu_data_buffer[len - take..].to_vec();

  if clean {
    imu_data_buffer.clear();
  } else {
    imu_data_buffer.drain(len - take..);
  }
  imu_data
}

pub fn get_mag_sample_buffer(take: usize, clean: bool) -> Vec<MagData> {
  let mut mag_data_buffer = MAG_DATA_BUFFER.lock().unwrap();
  let len = mag_data_buffer.len();
  let take = take.min(len); // 确保 take 不超过缓冲区长度

  // 获取最后 n 个元素
  let mag_data = mag_data_buffer[len - take..].to_vec();

  if clean {
    mag_data_buffer.clear();
  } else {
    mag_data_buffer.drain(len - take..);
  }
  mag_data
}

#[cfg_attr(feature = "python", pyo3::pyfunction)]
pub fn get_afe_buffer(take: usize, clean: bool) -> Vec<Vec<f64>> {
  let arr = get_afe_sample_buffer(take, clean)
    .into_iter()
    .map(|data| {
      let mut result = vec![data.seq_num as f64, data.lead_off_bits as f64];
      let flattened: Vec<u8> = data.channel_adc_value.iter().flatten().cloned().collect();
      result.extend(parse_afe_data(&flattened, 6.0));
      result
    })
    .collect();

  arr
}

#[cfg_attr(feature = "python", pyo3::pyfunction)]
pub fn get_imu_buffer(take: usize, clean: bool) -> Vec<Vec<i16>> {
  let arr = get_imu_sample_buffer(take, clean)
    .into_iter()
    .map(|sample| {
      let mut result = vec![sample.seq_num as i16];
      result.extend(parse_imu_data(&sample.acc_raw_data));
      result.extend(parse_imu_data(&sample.gyro_raw_data));
      result
    })
    .collect();

  arr
}

#[cfg_attr(feature = "python", pyo3::pyfunction)]
pub fn get_mag_buffer(take: usize, clean: bool) -> Vec<Vec<i16>> {
  let arr = get_mag_sample_buffer(take, clean)
    .into_iter()
    .map(|sample| {
      let mut result = vec![sample.seq_num as i16];
      result.extend(parse_imu_data(&sample.mag_raw_data));
      result
    })
    .collect();

  arr
}

pub fn add_afe_data_to_buffer(data: &AfeData) {
  let mut afe_data_buffer = AFE_DATA_BUFFER.lock().unwrap();
  afe_data_buffer.push(data.clone());

  let max_len = *AFE_BUFFER_LEN.lock().unwrap();
  if afe_data_buffer.len() > max_len {
    let excess = afe_data_buffer.len() - max_len;
    afe_data_buffer.drain(0..excess);
  }
}

pub fn add_imu_data_to_buffer(data: &ImuData) {
  let mut imu_data_buffer = IMU_DATA_BUFFER.lock().unwrap();
  imu_data_buffer.push(data.clone());

  let max_len = *IMU_BUFFER_LEN.lock().unwrap();
  if imu_data_buffer.len() > max_len {
    let excess = imu_data_buffer.len() - max_len;
    imu_data_buffer.drain(0..excess);
  }
}

pub fn add_mag_data_to_buffer(data: &MagData) {
  let mut mag_data_buffer = MAG_DATA_BUFFER.lock().unwrap();
  mag_data_buffer.push(data.clone());

  let max_len = *MAG_BUFFER_LEN.lock().unwrap();
  if mag_data_buffer.len() > max_len {
    let excess = mag_data_buffer.len() - max_len;
    mag_data_buffer.drain(0..excess);
  }
}
