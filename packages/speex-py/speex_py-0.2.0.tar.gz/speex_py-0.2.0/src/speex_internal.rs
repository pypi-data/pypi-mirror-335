use pyo3::{PyErr, PyObject, PyResult};
use std::ffi::{c_int, c_void};
use std::slice;

use crate::bindings::{
    speex_echo_cancellation, speex_echo_state_destroy, speex_echo_state_init, speex_preprocess_ctl,
    speex_preprocess_run, speex_preprocess_state_destroy, speex_preprocess_state_init,
    SpeexEchoState, SpeexPreprocessState, SPEEX_PREPROCESS_SET_AGC,
    SPEEX_PREPROCESS_SET_AGC_DECREMENT, SPEEX_PREPROCESS_SET_AGC_INCREMENT,
    SPEEX_PREPROCESS_SET_AGC_LEVEL, SPEEX_PREPROCESS_SET_AGC_MAX_GAIN,
    SPEEX_PREPROCESS_SET_DENOISE, SPEEX_PREPROCESS_SET_ECHO_STATE,
    SPEEX_PREPROCESS_SET_NOISE_SUPPRESS,
};

pub struct SpeexInternal {
    state: Option<*mut SpeexPreprocessState>,
    echo_state: Option<*mut SpeexEchoState>,
    frame_size: usize,
}

/// A tuple containing the input and echo audio data
pub enum WorkerPayload {
    ProcessRaw {
        input: Vec<i16>,
        echo: Vec<i16>,
        py_callback: PyObject,
    },
    SetDenoise {
        supression_db: Option<u8>,
    },
    SetEcho {
        filter_length: i32,
    },
    SetAgc {
        enabled: bool,
        level: Option<u16>,
        increment: Option<i32>,
        decrement: Option<i32>,
        max_gain: Option<i32>,
    },
    Stop,
}

