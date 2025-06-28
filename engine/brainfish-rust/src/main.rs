use brainfish_rust::Engine;
use log::{error, info};
use std::io::{self, BufRead, Write};

fn main() -> anyhow::Result<()> {
    // Initialize logging
    env_logger::init();
    info!("Starting BrainFish Rust interface");

    // Create and initialize engine
    let mut engine = Engine::new();
    if let Err(e) = engine.initialize() {
        error!("Failed to initialize engine: {}", e);
        return Err(e.into());
    }
    info!("Engine initialized successfully");

    // Create input reader
    let stdin = io::stdin();
    let mut reader = stdin.lock();
    let mut line = String::new();

    // Main UCI protocol loop
    loop {
        // Clear the line buffer
        line.clear();

        // Read input
        if reader.read_line(&mut line)? == 0 {
            break; // EOF
        }

        // Process command
        match engine.process_command(&line) {
            Ok(response) => {
                println!("{}", response);
                io::stdout().flush()?;

                // Check for quit command
                if line.trim() == "quit" {
                    info!("Received quit command, shutting down");
                    break;
                }
            }
            Err(e) => {
                error!("Error processing command: {}", e);
                println!("error processing command: {}", e);
                io::stdout().flush()?;
            }
        }
    }

    info!("BrainFish Rust interface shutting down");
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_engine_basic_commands() {
        let mut engine = Engine::new();
        engine.initialize().unwrap();

        // Test UCI command
        let response = engine.process_command("uci").unwrap();
        assert!(response.contains("BrainFish"));
        assert!(response.contains("uciok"));

        // Test isready command
        let response = engine.process_command("isready").unwrap();
        assert_eq!(response, "readyok");
    }
}
