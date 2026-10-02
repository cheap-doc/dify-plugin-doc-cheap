## Privacy Policy

This plugin connects Dify to the doc.cheap API (`https://api.doc.cheap`), which reads identity documents. It is published by doc.cheap. The full privacy policy of the service is at https://doc.cheap/privacy.

### Data Collection

- **Document images.** When you run Recognize Document, the image you give (a file, or the image at the URL you give) is sent to the doc.cheap API. Identity documents carry personal data: names, dates of birth, document numbers, nationality and a portrait.
- **Image URLs.** When you give an image URL, the plugin downloads that image itself and sends its bytes to the API; the URL is not sent.
- **API key.** The plugin needs a doc.cheap API key. Dify stores it as an encrypted credential; the plugin sends it only in the `Authorization` header of requests to `api.doc.cheap` and never logs it.
- **Scan IDs and references.** Get Scan and Delete Scan send the scan ID you give. An optional reference label you set is stored with the scan.
- The plugin itself stores nothing and collects no analytics.

### Data Usage

The image is used only to read the document and return the result to your Dify workflow. The only third-party service the plugin calls is doc.cheap (privacy policy: https://doc.cheap/privacy), plus the host of an image URL you supply, to download that image.

### Data Retention

- The image itself is not stored by doc.cheap after the reading.
- A scan result is kept only for its retention window: the Keep Result (Hours) option of the call (0 keeps nothing), or the account's default when the option is empty. You can delete a stored result at any time with the Delete Scan tool.
- Calls with the public sandbox key `sk_sandbox_public` store no result.

### Contact

Privacy questions: admin@doc.cheap.
