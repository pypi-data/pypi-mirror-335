//! Run with:
//!
//!     cargo run --no-default-features --example edu_test --features="examples, edu, serial"
//!

use async_std::task::sleep;
#[allow(unused_imports)]
use treadmill_sdk::proto::edu::enums::*;
use treadmill_sdk::proto::enums::MsgType;
use treadmill_sdk::proto::msg_parser::Parser;
use treadmill_sdk::serial::serialport::*;
use treadmill_sdk::{
  proto::edu::msg_builder::edu_msg_builder, utils::logging_desktop::init_logging,
};
use futures::StreamExt;
use std::error::Error;
use std::sync::Arc;
use std::time::Duration;
use tokio::sync::Mutex;
use tokio_serial::SerialStream;
treadmill_sdk::cfg_import_logging!();

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
  init_logging(log::Level::Debug);
  info!("Starting edu_test");
  // decode_msg().await;
  // return Ok(());

  let ports = list_available_ports(21059, 5);
  let port_name = ports.first();
  let port_name = match port_name {
    Some(port) => port.port_name.as_str(),
    None => {
      info!("No available port found");
      return Ok(());
    }
  };
  info!("Using port: {}", port_name);

  edu_msg_builder::set_via_mcu(true);
  edu_msg_builder::set_via_mcu(false);

  // 连接到串口
  let (reader_arc, writer_arc) = serial_open(port_name, 115200)?;
  listen_msg_stream(reader_arc).await;

  // 发送数据

  // let (_, data) = edu_msg_builder::get_dongle_info();
  // serial_write(writer_arc.clone(), &data).await;

  let (_, data) = edu_msg_builder::get_dongle_pair_stat();
  serial_write(writer_arc.clone(), &data).await;

  // let (_, data) = edu_msg_builder::get_dongle_pair_cfg();
  // serial_write(writer_arc.clone(), &data).await;

  // let (_, data) = edu_msg_builder::get_device_info();
  // serial_write(writer_arc.clone(), &data).await;

  // let (_, data) = edu_msg_builder::get_sensor_cfg();
  // serial_write(writer_arc.clone(), &data).await;

  // let (_, data) = edu_msg_builder::set_afe_config(AfeSampleRate::AFE_SR_OFF as i32, 0xff);
  // let (_, data) = edu_msg_builder::set_afe_config(AfeSampleRate::AFE_SR_250 as i32, 0xff);
  // serial_write(writer_arc.clone(), &data).await;

  // let (_, data) = edu_msg_builder::set_imu_config(ImuMode::ACC_GYRO as i32, EduImuSampleRate::IMU_SR_OFF as i32, 0, 0);
  // serial_write(writer_arc.clone(), &data).await;

  // let (_, data) = edu_msg_builder::set_mag_config(MagSampleRate::MAG_SR_OFF as i32, 0);
  // serial_write(writer_arc.clone(), &data).await;

  // let (_, data) = edu_msg_builder::start_data_stream();
  // serial_write(writer_arc.clone(), &data).await;

  sleep(Duration::from_secs(30)).await;

  Ok(())
}

pub async fn listen_msg_stream(reader_arc: Arc<Mutex<tokio::io::ReadHalf<SerialStream>>>) {
  let mut parser = Parser::new("mock-edu-device".into(), MsgType::Edu);
  let mut stream = parser.message_stream();
  tokio::spawn(async move {
    loop {
      while let Some(result) = stream.next().await {
        match result {
          Ok((_device_id, message)) => {
            debug!(
              "Received message: {:?}",
              serde_json::to_string(&message).unwrap()
            );
          }
          Err(e) => {
            error!("Error receiving message: {:?}", e);
          }
        }
      }
    }
  });
  let callback = move |data: Vec<u8>| {
    parser.receive_data(&data);
  };
  tokio::spawn(listen_serial_stream(reader_arc, callback));
}

