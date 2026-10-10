// Reconnaissance de texte pour les livrets scannés (macOS uniquement).
// Usage : swift src/ocr.swift data/originaux/monopoly.pdf > data/raw/monopoly.txt
// Le texte de chaque page est séparé par un saut de page (\f), comme pdftotext.
//
// ponytail: les lignes sortent dans l'ordre donné par Vision ; sur une page à
// plusieurs colonnes, elles peuvent se mélanger. À trier par colonne si ça gêne.
import Foundation
import PDFKit
import Vision

guard CommandLine.arguments.count == 2,
      let document = PDFDocument(url: URL(fileURLWithPath: CommandLine.arguments[1]))
else {
    FileHandle.standardError.write("Usage : swift src/ocr.swift scan.pdf\n".data(using: .utf8)!)
    exit(1)
}

var pages: [String] = []
for numero in 0..<document.pageCount {
    let page = document.page(at: numero)!
    let cadre = page.bounds(for: .mediaBox)
    let echelle: CGFloat = 3  // environ 216 points par pouce
    let taille = NSSize(width: cadre.width * echelle, height: cadre.height * echelle)
    guard let image = page.thumbnail(of: taille, for: .mediaBox)
        .cgImage(forProposedRect: nil, context: nil, hints: nil)
    else {
        pages.append("")
        continue
    }
    let requete = VNRecognizeTextRequest()
    requete.recognitionLevel = .accurate
    requete.recognitionLanguages = ["fr-FR"]
    requete.usesLanguageCorrection = true
    try VNImageRequestHandler(cgImage: image).perform([requete])
    let lignes = (requete.results ?? []).compactMap { $0.topCandidates(1).first?.string }
    pages.append(lignes.joined(separator: "\n"))
}
print(pages.joined(separator: "\u{0C}"), terminator: "")
