pub mod callback;
pub mod py_mod;
pub mod py_msg_parser;
// pub mod py_serial;
// pub mod py_tcp_client;

// cfg_if::cfg_if! {
//   if #[cfg(feature = "edu")] {
//     pub mod stark;
//   }
// }

#[cfg(feature = "edu")]
pub mod edu;

// #[cfg(feature = "ble")]
// pub mod ble;
