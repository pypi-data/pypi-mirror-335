use pyo3::prelude::*;
use pyo3::types::PyBytes;
use std::env;
use std::sync::mpsc::SendError;

// Include the generated bindings
#[allow(non_upper_case_globals)]
#[allow(non_camel_case_types)]
#[allow(non_snake_case)]
mod bindings {
    include!(concat!(env!("OUT_DIR"), "/bindings.rs"));
}

mod speex_internal;

#[pyclass]
struct SpeexPreprocessor {
    worker_thread: Option<std::thread::JoinHandle<()>>,
    tx: std::sync::mpsc::Sender<speex_internal::WorkerPayload>,
    #[pyo3(get, set)]
    pub frame_size: usize,
    #[pyo3(get, set)]
    pub sampling_rate: usize,
}

fn send_to_py_error(e: SendError<speex_internal::WorkerPayload>) -> PyErr {
    PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string())
}

#[pymethods]
impl SpeexPreprocessor {
    #[new]
    fn new(frame_size: usize, sampling_rate: usize) -> PyResult<Self> {
        let (tx, rx) = std::sync::mpsc::channel::<speex_internal::WorkerPayload>();

        let worker_thread = std::thread::spawn(move || {
            let mut internal = speex_internal::SpeexInternal::new(frame_size, sampling_rate)
                .expect("Failed to create SpeexInternal");

            while let Ok(payload) = rx.recv() {
                match payload {
                    speex_internal::WorkerPayload::ProcessRaw {
                        input,
                        echo,
                        py_callback,
                    } => {
                        let result = internal.process_raw(&input, &echo);

                        Python::with_gil(|py| match result {
                            Ok(ok_tuple) => {
                                // Convert Vec<i16> to Vec<u8> for Python
                                let (samples, vad) = ok_tuple;
                                let bytes: Vec<u8> = samples
                                    .iter()
                                    .flat_map(|&sample| sample.to_le_bytes())
                                    .collect();
                                let ok_tuple = (bytes, vad);
                                if let Err(e) = py_callback.call1(py, ok_tuple) {
                                    println!("Error calling callback: {:?}", e);
                                }
                            }
                            Err(e) => {
                                println!("Error processing raw data: {:?}", e);
                                if let Err(e) = py_callback.call1(py, (e,)) {
                                    println!("Error calling error callback: {:?}", e);
                                }
                            }
                        });
                    }
                    speex_internal::WorkerPayload::SetDenoise { supression_db } => {
                        if let Err(e) = internal.set_denoise(supression_db) {
                            println!("Error setting denoise: {:?}", e);
                        }
                    }
                    speex_internal::WorkerPayload::SetEcho { filter_length } => {
                        if let Err(e) = internal.set_echo(filter_length) {
                            println!("Error setting echo: {:?}", e);
                        }
                    }
                    speex_internal::WorkerPayload::SetAgc {
                        enabled,
                        level,
                        increment,
                        decrement,
                        max_gain,
                    } => {
                        if let Err(e) =
                            internal.set_agc(enabled, level, increment, decrement, max_gain)
                        {
                            println!("Error setting agc: {:?}", e);
                        }
                    }
                    speex_internal::WorkerPayload::Stop => {
                        break;
                    }
                }
            }
        });

        Ok(SpeexPreprocessor {
            worker_thread: Some(worker_thread),
            tx,
            frame_size,
            sampling_rate,
        })
    }

    /// Process the input audio data asynchronously
    #[pyo3(signature = (input, echo, callback))]
    fn process_async<'py>(
        &self,
        py: Python<'py>,
        input: &Bound<'py, PyBytes>,
        echo: &Bound<'py, PyBytes>,
        callback: &Bound<'py, PyAny>,
    ) -> PyResult<()> {
        if !callback.is_callable() {
            println!("Callback is not callable");
            return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                "Callback must be callable",
            ));
        }

        // Clone the input data
        // Convert u8 bytes to i16 samples (2 bytes per sample)
        let input_u8 = input.extract::<&[u8]>()?;
        let echo_u8 = echo.extract::<&[u8]>()?;

        // Validate that input and echo byte lengths are multiples of 2
        if input_u8.len() != self.frame_size * 2 {
            return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Input length must be {} bytes ({} samples a 2 bytes) ({} bytes given)",
                self.frame_size * 2,
                self.frame_size,
                input_u8.len()
            )));
        }

        if echo_u8.len() != self.frame_size * 2 {
            return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Echo length must be {} bytes ({} samples a 2 bytes) ({} bytes given)",
                self.frame_size * 2,
                self.frame_size,
                echo_u8.len()
            )));
        }

        // Create i16 vectors with half the length (2 bytes per i16)
        let input_bytes = input_u8
            .chunks_exact(2)
            .map(|chunk| i16::from_le_bytes([chunk[0], chunk[1]]))
            .collect();
        let echo_bytes = echo_u8
            .chunks_exact(2)
            .map(|chunk| i16::from_le_bytes([chunk[0], chunk[1]]))
            .collect();

        let payload = speex_internal::WorkerPayload::ProcessRaw {
            input: input_bytes,
            echo: echo_bytes,
            py_callback: callback.extract::<PyObject>()?,
        };

        self.tx.send(payload).map_err(send_to_py_error)?;

        Ok(())
    }

    #[pyo3(signature = (supression_db))]
    fn set_denoise(&mut self, supression_db: Option<u8>) -> PyResult<()> {
        let payload = speex_internal::WorkerPayload::SetDenoise { supression_db };
        self.tx.send(payload).map_err(send_to_py_error)
    }

    #[pyo3(signature = (filter_length))]
    fn set_echo(&mut self, filter_length: i32) -> PyResult<()> {
        let payload = speex_internal::WorkerPayload::SetEcho { filter_length };
        self.tx.send(payload).map_err(send_to_py_error)
    }
    #[pyo3(signature = (enabled, level = None, increment = None, decrement = None, max_gain = None))]
    fn set_agc(
        &mut self,
        enabled: bool,
        level: Option<u16>,
        increment: Option<i32>,
        decrement: Option<i32>,
        max_gain: Option<i32>,
    ) -> PyResult<()> {
        let payload = speex_internal::WorkerPayload::SetAgc {
            enabled,
            level,
            increment,
            decrement,
            max_gain,
        };
        self.tx.send(payload).map_err(send_to_py_error)
    }

    fn cleanup(&mut self) -> PyResult<()> {
        if let Some(worker_thread) = self.worker_thread.take() {
            let payload = speex_internal::WorkerPayload::Stop;
            self.tx.send(payload).map_err(send_to_py_error)?;
            worker_thread.join().map_err(|e| {
                PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Failed to join worker thread")
            })?;
        }
        Ok(())
    }
}

impl Drop for SpeexPreprocessor {
    fn drop(&mut self) {
        if self.worker_thread.is_some() {
            println!("dropping active SpeexPreprocessor, consider calling cleanup() manually");
        }
        if let Err(e) = self.cleanup() {
            println!("Error cleaning up SpeexPreprocessor: {:?}", e);
        }
    }
}

/// Returns the version of the speex-py wrapper
#[pyfunction]
fn version() -> PyResult<String> {
    Ok(format!(
        "{} (built on {})",
        env!("CARGO_PKG_VERSION", "unknown version"),
        env!("CARGO_BUILD_TIME", "unknown build time")
    ))
}

/// A Python module implemented in Rust.
#[pymodule]
fn speex_py(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<SpeexPreprocessor>()?;
    m.add_function(wrap_pyfunction!(version, m)?)?;
    Ok(())
}
