import SwiftUI

struct ContentView: View {
    @EnvironmentObject private var backend: LocalBackend

    var body: some View {
        VStack(spacing: 0) {
            HeaderBar()
            Divider()
            WebContainer(url: backend.webURL)
                .overlay(alignment: .top) {
                    if backend.isChecking {
                        ProgressView()
                            .controlSize(.small)
                            .padding(10)
                            .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 8))
                            .padding(.top, 12)
                    }
                }
        }
        .background(Color(nsColor: .windowBackgroundColor))
    }
}

private struct HeaderBar: View {
    @EnvironmentObject private var backend: LocalBackend
    @Environment(\.openURL) private var openURL

    var body: some View {
        HStack(spacing: 12) {
            VStack(alignment: .leading, spacing: 2) {
                Text("SgodAI Market Radar")
                    .font(.headline)
                Text("Core Engine + Agent Copilot")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }

            Spacer()

            StatusBadge(status: backend.status)

            Button {
                Task { await backend.checkHealth() }
            } label: {
                Label("Health", systemImage: "stethoscope")
            }
            .disabled(backend.isChecking)

            Button {
                backend.reloadToken += 1
            } label: {
                Label("Reload", systemImage: "arrow.clockwise")
            }

            Button {
                openURL(backend.webURL)
            } label: {
                Label("Browser", systemImage: "safari")
            }
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 10)
    }
}

private struct StatusBadge: View {
    let status: LocalBackend.Status

    var body: some View {
        Label(status.title, systemImage: status.symbol)
            .font(.caption.weight(.medium))
            .foregroundStyle(status.color)
            .padding(.horizontal, 10)
            .padding(.vertical, 6)
            .background(status.color.opacity(0.12), in: Capsule())
            .help(status.detail)
    }
}

#Preview {
    ContentView()
        .environmentObject(LocalBackend())
}
