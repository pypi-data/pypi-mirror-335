pub mod generated;
pub mod proto;
pub mod utils;

#[cfg(any(feature = "edu"))]
pub mod data_handler;

pub mod callback;

#[cfg(feature = "edu")]
pub mod edu;

// #[cfg(feature = "eeg-cap")]
// pub mod eeg_cap;

// #[cfg(feature = "stark")]
// pub mod stark;

// #[cfg(feature = "morpheus")]
// pub mod morpheus;

// #[cfg(target_family = "wasm")]
// pub mod wasm;

// #[cfg(target_env = "ohos")]
// pub mod ohos;

#[cfg(feature = "python")]
pub mod python;

// #[cfg(feature = "serial")]
// pub mod serial;

// #[cfg(feature = "ble")]
// pub mod ble;

// #[cfg(feature = "modbus")]
// pub mod modbus;

pub mod encrypt;
