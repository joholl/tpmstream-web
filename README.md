# tpmstream-web

This is a simple web interface for [tpmstream](https://github.com/joholl/tpmstream).

## Deployment

tpmstream-web is hosted at  [joholl.github.io/tpmstream-web](https://joholl.github.io/tpmstream-web/).

## How to get TPM traffic?

If using [tpm2-tss](https://github.com/tpm2-software/tpm2-tss)/[tpm2-tools](https://github.com/tpm2-software/tpm2-tools)/..., you can use the the `pcap` TCTI to dump the traffic.
Just copy-paste contents of `tpm2_log.pcap` as a hex string!

```bash
tpm2_getrandom --tcti=pcap:device:/dev/tpmrm0 --hex 10
xxd -p -c0 tpm2_log.pcap
# copy-paste the output to the web page
```