impl SpeexInternal {
    pub fn new(frame_size: usize, sampling_rate: usize) -> PyResult<Self> {
        let state =
            unsafe { speex_preprocess_state_init(frame_size as c_int, sampling_rate as c_int) };

        if state.is_null() {
            return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                "Failed to initialize Speex preprocessor",
            ));
        }
        Ok(Self {
            state: Some(state),
            echo_state: None,
            frame_size,
        })
    }

    pub fn process_raw(
        &self,
        input_bytes: &[i16],
        echo_bytes: &[i16],
    ) -> PyResult<(Vec<i16>, bool)> {
        match self.state {
            None => {
                return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                    "Speex preprocessor not initialized or already cleaned up",
                ))
            }
            Some(state) => {
                if state.is_null() {
                    return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                        "Speex preprocessor not initialized or already cleaned up",
                    ));
                }
                if input_bytes.len() != self.frame_size {
                    return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                        "Input length must be {} bytes ({} samples a 2 bytes) ({} bytes given)",
                        self.frame_size * 2,
                        self.frame_size,
                        input_bytes.len()
                    )));
                }

                // Create a copy of the input data that we'll modify
                let mut input_copy = input_bytes.to_vec();

                // Apply echo cancellation if echo state is available
                if let Some(echo_state) = self.echo_state {
                    let mut output_buffer = vec![0i16; self.frame_size];

                    unsafe {
                        speex_echo_cancellation(
                            echo_state,
                            input_copy.as_ptr() as *mut i16,
                            echo_bytes.as_ptr() as *mut i16,
                            output_buffer.as_mut_ptr(),
                        );
                    }

                    input_copy = output_buffer.to_vec();
                }

                // Process the audio
                let vad = unsafe { speex_preprocess_run(state, input_copy.as_mut_ptr()) };

                // Return the processed data and VAD result
                Ok((input_copy, vad != 0))
            }
        }
    }

    pub fn set_denoise(&mut self, supression_db: Option<u8>) -> PyResult<()> {
        let state = self.state.ok_or_else(|| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                "Speex preprocessor state is not initialized",
            )
        })?;
        unsafe {
            let mut enabled = if supression_db.is_some() { 1 } else { 0 } as c_int;
            let ret = speex_preprocess_ctl(
                state,
                SPEEX_PREPROCESS_SET_DENOISE as c_int,
                &mut enabled as *mut _ as *mut c_void,
            );

            if ret != 0 {
                return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                    "Failed to set denoise settings",
                ));
            }

            if let Some(supression_db) = supression_db {
                let mut supression = -(supression_db as i32);
                let ret = speex_preprocess_ctl(
                    state,
                    SPEEX_PREPROCESS_SET_NOISE_SUPPRESS as c_int,
                    &mut supression as *mut _ as *mut c_void,
                );

                if ret != 0 {
                    return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                        "Failed to set noise suppression level",
                    ));
                }
            }
        }
        Ok(())
    }

    pub fn set_echo(&mut self, filter_length: i32) -> PyResult<()> {
        let state = self.state.ok_or_else(|| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                "Speex preprocessor state is not initialized",
            )
        })?;
        if let Some(echo_state) = self.echo_state {
            unsafe {
                speex_echo_state_destroy(echo_state);
            }
        }
        unsafe {
            let raw_echo_state =
                speex_echo_state_init(self.frame_size as c_int, filter_length as c_int);
            if raw_echo_state.is_null() {
                return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                    "Failed to initialize Speex echo state",
                ));
            }

            let ret = speex_preprocess_ctl(
                state,
                SPEEX_PREPROCESS_SET_ECHO_STATE as c_int,
                raw_echo_state as *mut _ as *mut c_void,
            );

            if ret != 0 {
                speex_echo_state_destroy(raw_echo_state);
                return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                    "Failed to set echo state",
                ));
            }
            self.echo_state = Some(raw_echo_state);
        }
        Ok(())
    }

    pub fn set_agc(
        &mut self,
        enabled: bool,
        level: Option<u16>,
        increment: Option<i32>,
        decrement: Option<i32>,
        max_gain: Option<i32>,
    ) -> PyResult<()> {
        let state = self.state.ok_or_else(|| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                "Speex preprocessor state is not initialized",
            )
        })?;
        unsafe {
            let mut enabled_val = if enabled { 1 } else { 0 } as c_int;
            let ret = speex_preprocess_ctl(
                state,
                SPEEX_PREPROCESS_SET_AGC as c_int,
                &mut enabled_val as *mut _ as *mut c_void,
            );

            if ret != 0 {
                return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                    "Failed to set AGC settings",
                ));
            }

            // If AGC is enabled and level is provided, set the level
            if enabled && level.is_some() {
                let agc_level = level.expect("Level is required when AGC is enabled");

                // For AGC level, we need to use a float value
                let mut level_float = agc_level as f32;

                let ret = speex_preprocess_ctl(
                    state,
                    SPEEX_PREPROCESS_SET_AGC_LEVEL as c_int,
                    &mut level_float as *mut _ as *mut c_void,
                );

                if ret != 0 {
                    return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                        "Failed to set AGC level",
                    ));
                }
            }

            // Set AGC increment (how fast the gain can increase)
            if let Some(inc) = increment {
                let mut inc_val = inc as c_int;
                let ret = speex_preprocess_ctl(
                    state,
                    SPEEX_PREPROCESS_SET_AGC_INCREMENT as c_int,
                    &mut inc_val as *mut _ as *mut c_void,
                );

                if ret != 0 {
                    return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                        "Failed to set AGC increment",
                    ));
                }
            }

            // Set AGC decrement (how fast the gain can decrease)
            if let Some(dec) = decrement {
                let mut dec_val = dec as c_int;
                let ret = speex_preprocess_ctl(
                    state,
                    SPEEX_PREPROCESS_SET_AGC_DECREMENT as c_int,
                    &mut dec_val as *mut _ as *mut c_void,
                );

                if ret != 0 {
                    return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                        "Failed to set AGC decrement",
                    ));
                }
            }

            // Set AGC maximum gain
            if let Some(gain) = max_gain {
                let mut gain_val = gain as c_int;
                let ret = speex_preprocess_ctl(
                    state,
                    SPEEX_PREPROCESS_SET_AGC_MAX_GAIN as c_int,
                    &mut gain_val as *mut _ as *mut c_void,
                );

                if ret != 0 {
                    return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                        "Failed to set AGC max gain",
                    ));
                }
            }
        }
        Ok(())
    }

    pub fn cleanup(&mut self) -> PyResult<()> {
        if let Some(state) = self.state {
            unsafe {
                speex_preprocess_state_destroy(state);
            }
        }
        if let Some(echo_state) = self.echo_state {
            unsafe {
                speex_echo_state_destroy(echo_state);
            }
        }
        Ok(())
    }
}

impl Drop for SpeexInternal {
    fn drop(&mut self) {
        if let Err(e) = self.cleanup() {
            println!("Error cleaning up SpeexInternal: {:?}", e);
        }
    }
}
