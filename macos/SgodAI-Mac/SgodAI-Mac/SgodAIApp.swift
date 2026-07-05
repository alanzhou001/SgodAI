import SwiftUI

@main
struct SgodAIApp: App {
    @StateObject private var backend = LocalBackend()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(backend)
                .frame(minWidth: 1180, minHeight: 760)
                .task {
                    await backend.bootstrap()
                }
        }
        .windowStyle(.titleBar)
        .commands {
            CommandGroup(after: .appInfo) {
                Button("Check Local API") {
                    Task { await backend.checkHealth() }
                }
                .keyboardShortcut("r", modifiers: [.command, .shift])
            }
        }
    }
}
