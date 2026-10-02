# doc.cheap for Dify

**Author:** doc-cheap (Teoh Chin Heng) · **Version:** 0.0.1 · **Type:** tool
**Source:** https://github.com/cheap-doc/dify-plugin-doc-cheap

doc.cheap reads identity documents. Send a photo or scan of a passport, national ID card or driver's licence and get back the printed fields and the machine-readable zone, with its check digits verified, as structured JSON. You pay $0.01 per recognised document; when the image holds no document, or cannot be read, the call costs nothing. A new account gets 100 free credits every month.

## Tools

| Tool | What it does | Cost |
| --- | --- | --- |
| Recognize Document | Reads a document from an image file or an image URL (`POST /v1/scans`) | $0.01 when a document is recognised, otherwise free |
| Get Scan | Reads back a stored result by its ID (`GET /v1/scans/{id}`) | free |
| Delete Scan | Deletes a stored result before its window ends (`DELETE /v1/scans/{id}`) | free |
| Get Usage | Shows the credit balance and this month's usage (`GET /v1/usage`) | free |

## Setup

1. Install the plugin from the Dify Marketplace.
2. Get an API key: sign up at https://doc.cheap and create a live key (`sk_live_…`) in the cabinet. To try the plugin without an account, use the public sandbox key `sk_sandbox_public` (limited to 10 requests per hour per address; results are not stored, so Get Scan and Delete Scan answer "not found").
3. In Dify, open **Tools → doc.cheap → Authorize** and paste the key into **API Key**. Dify checks the key with `GET /v1/usage`, which spends no credit.

## Usage

Add **Recognize Document** to a workflow or give it to an agent. Pass either:

- **Image File** – a file from a Start node or an upload variable, or
- **Image URL** – a public http or https address of the image (up to 25 MiB).

Optional settings:

- **Expected Country** – the issuing country as a three-letter code such as `GRC`.
- **Reference** – your own label (up to 128 characters), returned with the scan.
- **Return Portrait** – include the cropped portrait in the full answer.
- **Keep Result (Hours)** – how long the result stays readable with Get Scan, 0–8760; empty means the account default, 0 keeps nothing.
- **Idempotency Key** – a retry with the same key returns the first result instead of running again.
- **Simplify** – on by default: a flat summary. Turn it off for the full answer with every field, crop and check.

### Example output (Simplify on)

```json
{
  "id": "0199…",
  "status": "recognized",
  "confidence": "high",
  "billed": true,
  "reference": "order-1042",
  "document_kind": "passport",
  "document_country": "UTO",
  "document_number": "L898902C3",
  "expiry_date": "2031-04-15",
  "is_expired": false,
  "surname": "ERIKSSON",
  "given_names": "ANNA MARIA",
  "birth_date": "1974-08-12",
  "sex": "F",
  "nationality": "UTO",
  "mrz_status": "passed"
}
```

The values above are the fictional specimen of the ICAO 9303 standard. `status` is `recognized`, `no_document_found`, `unreadable`, `unsupported_document` or `rejected`; only `recognized` is billed.

## Connection

The plugin talks only to `https://api.doc.cheap` over HTTPS, with the key in the `Authorization: Bearer` header. When you pass an Image URL, the plugin also downloads that image from its host. Errors carry the API's own error code, a link to its explanation and a request ID.

## Links

- Documentation: https://doc.cheap/docs
- API keys: https://doc.cheap/docs/concepts/api-keys-and-sessions
- Privacy policy: https://doc.cheap/privacy
- Support: admin@doc.cheap
