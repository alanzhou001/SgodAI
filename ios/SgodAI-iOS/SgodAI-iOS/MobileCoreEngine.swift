import Foundation
import SwiftUI

@MainActor
final class MobileCoreEngine: ObservableObject {
    enum Status {
        case checking
        case connected(String)
        case staticDemo
        case invalidEndpoint(String)

        var title: String {
            switch self {
            case .checking:
                return "Checking"
            case .connected:
                return "Core API"
            case .staticDemo:
                return "Offline Demo"
            case .invalidEndpoint:
                return "Setup"
            }
        }

        var detail: String {
            switch self {
            case .checking:
                return "Checking Core Engine connection."
            case .connected(let message):
                return message
            case .staticDemo:
                return "Using the bundled static frontend. Configure a Core Engine URL for real data."
            case .invalidEndpoint(let message):
                return message
            }
        }

        var symbol: String {
            switch self {
            case .checking:
                return "clock"
            case .connected:
                return "checkmark.circle"
            case .staticDemo:
                return "iphone"
            case .invalidEndpoint:
                return "exclamationmark.triangle"
            }
        }

        var color: Color {
            switch self {
            case .checking:
                return .secondary
            case .connected:
                return .green
            case .staticDemo:
                return .orange
            case .invalidEndpoint:
                return .red
            }
        }
    }

    @AppStorage("coreEngineBaseURL") var coreEngineBaseURL = ""
    @Published var status: Status = .checking
    @Published var isChecking = false
    @Published var reloadToken = 0
    @Published var webURL: URL = Bundle.main.url(
        forResource: "index",
        withExtension: "html",
        subdirectory: "public"
    ) ?? URL(string: "about:blank")!

    func bootstrap() async {
        await checkHealth()
    }

    func checkHealth() async {
        isChecking = true
        status = .checking
        defer { isChecking = false }

        let endpoint = coreEngineBaseURL.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !endpoint.isEmpty else {
            loadBundledDemo()
            return
        }
        guard let baseURL = URL(string: endpoint), ["http", "https"].contains(baseURL.scheme?.lowercased()) else {
            status = .invalidEndpoint("Enter a valid http or https Core Engine URL.")
            return
        }

        let healthURL = baseURL.appending(path: "api/system/health-check")
        do {
            var request = URLRequest(url: healthURL)
            request.timeoutInterval = 4
            let (data, response) = try await URLSession.shared.data(for: request)
            guard let http = response as? HTTPURLResponse, (200..<300).contains(http.statusCode) else {
                throw URLError(.badServerResponse)
            }
            let version = Self.apiVersion(from: data) ?? "unknown"
            webURL = baseURL
            status = .connected("Connected to SgodAI Core Engine \(version).")
            reloadToken += 1
        } catch {
            loadBundledDemo()
        }
    }

    func saveEndpoint(_ value: String) async {
        coreEngineBaseURL = value.trimmingCharacters(in: .whitespacesAndNewlines)
        await checkHealth()
    }

    func useBundledDemo() {
        coreEngineBaseURL = ""
        loadBundledDemo()
    }

    private func loadBundledDemo() {
        if let staticURL = Bundle.main.url(forResource: "index", withExtension: "html", subdirectory: "public") {
            webURL = staticURL
        }
        status = .staticDemo
        reloadToken += 1
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
