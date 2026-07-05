import Foundation
import SwiftUI

@MainActor
final class LocalBackend: ObservableObject {
    enum Status {
        case checking
        case live(String)
        case staticFallback
        case unavailable(String)

        var title: String {
            switch self {
            case .checking:
                return "Checking"
            case .live:
                return "Embedded API"
            case .staticFallback:
                return "Static Demo"
            case .unavailable:
                return "Offline"
            }
        }

        var detail: String {
            switch self {
            case .checking:
                return "Checking the local SgodAI API."
            case .live(let message):
                return message
            case .staticFallback:
                return "The local API is not running; the bundled static interface is loaded."
            case .unavailable(let message):
                return message
            }
        }

        var symbol: String {
            switch self {
            case .checking:
                return "clock"
            case .live:
                return "checkmark.circle"
            case .staticFallback:
                return "rectangle.on.rectangle"
            case .unavailable:
                return "exclamationmark.triangle"
            }
        }

        var color: Color {
            switch self {
            case .checking:
                return .secondary
            case .live:
                return .green
            case .staticFallback:
                return .orange
            case .unavailable:
                return .red
            }
        }
    }

    @Published var status: Status = .checking
    @Published var isChecking = false
    @Published var reloadToken = 0
    @Published var webURL = URL(string: "http://127.0.0.1:18765/")!

    private let port = 18765
    private let localURL = URL(string: "http://127.0.0.1:18765/")!
    private let healthURL = URL(string: "http://127.0.0.1:18765/api/system/health-check")!
    private var backendProcess: Process?

    func bootstrap() async {
        startBundledBackendIfNeeded()
        await checkHealth()
    }

    func checkHealth() async {
        isChecking = true
        status = .checking
        defer { isChecking = false }

        do {
            var request = URLRequest(url: healthURL)
            request.timeoutInterval = 2.5
            let (data, response) = try await URLSession.shared.data(for: request)
            guard let http = response as? HTTPURLResponse, (200..<300).contains(http.statusCode) else {
                throw URLError(.badServerResponse)
            }
            let version = Self.apiVersion(from: data) ?? "unknown"
            webURL = localURL
            status = .live("Running embedded SgodAI Core Engine \(version).")
            reloadToken += 1
        } catch {
            if backendProcess != nil {
                try? await Task.sleep(for: .milliseconds(700))
                if await retryHealthCheck() {
                    return
                }
            }
            if let staticURL = Bundle.main.url(forResource: "index", withExtension: "html", subdirectory: "public") {
                webURL = staticURL
                status = .staticFallback
                reloadToken += 1
            } else {
                status = .unavailable("Local API unavailable and bundled public/index.html was not found.")
            }
        }
    }

    private func retryHealthCheck() async -> Bool {
        for _ in 0..<8 {
            do {
                var request = URLRequest(url: healthURL)
                request.timeoutInterval = 1.5
                let (data, response) = try await URLSession.shared.data(for: request)
                guard let http = response as? HTTPURLResponse, (200..<300).contains(http.statusCode) else {
                    throw URLError(.badServerResponse)
                }
                let version = Self.apiVersion(from: data) ?? "unknown"
                webURL = localURL
                status = .live("Running embedded SgodAI Core Engine \(version).")
                reloadToken += 1
                return true
            } catch {
                try? await Task.sleep(for: .milliseconds(550))
            }
        }
        return false
    }

    private func startBundledBackendIfNeeded() {
        if backendProcess?.isRunning == true {
            return
        }
        guard let executable = Bundle.main.url(forResource: "sgodai-backend", withExtension: nil, subdirectory: "backend") else {
            return
        }

        let support = applicationSupportDirectory()
        let dataDir = support.appendingPathComponent("data", isDirectory: true)
        let logsDir = support.appendingPathComponent("logs", isDirectory: true)
        let envFile = support.appendingPathComponent(".env")
        try? FileManager.default.createDirectory(at: dataDir, withIntermediateDirectories: true)
        try? FileManager.default.createDirectory(at: logsDir, withIntermediateDirectories: true)
        createEnvPlaceholderIfNeeded(at: envFile)

        let process = Process()
        process.executableURL = executable
        process.currentDirectoryURL = Bundle.main.resourceURL
        process.environment = backendEnvironment(dataDir: dataDir, envFile: envFile)

        let logURL = logsDir.appendingPathComponent("backend.log")
        if !FileManager.default.fileExists(atPath: logURL.path) {
            FileManager.default.createFile(atPath: logURL.path, contents: nil)
        }
        if let logHandle = try? FileHandle(forWritingTo: logURL) {
            _ = try? logHandle.seekToEnd()
            process.standardOutput = logHandle
            process.standardError = logHandle
        }

        do {
            try process.run()
            backendProcess = process
        } catch {
            status = .unavailable("Embedded backend failed to start: \(error.localizedDescription)")
        }
    }

    private func backendEnvironment(dataDir: URL, envFile: URL) -> [String: String] {
        var env = ProcessInfo.processInfo.environment
        env["SGODAI_HOST"] = "127.0.0.1"
        env["SGODAI_PORT"] = String(port)
        env["SGODAI_PUBLIC_DIR"] = Bundle.main.resourceURL?.appendingPathComponent("public").path
        env["SGODAI_CONFIG_DIR"] = Bundle.main.resourceURL?.appendingPathComponent("configs").path
        env["SGODAI_DATA_DIR"] = dataDir.path
        env["SGODAI_DB_PATH"] = dataDir.appendingPathComponent("sgodai.sqlite").path
        env["SGODAI_ENV_FILE"] = envFile.path
        env["SGODAI_LOG_LEVEL"] = "info"
        env["PYTHONUNBUFFERED"] = "1"
        return env
    }

    private func applicationSupportDirectory() -> URL {
        let base = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask)[0]
        let directory = base.appendingPathComponent("SgodAI", isDirectory: true)
        try? FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        return directory
    }

    private func createEnvPlaceholderIfNeeded(at url: URL) {
        guard !FileManager.default.fileExists(atPath: url.path) else { return }
        let template = """
        # SgodAI desktop environment.
        # Fill these when you need DeepSeek or email from the installed app.
        DEEPSEEK_API_KEY=
        SMTP_HOST=smtp.qq.com
        SMTP_PORT=465
        SMTP_USE_SSL=true
        SMTP_USERNAME=
        SMTP_PASSWORD=
        SMTP_FROM=
        SMTP_FROM_NAME=SgodAI Market Radar
        """
        try? template.write(to: url, atomically: true, encoding: .utf8)
    }

    private static func apiVersion(from data: Data) -> String? {
        guard
            let root = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
            let components = root["components"] as? [String: Any],
            let api = components["api"] as? [String: Any],
            let version = api["version"] as? String
        else {
            return nil
        }
        return version
    }

    deinit {
        backendProcess?.terminate()
    }
}
