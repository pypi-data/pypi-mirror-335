use cfg_if::cfg_if;

cfg_if! {
  if #[cfg(feature = "edu")] {
    pub mod edu_proto;
    pub mod edu_proto_serde;
  }
}

pub mod treadmill_proto;
pub mod treadmill_proto_serde;

// #[cfg(feature = "examples")]
// #[allow(non_upper_case_globals, non_snake_case, non_camel_case_types)]
// pub mod crc_bindings;