#[allow(dead_code)]
async fn decode_msg() {
  let mut parser = Parser::new("mock-edu-device".into(), MsgType::Edu);
  let mut stream = parser.message_stream();
  tokio::spawn(async move {
    debug!("Starting read");
    while let Some(result) = stream.next().await {
      match result {
        Ok((device_id, message)) => {
          trace!(
            "Received message, device_id: {:?}, message: {:?}",
            device_id,
            message
          );
        }
        Err(e) => {
          error!("Error receiving message: {:?}", e);
        }
      }
    }
    debug!("Finished read");
  });
  #[allow(unused_variables)]
  let data = vec![
    0x42, 0x52, 0x4e, 0x43, 0x02, 0x0c, 0x02, 0x00, 0x01, 0x03, 0x00, 0x10, 0x01, 0x9b, 0xed, 0x42,
    0x52, 0x4e, 0x43, 0x02, 0x0c, 0x02, 0x00, 0x03, 0x01, 0x00, 0x12, 0x30, 0x08, 0x07, 0x22, 0x05,
    0x30, 0x2e, 0x30, 0x2e, 0x31, 0x2a, 0x22, 0x05, 0x30, 0x2e, 0x32, 0x2e, 0x34, 0x32, 0x13, 0x20,
    0x32, 0x30, 0x34, 0x2d, 0x31, 0x31, 0x2d, 0x32, 0x36, 0x20, 0x31, 0x38, 0x3a, 0x32, 0x36, 0x3a,
    0x35, 0x36, 0x3a, 0x07, 0x62, 0x64, 0x39, 0x31, 0x39, 0x65, 0x34, 0x40, 0x46, 0x71, 0xe1,
  ];
  let data = vec![
    0x42, 0x52, 0x4e, 0x43, 0x02, 0x0c, 0x24, 0x00, 0x03, 0x01, 0x00, 0x5a, 0x10, 0x1a, 0x04, 0x08,
    0x03, 0x10, 0x02, 0x25, 0x00, 0x00, 0x00, 0x39, 0x2d, 0x00, 0x00, 0x7a, 0x3d, 0x6a, 0x09, 0x12,
    0x02, 0x08, 0x02, 0x1d, 0x00, 0x00, 0xc8, 0x3a, 0xaa, 0x01, 0x04, 0x1a, 0x02, 0x08, 0x03, 0x75,
    0xb6,
  ];
  parser.receive_data(&data);

  // let data2 = [
  //   66, 82, 78, 67, 2, 12, 248, 1, 3, 1, 0, 162, 1, 244, 3, 8, 211, 209, 1, 34, 60, 229, 89, 63,
  //   223, 219, 211, 236, 220, 242, 249, 222, 38, 245, 18, 216, 229, 101, 207, 223, 207, 55, 236,
  //   196, 13, 249, 208, 252, 245, 28, 152, 229, 114, 67, 223, 198, 223, 236, 172, 116, 249, 194,
  //   169, 245, 31, 76, 229, 117, 151, 223, 188, 128, 236, 157, 131, 249, 192, 194, 245, 54, 140, 34,
  //   60, 23, 198, 99, 157, 249, 228, 164, 188, 215, 27, 9, 150, 96, 176, 147, 24, 68, 187, 158, 66,
  //   190, 164, 129, 41, 26, 153, 213, 96, 186, 209, 24, 208, 87, 158, 156, 38, 164, 40, 141, 26, 10,
  //   196, 96, 195, 120, 25, 73, 150, 158, 233, 61, 163, 226, 151, 25, 136, 253, 96, 211, 57, 34, 60,
  //   238, 252, 54, 235, 0, 245, 233, 87, 130, 235, 185, 54, 239, 63, 175, 239, 0, 240, 235, 5, 4,
  //   233, 87, 115, 235, 180, 104, 239, 60, 170, 239, 3, 33, 235, 10, 226, 233, 85, 215, 235, 172,
  //   237, 239, 55, 38, 239, 2,
  // ];
  // let data3 = [
  //   189, 235, 13, 2, 233, 85, 202, 235, 172, 33, 239, 57, 156, 34, 60, 27, 184, 108, 207, 239, 238,
  //   223, 213, 58, 46, 157, 231, 83, 230, 105, 28, 6, 104, 208, 14, 60, 223, 153, 59, 46, 79, 67,
  //   83, 247, 212, 28, 103, 19, 208, 79, 105, 223, 87, 90, 45, 238, 210, 83, 253, 66, 28, 172, 28,
  //   208, 106, 134, 223, 28, 138, 45, 161, 142, 84, 27, 75, 34, 60, 246, 43, 96, 11, 244, 64, 4,
  //   174, 185, 236, 52, 22, 227, 63, 107, 246, 17, 74, 11, 234, 203, 4, 193, 121, 236, 74, 162, 227,
  //   56, 103, 245, 244, 118, 11, 218, 64, 4, 211, 93, 236, 93, 111, 227, 41, 59, 245, 213, 38, 11,
  //   208,
  // ];
  // parser.receive_data(&data2);
  // parser.receive_data(&data3);
  sleep(Duration::from_secs(1)).await;
}
