import SwiftUI

struct ContentView: View {
    @EnvironmentObject private var coreEngine: MobileCoreEngine
    @Environment(\.openURL) private var openURL
    @State private var showingSettings = false

    var body: some View {
        NavigationStack {
            WebContainer(url: coreEngine.webURL)
                .overlay(alignment: .top) {
                    if coreEngine.isChecking {
                        ProgressView()
                            .controlSize(.regular)
                            .padding(10)
                            .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 10))
                            .padding(.top, 12)
                    }
                }
                .navigationTitle("SgodAI")
                .navigationBarTitleDisplayMode(.inline)
                .toolbar {
                    ToolbarItem(placement: .topBarLeading) {
                        StatusBadge(status: coreEngine.status)
                    }
                    ToolbarItemGroup(placement: .topBarTrailing) {
                        Button {
                            Task { await coreEngine.checkHealth() }
                        } label: {
                            Image(systemName: "stethoscope")
                        }
                        .disabled(coreEngine.isChecking)

                        Button {
                            coreEngine.reloadToken += 1
                        } label: {
                            Image(systemName: "arrow.clockwise")
                        }

                        Button {
                            showingSettings = true
                        } label: {
                            Image(systemName: "gearshape")
                        }
                    }
                }
                .sheet(isPresented: $showingSettings) {
                    SettingsView()
                        .environmentObject(coreEngine)
                }
        }
    }
}

private struct StatusBadge: View {
    let status: MobileCoreEngine.Status

    var body: some View {
        Label(status.title, systemImage: status.symbol)
            .font(.caption.weight(.semibold))
            .foregroundStyle(status.color)
            .lineLimit(1)
            .padding(.horizontal, 8)
            .padding(.vertical, 5)
            .background(status.color.opacity(0.12), in: Capsule())
            .accessibilityLabel(status.detail)
    }
}

private struct SettingsView: View {
    @EnvironmentObject private var coreEngine: MobileCoreEngine
    @Environment(\.dismiss) private var dismiss
    @State private var endpoint = ""

    var body: some View {
        NavigationStack {
            Form {
                Section("Core Engine") {
                    TextField("http://192.168.1.10:8000/", text: $endpoint)
                        .textInputAutocapitalization(.never)
                        .keyboardType(.URL)
                        .autocorrectionDisabled()

                    Button {
                        Task {
                            await coreEngine.saveEndpoint(endpoint)
                            dismiss()
                        }
                    } label: {
                        Label("Save and Check", systemImage: "checkmark.circle")
                    }

                    Button(role: .destructive) {
                        coreEngine.useBundledDemo()
                        endpoint = ""
                        dismiss()
                    } label: {
                        Label("Use Bundled Demo", systemImage: "iphone")
                    }
                }

                Section("Status") {
                    Label(coreEngine.status.title, systemImage: coreEngine.status.symbol)
                        .foregroundStyle(coreEngine.status.color)
                    Text(coreEngine.status.detail)
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                }

                Section("Notes") {
                    Text("iOS cannot execute the bundled Python backend. Run SgodAI Core Engine on your Mac, local server, or cloud host, then enter its URL here.")
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                }
            }
            .navigationTitle("Connection")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
            .onAppear {
                endpoint = coreEngine.coreEngineBaseURL
            }
        }
        .presentationDetents([.medium, .large])
    }
}

#Preview {
    ContentView()
        .environmentObject(MobileCoreEngine())
}
