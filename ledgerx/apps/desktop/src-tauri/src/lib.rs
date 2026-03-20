#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use serde::Serialize;
use tauri::Manager;
use tauri_plugin_dialog::DialogExt;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_single_instance::init(|app, _argv, _cwd| {
            if let Some(w) = app.get_webview_window("main") {
                let _ = w.set_focus();
            }
        }))
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_updater::Builder::new().build())
        .invoke_handler(tauri::generate_handler![
            open_file_dialog,
            save_file_dialog,
            get_local_ip,
            check_tally_running,
            read_local_file,
            get_system_info,
            launch_ollama,
            check_ollama_status,
        ])
        .run(tauri::generate_context!())
        .expect("error while running LedgerX");
}

fn file_path_to_string(p: &tauri_plugin_dialog::FilePath) -> String {
    p.to_string()
}

#[tauri::command]
async fn open_file_dialog(app_handle: tauri::AppHandle) -> Result<Option<String>, String> {
    let path = tauri::async_runtime::spawn_blocking(move || {
        app_handle
            .dialog()
            .file()
            .add_filter("Tally / Data", &["xml", "csv", "xlsx"])
            .blocking_pick_file()
    })
    .await
    .map_err(|e| e.to_string())?
    .map(|p| file_path_to_string(&p));
    Ok(path)
}

#[tauri::command]
async fn save_file_dialog(
    app_handle: tauri::AppHandle,
    data: String,
    filename: String,
) -> Result<Option<String>, String> {
    let path = tauri::async_runtime::spawn_blocking({
        let app_handle = app_handle.clone();
        move || {
            app_handle
                .dialog()
                .file()
                .set_file_name(&filename)
                .blocking_save_file()
        }
    })
    .await
    .map_err(|e| e.to_string())?;
    match path {
        Some(p) => {
            let path_str = file_path_to_string(&p);
            std::fs::write(&path_str, data).map_err(|e| e.to_string())?;
            Ok(Some(path_str))
        }
        None => Ok(None),
    }
}

#[tauri::command]
fn get_local_ip() -> Result<String, String> {
    let socket = std::net::UdpSocket::bind("0.0.0.0:0").map_err(|e| e.to_string())?;
    socket.connect("8.8.8.8:80").map_err(|e| e.to_string())?;
    let addr = socket.local_addr().map_err(|e| e.to_string())?;
    Ok(addr.ip().to_string())
}

#[tauri::command]
fn check_tally_running() -> Result<bool, String> {
    #[cfg(target_os = "windows")]
    {
        use std::process::Command;
        let out = Command::new("tasklist")
            .output()
            .map_err(|e| e.to_string())?;
        let s = String::from_utf8_lossy(&out.stdout);
        Ok(s.to_lowercase().contains("tally") || s.to_lowercase().contains("tallyprime"))
    }
    #[cfg(not(target_os = "windows"))]
    {
        let _ = ();
        Ok(false)
    }
}

#[tauri::command]
async fn read_local_file(path: String) -> Result<String, String> {
    let content = std::fs::read_to_string(&path).map_err(|e| e.to_string())?;
    Ok(content)
}

#[derive(Serialize)]
struct SystemInfo {
    os: String,
    arch: String,
    total_memory_mb: u64,
    free_disk_mb: Option<u64>,
}

#[tauri::command]
fn get_system_info() -> Result<SystemInfo, String> {
    let total_memory_mb = {
        #[cfg(target_os = "linux")]
        {
            std::fs::read_to_string("/proc/meminfo")
                .ok()
                .and_then(|s| {
                    s.lines()
                        .find(|l| l.starts_with("MemTotal:"))
                        .and_then(|l| l.split_whitespace().nth(1)?.parse::<u64>().ok())
                })
                .map(|kb| kb / 1024)
                .unwrap_or(0)
        }
        #[cfg(not(target_os = "linux"))]
        {
            0_u64
        }
    };
    Ok(SystemInfo {
        os: std::env::consts::OS.to_string(),
        arch: std::env::consts::ARCH.to_string(),
        total_memory_mb,
        free_disk_mb: None,
    })
}

#[tauri::command]
async fn launch_ollama(app_handle: tauri::AppHandle) -> Result<bool, String> {
    #[cfg(target_os = "windows")]
    let _ = std::process::Command::new("ollama").arg("serve").spawn();
    #[cfg(not(target_os = "windows"))]
    let _ = tauri_plugin_shell::Shell::new(&app_handle)
        .sidecar("ollama")
        .map_err(|e| e.to_string())?
        .args(["serve"])
        .spawn()
        .map_err(|e| e.to_string())?;
    Ok(true)
}

#[tauri::command]
async fn check_ollama_status() -> Result<bool, String> {
    match std::net::TcpStream::connect_timeout(
        &std::net::SocketAddr::from(([127, 0, 0, 1], 11434)),
        std::time::Duration::from_secs(2),
    ) {
        Ok(_) => Ok(true),
        Err(_) => Ok(false),
    }
}
