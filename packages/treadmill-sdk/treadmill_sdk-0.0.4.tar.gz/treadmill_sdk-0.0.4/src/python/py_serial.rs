use crate::python::py_msg_parser::MessageParser;
use crate::serial::serialport::*;
use pyo3::prelude::*;
use pyo3::types::PyBytes;
use pyo3_async_runtimes::tokio::future_into_py;
use std::sync::Arc;
use tokio::io::{AsyncWriteExt, WriteHalf};
use tokio::sync::Mutex;
use tokio_serial::{SerialPortInfo, SerialStream};
crate::cfg_import_logging!();

#[pyfunction]
pub fn available_usb_ports(vid: u16, pid: u16) -> PyResult<PyObject> {
  let usb_ports: Vec<SerialPortInfo> = list_available_ports(vid, pid);
  let usb_ports_json: Vec<_> = usb_ports
    .into_iter()
    .map(|port| {
      serde_json::json!({
          "port_name": port.port_name,
      })
    })
    .collect();
  // let json = serde_json::to_vec(&usb_ports).unwrap();
  let json = serde_json::to_vec(&usb_ports_json).unwrap();
  Python::with_gil(|py| Ok::<Py<PyAny>, PyErr>(PyBytes::new(py, &json).into()))
}

#[pyclass]
pub struct PySerialStream {
  pub port_name: String,
  pub baudrate: u32,
  pub writer: Arc<Mutex<Option<WriteHalf<SerialStream>>>>,
}

#[pymethods]
impl PySerialStream {
  #[new]
  pub fn new(port_name: String, baudrate: u32) -> PyResult<Self> {
    Ok(PySerialStream {
      port_name,
      baudrate,
      writer: Arc::new(Mutex::new(None)),
    })
  }

  pub fn start_data_stream<'a>(
    &self,
    py: Python<'a>,
    py_parser: PyRefMut<MessageParser>,
  ) -> PyResult<Bound<'a, PyAny>> {
    let mut parser = py_parser.clone();
    let _ = parser.start_message_stream(py);

    let port_name = self.port_name.clone();
    let baudrate = self.baudrate;
    let writer_handle = self.writer.clone();

    future_into_py(py, async move {
      let callback = move |data: Vec<u8>| {
        parser.receive_data(&data);
      };
      let (reader, writer) = serial_open_2(&port_name, baudrate).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
          "Failed to open serial port: {:?}",
          e
        ))
      })?;
      *writer_handle.lock().await = Some(writer);

      tokio::spawn(listen_serial_stream(reader, Box::new(callback)));
      // info!("listen_serial_stream done");
      Python::with_gil(|_| Ok(()))
    })
  }

  pub fn write_data<'a>(&self, py: Python<'a>, data: Vec<u8>) -> PyResult<Bound<'a, PyAny>> {
    let writer_handle = self.writer.clone();
    future_into_py(py, async move {
      let mut writer = writer_handle.lock().await;
      if let Some(writer) = writer.as_mut() {
        if let Err(e) = writer.write_all(&data).await {
          error!("Failed to write to serial port: {}", e);
        }
      }
      Python::with_gil(|_| Ok(()))
    })
  }
}

// let stream = ModbusContext::serial_open(&port_name, baudrate).map_err(|e| {
//   PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
//     "Failed to open serial port: {:?}",
//     e
//   ))
// })?;

// Ok(PySerialStream {
//   port_name,
//   stream: Arc::new(Mutex::new(stream)),
// })
// pub fn attach_slave<'a>(&self, py: Python<'a>, slave_id: u8) -> PyResult<Bound<'a, PyAny>> {
//   let stream_arc = self.stream.clone();
//   let port_name = self.port_name.clone();

//   future_into_py(py, async move {
//     let stream_guard = stream_arc.lock().await;
//     let stream = *stream_guard; // TODO: SerialStream NOT Clone
//     let ctx = ModbusContext::attach_slave(stream, &port_name, slave_id).map_err(|e| {
//       PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
//         "Failed to attach slave: {:?}",
//         e
//       ))
//     })?;

//     let client = PyModbusClient {
//       ctx: Arc::new(Mutex::new(ctx)),
//     };
//     Python::with_gil(|_| Ok(client))
//   })
// }
// }
