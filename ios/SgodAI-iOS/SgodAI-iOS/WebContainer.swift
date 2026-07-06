import SwiftUI
import WebKit

struct WebContainer: UIViewRepresentable {
    @EnvironmentObject private var coreEngine: MobileCoreEngine
    let url: URL

    func makeUIView(context: Context) -> WKWebView {
        let configuration = WKWebViewConfiguration()
        configuration.defaultWebpagePreferences.allowsContentJavaScript = true

        let webView = WKWebView(frame: .zero, configuration: configuration)
        webView.allowsBackForwardNavigationGestures = true
        webView.scrollView.contentInsetAdjustmentBehavior = .never
        webView.isOpaque = false
        webView.backgroundColor = .clear
        return webView
    }

    func updateUIView(_ webView: WKWebView, context: Context) {
        let currentURL = webView.url?.absoluteString
        let targetURL = url.absoluteString
        let tokenChanged = context.coordinator.lastReloadToken != coreEngine.reloadToken

        guard currentURL != targetURL || tokenChanged else { return }
        context.coordinator.lastReloadToken = coreEngine.reloadToken

        if url.isFileURL {
            let readAccessURL = url.deletingLastPathComponent()
            webView.loadFileURL(url, allowingReadAccessTo: readAccessURL)
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
