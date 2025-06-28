use std::ffi::{CStr, CString};
use std::os::raw::c_char;
use std::sync::Once;
use log::{error, info, warn};
use thiserror::Error;

static INIT: Once = Once::new();

#[derive(Error, Debug)]
pub enum EngineError {
    #[error("Failed to initialize engine")]
    InitializationError,
    #[error("Invalid FEN string")]
    InvalidFen,
    #[error("Engine not initialized")]
    NotInitialized,
    #[error("FFI error: {0}")]
    FfiError(String),
}

pub struct Engine {
    initialized: bool,
}

impl Engine {
    pub fn new() -> Self {
        INIT.call_once(|| {
            env_logger::init();
        });
        
        Self {
            initialized: false,
        }
    }

    pub fn initialize(&mut self) -> Result<(), EngineError> {
        if self.initialized {
            warn!("Engine already initialized");
            return Ok(());
        }

        info!("Initializing BrainFish engine");
        // TODO: Add actual initialization logic
        self.initialized = true;
        Ok(())
    }

    pub fn process_command(&self, command: &str) -> Result<String, EngineError> {
        if !self.initialized {
            return Err(EngineError::NotInitialized);
        }

        // TODO: Implement actual command processing
        match command.trim() {
            "uci" => Ok(String::from("id name BrainFish\nid author BlackBoxAI\nuciok")),
            "isready" => Ok(String::from("readyok")),
            _ => Ok(String::from("unknown command")),
        }
    }

    pub fn analyze_position(&self, fen: &str, depth: i32) -> Result<String, EngineError> {
        if !self.initialized {
            return Err(EngineError::NotInitialized);
        }

        if !self.validate_fen(fen) {
            return Err(EngineError::InvalidFen);
        }

        // TODO: Implement actual position analysis
        Ok(format!("info depth {} score cp 100 pv e2e4 e7e5", depth))
    }

    fn validate_fen(&self, fen: &str) -> bool {
        // TODO: Implement proper FEN validation
        !fen.is_empty() && fen.contains('/')
    }
}

// FFI interface

#[no_mangle]
pub extern "C" fn engine_new() -> *mut Engine {
    match std::panic::catch_unwind(|| {
        Box::into_raw(Box::new(Engine::new()))
    }) {
        Ok(engine) => engine,
        Err(_) => std::ptr::null_mut(),
    }
}

#[no_mangle]
pub extern "C" fn engine_free(ptr: *mut Engine) {
    if !ptr.is_null() {
        unsafe {
            drop(Box::from_raw(ptr));
        }
    }
}

#[no_mangle]
pub extern "C" fn engine_initialize(ptr: *mut Engine) -> bool {
    let engine = unsafe {
        if ptr.is_null() {
            error!("Null pointer passed to engine_initialize");
            return false;
        }
        &mut *ptr
    };

    match engine.initialize() {
        Ok(_) => true,
        Err(e) => {
            error!("Failed to initialize engine: {}", e);
            false
        }
    }
}

#[no_mangle]
pub extern "C" fn engine_process_command(
    ptr: *const Engine,
    command: *const c_char,
) -> *mut c_char {
    let result = std::panic::catch_unwind(|| {
        let engine = unsafe {
            if ptr.is_null() {
                return CString::new("null engine pointer").unwrap().into_raw();
            }
            &*ptr
        };

        let c_str = unsafe {
            if command.is_null() {
                return CString::new("null command pointer").unwrap().into_raw();
            }
            CStr::from_ptr(command)
        };

        let command_str = match c_str.to_str() {
            Ok(s) => s,
            Err(_) => return CString::new("invalid UTF-8").unwrap().into_raw(),
        };

        match engine.process_command(command_str) {
            Ok(response) => CString::new(response).unwrap().into_raw(),
            Err(e) => CString::new(format!("error: {}", e)).unwrap().into_raw(),
        }
    });

    match result {
        Ok(ptr) => ptr,
        Err(_) => CString::new("panic occurred").unwrap().into_raw(),
    }
}

#[no_mangle]
pub extern "C" fn engine_free_string(ptr: *mut c_char) {
    if !ptr.is_null() {
        unsafe {
            drop(CString::from_raw(ptr));
        }
    }
}

// Tests
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_engine_initialization() {
        let mut engine = Engine::new();
        assert!(!engine.initialized);
        assert!(engine.initialize().is_ok());
        assert!(engine.initialized);
    }

    #[test]
    fn test_process_command() {
        let mut engine = Engine::new();
        engine.initialize().unwrap();
        
        let response = engine.process_command("uci").unwrap();
        assert!(response.contains("BrainFish"));
        
        let response = engine.process_command("isready").unwrap();
        assert_eq!(response, "readyok");
    }
}
