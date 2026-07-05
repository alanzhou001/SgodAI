import SwiftUI
import WebKit

struct WebContainer: NSViewRepresentable {
    @EnvironmentObject private var backend: LocalBackend
    let url: URL

    func makeNSView(context: Context) -> WKWebView {
        let configuration = WKWebViewConfiguration()
        configuration.defaultWebpagePreferences.allowsContentJavaScript = true
        configuration.preferences.setValue(true, forKey: "allowFileAccessFromFileURLs")

        let webView = WKWebView(frame: .zero, configuration: configuration)
        webView.allowsBackForwardNavigationGestures = true
        webView.setValue(false, forKey: "drawsBackground")
        return webView
    }

    func updateNSView(_ webView: WKWebView, context: Context) {
        let currentURL = webView.url?.absoluteString
        let targetURL = url.absoluteString
        let tokenChanged = context.coordinator.lastReloadToken != backend.reloadToken

        guard currentURL != targetURL || tokenChanged else { return }
        context.coordinator.lastReloadToken = backend.reloadToken

        if url.isFileURL {
            let allowingReadAccessTo = url.deletingLastPathComponent()
            webView.loadFileURL(url, allowingReadAccessTo: allowingReadAccessTo)
        } else {
            webView.load(URLRequest(url: url))
        }
    }

    func makeCoordinator() -> Coordinator {
        Coordinator()
    }

    final class Coordinator {
        var lastReloadToken = -1
    }
}
