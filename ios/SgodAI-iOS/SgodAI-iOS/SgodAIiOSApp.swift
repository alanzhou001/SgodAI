import SwiftUI

@main
struct SgodAIiOSApp: App {
    @StateObject private var coreEngine = MobileCoreEngine()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(coreEngine)
                .task {
                    await coreEngine.bootstrap()
                }
        }
    }
}
