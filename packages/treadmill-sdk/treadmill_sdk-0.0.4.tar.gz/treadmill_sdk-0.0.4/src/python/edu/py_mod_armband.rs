use pyo3::prelude::*;

crate::cfg_import_logging!();

pub fn register_child_module_armband(_m: &Bound<'_, PyModule>) -> PyResult<()> {
  // enums
  // m.add_class::<EegSampleRate>()?;

  // functions
  // m.add_function(wrap_pyfunction!(set_eeg_buffer_cfg, m)?)?;

  Ok(())
}
