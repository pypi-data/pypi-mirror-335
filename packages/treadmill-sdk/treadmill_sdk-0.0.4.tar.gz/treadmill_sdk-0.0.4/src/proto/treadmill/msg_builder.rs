use crate::encrypt::aes_gcm::default_decrypt;
use crate::proto::enums::*;
use crate::proto::msg_builder::Builder;
use crate::{generated::treadmill_proto::*, impl_enum_conversion};
use serde::{Deserialize, Serialize};

crate::cfg_import_logging!();

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum TreadmillMessage {
  AnalysisResult(Box<GaitAnalysisResult>),
  // Dongle2App(Box<DongleApp>),
}
impl_enum_conversion!(TreadmillModuleId, APP = 1, PITPAT = 2, ALGO = 3);

impl TreadmillMessage {
  pub fn parse_message(payload: &[u8]) -> Result<TreadmillMessage, ParseError> {
    // trace!("parse_message, payload: {:02x?}", payload);
    let decrypted = default_decrypt(&payload).map_err(|e| ParseError::DecryptError(e.into()))?;
    // trace!("parse_message, decrypted: {:02x?}", decrypted);
    let resp = decode::<SensorApp>(&decrypted)?;
    if let Some(result) = resp.ga_result {
      cfg_if::cfg_if! {
        if #[cfg(feature = "python")] {
          use crate::python::callback::on_recv_gait_result;
          on_recv_gait_result(result.clone());
        } else {
          use crate::encrypt::callback_c::on_recv_gait_result;
          on_recv_gait_result(result.clone());
        }
      }
      Ok(TreadmillMessage::AnalysisResult(Box::new(result)))
    } else {
      Err(ParseError::ContentError(anyhow::anyhow!(
        "No GaitAnalysisResult in SensorApp"
      )))
    }
  }
}

impl Builder {
  pub fn build_to_app(&self, payload: &[u8]) -> Vec<u8> {
    self.build_msg(
      payload,
      TreadmillModuleId::PITPAT.into(),
      TreadmillModuleId::APP.into(),
    )
  }
}

pub mod tml_msg_builder {
  // use crate::generated::treadmill_proto::*;
  use crate::{
    generated::treadmill_proto::GaitAnalysisResult,
    proto::{enums::MsgType, msg_builder::Builder},
  };
  use lazy_static::lazy_static;
  use prost::Message;
  use std::sync::atomic::{AtomicU32, Ordering};
  crate::cfg_import_logging!();

  lazy_static! {
    static ref BUILDER: Builder = Builder::new(MsgType::Treadmill);
    static ref MSG_ID: AtomicU32 = AtomicU32::new(1);
  }

  pub fn gen_msg_id() -> u32 {
    MSG_ID.fetch_add(1, Ordering::SeqCst)
  }

  pub fn build_to_app(payload: &[u8]) -> Vec<u8> {
    BUILDER.build_to_app(payload)
  }

  pub fn encode_to_app(msg: GaitAnalysisResult) -> (u32, Vec<u8>) {
    info!(
      "encode_app_to_dongle, msg: {:?}",
      serde_json::to_string(&msg).unwrap_or_else(|_| "".to_string())
    );
    // msg.msg_id = gen_msg_id();
    (msg.msg_id, BUILDER.build_to_app(&msg.encode_to_vec()))
  }
}
