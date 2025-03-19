use std::sync::Mutex;

use crate::generated::treadmill_proto::{gait_analysis_result::*, *};
use crate::proto::enums::MsgType;
use crate::proto::msg_parser::Parser;
use crate::utils::logging::LogLevel;
use crate::utils::logging_desktop as logging;

crate::cfg_import_logging!();

/// 初始化日志记录功能
///
/// # 参数
/// - `level`: 日志级别
#[no_mangle]
pub extern "C" fn initialize_logging(level: LogLevel) {
  logging::initialize_logging(level);
}

pub type GaitDataCallback =
  extern "C" fn(timmstamp: u32, left_foot: bool, pattern: u32, gait_duration: u32);

pub type AbnormalEventCallback = extern "C" fn(timmstamp: u32, event_type: u32);

lazy_static::lazy_static! {
  pub(crate) static ref GAIT_DATA_CALLBACK: Mutex<Option<GaitDataCallback>> = Mutex::new(None);
  pub(crate) static ref ABNORMAL_EVENT_CALLBACK: Mutex<Option<AbnormalEventCallback>> = Mutex::new(None);
  pub(crate) static ref MSG_PARSER: Mutex<Parser> = Mutex::new(Parser::new("treadmill-device".into(), MsgType::Treadmill));
}

/// Sets the callback for GaitAnalysisResult data.
///
/// # Arguments
/// * `callback` - The function to call when receiving GaitAnalysisResult data.
#[no_mangle]
pub extern "C" fn set_gait_data_callback(cb: GaitDataCallback) {
  // pub extern "C" fn set_gait_data_callback(cb: extern "C" fn(timmstamp: u32, left_foot: bool, pattern: u32, gait_duration: u32)) {
  let mut cb_guard = GAIT_DATA_CALLBACK.lock().unwrap();
  *cb_guard = Some(cb);
}

/// Sets the callback for AbnormalEvent data.
///
/// # Arguments
/// * `callback` - The function to call when receiving AbnormalEvent data.
#[no_mangle]
pub extern "C" fn set_abnormal_event_callback(cb: AbnormalEventCallback) {
  // pub extern "C" fn set_abnormal_event_callback(cb: extern "C" fn(timmstamp: u32, event_type: u32)) {
  let mut cb_guard = ABNORMAL_EVENT_CALLBACK.lock().unwrap();
  *cb_guard = Some(cb);
}

fn run_gait_data_callback(timestamp: u32, left_foot: bool, pattern: u32, gait_duration: u32) {
  let cb = GAIT_DATA_CALLBACK.lock().unwrap();
  if let Some(cb) = &*cb {
    cb(timestamp, left_foot, pattern, gait_duration);
  }
}

fn run_abnormal_event_callback(timestamp: u32, event_type: u32) {
  let cb = ABNORMAL_EVENT_CALLBACK.lock().unwrap();
  if let Some(cb) = &*cb {
    cb(timestamp, event_type.into());
  }
}

/// Receives a pointer to data and its length from C.
/// The data is borrowed and not freed by this function.
/// The caller is responsible for managing the memory.
#[no_mangle]
pub extern "C" fn did_receive_data(data: *const u8, len: usize) {
  if data.is_null() || len == 0 {
    // 处理空指针或无效长度的情况
    return;
  }
  let data = unsafe { std::slice::from_raw_parts(data, len) };
  handle_receive_data(data);
}

pub fn handle_receive_data(data: &[u8]) {
  let mut parser = MSG_PARSER.lock().unwrap();
  parser.receive_data(data);
}

pub fn on_recv_gait_result(result: GaitAnalysisResult) {
  if result.abnormal_gait > 0 {
    run_abnormal_event_callback(
      result.timestamp,
      result.abnormal_gait as u32,
      // AbnormalGait::try_from(result.abnormal_gait).unwrap(),
    );
  }
  if result.foot > 0 && result.gait_duration > 0 {
    run_gait_data_callback(
      result.timestamp,
      result.foot == FootStrike::LeftFoot as i32,
      result.pattern as u32,
      // GaitPattern::try_from(result.pattern).unwrap(),
      result.gait_duration as u32,
    );
  }
}
