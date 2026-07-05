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
                return "Local API"
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
    @Published var webURL = URL(string: "http://127.0.0.1:8000/")!

    private let localURL = URL(string: "http://127.0.0.1:8000/")!
    private let healthURL = URL(string: "http://127.0.0.1:8000/api/system/health-check")!

    func bootstrap() async {
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
            status = .live("Connected to SgodAI local API \(version).")
            reloadToken += 1
        } catch {
            if let staticURL = Bundle.main.url(forResource: "index", withExtension: "html", subdirectory: "public") {
                webURL = staticURL
                status = .staticFallback
                reloadToken += 1
            } else {
                status = .unavailable("Local API unavailable and bundled public/index.html was not found.")
            }
        }
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
}
