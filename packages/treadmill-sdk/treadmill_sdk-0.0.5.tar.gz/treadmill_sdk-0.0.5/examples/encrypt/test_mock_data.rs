use std::fs::File;
use std::io::BufRead;
use std::io::BufReader;
use std::thread::sleep;
use std::time::Duration;
use treadmill_sdk::encrypt::callback_c::*;
// use treadmill_sdk::generated::treadmill_proto::gait_analysis_result::GaitPattern;
// use treadmill_sdk::generated::treadmill_proto::AbnormalGait;
use treadmill_sdk::utils::logging::LogLevel;

treadmill_sdk::cfg_import_logging!();

/// cargo run --example test_mock_data
#[tokio::main]
async fn main() -> anyhow::Result<(), anyhow::Error> {
  initialize_logging(LogLevel::Info);

  set_gait_data_callback(on_gait_analysis_result);
  set_abnormal_event_callback(on_abnormal_event);
  let hex_str_fw = "42 52 4E 43 02 13 1E 00 03 01 A5 5A ED A9 F1 8A E0 15 7C 0A FF E5 F3 3D 7F 59 28 BE 6C 53 7D EE 0C 40 94 B7 E6 72 26 56 D5 C4 9E
42 52 4E 43 02 13 1F 00 03 01 A5 5A EC A9 E5 8A C0 B9 65 13 D6 25 1C 6A 2E 88 D7 B0 4F 5D 52 E9 E6 0D 4B 47 07 1B 0F DF 2A DC AC 73";
  // parse hex_str_fw to hex_str like "42524E4302131F000301A55AEC..."
  let hex_str_fw = hex_str_fw.replace(" ", "").replace("\n", "");
  handle_receive_data(&hex::decode(hex_str_fw)?);
  // return Ok(());

  let file_path = format!("examples/encrypt/tml_mock_data.dat");
  let f = File::open(file_path).unwrap();

  let result: Result<(), anyhow::Error> = async {
    let mut reader = BufReader::new(f);
    let mut buffer = String::new();
    let mut line_index = 1;
    while reader.read_line(&mut buffer).unwrap() > 0 {
      let hex_str = buffer.trim();
      // let hex_str = "42524E43020c19000301005AE6B103EF6C0D340A5B56AFC330B30D224FA497845294FE7887F9";
      if hex_str.len() % 2 != 0 {
        error!(
          "Error: Odd number of digits in line {}, buf: {:}",
          line_index, hex_str
        );
        buffer.clear();
        break;
      }
      let data: Vec<u8> = hex::decode(hex_str)?;
      handle_receive_data(&data);
      trace!(
        "line: {}, data: {:02x?}, len: {}",
        line_index,
        data,
        data.len()
      );
      line_index += 1;
      buffer.clear();
      // break;
    }
    Ok(())
  }
  .await;

  if let Err(e) = result {
    error!("Error: {}", e);
  }

  sleep(Duration::from_secs(1));

  Ok(())
}

extern "C" fn on_gait_analysis_result(
  timestamp: u32,
  left_foot: bool,
  pattern: u32,
  gait_duration: u32,
) {
  info!(
    "timestamp: {}, left_foot: {}, pattern: {:?}, gait_duration: {}",
    timestamp, left_foot, pattern, gait_duration
  );
}

extern "C" fn on_abnormal_event(timestamp: u32, event_type: u32) {
  info!("timestamp: {}, event_type: {:?}", timestamp, event_type);
}

// use futures::StreamExt;
// use treadmill_sdk::proto::enums::MsgType;
// use treadmill_sdk::proto::msg_parser::Parser;
// fn lis_msg() {
//   let mut parser = Parser::new("treadmill-device".into(), MsgType::Treadmill);
// let mut stream = parser.message_stream();
// tokio::spawn(async move {
//   debug!("Starting read");
//   while let Some(result) = stream.next().await {
//     match result {
//       Ok((device_id, message)) => {
//         trace!(
//           "Received message, device_id: {:?}, message: {:?}",
//           device_id,
//           message
//         );
//       }
//       Err(e) => {
//         error!("Error receiving message: {:?}", e);
//       }
//     }
//   }
//   debug!("Finished read");
// });
// }
