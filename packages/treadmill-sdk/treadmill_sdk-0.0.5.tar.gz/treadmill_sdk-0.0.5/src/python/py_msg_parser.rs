use crate::proto::enums::handle_resp_message;
use crate::proto::{enums::MsgType, msg_parser::*};
use futures::StreamExt;
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::types::*;
use pyo3_async_runtimes::tokio::future_into_py;
use std::pin::Pin;
use std::sync::Arc;
use tokio::sync::Mutex;

crate::cfg_import_logging!();

#[pyclass]
#[derive(Clone)]
pub struct MessageParser {
  pub inner: Parser,
  pub stream: MessageStream,
}

#[pymethods]
impl MessageParser {
  #[new]
  pub fn py_new(device_id: String, msg_type: MsgType) -> Self {
    let parser = Parser::new(device_id, msg_type);
    let stream = parser.message_stream();
    MessageParser {
      inner: parser,
      stream: MessageStream {
        inner: Arc::new(Mutex::new(stream)),
      },
    }
  }

  pub fn receive_data(&mut self, data: &[u8]) {
    // trace!("Received data: {:?}", data);
    self.inner.receive_data(data);
  }

  pub fn start_message_stream<'a>(&self, py: Python<'a>) -> PyResult<Bound<'a, PyAny>> {
    let parser_arc = Arc::new(Mutex::new(self.inner.clone()));
    let parser = parser_arc.clone();

    future_into_py(py, async move {
      let parser = parser.lock().await;
      let mut stream = parser.message_stream();
      tokio::spawn(async move {
        // trace!("Starting receive message");
        while let Some(result) = stream.next().await {
          if let Ok((device_id, message)) = result {
            handle_resp_message(device_id.clone(), &message);
          }
        }
      });
      Ok(())
    })
  }
}

#[pyclass]
#[derive(Clone)]
pub struct MessageStream {
  inner: ArcMutexStream,
}

#[pymethods]
impl MessageStream {
  fn __aiter__(slf: PyRef<Self>) -> PyRef<Self> {
    slf
  }

  fn __anext__(slf: PyRefMut<Self>) -> PyResult<PyObject> {
    let stream = Arc::clone(&slf.inner);
    let future = async move {
      let mut stream = stream.lock().await;
      let mut pin_stream = Pin::new(&mut *stream);
      match pin_stream.next().await {
        Some(Ok((_device_id, message))) => {
          let json = serde_json::to_vec(&message).unwrap();
          Python::with_gil(|py| Ok::<Py<PyAny>, PyErr>(PyBytes::new(py, &json).into()))
        }
        // Err(RecvError::Lagged(n)) => println!("Channel lagged by {}", n),
        Some(Err(e)) => Python::with_gil(|py| {
          let py_err = PyErr::new::<PyRuntimeError, _>(format!("{:?}", e));
          #[allow(deprecated)]
          Ok::<Py<PyAny>, PyErr>(py_err.to_object(py))
        }),
        None => Python::with_gil(|py| {
          let py_err = PyErr::new::<PyRuntimeError, _>("Stream ended unexpectedly");
          #[allow(deprecated)]
          Ok::<Py<PyAny>, PyErr>(py_err.to_object(py))
        }),
      }
    };
    future_into_py(slf.py(), future).map(|bound| bound.into())
  }
}

// fn json_to_pydict<'a>(py: Python<'a>, value: &'a Value) -> PyResult<Bound<'a, PyDict>> {
//   let dict = PyDict::new_bound(py);
//   if let Value::Object(map) = value {
//     for (key, val) in map {
//       let py_key = PyString::new_bound(py, key);
//       let py_val = json_to_py(py, val)?;
//       dict.set_item(py_key, py_val)?;
//     }
//   }
//   Ok(dict)
// }

// fn json_to_py(py: Python, value: &Value) -> PyResult<PyObject> {
//   match value {
//     Value::Null => Ok(py.None()),
//     Value::Bool(b) => Ok(b.into_py(py)),
//     Value::Number(num) => {
//       if let Some(i) = num.as_i64() {
//         Ok(i.into_py(py))
//       } else if let Some(u) = num.as_u64() {
//         Ok(u.into_py(py))
//       } else if let Some(f) = num.as_f64() {
//         Ok(f.into_py(py))
//       } else {
//         Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
//           "Invalid number",
//         ))
//       }
//     }
//     Value::String(s) => Ok(PyString::new_bound(py, s).into_py(py)),
//     Value::Array(arr) => {
//       let py_list = PyList::new_bound(py, &[]); // todo: cannot infer type
//       for val in arr {
//         py_list.append(json_to_py(py, val)?)?;
//       }
//       Ok(py_list.into_py(py))
//     }
//     Value::Object(_) => Ok(json_to_pydict(py, value)?.into_py(py)),
//   }
// }
