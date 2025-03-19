#[macro_export]
macro_rules! impl_enum_conversion {
  ($name:ident, $($variant:ident = $value:expr),+) => {
    // #[cfg_attr(target_family = "wasm", wasm_bindgen::prelude::wasm_bindgen)]
    #[cfg_attr(feature = "python", pyo3::pyclass(eq, eq_int))]
    #[derive(Debug, Clone, Copy, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
    #[repr(u8)]
    pub enum $name {
      $($variant = $value),+
    }

    impl From<u8> for $name {
      fn from(value: u8) -> Self {
        match value {
          $($value => $name::$variant,)+
          _ => panic!("Invalid value for enum {}", stringify!($name))
        }
      }
    }

    impl Into<u8> for $name {
      fn into(self) -> u8 {
        self as u8
      }
    }
  };
}

#[macro_export]
macro_rules! impl_enum_u16_conversion {
  ($name:ident, $($variant:ident = $value:expr),+) => {
    // #[cfg_attr(target_family = "wasm", wasm_bindgen::prelude::wasm_bindgen)]
    #[cfg_attr(feature = "python", pyo3::pyclass(eq, eq_int))]
    #[derive(Debug, Clone, Copy, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
    #[repr(u16)]
    pub enum $name {
      $($variant = $value),+
    }

    impl $name {
      pub fn from_u16(value: u16) -> Option<Self> {
        match value {
          $($value => Some($name::$variant),)+
          _ => None,
        }
      }

      // 将枚举实例转换为 u16
      pub fn to_u16(self) -> u16 {
        self as u16
      }
    }

    impl Into<$name> for u16 {
      fn into(self) -> $name {
        $name::from_u16(self).unwrap_or_else(|| $name::from_u16(0).unwrap())
      }
    }
  };
}

#[macro_export]
macro_rules! impl_enum_u32_conversion {
  ($name:ident, $($variant:ident = $value:expr),+) => {
    // #[cfg_attr(target_family = "wasm", wasm_bindgen::prelude::wasm_bindgen)]
    #[cfg_attr(feature = "python", pyo3::pyclass(eq, eq_int))]
    #[derive(Debug, Clone, Copy, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
    #[repr(u32)]
    pub enum $name {
      $($variant = $value),+
    }

    impl $name {
      pub fn from_u32(value: u32) -> Option<Self> {
        match value {
          $($value => Some($name::$variant),)+
          _ => None,
        }
      }

      // 将枚举实例转换为 u32
      pub fn to_u32(self) -> u32 {
        self as u32
      }
    }

    impl Into<$name> for u32 {
      fn into(self) -> $name {
        $name::from_u32(self).unwrap_or_else(|| $name::from_u32(0).unwrap())
      }
    }

    impl From<u32> for $name {
      fn from(value: u32) -> Self {
        $name::from_u32(self).unwrap_or_else(|| $name::from_u32(0).unwrap())
      }
    }
  };
}

#[macro_export]
macro_rules! cfg_import_logging {
  () => {
    #[cfg(feature = "tracing-log")]
    #[allow(unused_imports)]
    use tracing::*;

    #[cfg(not(feature = "tracing-log"))]
    #[allow(unused_imports)]
    use log::*;
  };
}

cfg_import_logging!();
